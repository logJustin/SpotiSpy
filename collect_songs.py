#!/usr/bin/env python3
"""
Song collection script for SpotiSpy

This script fetches recent songs from Spotify API and saves them to the database.
Used by the hourly cronjob (write_recent_song.sh) to collect listening data
without sending any Slack messages.

Usage:
    python collect_songs.py [--hours N]  # Collect songs from last N hours (default: 1)
"""

import sys
import os
import argparse

# Add the project root to Python path so we can import spotispy modules
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from spotispy.helpers import get_logger, validate_environment_vars, get_last_hour_timestamp
from spotispy.spotify import get_recent_tracks
from spotispy.database import save_songs, check_for_duplicates


def collect_recent_songs(hours_back=1):
    """
    Collect recent songs from Spotify and save to database
    
    Args:
        hours_back: Number of hours back to fetch songs from
        
    Returns:
        Boolean indicating success
    """
    logger = get_logger()
    logger.info("Starting song collection (last %s hours)", hours_back)
    
    try:
        # Validate environment
        is_valid, missing_vars = validate_environment_vars()
        if not is_valid:
            logger.error("Missing environment variables: %s", missing_vars)
            return False
        
        # Calculate timestamp for N hours ago
        from datetime import datetime, timedelta
        hours_ago = datetime.now() - timedelta(hours=hours_back)
        timestamp_ms = int(hours_ago.timestamp() * 1000)
        
        # Fetch recent tracks from Spotify
        logger.info("Fetching recent tracks from Spotify...")
        recent_songs = get_recent_tracks(timestamp_ms, limit=50)
        
        if not recent_songs:
            logger.info("No new songs found from Spotify API")
            return True
        
        logger.info("Found %s songs from Spotify API", len(recent_songs))
        
        # Check for duplicates to avoid saving the same song twice
        logger.info("Checking for duplicates in database...")
        new_songs = check_for_duplicates(recent_songs)
        
        if not new_songs:
            logger.info("All songs already exist in database")
            return True
        
        logger.info("Found %s new songs to save", len(new_songs))
        
        # Save new songs to database
        logger.info("Saving songs to database...")
        success = save_songs(new_songs)
        
        if success:
            logger.info("Successfully saved %s songs to database", len(new_songs))
            return True
        else:
            logger.error("Failed to save songs to database")
            return False
            
    except Exception as e:
        logger.error("Unexpected error in song collection: %s", e, exc_info=True)
        return False


def main():
    """Main function - handles command line arguments and execution"""
    parser = argparse.ArgumentParser(description='Collect recent songs from Spotify')
    parser.add_argument('--hours', type=int, default=1, 
                       help='Number of hours back to fetch songs from (default: 1)')
    
    args = parser.parse_args()
    
    logger = get_logger()
    logger.info("SpotiSpy song collection starting...")
    
    # Validate hours parameter
    if args.hours <= 0:
        logger.error("Hours must be positive number")
        sys.exit(1)
    
    success = collect_recent_songs(args.hours)
    
    if success:
        logger.info("Song collection completed successfully")
        sys.exit(0)
    else:
        logger.error("Song collection completed with errors")
        sys.exit(1)


if __name__ == '__main__':
    main()