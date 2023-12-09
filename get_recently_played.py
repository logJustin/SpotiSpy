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


def get_tracklist(start_time):
    tracklist = spotify.current_user_recently_played(
        limit=50, after=start_time, before=None)

    song_list = []
    length = len(tracklist['items'])
    for index in range(length):
        song_data = tracklist['items'][index]
        song_info = {
            "album": song_data['track']['album']['name'],
            "artist": song_data['track']['album']['artists'][0]['name'],
            "duration": int(song_data['track']['duration_ms'])/1000,
            "played_at": song_data['played_at'],
            "release_date": song_data['track']['album']['release_date'],
            "song": song_data['track']['name'],
            "song_popularity": song_data['track']['popularity'],
        }
        song_list.append(song_info)
    if song_list == []:
        pprint('Zero songs listened to')
        return song_list
    else:
        return song_list


if __name__ == '__main__':
    hour_ago_epoch = last_hour()
    list = get_tracklist(hour_ago_epoch)
    for track in range(len(list)):
        pprint(f"{track+1}: {list[track]['song']} by {list[track]['artist']}")
