#!/bin/bash

# Change directory to where the Python script is located
cd $HOME/Documents/SpotiSpy

# Path to your virtual environment
VENV_PATH="$HOME/Documents/SpotiSpy/spotispyvenv"

# Activate the virtual environment
source $VENV_PATH/bin/activate

# Install the required packages (optional if already installed)
pip install openpyxl slack_sdk python-dotenv spotipy

# Run your script
python3 excel.py

# Deactivate the virtual environment
deactivate








