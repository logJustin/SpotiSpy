"""
Weekly Analysis Module for SpotiSpy

Provides comprehensive weekly listening analytics including:
- Total listening time and song counts
- Daily patterns and trends
- Top artists and album deep dives
- Streak tracking and personal records
- Album binge detection
- Listening consistency analysis
"""

from collections import defaultdict, Counter
from datetime import datetime, timedelta
from spotispy.helpers import get_logger, get_date_string, format_time_duration


def get_last_7_days_data():
    """
    Get listening data for the last 7 days
    
    Returns:
        Dictionary with date strings as keys and song lists as values
    """
    from spotispy.database import get_songs_for_single_date
    
    logger = get_logger()
    songs_by_day = {}
    
    for days_ago in range(7):
        date_str = get_date_string(days_ago)
        songs = get_songs_for_single_date(date_str)
        songs_by_day[date_str] = songs
        logger.info("Date %s: %s songs", date_str, len(songs))
    
    return songs_by_day


def calculate_daily_totals(songs_by_day):
    """
    Calculate daily listening totals
    
    Args:
        songs_by_day: Dictionary with date keys and song lists as values
        
    Returns:
        Dictionary with daily statistics
    """
    daily_stats = {}
    
    for date, songs in songs_by_day.items():
        total_seconds = sum(song.get('duration', 0) for song in songs)
        total_minutes = total_seconds / 60
        
        daily_stats[date] = {
            'songs': len(songs),
            'total_seconds': total_seconds,
            'total_minutes': total_minutes,
            'formatted_time': format_time_duration(total_seconds)
        }
    
    return daily_stats


def find_weekly_top_artists(songs_by_day, limit=5):
    """
    Find top artists across the entire week
    
    Args:
        songs_by_day: Dictionary with date keys and song lists as values
        limit: Number of top artists to return
        
    Returns:
        List of tuples (artist, total_seconds, song_count)
    """
    artist_stats = defaultdict(lambda: {'seconds': 0, 'songs': 0})
    
    for date, songs in songs_by_day.items():
        for song in songs:
            artist = song.get('artist', 'Unknown Artist')
            duration = song.get('duration', 0)
            
            artist_stats[artist]['seconds'] += duration
            artist_stats[artist]['songs'] += 1
    
    # Sort by total listening time
    sorted_artists = sorted(
        artist_stats.items(),
        key=lambda x: x[1]['seconds'],
        reverse=True
    )
    
    return [
        (artist, stats['seconds'], stats['songs'])
        for artist, stats in sorted_artists[:limit]
    ]


def detect_album_binges(songs_by_day, min_consecutive=3):
    """
    Detect album listening sessions (3+ consecutive songs from same album)
    
    Args:
        songs_by_day: Dictionary with date keys and song lists as values
        min_consecutive: Minimum consecutive songs to count as a binge
        
    Returns:
        List of album binge sessions
    """
    all_binges = []
    
    for date, songs in songs_by_day.items():
        if not songs:
            continue
            
        # Sort songs by played_at time
        sorted_songs = sorted(songs, key=lambda x: x.get('played_at', ''))
        
        current_sequence = []
        
        for song in sorted_songs:
            album = song.get('album', '')
            artist = song.get('artist', '')
            
            # Check if this continues the current album sequence
            if (current_sequence and 
                album == current_sequence[-1].get('album', '') and
                artist == current_sequence[-1].get('artist', '')):
                current_sequence.append(song)
            else:
                # End of sequence - check if it was long enough to be a binge
                if len(current_sequence) >= min_consecutive:
                    total_duration = sum(s.get('duration', 0) for s in current_sequence)
                    all_binges.append({
                        'date': date,
                        'album': current_sequence[0].get('album', ''),
                        'artist': current_sequence[0].get('artist', ''),
                        'song_count': len(current_sequence),
                        'total_duration': total_duration,
                        'formatted_duration': format_time_duration(total_duration)
                    })
                
                # Start new sequence
                current_sequence = [song]
        
        # Check final sequence
        if len(current_sequence) >= min_consecutive:
            total_duration = sum(s.get('duration', 0) for s in current_sequence)
            all_binges.append({
                'date': date,
                'album': current_sequence[0].get('album', ''),
                'artist': current_sequence[0].get('artist', ''),
                'song_count': len(current_sequence),
                'total_duration': total_duration,
                'formatted_duration': format_time_duration(total_duration)
            })
    
    # Sort by duration (longest binges first)
    return sorted(all_binges, key=lambda x: x['total_duration'], reverse=True)


