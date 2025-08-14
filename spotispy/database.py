import os
import time
import requests
import urllib.parse
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from spotispy.helpers import get_logger

# Define Central Time timezone
CENTRAL_TZ = timezone(timedelta(hours=-5))  # CDT (Central Daylight Time)

load_dotenv()


def parse_datetime_robust(datetime_str):
    """
    Robustly parse datetime strings with various microsecond formats
    Handles both Z suffix and +00:00 timezone formats
    """
    # Handle Z suffix
    if datetime_str.endswith('Z'):
        datetime_str = datetime_str.replace('Z', '+00:00')
    
    # Split datetime and timezone parts
    if '+' in datetime_str:
        dt_part, tz_part = datetime_str.rsplit('+', 1)
        tz_part = '+' + tz_part
    else:
        dt_part = datetime_str
        tz_part = ''
    
    # Handle microseconds - ensure they have 6 digits
    if '.' in dt_part:
        base_part, microsec_part = dt_part.rsplit('.', 1)
        # Pad or truncate to 6 digits
        microsec_part = microsec_part.ljust(6, '0')[:6]
        dt_part = f"{base_part}.{microsec_part}"
    
    # Reconstruct the datetime string
    full_datetime_str = dt_part + tz_part
    
    return datetime.fromisoformat(full_datetime_str)


SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SONGS_TABLE = 'songs'

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
}


def get_yesterdays_songs():
    """Get all songs played in the last 24 hours from Supabase (Central Time)"""
    logger = get_logger()
    
    # Get current time in Central timezone
    now_central = datetime.now(CENTRAL_TZ)
    
    # Get 24 hours ago in Central time, then convert to UTC for database query
    one_day_ago_central = now_central - timedelta(hours=24)
    one_day_ago_utc = one_day_ago_central.astimezone(timezone.utc)
    one_day_ago_iso = one_day_ago_utc.isoformat().replace('+00:00', 'Z')

    endpoint = f"{SUPABASE_URL}/rest/v1/{SONGS_TABLE}?played_at=gte.{one_day_ago_iso}&order=played_at.desc"

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        songs = response.json()
        
        logger.info("Fetched %s songs from database", len(songs))
        return songs
        
    except requests.RequestException as e:
        logger.error("Error fetching from database: %s", e)
        return []


def get_songs_for_date_range(start_date, end_date):
    """
    Get songs for a specific date range
    
    Args:
        start_date: ISO date string (e.g., '2025-03-15')
        end_date: ISO date string (e.g., '2025-03-21')
        
    Returns:
        List of song dictionaries
    """
    logger = get_logger()
    
    endpoint = f"{SUPABASE_URL}/rest/v1/{SONGS_TABLE}?played_at=gte.{start_date}T00:00:00Z&played_at=lt.{end_date}T23:59:59Z&order=played_at.desc"

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        songs = response.json()
        
        logger.info("Fetched %s songs for date range %s to %s", len(songs), start_date, end_date)
        return songs
        
    except requests.RequestException as e:
        logger.error("Error fetching date range from database: %s", e)
        return []


def get_songs_for_single_date(date_str):
    """
    Get songs for a specific single date
    
    Args:
        date_str: ISO date string (e.g., '2025-03-15')
        
    Returns:
        List of song dictionaries for that date
    """
    logger = get_logger()
    
    # Query from start of date to start of next date
    start_time = f"{date_str}T00:00:00Z"
    
    # Calculate next day
    from datetime import datetime, timedelta
    date_obj = datetime.fromisoformat(date_str)
    next_date = date_obj + timedelta(days=1)
    end_time = next_date.strftime("%Y-%m-%dT00:00:00Z")
    
    endpoint = f"{SUPABASE_URL}/rest/v1/{SONGS_TABLE}?played_at=gte.{start_time}&played_at=lt.{end_time}&order=played_at.desc"

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        songs = response.json()
        
        logger.info("Fetched %s songs for date %s", len(songs), date_str)
        return songs
        
    except requests.RequestException as e:
        logger.error("Error fetching songs for date %s: %s", date_str, e)
        return []


