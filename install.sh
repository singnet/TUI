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
sudo apt -y remove needrestart
REQUIRED_PKGS="git golang-cfssl nodejs npm make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl protobuf-compiler"
for pkg in $REQUIRED_PKGS; do
    if ! dpkg -l | grep -qw $pkg; then
        sudo apt -y update && sudo apt -y upgrade
        sudo apt install -y $REQUIRED_PKGS
        break
    fi
done

# 2. Install PyEnv
if [ ! -d "$HOME/.pyenv" ]; then
    curl -s -S -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
    echo 'eval "$(pyenv init -)"' >> ~/.profile
fi

if [ -f "~/.bash_profile" ]; then
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
    echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
    echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
fi

if [ -f "~/.bash_login"]; then
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_login
    echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_login
    echo 'eval "$(pyenv init -)"' >> ~/.bash_login
fi 

# 3. Create ENV using PyEnv
ENV_NAME="venv-snet-3.7.17"
if ! pyenv versions | grep -q $ENV_NAME; then
    pyenv install -v 3.7.17
    pyenv virtualenv 3.7.17 $ENV_NAME
    cd ~ && mkdir -p snet && cd snet
    pyenv local $ENV_NAME
    python -m venv venv
    source venv/bin/activate
    export WORK_DIR="$HOME/snet"
fi

# 4. Install Docker image with ETCD
if [ ! -f "docker-etcd-setup.sh" ]; then
    bash application/terminal/docker-etcd.sh
    sudo usermod -aG docker $USER
fi

# 5. Set Docker Local and Public ETCD addresses
export LOCAL_ETCD_NODE_URL=`hostname -I | awk '{print $1}'`+":2380"
export PUBLIC_ETCD_NODE_URL="https://13.48.190.33:2379"

# 6. Generating certificates for project
export SNET_CERT_FOLDER="/var/lib/etcd/cfssl"
if [ ! -d "$SNET_CERT_FOLDER" ]; then
    mkdir -p $SNET_CERT_FOLDER
    # Assuming you have the JSON files for certificates in the correct place
    cfssl gencert -initca $SNET_CERT_FOLDER/ca-csr.json | cfssljson -bare ca -
    cfssl gencert -ca=$SNET_CERT_FOLDER/ca.pem -ca-key=$SNET_CERT_FOLDER/ca-key.pem -config=$SNET_CERT_FOLDER/ca-config.json -profile=server $SNET_CERT_FOLDER/server.json | cfssljson -bare server
    cfssl gencert -ca=$SNET_CERT_FOLDER/ca.pem -ca-key=$SNET_CERT_FOLDER/ca-key.pem -config=$SNET_CERT_FOLDER/ca-config.json -profile=peer $SNET_CERT_FOLDER/member-1.json | cfssljson -bare member-1
    cfssl gencert -ca=$SNET_CERT_FOLDER/ca.pem -ca-key=$SNET_CERT_FOLDER/ca-key.pem -config=$SNET_CERT_FOLDER/ca-config.json -profile=client $SNET_CERT_FOLDER/client.json | cfssljson -bare client
fi
docker start docker-etcd-node-1 || docker restart docker-etcd-node-1

# 7. Install daemon
if [ ! -f "~/snet/snetd" ]; then
    wget "https://drive.google.com/u/0/uc?id=1jbme-TD_HVOlyvkdcT_B0iOOzUpM9c3r&export=download" -O snetd
    sudo chmod +x snetd
fi
if [ ! -f "snetd.config.json" ]; then
    touch snetd.config.json
fi

# 8. Install snet-cli
if [ ! -d "$HOME/snet/snet-cli" ]; then
    source $HOME/snet/venv/bin/activate
    git clone https://github.com/singnet/snet-cli.git $HOME/snet/snet-cli
    cd $HOME/snet/snet-cli/packages/snet_cli
    ./scripts/blockchain install
    python -m pip install -e .
fi

# Patch for deprecated RIPEMD160 (if necessary)
echo "from Crypto.Hash.RIPEMD160 import RIPEMD160Hash, new" > $HOME/snet/venv/lib/python3.7/site-packages/Crypto/Hash/RIPEMD.py


# Finalizing
cd "$HOME/snet"
source venv/bin/activate
snet

echo "Installation and setup completed!"