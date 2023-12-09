# 🎵 SpotiSpy 📊

This Python script is your musical companion, designed to fetch and organize your recently played songs from Spotify. It leverages Spotipy for simplicity, the Spotify API to retrieve the tracklist, the openpyxl library for seamless Excel workbook handling, and the Slack integration for automated messaging.

## Prerequisites 🛠️

Before embarking on your musical journey with this script, ensure you have the necessary dependencies installed: `pip install openpyxl spotipy python-dotenv slack_sdk`


## Slack Integration 🚀

To enable Slack integration and receive notifications, follow these steps:

1. Create a Slack App on the [Slack API Dashboard](https://api.slack.com/apps).
2. Add the Slack Bot Token to your .env file:
```
SLACK_BOT_TOKEN=your_slack_bot_token
```
3. Update the `spotify_channel_id` in the script based on your Slack channels inside `messenger.py`.


## Setup Spotify API Credentials 🎧

1. Obtain your Spotify API credentials by creating a new application on the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).
2. Configure your .env file:
    ```
    SPOTIFY_CLIENT_ID=your_client_id
    SPOTIFY_CLIENT_SECRET=your_client_secret
    SPOTIPY_REDIRECT_URI=your_redirect_uri
    ```


## Script Overview 📝
This script harmonizes with your tunes by:

1. 📡 Fetching the tracklist of songs played in the last hour using the get_recently_played and get_last_hour functions.
2. 📊 Creating or opening an Excel workbook (./data/{date}.xlsx), with each worksheet named after the starting hour of the tracklist.
3. ✍️ Writing song details (name, artist, album, duration, release date, played at, song popularity) to the worksheet.
4. 💾 Saving the workbook, ensuring your music data is safely stored.
5. 💻 On Windows Machines, use Task Scheduler to:
    - Execute `excel.py` in the last minute of each hour.
    - Execute `send_analysis.py` each day at the time of your choosing.
        - `send_analysis.py` will deliver a customized Slack messge with the data found in [Features](#features-🌟)


## Features 🌟
In addition to tracking your recently played songs, this script offers additional features:

1. Top Listens: Get insights into your top songs, albums, and artists from yesterday.
2. Most Popular Track: Discover the most popular song you listened to yesterday.
3. Most Listened Hour: Find out the hour during which you listened to the most music.


## Customization 🎨
- Data Storage: By default, the script saves the Excel workbook in the ./data/ directory. Customize the storage path by modifying the workbook_path.
- Data Columns: Adjust the columns and their order by modifying the write_workbook function inside `excel.py` where the information is written.
- Feel free to customize the script to match your rhythm and preferences. Let the music play! 🎶