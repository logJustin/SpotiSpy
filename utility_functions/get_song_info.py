import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
import os
from dotenv import load_dotenv
from get_last_hour import last_hour

load_dotenv()

spotify_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
scope = 'user-read-recently-played'

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=spotify_id, client_secret=spotify_secret, redirect_uri=redirect_uri, scope=scope))

if __name__ == '__main__':
    movements_daylily_track_uri = "6AgtouHw1KrKy1PsoLjY3o"
    track = spotify.track(movements_daylily_track_uri, market=None)
    pprint(track)
