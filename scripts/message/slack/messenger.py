import os
from pprint import pprint
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from scripts.general.logger import app_logger

load_dotenv()

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
SPOTIFY_CHANNEL_ID = "C063HV2H62V"


def send_message(message):
    try:
        # Call the conversations.list method using the WebClient
        result = client.chat_postMessage(
            channel=SPOTIFY_CHANNEL_ID,
            text=message
        )

        pprint("Message successfully sent!")
        app_logger.info("Message successfully sent!")

        return result
    except SlackApiError as e:
        pprint(f"Error: {e}")
        return None

if __name__ == '__main__':
    send_message('Hello 😃')
    