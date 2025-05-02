#!/bin/bash

# Path to your virtual environment
VENV_PATH="$HOME/Documents/SpotiSpy/spotispyvenv"

# Activate the virtual environment
source $VENV_PATH/bin/activate

# Install the required packages
pip install openpyxl slack_sdk python-dotenv spotipy

# Run your script
python3 $HOME/Documents/SpotiSpy/send_analysis.py

# Deactivate the virtual environment
deactivate
