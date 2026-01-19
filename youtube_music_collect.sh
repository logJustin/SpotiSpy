#!/bin/bash

# YouTube Music collection script for SpotiSpy cronjob
# Collects YouTube Music listening history and saves to database
# Runs every 6 hours via cronjob

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source spotispyvenv/bin/activate

# Run the collection script
echo "$(date): Starting YouTube Music collection..."
python collect_youtube_music.py

# Log the exit code
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "$(date): YouTube Music collection completed successfully"
else
    echo "$(date): YouTube Music collection failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE