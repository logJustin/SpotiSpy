from messenger import send_message
from spotify_client import spotify_client
from logger import app_logger

spotify = spotify_client()

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
        app_logger.info("Currently playing %s - %s - %s", track, artist,tid)
        send_message(f"Currently playing {track} by {artist}")
    else:
        app_logger.info('No song playing!')
        send_message("No song is currently playing!")
        print('No song playing!')


if __name__ == '__main__':
    main()
