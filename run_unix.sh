#!/bin/bash

# Function to prompt user for installation
prompt_install() {
    read -p "$1 is not installed. Would you like to install it now? (y/n): " response
    if [[ "$response" == "y" ]]; then
        eval "$2"
        if [[ $? -ne 0 ]]; then
            echo "Failed to install $1. Please install it manually and rerun the script."
            exit 1
        fi
        # Recheck installation
        eval "$3"
        if [[ $? -ne 0 ]]; then
            echo "Failed to detect $1 after installation. Please install it manually and rerun the script."
            exit 1
        fi
    else
        echo "Please install $1 to continue."
        exit 1
    fi
}

# Check if Python is installed and its version
command -v python3 &>/dev/null || prompt_install "Python 3" "sudo apt-get update && sudo apt-get install python3 -y" "command -v python3 &>/dev/null"
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    echo "Python version must be 3.10 or higher. You have Python $PYTHON_VERSION."
    exit 1
fi

# Check for pip
python3 -m pip --version &>/dev/null || prompt_install "pip" "sudo apt-get install python3-pip -y" "python3 -m pip --version &>/dev/null"

# Check for venv
python3 -m venv --help &>/dev/null || prompt_install "venv" "sudo apt-get install python3-venv -y" "python3 -m venv --help &>/dev/null"

# Check for ensurepip
python3 -c "import ensurepip" &>/dev/null || prompt_install "ensurepip" "sudo apt-get install python3-venv -y" "python3 -c 'import ensurepip' &>/dev/null"

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
