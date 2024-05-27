#!/bin/bash

# Check if Python is installed
if ! command -v python &>/dev/null; then
    echo "Python is not installed. Please install Python to continue."
    exit 1
fi

# Check Python version (requires Python 3.10 or greater)
PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    echo "Python version must be 3.10 or higher. You have Python $PYTHON_VERSION."
    exit 1
fi

# Check for the virtual environment folder
if [ ! -d "tui_venv" ]; then
    # Create the virtual environment
    python -m venv tui_venv
    echo "Virtual environment created."

    # Activate the virtual environment
    source tui_venv/bin/activate
    echo "Virtual environment activated."

    # Install requirements from the requirements.txt file
    pip install -r requirements.txt
    echo "Dependencies installed."
else
    # Activate the virtual environment
    source tui_venv/bin/activate
    echo "Virtual environment activated."
fi

python application/main.py