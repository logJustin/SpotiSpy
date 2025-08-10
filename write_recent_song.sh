#!/bin/bash

# SpotiSpy Song Collection Script (Hourly Cronjob)
# This script ONLY collects songs from Spotify API and saves to database
# NO Slack messages are sent - that's handled by analysis.sh (daily cronjob)

# Detect which system we're on and set the base path accordingly
if [[ "$(uname)" == "Darwin" ]]; then
    # macOS
    BASE_PATH="/Users/justinreynolds/Documents/SpotiSpy"
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

# Check if activation worked
if [ "$VIRTUAL_ENV" = "" ]; then
    echo "Virtual environment activation failed!"
    exit 1
fi

# Run song collection (NO messaging)
echo "Collecting recent songs from Spotify..."
python3 collect_songs.py --hours 1

# Capture exit code
exit_code=$?

# Deactivate the virtual environment
deactivate

if [ $exit_code -eq 0 ]; then
    echo "Song collection completed successfully!"
else
    echo "Song collection failed with exit code: $exit_code"
fi

exit $exit_code








