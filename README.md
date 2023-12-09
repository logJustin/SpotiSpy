# 🎵 Recently Played Songs Tracker 📊

This Python script is your musical companion, designed to fetch and organize your recently played songs from a music streaming service. It leverages the Spotify API to retrieve the tracklist and the openpyxl library for seamless Excel workbook handling.

## Prerequisites 🛠️

Before embarking on your musical journey with this script, ensure you have the necessary dependencies installed: `pip install openpyxl`

## Usage 🚀
Setup Spotify API:

Obtain your Spotify API credentials by creating a new application on the Spotify Developer Dashboard.
Note down your Client ID and Client Secret.
Configure the Script:

Replace get_recently_played and get_last_hour imports with the actual implementations or use them as placeholders and implement your methods.
Insert your Spotify API credentials in the designated script location.
Run the Script:

Execute the script using the following command:
`python excel.py`

## Script Overview 📝
This script harmonizes with your tunes by:

1. 📡 Fetching the tracklist of songs played in the last hour using the get_recently_played and get_last_hour functions.
2. 📊 Creating or opening an Excel workbook (./data/{date}.xlsx), with each worksheet named after the starting hour of the tracklist.
3. ✍️ Writing song details (name, artist, album, duration, release date, played at, song popularity) to the worksheet.
4. 💾 Saving the workbook, ensuring your music data is safely stored.

## Customization 🎨
Data Storage: By default, the script saves the Excel workbook in the ./data/ directory. Customize the storage path by modifying the workbook_path.
Data Columns: Adjust the columns and their order by modifying the write_workbook function where the information is written.
Feel free to customize the script to match your rhythm and preferences. Let the music play! 🎶