import os
from datetime import datetime
from dotenv import load_dotenv
import requests
import pandas as pd
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

def process_excel_file(file_path):
    """Process an Excel file and insert songs into Supabase."""
    app_logger.info("Processing file: %s", os.path.basename(file_path))

    try:
        excel_file = pd.ExcelFile(file_path)
        total_songs = 0
        field_map = ['song', 'artist', 'album', 'duration', 'release_date', 'played_at', 'song_popularity']
        all_songs_data = []

        for sheet in excel_file.sheet_names:
            try:
                df = excel_file.parse(sheet, header=None).dropna(how='all')
                if df.empty:
                    continue
            except Exception as e:
                print(f"  > Error reading worksheet {sheet}: {str(e)}")
                continue

            for _, row in df.iterrows():
                values = row.tolist()
                if pd.isna(values[0]) or pd.isna(values[1]):
                    continue  # Must have at least song and artist

                song_data = {
                    field_map[i]: values[i]
                    for i in range(min(len(values), len(field_map)))
                    if pd.notna(values[i])
                }

                # Format fields
                if 'release_date' in song_data:
                    try:
                        song_data['release_date'] = pd.to_datetime(song_data['release_date']).strftime('%Y-%m-%d')
                    except:
                        val = song_data['release_date']
                        if isinstance(val, (int, str)) and str(val).isdigit():
                            song_data['release_date'] = f"{val}-01-01"

                if 'played_at' in song_data:
                    try:
                        song_data['played_at'] = normalize_played_at(song_data['played_at'])
                    except:
                        pass

                if 'song' in song_data and 'artist' in song_data:
                    all_songs_data.append(song_data)  # Collect song data for later processing

        # Check for duplicates before inserting
        total_songs = batch_insert_songs_to_supabase(all_songs_data)

        app_logger.info("Completed processing file %s. Total songs added: %s", os.path.basename(file_path), total_songs)
        return total_songs

    except Exception as e:
        app_logger.info("Error processing file %s: %s", os.path.basename(file_path), str(e))
        return 0

def batch_insert_songs_to_supabase(songs_data):
    """Batch insert songs into Supabase after checking for duplicates."""
    new_songs = []
    total_songs_added = 0

    for song_data in songs_data:
        song_data['played_at'] = normalize_played_at(song_data['played_at'])
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
            
            app_logger.info("Uploading: %s", new_songs)

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

def main():
    # Get the directory containing Excel files
    excel_dir = "/Users/justinreynolds/Documents/SpotiSpy/data"
    
    if not os.path.isdir(excel_dir):
        app_logger.info("Error: %s is not a valid directory", excel_dir)
        return
    
    # Get list of Excel files
    excel_files = [
        os.path.join(excel_dir, f) for f in os.listdir(excel_dir)
        if f.endswith('.xlsx')
    ]
    
    if not excel_files:
        app_logger.info("No Excel files found in %s", excel_dir)
        return
    
    app_logger.info("Found %s Excel files to process", len(excel_files))
    
    # Process each Excel file
    total_songs_processed = 0
    for file_path in excel_files:
        songs_processed = process_excel_file(file_path)
        total_songs_processed += songs_processed
    
    app_logger.info("All files processed. Total songs added to Supabase: %s", total_songs_processed)

if __name__ == "__main__":
    main()
    # insert_song_to_supabase( {"song": "360", "artist": "Charli xcx", "album": "BRAT", "duration": 133.805, "release_date": "2024-06-07", "played_at": "2025-02-12T21:39:48.911000+00:00", "song_popularity": 80})
    