import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
test_channel_id = "C063AFNSPPE"
spotify_channel_id = "C063HV2H62V"


def send_message(message):
    try:
        # Call the conversations.list method using the WebClient
        result = client.chat_postMessage(
            channel=spotify_channel_id,
            text=message
        )
    except SlackApiError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    message = "Welcome from Kiki's Delivery Service"
    send_message(message)