def save_songs(song_list):
    """
    Save songs to Supabase database
    
    Args:
        song_list: List of song dictionaries to save
        
    Returns:
        Boolean indicating success
    """
    logger = get_logger()
    
    if not song_list:
        logger.info("No songs to save")
        return True
    
    endpoint = f"{SUPABASE_URL}/rest/v1/{SONGS_TABLE}"
    
    try:
        response = requests.post(endpoint, headers=headers, json=song_list, timeout=10)
        response.raise_for_status()
        
        logger.info("Successfully saved %s songs to database", len(song_list))
        return True
        
    except requests.RequestException as e:
        logger.error("Error saving to database: %s", e)
        if hasattr(e, 'response') and e.response is not None:
            logger.error("Response status: %s", e.response.status_code)
            logger.error("Response body: %s", e.response.text)
        return False


def group_songs_by_hour(songs_data):
    """
    Group songs by hour for analysis
    
    Args:
        songs_data: List of song dictionaries
        
    Returns:
        Dictionary with hourly structure for analysis
    """
    if not songs_data:
        return {"history": []}
    
    # Group songs by hour
    hourly_history = defaultdict(list)

    for song in songs_data:
        # Parse the ISO timestamp (UTC) and convert to Central Time for grouping
        dt_utc = datetime.fromisoformat(song['played_at'].replace('Z', '')).replace(tzinfo=timezone.utc)
        dt_central = dt_utc.astimezone(CENTRAL_TZ)
        hour_key = dt_central.strftime("%H:00")
        hourly_history[hour_key].append(song)

    # Structure history list for compatibility with existing analysis
    history = []
    for hour, songs in hourly_history.items():
        history.append({
            hour: {
                "songs": songs
            }
        })

    return {"history": history}


def check_for_duplicates(songs_to_check):
    """
    Check if songs already exist in database to avoid duplicates
    
    Args:
        songs_to_check: List of song dictionaries
        
    Returns:
        List of songs that don't exist in database
    """
    logger = get_logger()
    
    if not songs_to_check:
        return []
    
    # Get played_at times to check and normalize format
    timestamps = []
    for song in songs_to_check:
        # Parse and re-format to ensure consistent timestamp format
        dt = parse_datetime_robust(song['played_at'])
        # Store as ISO with Z suffix for consistency
        normalized_ts = dt.isoformat().replace('+00:00', 'Z')
        timestamps.append(normalized_ts)
    
    # Query existing songs with these timestamps
    # Use URL encoding for the timestamp values
    timestamp_filter = ",".join(urllib.parse.quote(f'"{ts}"') for ts in timestamps)
    endpoint = f"{SUPABASE_URL}/rest/v1/{SONGS_TABLE}?played_at=in.({timestamp_filter})&select=played_at"
    
    try:
        logger.debug("Duplicate check endpoint: %s", endpoint)
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        existing_songs = response.json()
        logger.debug("Found %s existing songs in database", len(existing_songs))
        
        # Normalize existing timestamps for comparison
        existing_timestamps = set()
        for song in existing_songs:
            dt = parse_datetime_robust(song['played_at'])
            normalized_ts = dt.isoformat().replace('+00:00', 'Z')
            existing_timestamps.add(normalized_ts)
        
        # Filter out songs that already exist using normalized timestamps
        new_songs = []
        for i, song in enumerate(songs_to_check):
            if timestamps[i] not in existing_timestamps:
                new_songs.append(song)
        
        logger.info("Found %s new songs out of %s total", len(new_songs), len(songs_to_check))
        return new_songs
        
    except requests.RequestException as e:
        logger.error("Error checking for duplicates: %s", e)
        # If we can't check, better to risk duplicates than lose data
        return songs_to_check


if __name__ == "__main__":
    # Test database functions
    logger = get_logger()
    logger.info("Testing database connection...")
    
    songs = get_yesterdays_songs()
    logger.info("Found %s songs from yesterday", len(songs))
    
    if songs:
        grouped = group_songs_by_hour(songs[:5])  # Test with first 5 songs
        logger.info("Grouped into %s hourly buckets", len(grouped['history']))