def analyze_listening_patterns(daily_stats):
    """
    Analyze weekly listening patterns and trends
    
    Args:
        daily_stats: Dictionary with daily statistics
        
    Returns:
        Dictionary with pattern analysis
    """
    if not daily_stats:
        return {}
    
    # Calculate totals
    total_minutes = sum(stats['total_minutes'] for stats in daily_stats.values())
    total_songs = sum(stats['songs'] for stats in daily_stats.values())
    
    # Find peak and quiet days
    days_with_data = [(date, stats) for date, stats in daily_stats.items() if stats['total_minutes'] > 0]
    
    if not days_with_data:
        return {
            'total_minutes': 0,
            'total_songs': 0,
            'total_formatted': '0 minutes',
            'average_minutes': 0,
            'peak_day': None,
            'quietest_day': None,
            'active_days': 0
        }
    
    peak_date, peak_stats = max(days_with_data, key=lambda x: x[1]['total_minutes'])
    quietest_date, quietest_stats = min(days_with_data, key=lambda x: x[1]['total_minutes'])
    
    # Calculate averages
    average_minutes = total_minutes / 7  # Always 7 days in a week
    active_days = len(days_with_data)
    
    return {
        'total_minutes': total_minutes,
        'total_songs': total_songs,
        'total_formatted': format_time_duration(total_minutes * 60),
        'average_minutes': average_minutes,
        'average_formatted': format_time_duration(average_minutes * 60),
        'peak_day': {
            'date': peak_date,
            'minutes': peak_stats['total_minutes'],
            'formatted': peak_stats['formatted_time'],
            'songs': peak_stats['songs']
        },
        'quietest_day': {
            'date': quietest_date,
            'minutes': quietest_stats['total_minutes'],
            'formatted': quietest_stats['formatted_time'],
            'songs': quietest_stats['songs']
        },
        'active_days': active_days
    }


def calculate_listening_streak(daily_stats):
    """
    Calculate current listening streak (consecutive days with music)
    
    Args:
        daily_stats: Dictionary with daily statistics (ordered by date)
        
    Returns:
        Integer representing current streak in days
    """
    if not daily_stats:
        return 0
    
    # Sort dates in reverse order (newest first)
    sorted_dates = sorted(daily_stats.keys(), reverse=True)
    
    streak = 0
    for date in sorted_dates:
        if daily_stats[date]['total_minutes'] > 0:
            streak += 1
        else:
            break
    
    return streak


def create_weekly_chart(daily_stats, max_width=10):
    """
    Create ASCII chart showing weekly listening pattern
    
    Args:
        daily_stats: Dictionary with daily statistics
        max_width: Maximum width of bars
        
    Returns:
        String with ASCII chart
    """
    if not daily_stats:
        return "No listening data available"
    
    # Sort by date to ensure Monday-Sunday order
    sorted_dates = sorted(daily_stats.keys())
    
    # Find max value for scaling
    max_minutes = max(stats['total_minutes'] for stats in daily_stats.values())
    if max_minutes == 0:
        return "No listening detected this week"
    
    # Day names for display
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    chart_lines = []
    for i, date in enumerate(sorted_dates):
        stats = daily_stats[date]
        day_name = day_names[i] if i < 7 else f"Day{i+1}"
        
        # Calculate bar width
        percentage = (stats['total_minutes'] / max_minutes) * 100 if max_minutes > 0 else 0
        filled_width = int((percentage / 100) * max_width)
        empty_width = max_width - filled_width
        
        # Create bar
        bar = "█" * filled_width + "░" * empty_width
        
        # Format time display
        hours = int(stats['total_minutes'] // 60)
        mins = int(stats['total_minutes'] % 60)
        
        if hours > 0:
            time_display = f"{hours}h {mins}m"
        elif mins > 0:
            time_display = f"{mins}m"
        else:
            time_display = "0m"
        
        # Mark peak day
        is_peak = stats['total_minutes'] == max_minutes and stats['total_minutes'] > 0
        peak_marker = " ← Peak!" if is_peak else ""
        
        line = f"{day_name}: {bar} {time_display}{peak_marker}"
        chart_lines.append(line)
    
    return "\n".join(chart_lines)


def run_weekly_analysis():
    """
    Main function to run complete weekly analysis
    
    Returns:
        Dictionary with complete weekly analysis results
    """
    logger = get_logger()
    logger.info("Starting comprehensive weekly analysis")
    
    try:
        # Get last 7 days of data
        songs_by_day = get_last_7_days_data()
        
        # Calculate daily totals
        daily_stats = calculate_daily_totals(songs_by_day)
        
        # Analyze overall patterns
        patterns = analyze_listening_patterns(daily_stats)
        
        # Find top artists
        top_artists = find_weekly_top_artists(songs_by_day, limit=5)
        
        # Detect album binges
        album_binges = detect_album_binges(songs_by_day)
        
        # Calculate streak
        streak = calculate_listening_streak(daily_stats)
        
        # Create weekly chart
        weekly_chart = create_weekly_chart(daily_stats)
        
        return {
            'daily_stats': daily_stats,
            'patterns': patterns,
            'top_artists': top_artists,
            'album_binges': album_binges[:3],  # Top 3 binges
            'streak': streak,
            'weekly_chart': weekly_chart,
            'raw_data': songs_by_day
        }
        
    except Exception as e:
        logger.error("Error in weekly analysis: %s", e, exc_info=True)
        return None


if __name__ == "__main__":
    # Test weekly analysis
    logger = get_logger()
    logger.info("Testing weekly analysis module...")
    
    results = run_weekly_analysis()
    if results:
        logger.info("Weekly analysis completed successfully")
        logger.info("Total listening time: %s", results['patterns'].get('total_formatted', 'Unknown'))
        logger.info("Peak day: %s", results['patterns'].get('peak_day', {}).get('date', 'Unknown'))
        logger.info("Current streak: %s days", results['streak'])
    else:
        logger.error("Weekly analysis failed")