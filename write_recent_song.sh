#!/bin/bash

# SpotiSpy Song Collection Script (Hourly Cronjob)
# This script collects songs from both Spotify API and YouTube Music and saves to database
# NO Slack messages are sent - that's handled by analysis.sh (daily cronjob)

# Detect which system we're on and set the base path accordingly
if [[ "$(uname)" == "Darwin" ]]; then
    # macOS
    BASE_PATH="/Users/justinreynolds/Documents/Programming/SpotiSpy"
elif [[ -d "/home/justinreynolds" ]]; then
    # Raspberry Pi
    BASE_PATH="/home/justinreynolds/Documents/SpotiSpy"
else
    BASE_PATH="$(pwd)"
fi

echo "Song collection starting - base path: $BASE_PATH"

cd "$BASE_PATH" || {
    echo "Error: Could not change to directory $BASE_PATH"
    exit 1
}

VENV_NAME="spotispyvenv"
VENV_PATH="$BASE_PATH/$VENV_NAME"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    echo "Please run analysis.sh first to create the environment"
    exit 1
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Suppress urllib3 OpenSSL warning
export PYTHONWARNINGS="ignore"

# Check if activation worked
if [ "$VIRTUAL_ENV" = "" ]; then
    echo "Virtual environment activation failed!"
    exit 1
fi

# Run song collection from both sources (NO messaging)
echo "Collecting recent songs from Spotify..."
python3 collect_songs.py --hours 1
spotify_exit_code=$?

if [ $spotify_exit_code -eq 0 ]; then
    echo "Spotify collection completed successfully"
else
    echo "Spotify collection failed with exit code: $spotify_exit_code"
fi

echo "Collecting songs from YouTube Music..."
python3 -m spotispy.youtube_music
youtube_exit_code=$?

if [ $youtube_exit_code -eq 0 ]; then
    echo "YouTube Music collection completed successfully"
else
    echo "YouTube Music collection failed with exit code: $youtube_exit_code"
fi

# Overall exit code: fail if either source failed
if [ $spotify_exit_code -eq 0 ] && [ $youtube_exit_code -eq 0 ]; then
    exit_code=0
else
    exit_code=1
fi

# Deactivate the virtual environment
deactivate

if [ $exit_code -eq 0 ]; then
    echo "Song collection from all sources completed successfully!"
else
    echo "Song collection completed with errors (exit code: $exit_code)"
fi

exit $exit_code








