from collections import defaultdict
from scripts.general.logger import app_logger
from scripts.message.slack.messenger import send_message


def format_duration(time):
    minutes, seconds = divmod(time, 60)
    total = f"{int(minutes)}:{str(int(seconds)).zfill(2)}"
    return total

def sum_minutes_per_hour(day):
    for hour in day['history']:
        hourly_duration = 0
        for songs_played_time in hour:
            for song in hour[songs_played_time]['songs']:
                hourly_duration += float(song['duration'])
            hour[songs_played_time]['minutes_listened'] = format_duration(hourly_duration)


def find_multiple_played(day, type):
    item_counts = defaultdict(int)
    hours_multiple_plays = {}

    for hour_data in day['history']:
        for song in hour_data.values():
            for info in song['songs']:
                if type == 'artist':
                    artist_song_album = info[type]
                    item_counts[artist_song_album] += 1
                else:
                    artist_song_album = f"{info[type]} by {info['artist']}"
                    item_counts[artist_song_album] += 1

    hours_multiple_plays = {artist_song_album: count for artist_song_album,
                            count in item_counts.items() if count > 1}
    day[f'multiple_listened_{type}s'] = hours_multiple_plays

def days_duration(day):
    total_seconds = 0
    for hour_data in day['history']:
        for _, data in hour_data.items():
            # Splitting the time string into minutes and seconds
            minutes_listened = data['minutes_listened'].split(':')
            # Converting minutes and seconds to integers
            minutes_duration = int(minutes_listened[0])
            seconds_duration = int(minutes_listened[1])
            # Calculating total duration in seconds
            total_seconds += minutes_duration * 60 + seconds_duration

    # Calculating hours, minutes, and seconds from total_seconds
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    day['time_listened'] = f'{hours:02}:{minutes:02}:{seconds:02}'
    # print(f'duration: {hours:02}:{minutes:02}:{seconds:02}')

def top_listens(music_list, item, verb):
    """Track and report top listened tracks, albums, or artists"""
    app_logger.info("Calculating top %s listens", item)
    
    try:
        # Sort the data based on the number of times each song has been listened to
        sorted_tracks = sorted(
            music_list[f'multiple_listened_{item}'].items(), key=lambda x: x[1], reverse=True)
        # Take the top three items (artists, albums, songs)
        top_three_tracks = sorted_tracks[:3]
        length_of_items = len(top_three_tracks)

        if length_of_items == 0:
            app_logger.info('Top listens: No multiples of %s listened to yesterday!', item)
            return

        if length_of_items == 1:
            message_first_part = f"*Your top {item[:-1]} from yesterday!*\n"
            message_second_part = ""
            for x in range(length_of_items):
                message_second_part += f"{top_three_tracks[x][1]} {verb}: {top_three_tracks[x][0]}\n"
        else:
            message_first_part = f"*Your top {length_of_items} {item} from yesterday!*\n"
            message_second_part = ""
            for x in range(length_of_items):
                message_second_part += f"{top_three_tracks[x][1]} {verb}: {top_three_tracks[x][0]}\n"

        app_logger.info("Sending message with top %s %s", length_of_items, item)
        send_message(message_first_part + message_second_part)
    except KeyError as e:
        app_logger.error("Key error in top_listens for %s: %s", item, e)
        raise
    except Exception as e:
        app_logger.error("Error in top_listens for %s: %s", item, e)
        raise
