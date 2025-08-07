#!/bin/bash

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

echo "Using base path: $BASE_PATH"

cd "$BASE_PATH" || {
    echo "Error: Could not change to directory $BASE_PATH"
    exit 1
}

VENV_NAME="spotispyvenv"
VENV_PATH="$BASE_PATH/$VENV_NAME"

# Check if we should create/recreate the virtual environment
if [ ! -d "$VENV_PATH" ] || [ "$1" == "--rebuild" ]; then
    # Remove old virtual environment if it exists
    if [ -d "$VENV_PATH" ]; then
        echo "Removing old virtual environment..."
        rm -rf "$VENV_PATH"
    fi

    # Create a new virtual environment
    echo "Creating new virtual environment at $VENV_PATH..."
    python3 -m venv "$VENV_PATH"
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Check if activation worked
if [ "$VIRTUAL_ENV" = "" ]; then
    echo "Virtual environment activation failed!"
    exit 1
fi

# Install required packages
echo "Installing required packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Run your script
echo "Running analysis script..."
python3 main.py --enhanced

echo " "
echo " "

# Deactivate the virtual environment
deactivate

echo "Analysis complete!"