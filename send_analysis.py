from messenger import send_message
from fetch_excel_data import summarized_excel_object
from datetime import datetime, timedelta
from pprint import pprint


def top_listens(data, type, verb):
    # Sort the data based on the number of times each song has been listened to
    sorted_tracks = sorted(
        data[f'multiple_listened_{type}'].items(), key=lambda x: x[1], reverse=True)
    # Take the top three items (artists, albums, songs)
    top_three_tracks = sorted_tracks[:3]
    length_of_items = len(top_three_tracks)

    if length_of_items == 0:
        print(f'Top listens: No multiples of {type} listened to yesterday!')
        return
    if length_of_items == 1:
        message_first_part = f"*Your top {type[:-1]} from yesterday!*\n"
        message_second_part = ""
        for x in range(length_of_items):
            message_second_part += f"{top_three_tracks[x][1]} {verb}: {top_three_tracks[x][0]}\n"
    else:
        message_first_part = f"*Your top {length_of_items} {type} from yesterday!*\n"
        message_second_part = ""
        for x in range(length_of_items):
            message_second_part += f"{top_three_tracks[x][1]} {verb}: {top_three_tracks[x][0]}\n"

    send_message(message_first_part + message_second_part)


def most_popular_track(data):
    highest_popularity = 0
    most_popular_song = None

    for hour_data in data:
        for hour in hour_data:
            hours_songs = hour_data[hour]['songs']

            for song in hours_songs:
                song_popularity = int(song['song_popularity'])
                if song_popularity > highest_popularity:
                    highest_popularity = song_popularity
                    most_popular_song = song

    message = f'The most popular song you listened to yesterday was *{most_popular_song["song"]}* by *{most_popular_song["artist"]}* with a popularity score of {most_popular_song["song_popularity"]}.'
    send_message(message)


def convert_duration_to_minutes(duration_str):
    hours, minutes = map(int, duration_str.split(':'))
    return hours * 60 + minutes


def most_listened_hour(data):
    longest_time_minutes = 0
    hour_of_longest_listens = None

    for hour_data in data:
        for hour in hour_data:
            duration_str = hour_data[hour]['minutes_listened']
            duration_minutes = convert_duration_to_minutes(duration_str)
            # print(hour, duration_minutes)
            if duration_minutes > longest_time_minutes:
                longest_time_minutes = duration_minutes
                hour_of_longest_listens = hour

    if longest_time_minutes != 0:
        hours, minutes = divmod(longest_time_minutes, 60)
        message = f'Yesterday, the hour you listened to most music was at {hour_of_longest_listens} with a listen time of {hours:02}:{minutes:02}'
        send_message(message)
    else:
        print(f'Most listened to hour: No songs listened to yesterday!')
        return


if __name__ == '__main__':
    try:
        data = summarized_excel_object()
        top_listens(data, 'songs', 'listens')
        top_listens(data, 'albums', 'listens')
        top_listens(data, 'artists', 'songs')
        most_popular_track(data['history'])
        most_listened_hour(data['history'])

        # total amount of songs I listened to across how many hours:minutes
    except Exception as e:
        print(e)
