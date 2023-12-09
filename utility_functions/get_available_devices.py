import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
import os
from dotenv import load_dotenv
load_dotenv()

spotify_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
scope = 'user-read-playback-state'

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=spotify_id, client_secret=spotify_secret, redirect_uri=redirect_uri, scope=scope))


def get_devices():
    device_list = spotify.devices()
    pprint(device_list)


if __name__ == '__main__':
    get_devices()
