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

# Detect package manager
if command -v apt-get &>/dev/null; then
    PM_INSTALL="sudo apt-get install -y"
elif command -v yum &>/dev/null; then
    PM_INSTALL="sudo yum install -y"
elif command -v dnf &>/dev/null; then
    PM_INSTALL="sudo dnf install -y"
elif command -v zypper &>/dev/null; then
    PM_INSTALL="sudo zypper install -y"
else
    echo "Unsupported package manager. Please install Python 3.10 or higher manually."
    exit 1
fi

# Check if Python >= 3.10 is installed
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' 2>/dev/null || true)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [[ -z "$PYTHON_MAJOR" || "$PYTHON_MAJOR" -lt 3 || ( "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 10 ) ]]; then
    prompt_install "Python 3.10 or higher" "$PM_INSTALL python3.11" '[[ "$(python3.11 -c "import sys; print(\".\".join(map(str, sys.version_info[:3])))" 2>/dev/null)" == "3.11.9" ]]'
fi

# Ensure python points to the correct version
sudo ln -sf $(which python3) /usr/local/bin/python

# Determine the correct venv package name
VENV_PKG="python3.$PYTHON_MINOR-venv"

# Check for python3-venv
python3 -m venv --help &>/dev/null || prompt_install "python3-venv" "$PM_INSTALL $VENV_PKG" "python3 -m venv --help &>/dev/null"

# Check for pip
python3 -m pip --version &>/dev/null || prompt_install "pip" "$PM_INSTALL python3-pip" "python3 -m pip --version &>/dev/null"

# Check for ensurepip
python3 -c "import ensurepip" &>/dev/null || prompt_install "ensurepip" "$PM_INSTALL $VENV_PKG" "python3 -c 'import ensurepip' &>/dev/null"

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

# Run the main.py script
python3 application/main.py
if [ $? -ne 0 ]; then
    echo "Failed to run the application."
    exit 1
fi
