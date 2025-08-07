#!/usr/bin/env python3
"""
Main entry point for SpotiSpy daily analysis

This replaces the old scripts/message/send_analysis.py and serves as the 
main cronjob entry point for daily music analysis and Slack messaging.
"""

import sys
import os

# Add the project root to Python path so we can import spotispy modules
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from spotispy.helpers import get_logger, validate_environment_vars, is_sunday
from spotispy.database import get_yesterdays_songs
from spotispy.analysis import analyze_listening_day
from spotispy.messages import send_daily_analysis


def run_daily_analysis():
    """
    Run the complete daily analysis pipeline
        
    Returns:
        Boolean indicating success
    """
    logger = get_logger()
    logger.info("Starting daily SpotiSpy analysis")
    
    try:
        # Validate environment
        is_valid, missing_vars = validate_environment_vars()
        if not is_valid:
            logger.error("Missing environment variables: %s", missing_vars)
            return False
        
        # Get yesterday's songs from database
        logger.info("Fetching yesterday's listening data...")
        songs = get_yesterdays_songs()
        
        if not songs:
            logger.warning("No songs found for yesterday")
            # Could still send a "no music listened" message
            return True
        
        logger.info("Found %s songs to analyze", len(songs))
        
        # Analyze the listening data
        logger.info("Running analysis...")
        analysis_results = analyze_listening_day(songs)
        
        # Send to Slack
        logger.info("Sending daily summary to Slack...")
        success = send_daily_analysis(analysis_results, songs)
        
        if success:
            logger.info("Daily analysis completed successfully!")
            return True
        else:
            logger.error("Failed to send daily analysis")
            return False
            
    except KeyError as e:
        logger.error("Missing key in data structure: %s", e, exc_info=True)
        return False
    except ValueError as e:
        logger.error("Invalid value in data: %s", e, exc_info=True)
        return False
    except Exception as e:
        logger.error("Unexpected error in daily analysis: %s", e, exc_info=True)
        return False


def run_weekly_summary():
    """
    Run weekly summary (placeholder for Sunday summaries)
    
    Returns:
        Boolean indicating success
    """
    logger = get_logger()
    logger.info("Running weekly summary...")
    
    # For now, just a placeholder
    from spotispy.messages import send_weekly_summary
    return send_weekly_summary({})


def main():
    """Main function - handles command line arguments and execution"""
    logger = get_logger()
    
    # Check command line arguments
    weekly_only = '--weekly' in sys.argv or '-w' in sys.argv
    help_requested = '--help' in sys.argv or '-h' in sys.argv
    
    if help_requested:
        print("SpotiSpy Daily Analysis")
        print()
        print("Usage: python main.py [options]")
        print()
        print("Options:")
        print("  --weekly, -w      Run weekly summary only (normally auto-detected on Sundays)")
        print("  --help, -h        Show this help message")
        print()
        print("Normal usage (for cronjob):")
        print("  python main.py")
        print()
        return
    
    logger.info("SpotiSpy starting...")
    
    # Determine what to run
    if weekly_only:
        # Force weekly summary
        success = run_weekly_summary()
    elif is_sunday():
        # Run both daily and weekly on Sundays
        daily_success = run_daily_analysis()
        weekly_success = run_weekly_summary()
        success = daily_success and weekly_success
    else:
        # Just run daily analysis
        success = run_daily_analysis()
    
    if success:
        logger.info("SpotiSpy completed successfully")
        sys.exit(0)
    else:
        logger.error("SpotiSpy completed with errors")
        sys.exit(1)


if __name__ == '__main__':
    main()