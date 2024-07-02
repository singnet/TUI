#!/bin/sh

# Detect architecture
if [[ $(uname -m) == 'arm64' ]]; then
    BREW_PATH="/opt/homebrew/bin/brew"
elif [[ $(uname -m) == 'x86_64' ]]; then
    BREW_PATH="/usr/local/bin/brew"
else
    echo "Could not detect architecture. Please ensure you are running this with an Intel or Silicon CPU Mac"
    exit 1
fi

# Detect the shell
if [ -n "$ZSH_VERSION" ]; then
    SHELL_NAME="zsh"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_NAME="bash"
else
    echo "Unsupported shell. Please run this script using bash or zsh."
    exit 1
fi

# Function to prompt user for installation
prompt_install() {
    if [ "$SHELL_NAME" = "zsh" ]; then
        read "response?$1 is not installed or is out of date. Would you like to install it now? (y/n): "
    else
        read -p "$1 is not installed or is out of date. Would you like to install it now? (y/n): " response
    fi

    if [[ "$response" == "y" ]]; then
        eval "$2"
        if [[ $? -ne 0 ]]; then
            echo "Failed to install $1. Please install it manually and rerun the script."
            exit 1
        fi
        # Re-source Homebrew after installation
        if [[ "$1" == "Homebrew" ]]; then
            if [ "$SHELL_NAME" = "zsh" ]; then
                echo 'eval "$('$BREW_PATH' shellenv)"' >> ~/.zshrc
                echo 'eval "$('$BREW_PATH' shellenv)"' >> ~/.zprofile
                eval "$($BREW_PATH shellenv)"
            else
                echo 'eval "$('$BREW_PATH' shellenv)"' >> ~/.bash_profile
                eval "$($BREW_PATH shellenv)"
            fi
        fi
    else
        echo "Please install $1 to continue."
        exit 1
    fi
}

# Check if Homebrew is installed
eval "$($BREW_PATH shellenv)"
command -v brew &>/dev/null || prompt_install "Homebrew" 'NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'

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
    python3 -m venv tui_venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        rm -r tui_venv
        exit 1
    fi
    echo "Virtual environment created."
    source tui_venv/bin/activate
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies."
        exit 1
    fi
    echo "Dependencies installed."
    deactivate
fi

# Activate the virtual environment
if [ -f "tui_venv/bin/activate" ]; then
    source tui_venv/bin/activate
    echo "Virtual environment activated."
else
    echo "Failed to find the virtual environment activation script."
    rm -r tui_venv
    exit 1
fi

# Check if "update" argument is passed
if [[ "$1" == "update" ]]; then
    echo "Updating dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "Dependencies updated."
fi

# Run the main.py script

# Check if "dev" argument is passed
if [[ "$1" == "dev" ]]; then
    echo "Running in DEV mode"
    textual run --dev application/main.py
else
    python3 application/main.py
fi

if [ $? -ne 0 ]; then
    echo "Failed to run the application."
    exit 1
fi
