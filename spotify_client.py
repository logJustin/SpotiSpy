
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from logger import app_logger

load_dotenv()

def spotify_client():
    spotify_id = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
    scope = 'user-read-recently-played'

    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=spotify_id, client_secret=spotify_secret, redirect_uri=redirect_uri, scope=scope))

    return spotify

if __name__ == "__main__":
    client = spotify_client()
    app_logger.info("Spotify client created successfully!")
    # Example usage
    recent_tracks = client.current_user_recently_played(limit=5)
    app_logger.info("Found %s recent tracks", len(recent_tracks['items']))
    