#!/bin/bash

# Function to prompt user for installation
prompt_install() {
    read -p "$1 is not installed or is out of date. Would you like to install it now? (y/n): " response
    if [[ "$response" == "y" ]]; then
        eval "$2"
        if [[ $? -ne 0 ]]; then
            echo "Failed to install $1. Please install it manually and rerun the script."
            exit 1
        fi
        # Re-source Homebrew after installation
        if [[ "$1" == "Homebrew" ]]; then
            echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.bash_profile
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    else
        echo "Please install $1 to continue."
        exit 1
    fi
}

# Check if Homebrew is installed
command -v brew &>/dev/null || prompt_install "Homebrew" 'NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'

# Update PATH for Homebrew
if [[ -e ~/.bash_profile ]]; then
    source ~/.bash_profile
fi
eval "$(/usr/local/bin/brew shellenv)"

# Check if Python >= 3.10 is installed
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' 2>/dev/null || true)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [[ -z "$PYTHON_MAJOR" || "$PYTHON_MAJOR" -lt 3 || ( "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 10 ) ]]; then
    prompt_install "Python >= 3.10" "brew install python && brew link --overwrite --force python"
fi

# Ensure python points to the correct version
ln -sf $(brew --prefix)/bin/python3 $(brew --prefix)/bin/python

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

# Run the main.py script
python application/main.py
