import os
from datetime import datetime 
from dotenv import load_dotenv
import requests
from scripts.download.supabase.check_duplicate_record import song_exists
from scripts.general.logger import app_logger

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SONGS_TABLE = 'songs'

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'  # Don't return the inserted rows
}

def batch_insert_songs_to_supabase(songs_data):
    """Batch insert songs into Supabase after checking for duplicates."""
    new_songs = []
    total_songs_added = 0

    for song_data in songs_data:
        # Check if song already exists in the DB
        if song_exists(song_data['song'], song_data['played_at']):
            played_at_time = datetime.fromisoformat(song_data['played_at']).strftime('%Y-%m-%d %H:%M')
            print(f"PRINT:   > Duplicate found for {song_data['song']} at {played_at_time}." )
            continue  # Skip this song if it already exists
        new_songs.append(song_data)

    if new_songs:
        # Send new songs to Supabase in a batch request
        endpoint = f"{SUPABASE_URL}/rest/v1/{SONGS_TABLE}"

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=new_songs,
                timeout=10
            )

            if response.status_code == 201:
                total_songs_added = len(new_songs)
            else:
                app_logger.info("  Supabase error: Status %s, %s", response.status_code, response.text)
        except Exception as e:
            app_logger.info("  Error inserting to Supabase: %s", str(e))
    
    return total_songs_added

def normalize_played_at(played_at):
    try:
        dt = datetime.fromisoformat(played_at)
        return dt.isoformat()
    except Exception:
        return played_at   
    
if __name__ == "__main__":
    batch_insert_songs_to_supabase([{"song": "360", "artist": "Charli xcx", "album": "BRAT", "duration": 133.805, "release_date": "2024-06-07", "played_at": "2025-02-12T21:39:48.911000+00:00", "song_popularity": 80},{"song": "360", "artist": "Charli xcx", "album": "BRAT", "duration": 133.805, "release_date": "2024-06-07", "played_at": "2025-02-12T21:39:48.911000+00:00", "song_popularity": 80}])
    