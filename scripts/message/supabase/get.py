import os
import json
from collections import defaultdict
from datetime import datetime
import time
import requests
from dotenv import load_dotenv
from scripts.message.analysis.utils import days_duration, find_multiple_played, sum_minutes_per_hour
from scripts.general.logger import app_logger

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SONGS_TABLE = 'songs'

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
}

def get_recent_songs():
    """Fetch songs played within the last hour."""
    one_day_ago_seconds = time.time() - (60 * 60 * 24)
    one_day_ago_epoch = int(one_day_ago_seconds)
    one_hour_ago_iso = datetime.fromtimestamp(one_day_ago_epoch).isoformat() + 'Z'  # Ensure Zulu time for UTC

    endpoint = f"{SUPABASE_URL}/rest/v1/{SONGS_TABLE}?played_at=gte.{one_hour_ago_iso}&order=played_at.desc"

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        print("res", json.dumps(response.json(), indent=2))
        response.raise_for_status()
        return response.json()
    
    except requests.RequestException as e:
        print(f"Error fetching recent songs: {e}")
        return []
    

def build_day_from_supabase(songs_data):
    """Convert Supabase song rows into structured history format"""

    # Group songs by hour
    hourly_history = defaultdict(list)

    for song in songs_data:
        # Assuming song['played_at'] is ISO timestamp string
        dt = datetime.fromisoformat(song['played_at'])
        hour_key = dt.strftime("%H:00")
        hourly_history[hour_key].append(song)

    # Structure history list like the Excel version
    history = []
    for hour, songs in hourly_history.items():
        history.append({
            hour: {
                "songs": songs
            }
        })

    return {"history": history}


def summarized_supabase_object():
    try:
        songs_data = get_recent_songs()
        app_logger.info("Fetched %s recent songs", len(songs_data))

        if not songs_data:
            app_logger.info("No recent songs found")
            return {}

        day = build_day_from_supabase(songs_data)
        sum_minutes_per_hour(day)
        find_multiple_played(day, 'song')
        find_multiple_played(day, 'artist')
        find_multiple_played(day, 'album')
        days_duration(day)
        return day, songs_data

    except Exception as e:
        app_logger.error("Error building summarized_supabase_object: %s", e)
        raise
