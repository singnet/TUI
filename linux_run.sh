#!/bin/bash

# Function to prompt user for installation
prompt_install() {
    read -p "$1 is not installed or not sufficient. Would you like to install it now? (y/n): " response
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

# Check for pip
python3 -m pip --version &>/dev/null || prompt_install "pip" "python3 -m ensurepip --upgrade" "python3 -m pip --version &>/dev/null"

# Check for venv
python3 -m venv --help &>/dev/null || prompt_install "venv" "python3 -m pip install virtualenv" "python3 -m venv --help &>/dev/null"

# Check for ensurepip
python3 -c "import ensurepip" &>/dev/null || prompt_install "ensurepip" "python3 -m pip install --upgrade pip" "python3 -c 'import ensurepip' &>/dev/null"

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
