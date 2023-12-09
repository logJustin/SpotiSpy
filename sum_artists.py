import get_recently_played
from get_last_hour import last_hour

hour_ago_epoch = last_hour()
tracklist = get_recently_played.get_tracklist(hour_ago_epoch)

artist_count = {}  # Use a dictionary to store artist counts

for track in tracklist:
    artist = track['artist']
    if artist in artist_count:
        artist_count[artist] += 1
    else:
        artist_count[artist] = 1


for artist, count in artist_count.items():
    print(f"{artist}: {count}")
