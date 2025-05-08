import os
from dotenv import load_dotenv
import requests


load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SONGS_TABLE = 'songs'

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

def song_exists(song_name, played_at_timestamp):
    endpoint = f"{SUPABASE_URL}/rest/v1/{SONGS_TABLE}"

    params = {
        'song': f"eq.{song_name}",
        'played_at': f"eq.{played_at_timestamp}"
    }

    try:
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return bool(response.json())
        else:
            print(f"  Supabase check error: Status {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print(f"  Error checking if song exists in Supabase: {str(e)}")
        return False


if __name__ == "__main__":
    song_already_exists = song_exists("With You", "2024-10-08T12:42:49.161000+00:00")
    print('exists', song_already_exists)
    