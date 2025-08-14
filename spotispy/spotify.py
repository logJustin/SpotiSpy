import os
from datetime import datetime
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotispy.helpers import get_logger

load_dotenv()

def normalize_release_date(date_str):
    """
    Normalize Spotify release dates to YYYY-MM-DD format
    Handles formats: YYYY, YYYY-MM, YYYY-MM-DD
    """
    if not date_str:
        return "1900-01-01"  # Default for missing dates
    
    parts = date_str.split('-')
    
    if len(parts) == 1:  # Just year: "1976"
        return f"{parts[0]}-01-01"
    elif len(parts) == 2:  # Year-month: "1967-08"
        return f"{parts[0]}-{parts[1]}-01"
    else:  # Already full date: "1973-01-01"
        return date_str

def create_spotify_client():
    """Create and return authenticated Spotify client"""
    spotify_id = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
    scope = 'user-read-recently-played'

    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=spotify_id, 
        client_secret=spotify_secret, 
        redirect_uri=redirect_uri, 
        scope=scope
    ))

    return spotify


def get_recent_tracks(start_time, limit=50):
    """
    Get recently played tracks from Spotify
    
    Args:
        start_time: Unix timestamp in milliseconds
        limit: Maximum number of tracks to fetch
        
    Returns:
        List of song dictionaries with standardized format
    """
    logger = get_logger()
    spotify = create_spotify_client()
    
    try:
        tracklist = spotify.current_user_recently_played(
            limit=limit, after=start_time, before=None)

        song_list = []
        for item in tracklist['items']:
            song_data = item
            song_info = {
                "album": song_data['track']['album']['name'],
                "artist": song_data['track']['album']['artists'][0]['name'],
                "duration": int(song_data['track']['duration_ms']) / 1000,
                "played_at": datetime.fromisoformat(song_data['played_at'].replace('Z', '+00:00')).isoformat(),
                "release_date": normalize_release_date(song_data['track']['album']['release_date']),
                "song": song_data['track']['name'],
                "song_popularity": song_data['track']['popularity'],
            }
            song_list.append(song_info)

        if not song_list:
            logger.info('No recent songs found from Spotify')
        else:
            logger.info('Fetched %s songs from Spotify', len(song_list))

        return song_list
        
    except Exception as e:
        logger.error("Error fetching from Spotify: %s", e)
        return []


def get_audio_features(track_ids):
    """
    Get audio features (energy, valence, etc.) for tracks
    
    Args:
        track_ids: List of Spotify track IDs
        
    Returns:
        List of audio feature dictionaries
    """
    logger = get_logger()
    spotify = create_spotify_client()
    
    try:
        # Spotify API allows max 100 tracks at a time
        features_list = []
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i:i+100]
            features = spotify.audio_features(batch)
            if features:
                features_list.extend([f for f in features if f is not None])
        
        logger.info('Fetched audio features for %s tracks', len(features_list))
        return features_list
        
    except Exception as e:
        logger.error("Error fetching audio features: %s", e)
        return []


if __name__ == "__main__":
    # Test the Spotify client
    from spotispy.helpers import get_last_hour_timestamp
    
    logger = get_logger()
    logger.info("Testing Spotify client...")
    
    hour_ago = get_last_hour_timestamp()
    tracks = get_recent_tracks(hour_ago, limit=5)
    
    for i, track in enumerate(tracks, 1):
        logger.info('%s: %s by %s', i, track['song'], track['artist'])