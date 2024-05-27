#!/bin/bash

# Check if Python is installed and its version
command -v python3 &>/dev/null || { echo "Python 3 is not installed. Please install Python 3 to continue."; exit 1; }
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    echo "Python version must be 3.10 or higher. You have Python $PYTHON_VERSION."
    exit 1
fi

# Check for pip and venv
python3 -m pip --version &>/dev/null || { echo "pip is not installed. Please install pip."; exit 1; }
python3 -m venv --help &>/dev/null || { echo "venv is not installed. Please install the Python venv module."; exit 1; }

# Check for ensurepip
python3 -c "import ensurepip" &>/dev/null || { 
    echo "The ensurepip module is not available, which is needed to create a virtual environment."
    echo "On Debian/Ubuntu systems, you can install it by running: sudo apt install python3.x-venv"
    echo "After installing the python3-venv package, please rerun this script."
    exit 1; 
}

# Check for the virtual environment folder
if [ ! -d "tui_venv" ]; then
    # Create the virtual environment
    python3 -m venv tui_venv
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

# Run the main.py script
python3 application/main.py
