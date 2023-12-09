import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
import os
from dotenv import load_dotenv
from messenger import send_message
load_dotenv()

spotify_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
scope = 'user-read-currently-playing'

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=spotify_id, client_secret=spotify_secret, redirect_uri=redirect_uri, scope=scope))


def get_current_song():
    # Get track information
    track = spotify.current_user_playing_track()

    if track is not None:
        artist = track["item"]["artists"][0]["name"]
        t_name = track["item"]["name"]
        t_id = track["item"]["id"]
        return artist, t_name, t_id
    else:
        return None, None, None


def main():
    artist, track, tid = get_current_song()
    if artist and track:
        pprint(f"Currently playing {track} - {artist} - {tid}")
        send_message(f"Currently playing {track} by {artist}")
    else:
        send_message(f"No song is currently playing!")
        print('No song playing!')


if __name__ == '__main__':
    main()
