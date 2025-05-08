from datetime import datetime
from pprint import pprint
from scripts.download.spotify.spotify_client import spotify_client
from scripts.general.get_last_hour import last_hour
from scripts.general.logger import app_logger

spotify = spotify_client()

def get_tracklist(start_time):
    tracklist = spotify.current_user_recently_played(
        limit=50, after=start_time, before=None)

    song_list = []
    tracklist_length = len(tracklist['items'])
    for i in range(tracklist_length):
        song_data = tracklist['items'][i]
        song_info = {
            "album": song_data['track']['album']['name'],
            "artist": song_data['track']['album']['artists'][0]['name'],
            "duration": int(song_data['track']['duration_ms'])/1000,
            "played_at": datetime.fromisoformat(song_data['played_at']).isoformat(),
            "release_date": song_data['track']['album']['release_date'],
            "song": song_data['track']['name'],
            "song_popularity": song_data['track']['popularity'],
        }
        song_list.append(song_info)
    if not song_list:
        pprint('Zero songs listened to')
        app_logger.info('Zero songs listened to')

    return song_list



if __name__ == '__main__':
    hour_ago_epoch = last_hour()
    tracks = get_tracklist(hour_ago_epoch)
    for index, track in enumerate(tracks):
        pprint(f"{index+1}: {track['song']} by {track['artist']}")
        app_logger.info('%s: %s by %s', index+1, track['song'], track['artist'])
