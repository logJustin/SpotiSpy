from collections import defaultdict
from datetime import timedelta
from spotispy.helpers import get_logger


def calculate_daily_energy(songs_data):
    """
    Calculate weighted average energy level for the day
    
    Args:
        songs_data: List of songs with 'energy' and 'duration' fields
        
    Returns:
        Float: Energy percentage (0-100)
    """
    if not songs_data:
        return 0
    
    total_weighted_energy = 0
    total_duration = 0
    
    for song in songs_data:
        # Skip songs without energy data
        if 'energy' not in song or 'duration' not in song:
            continue
            
        energy = song['energy']  # 0.0 - 1.0
        duration = song['duration']
        
        total_weighted_energy += energy * duration
        total_duration += duration
    
    if total_duration == 0:
        return 0
    
    # Calculate weighted average and convert to percentage
    avg_energy = total_weighted_energy / total_duration
    return round(avg_energy * 100, 1)


def calculate_daily_mood(songs_data):
    """
    Calculate weighted average mood (valence) level for the day
    
    Args:
        songs_data: List of songs with 'valence' and 'duration' fields
        
    Returns:
        Float: Mood percentage (0-100, where higher = happier)
    """
    if not songs_data:
        return 0
    
    total_weighted_valence = 0
    total_duration = 0
    
    for song in songs_data:
        # Skip songs without valence data
        if 'valence' not in song or 'duration' not in song:
            continue
            
        valence = song['valence']  # 0.0 - 1.0
        duration = song['duration']
        
        total_weighted_valence += valence * duration
        total_duration += duration
    
    if total_duration == 0:
        return 0
    
    # Calculate weighted average and convert to percentage
    avg_valence = total_weighted_valence / total_duration
    return round(avg_valence * 100, 1)


def format_duration(time_seconds):
    """Convert seconds to MM:SS format"""
    minutes, seconds = divmod(int(time_seconds), 60)
    return f"{minutes}:{seconds:02d}"


def calculate_hourly_totals(day_data):
    """Calculate total listening time per hour"""
    for hour_block in day_data['history']:
        for hour_key, hour_data in hour_block.items():
            hourly_duration = 0
            for song in hour_data['songs']:
                hourly_duration += float(song['duration'])
            hour_data['minutes_listened'] = format_duration(hourly_duration)


def find_top_items(day_data, item_type):
    """
    Find multiple-played songs, artists, or albums
    
    Args:
        day_data: Structured day data with history
        item_type: 'song', 'artist', or 'album'
        
    Returns:
        Dictionary with items that were played multiple times
    """
    item_counts = defaultdict(int)

    for hour_block in day_data['history']:
        for hour_key, hour_data in hour_block.items():
            for song in hour_data['songs']:
                if item_type == 'artist':
                    item_key = song[item_type]
                else:
                    item_key = f"{song[item_type]} by {song['artist']}"
                
                item_counts[item_key] += 1

    # Only return items played more than once
    multiple_plays = {item: count for item, count in item_counts.items() if count > 1}
    
    return multiple_plays


def calculate_total_listening_time(day_data):
    """Calculate total listening time for the day"""
    total_seconds = 0
    
    for hour_block in day_data['history']:
        for hour_key, hour_data in hour_block.items():
            # Parse the minutes_listened time string
            if 'minutes_listened' in hour_data:
                time_parts = hour_data['minutes_listened'].split(':')
                minutes = int(time_parts[0])
                seconds = int(time_parts[1])
                total_seconds += minutes * 60 + seconds

    # Format as HH:MM:SS
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours:02}:{minutes:02}:{seconds:02}'


def find_most_popular_song(history_data):
    """Find the song with highest Spotify popularity score"""
    highest_popularity = 0
    most_popular_song = None

    for hour_block in history_data:
        for hour_key, hour_data in hour_block.items():
            for song in hour_data['songs']:
                popularity = int(song.get('song_popularity', 0))
                if popularity > highest_popularity:
                    highest_popularity = popularity
                    most_popular_song = song

    return most_popular_song


