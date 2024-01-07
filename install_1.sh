#!/bin/bash

# 0. Check if machine is ubuntu
if [ ! -f "/etc/lsb-release" ]; then
    echo "This sNET-CLI is only compatible with Ubuntu, please ensure the system you are attempting to run the install script on is Ubuntu"
    exit 1
fi

# 0.5 Check if machine is amd64
if [ ! "$(uname -m)" == "x86_64" ]; then
    echo "This sNET-CLI is only compatible with amd64, please ensure the system you are attempting to run the install script on is amd64"
    exit 1
fi

# 1. Update and install packages for Ubuntu
echo "Updating and installing packages"
sudo apt -y update && sudo apt -y upgrade
REQUIRED_PKGS="git golang-cfssl nodejs npm make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl protobuf-compiler"
sudo apt install -y $REQUIRED_PKGS

cd "$HOME"

# 2. Install PyEnv
if [ ! -d "$HOME/.pyenv" ]; then
    curl https://pyenv.run | bash
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> $HOME/.bashrc
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> $HOME/.bashrc
    echo 'eval "$(pyenv init -)"' >> $HOME/.bashrc

    if [ -f "$HOME/.profile" ]; then
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> $HOME/.profile
        echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> $HOME/.profile
        echo 'eval "$(pyenv init -)"' >> $HOME/.profile
    fi

    if [ -f "$HOME/.bash_profile" ]; then
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> $HOME/.bash_profile
        echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> $HOME/.bash_profile
        echo 'eval "$(pyenv init -)"' >> $HOME/.bash_profile
    fi

    if [ -f "$HOME/.bash_login" ]; then
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> $HOME/.bash_login
        echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> $HOME/.bash_login
        echo 'eval "$(pyenv init -)"' >> $HOME/.bash_login
    fi 
fi

# 2.5 Reset shell for pyenv
echo "PyEnv installed and set up, please continue to 'install_2.sh'"
exec "$SHELL"