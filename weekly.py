#!/usr/bin/env python3
"""
Weekly analysis for SpotiSpy (Sunday summaries)

This can be run standalone or is automatically triggered on Sundays by main.py
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from spotispy.helpers import get_logger, get_date_string
from spotispy.database import get_songs_for_date_range
from spotispy.analysis import analyze_listening_day
from spotispy.messages import send_slack_message, create_progress_bar


def analyze_weekly_data(songs_by_day):
    """
    Analyze a week's worth of listening data
    
    Args:
        songs_by_day: Dictionary with date keys and song lists as values
        
    Returns:
        Dictionary with weekly analysis results
    """
    logger = get_logger()
    
    # Calculate daily totals
    daily_stats = {}
    total_songs = 0
    total_minutes = 0
    
    for date, songs in songs_by_day.items():
        if songs:
            day_analysis = analyze_listening_day(songs)
            
            # Extract just the time in minutes for easier comparison
            time_parts = day_analysis['total_time'].split(':')
            minutes = int(time_parts[0]) * 60 + int(time_parts[1]) + int(time_parts[2]) / 60
            
            daily_stats[date] = {
                'songs': len(songs),
                'minutes': minutes,
                'formatted_time': day_analysis['total_time'],
                'top_artist': list(day_analysis['top_artists'].keys())[0] if day_analysis['top_artists'] else None
            }
            
            total_songs += len(songs)
            total_minutes += minutes
        else:
            daily_stats[date] = {
                'songs': 0,
                'minutes': 0,
                'formatted_time': '0:00:00',
                'top_artist': None
            }
    
    # Find peak day
    peak_day = max(daily_stats.keys(), key=lambda d: daily_stats[d]['minutes'])
    peak_minutes = daily_stats[peak_day]['minutes']
    
    # Calculate average
    avg_minutes = total_minutes / 7 if total_minutes > 0 else 0
    
    # Format total time
    total_hours = int(total_minutes // 60)
    remaining_minutes = int(total_minutes % 60)
    
    return {
        'total_songs': total_songs,
        'total_time_formatted': f"{total_hours}h {remaining_minutes}m",
        'daily_stats': daily_stats,
        'peak_day': peak_day,
        'peak_minutes': peak_minutes,
        'average_minutes': avg_minutes
    }


def create_weekly_chart(daily_stats, max_width=10):
    """Create ASCII chart for weekly listening"""
    if not daily_stats:
        return "No data available"
    
    # Get max value for scaling
    max_minutes = max(stats['minutes'] for stats in daily_stats.values())
    if max_minutes == 0:
        return "No listening detected this week"
    
    chart_lines = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Sort daily_stats by date to ensure proper day order
    sorted_dates = sorted(daily_stats.keys())
    
    for i, date in enumerate(sorted_dates):
        stats = daily_stats[date]
        day_name = days[i] if i < len(days) else f"Day {i+1}"
        
        # Calculate bar width proportional to max value
        if max_minutes > 0:
            bar_width = int((stats['minutes'] / max_minutes) * max_width)
        else:
            bar_width = 0
            
        empty_width = max_width - bar_width
        
        # Create visual bar
        bar = "█" * bar_width + "░" * empty_width
        
        # Format time nicely
        hours = int(stats['minutes'] // 60)
        mins = int(stats['minutes'] % 60)
        time_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
        
        # Add peak day indicator
        peak_indicator = " ← Peak!" if date == max(daily_stats.keys(), key=lambda d: daily_stats[d]['minutes']) else ""
        
        line = f"  {day_name[:3]} {bar}  {time_str}{peak_indicator}"
        chart_lines.append(line)
    
    return "\n".join(chart_lines)


def format_weekly_message(weekly_analysis):
    """Format the weekly summary message"""
    message_parts = []
    
    # Header
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6)
    date_range = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    
    message_parts.append(f"🗓️ WEEKLY WRAPPED - {date_range}")
    message_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # The numbers
    numbers_section = f"📊 THE NUMBERS\n"
    numbers_section += f"🎧 Total: {weekly_analysis['total_time_formatted']} across 7 days\n"
    numbers_section += f"🎵 {weekly_analysis['total_songs']} songs"
    
    # Add peak day info
    if weekly_analysis['peak_minutes'] > 0:
        peak_day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        peak_date = weekly_analysis['peak_day']
        peak_stats = weekly_analysis['daily_stats'][peak_date]
        peak_hours = int(peak_stats['minutes'] // 60)
        peak_mins = int(peak_stats['minutes'] % 60)
        
        numbers_section += f"\n🏆 Personal record: {peak_day_name[list(weekly_analysis['daily_stats'].keys()).index(peak_date)]} with {peak_hours}h {peak_mins}m!"
    
    message_parts.append(numbers_section)
    
    # Weekly chart
    chart_section = f"📈 WEEK AT A GLANCE\nListening Time:\n"
    chart_section += create_weekly_chart(weekly_analysis['daily_stats'])
    message_parts.append(chart_section)
    
    # Consistency insights
    avg_hours = int(weekly_analysis['average_minutes'] // 60)
    avg_mins = int(weekly_analysis['average_minutes'] % 60)
    
    insights_section = f"💫 WEEKLY INSIGHTS\n"
    insights_section += f"📊 Daily average: {avg_hours}h {avg_mins}m\n"
    
    # Find quietest day
    quietest_day = min(weekly_analysis['daily_stats'].keys(), 
                      key=lambda d: weekly_analysis['daily_stats'][d]['minutes'])
    quietest_stats = weekly_analysis['daily_stats'][quietest_day]
    
    if quietest_stats['minutes'] == 0:
        insights_section += f"😴 Quiet day: {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][list(weekly_analysis['daily_stats'].keys()).index(quietest_day)]} (no music)"
    else:
        quiet_hours = int(quietest_stats['minutes'] // 60)
        quiet_mins = int(quietest_stats['minutes'] % 60)
        insights_section += f"😌 Quietest day: {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][list(weekly_analysis['daily_stats'].keys()).index(quietest_day)]} ({quiet_hours}h {quiet_mins}m)"
    
    message_parts.append(insights_section)
    
    return "\n\n".join(message_parts)


def run_weekly_analysis():
    """Run the complete weekly analysis"""
    logger = get_logger()
    logger.info("Starting weekly analysis")
    
    try:
        # Get the last 7 days of data
        songs_by_day = {}
        
        for days_ago in range(7):
            date_str = get_date_string(days_ago)
            
            # For now, we'll use the daily song fetch (this could be optimized)
            if days_ago == 0:
                from spotispy.database import get_yesterdays_songs
                songs = get_yesterdays_songs()
            else:
                # Get songs for specific date - this would need a new database function
                songs = []  # Placeholder - would need get_songs_for_date function
            
            songs_by_day[date_str] = songs
            logger.info("Date %s: %s songs", date_str, len(songs))
        
        # Analyze weekly data
        weekly_analysis = analyze_weekly_data(songs_by_day)
        
        # Format and send message
        message = format_weekly_message(weekly_analysis)
        
        logger.info("Sending weekly summary to Slack...")
        success = send_slack_message(message)
        
        if success:
            logger.info("Weekly analysis completed successfully!")
            return True
        else:
            logger.error("Failed to send weekly analysis")
            return False
            
    except Exception as e:
        logger.error("Error in weekly analysis: %s", e, exc_info=True)
        return False


def main():
    """Main function for standalone weekly analysis"""
    logger = get_logger()
    logger.info("Running standalone weekly analysis...")
    
    success = run_weekly_analysis()
    
    if success:
        logger.info("Weekly analysis completed successfully")
        sys.exit(0)
    else:
        logger.error("Weekly analysis failed")
        sys.exit(1)


if __name__ == '__main__':
    main()