def find_peak_listening_hour(history_data):
    """Find the hour with the most listening time"""
    peak_minutes = 0
    peak_hour = None
    
    for hour_block in history_data:
        for hour_key, hour_data in hour_block.items():
            if 'minutes_listened' not in hour_data:
                continue
                
            time_parts = hour_data['minutes_listened'].split(':')
            total_minutes = int(time_parts[0]) + int(time_parts[1]) / 60
            
            if total_minutes > peak_minutes:
                peak_minutes = total_minutes
                peak_hour = hour_key

    return peak_hour, peak_minutes


def format_listening_duration(song_list):
    """Format total listening time in a human-readable way"""
    try:
        total_seconds = sum(song['duration'] for song in song_list)
        time_string = str(timedelta(seconds=int(total_seconds)))
        
        time_parts = time_string.split(':')
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
        
        if hours > 0:
            return f'{hours} hours, {minutes} minutes, and {seconds} seconds'
        elif minutes > 0:
            return f'{minutes} minutes and {seconds} seconds'
        else:
            return f'{seconds} seconds'
            
    except Exception as e:
        logger = get_logger()
        logger.error("Error formatting duration: %s", e)
        return "unknown duration"


def analyze_listening_day(raw_songs):
    """
    Main analysis function - processes raw songs into insights
    
    Args:
        raw_songs: List of song dictionaries from database
        
    Returns:
        Dictionary with all analysis results
    """
    if not raw_songs:
        return {
            'total_songs': 0,
            'total_time': '0:00:00',
            'top_songs': {},
            'top_artists': {},
            'top_albums': {},
            'most_popular': None,
            'peak_hour': None,
            'energy_level': 0,
            'mood_level': 0
        }
    
    # Import here to avoid circular imports
    from spotispy.database import group_songs_by_hour
    
    # Group songs by hour for analysis
    day_data = group_songs_by_hour(raw_songs)
    
    # Calculate hourly totals
    calculate_hourly_totals(day_data)
    
    # Find top items
    top_songs = find_top_items(day_data, 'song')
    top_artists = find_top_items(day_data, 'artist') 
    top_albums = find_top_items(day_data, 'album')
    
    # Calculate totals and peaks
    total_time = calculate_total_listening_time(day_data)
    most_popular = find_most_popular_song(day_data['history'])
    peak_hour, peak_minutes = find_peak_listening_hour(day_data['history'])
    
    # Calculate mood/energy (will be 0 if no audio features available)
    energy_level = calculate_daily_energy(raw_songs)
    mood_level = calculate_daily_mood(raw_songs)
    
    return {
        'total_songs': len(raw_songs),
        'total_time': total_time,
        'total_time_formatted': format_listening_duration(raw_songs),
        'top_songs': top_songs,
        'top_artists': top_artists,
        'top_albums': top_albums,
        'most_popular': most_popular,
        'peak_hour': peak_hour,
        'peak_minutes': peak_minutes,
        'energy_level': energy_level,
        'mood_level': mood_level,
        'raw_data': raw_songs,
        'structured_data': day_data
    }


if __name__ == "__main__":
    # Test analysis functions
    logger = get_logger()
    logger.info("Testing analysis functions...")
    
    # Test with sample data
    sample_songs = [
        {
            'song': 'Test Song',
            'artist': 'Test Artist',
            'album': 'Test Album',
            'duration': 200,
            'energy': 0.8,
            'valence': 0.6,
            'song_popularity': 75,
            'played_at': '2025-03-15T10:30:00Z'
        }
    ]
    
    results = analyze_listening_day(sample_songs)
    logger.info("Analysis complete: %s songs, energy: %s%%, mood: %s%%", 
                results['total_songs'], results['energy_level'], results['mood_level'])