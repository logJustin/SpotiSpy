from scripts.download.spotify.get_recently_played import get_tracklist
from scripts.download.supabase.batch_upload import batch_insert_songs_to_supabase
from scripts.general.get_last_hour import last_hour
from scripts.general.logger import app_logger

if __name__ == "__main__":
    hour_ago_epoch = last_hour()
    tracks = get_tracklist(hour_ago_epoch)
    AMOUNT = batch_insert_songs_to_supabase(tracks)
    if(AMOUNT == 0):
        app_logger.info("No songs uploaded.")
    if(AMOUNT == 1):
        app_logger.info("Uploading %s song", AMOUNT)
    if(AMOUNT > 1):
        app_logger.info("Uploading %s songs", AMOUNT)
    