from logger import app_logger
from messenger import send_message
from fetch_excel_data import summarized_excel_object


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


def most_popular_track(music_list):
    """Find and report the most popular track listened to"""
    app_logger.info("Finding most popular track")

    try:
        highest_popularity = 0
        most_popular_song = None

        for hour_data in music_list:
            for hour in hour_data:
                hours_songs = hour_data[hour]['songs']

                for song in hours_songs:
                    song_popularity = int(song['song_popularity'])
                    if song_popularity > highest_popularity:
                        highest_popularity = song_popularity
                        most_popular_song = song

        if most_popular_song:
            message = f'The most popular song you listened to yesterday was *{most_popular_song["song"]}* by *{most_popular_song["artist"]}* with a popularity score of {most_popular_song["song_popularity"]}.'
            app_logger.info("Most popular song found: %s with score %s", most_popular_song['song'], most_popular_song['song_popularity'])
            send_message(message)
        else:
            app_logger.info("No songs found to determine most popular")
    except (KeyError, TypeError) as e:
        app_logger.error("Data structure error in most_popular_track: %s", e)
        raise
    except Exception as e:
        app_logger.error("Error in most_popular_track: %s", e)
        raise


def convert_duration_to_minutes(duration_str):
    """Convert a HH:MM duration string to minutes"""
    try:
        hours, minutes = map(int, duration_str.split(':'))
        return hours * 60 + minutes
    except ValueError as e:
        app_logger.error("Invalid duration format: %s",duration_str)
        raise ValueError(f"Invalid duration format: {duration_str}") from e


def most_listened_hour(music_list):
    """Find and report the hour with the most listening time"""
    app_logger.info("Calculating most listened hour")

    try:
        longest_time_minutes = 0
        hour_of_longest_listens = None

        for hour_data in music_list:
            for hour in hour_data:
                duration_str = hour_data[hour]['minutes_listened']
                duration_minutes = convert_duration_to_minutes(duration_str)
                app_logger.debug("Hour %s: %s minutes", hour, duration_minutes)
                if duration_minutes > longest_time_minutes:
                    longest_time_minutes = duration_minutes
                    hour_of_longest_listens = hour

        if longest_time_minutes != 0:
            hours, minutes = divmod(longest_time_minutes, 60)
            message = f'Yesterday, the hour you listened to most music was at {hour_of_longest_listens} with a listen time of {hours:02}:{minutes:02}'
            app_logger.info("Most listened hour: %s with %02d:%02d", hour_of_longest_listens, hours, minutes)
            send_message(message)
        else:
            app_logger.info('No songs listened to yesterday')
            print('Most listened to hour: No songs listened to yesterday!')
    except KeyError as e:
        app_logger.error("Missing key in most_listened_hour: %s", e)
        raise
    except Exception as e:
        app_logger.error("Error in most_listened_hour: %s", e)
        raise


if __name__ == '__main__':
    app_logger.info("Starting music tracker analysis")
    try:
        app_logger.info("Fetching excel data")
        data = summarized_excel_object()

        app_logger.info("Running top listens analysis")
        top_listens(data, 'songs', 'listens')
        top_listens(data, 'albums', 'listens')
        top_listens(data, 'artists', 'songs')

        app_logger.info("Running popularity and listening hours analysis")
        most_popular_track(data['history'])
        most_listened_hour(data['history'])

        app_logger.info("Analysis completed successfully")
    except KeyError as e:
        app_logger.error("Missing key in data structure: %s", e, exc_info=True)
        print(f"Data error: {e}")
    except ValueError as e:
        app_logger.error("Invalid value in data: %s", e, exc_info=True)
        print(f"Value error: {e}")
    except FileNotFoundError as e:
        app_logger.error("File not found: %s", e, exc_info=True)
        print(f"File not found: {e}")
    except Exception as e:
        app_logger.error("Unexpected %s error: %s", type(e).__name__, e, exc_info=True)
        print(f"Unexpected {type(e).__name__} error: {e}")