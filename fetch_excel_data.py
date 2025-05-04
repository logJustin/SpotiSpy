import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from openpyxl import load_workbook
from logger import app_logger

def open_workbook():
    today = datetime.today().date()
    yesterday = today - timedelta(days=1)
    yesterday_str = str(yesterday)

    workbook_path = os.path.expanduser(f'~/Documents/SpotiSpy/data/{yesterday_str}.xlsx')
    workbook_location = Path(workbook_path)

    if workbook_location.is_file():
        wb = load_workbook(filename=workbook_path)
        return wb
    raise FileNotFoundError(f"No workbook found at: {workbook_location}")


def build_song_info(row):
    return {
        "album": row[2].value,
        "artist": row[1].value,
        "duration": row[3].value,
        "played_at": row[5].value,
        "release_date": row[4].value,
        "song": row[0].value,
        "song_popularity": row[6].value,
    }


def build_day_dictionary(workbook):
    day_dictionary = {'history': []}
    for ws in workbook:
        hourly_key = ws.title
        hours_songs = [build_song_info(row) for row in ws.rows]
        # Create a dictionary for each hour
        day_dictionary['history'].append({hourly_key: {"songs": hours_songs}})
    return day_dictionary


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
        for data in hour_data.items():
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


def summarized_excel_object():
    try:
        wb = open_workbook()
        todays_history = build_day_dictionary(wb)
        sum_minutes_per_hour(todays_history)
        find_multiple_played(todays_history, 'song')
        find_multiple_played(todays_history, 'artist')
        find_multiple_played(todays_history, 'album')
        days_duration(todays_history)
        return todays_history
    except Exception as e:
        app_logger.debug(e)


if __name__ == '__main__':
    try:
        wb = open_workbook()
        todays_history = build_day_dictionary(wb)
        sum_minutes_per_hour(todays_history)
        find_multiple_played(todays_history, 'song')
        find_multiple_played(todays_history, 'artist')
        find_multiple_played(todays_history, 'album')
        days_duration(todays_history)
        app_logger.info(todays_history)

    except FileNotFoundError as e:
        app_logger.debug(e)
    except Exception as e:
        app_logger.debug(e)
