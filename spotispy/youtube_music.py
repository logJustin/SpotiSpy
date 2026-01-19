import os
import time
import traceback
from datetime import datetime
from dotenv import load_dotenv
from ytmusicapi import YTMusic
from .spotify import create_spotify_client, normalize_release_date
from .helpers import get_logger
from .database import save_songs, check_youtube_music_duplicates

load_dotenv()

def get_recent_youtube_music_history(ytmusic_client, hours_limit=2):
    """Get recent YouTube Music listening history (last ~2 hours) and enrich with Spotify data"""
    logger = get_logger()
    
    try:
        raw_history = ytmusic_client.get_history()
        missing = 0
        
        if not raw_history:
            return []
        
        # Limit to approximately last 2 hours (estimate ~20 songs per hour)
        max_songs = hours_limit * 20
        limited_history = raw_history[:max_songs]
        
        recent_songs = []
        total_songs = len(limited_history)
        logger.info(f"Processing {total_songs} recent songs from YouTube Music history (last {hours_limit} hours)")
        
        for i, song in enumerate(limited_history, 1):
            # 1. Skip if song data is missing
            if not song:
                continue

            # 2. Robust Album Extraction
            # Check if 'album' exists AND is not None before accessing 'name'
            album_obj = song.get('album')
            if album_obj and isinstance(album_obj, dict):
                album_name = album_obj.get('name', 'Unknown Album')
            else:
                album_name = 'Single' # Common for Remixes/UGC on YT

            # 3. Robust Artist Extraction
            artists = song.get('artists', [])
            artist_name = artists[0].get('name', 'Unknown Artist') if artists else 'Unknown Artist'
            
            # 4. Get Spotify Data with rate limiting
            spotify_data = get_spotify_data(song['title'], album_name, artist_name)
            
            if spotify_data == ['1900-01-01', 0]:
                missing += 1
            
            # Always format the song, even with missing Spotify data
            formatted_song = format_song(song, spotify_data)
            if formatted_song:  # Only add if formatting succeeded
                recent_songs.append(formatted_song)
                
            # Progress indicator and rate limiting
            if i % 10 == 0:
                logger.info(f"Processed {i}/{total_songs} songs ({i/total_songs*100:.1f}%)")
            time.sleep(0.2)  # Rate limiting to prevent API timeouts
            
        logger.info(f"{missing} missing songs out of {len(limited_history)}")
        if missing > 0:
            logger.warning(f"Could not find Spotify data for {missing} songs")
        
        return recent_songs
    except Exception as e:
        logger.error(f"Error getting YouTube Music history: {e}")
        return []

def get_spotify_data(song_title, youtube_album, artist):
    """Get spotify song data with fallback logic"""
    logger = get_logger()
    
    try:
        spotify_client = create_spotify_client()
        
        # 1. Try specific field search
        query = f"track:{song_title} artist:{artist}"
        if youtube_album:
            query += f" album:{youtube_album}"
            
        results = spotify_client.search(q=query, limit=5, type='track', market='US')
        tracks = results.get('tracks', {}).get('items', [])

        # 2. Fallback: Search without album if no results (Album names often mismatch)
        if not tracks:
            query_fallback = f"track:{song_title} artist:{artist}"
            results = spotify_client.search(q=query_fallback, limit=5, type='track', market='US')
            tracks = results.get('tracks', {}).get('items', [])

        if not tracks:
            logger.debug(f"No Spotify results found for '{song_title}' by '{artist}'")
            return ['1900-01-01', 0]

        # Pick the first result
        best_match = tracks[0]
        
        # Uncomment for debugging:
        # print(f"Match found: {best_match['name']} on {best_match['album']['name']}")
        
        return [
            normalize_release_date(best_match['album'].get('release_date', '1900-01-01')),
            best_match.get('popularity', 0)
        ]

    except Exception as e:
        logger.error(f"Error getting spotify data for '{song_title}' by '{artist}': {e}")
        return ['1900-01-01', 0]

def format_song(song, spotify_data):
    """Standardize the song object with default values when Spotify data is missing"""
    try:
        # Use default values if Spotify data is missing or invalid
        release_date = '1900-01-01'
        popularity = 0
        
        if spotify_data and len(spotify_data) >= 2:
            release_date = normalize_release_date(spotify_data[0])
            popularity = spotify_data[1]
            
        return {
            "song": song.get('title'),
            "artist": song['artists'][0]['name'] if song.get('artists') else 'Unknown',
            "album": song.get('album', {}).get('name', 'Single'),
            "duration": song.get('duration_seconds'),
            "release_date": release_date,
            "played_at": datetime.now().isoformat(),
            "song_popularity": popularity,
            "source": 'YoutubeMusic'
        }
    except Exception as e:
        logger.error(f"Error formatting song '{song.get('title', 'Unknown')}': {e}")
        return None


def collect_youtube_music_songs():
    """
    Collect YouTube Music songs and save to database with duplicate checking
    
    Returns:
        Boolean indicating success
    """
    logger = get_logger()
    
    try:
        browser_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'browser.json')
        logger.info(f"Using browser auth file: {browser_path}")
        ytmusic = YTMusic(browser_path)
        
        # Get all YouTube Music history
        songs = get_recent_youtube_music_history(ytmusic)
        
        if not songs:
            logger.info("No songs found from YouTube Music")
            return True
            
        logger.info(f"Found {len(songs)} songs from YouTube Music")
        
        # Add small delay to ensure any previous database transactions are committed
        logger.debug("Waiting for database consistency...")
        time.sleep(3)
        
        # Check for duplicates using YouTube Music-specific logic (content-based)
        logger.info("Checking for duplicates in database...")
        new_songs = check_youtube_music_duplicates(songs, hours_back=2)
        
        if not new_songs:
            logger.info("All songs already exist in database")
            return True
            
        logger.info(f"Found {len(new_songs)} new songs to save")
        
        # Save new songs to database
        logger.info("Saving songs to database...")
        success = save_songs(new_songs)
        
        if success:
            logger.info(f"Successfully saved {len(new_songs)} songs to database")
            return True
        else:
            logger.error("Failed to save songs to database")
            return False
            
    except Exception as e:
        logger.error(f"Error collecting YouTube Music songs: {e}")
        traceback.print_exc()
        return False


# Test code when run directly
if __name__ == "__main__":
    import sys
    logger = get_logger()
    logger.info("YouTube Music collection starting...")
    
    success = collect_youtube_music_songs()
    
    if success:
        logger.info("YouTube Music collection completed successfully")
        sys.exit(0)
    else:
        logger.error("YouTube Music collection completed with errors")
        sys.exit(1)
