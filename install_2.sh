#!/bin/bash

# 2.75 Install Python build dependancies
sudo apt update
sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# 3. Create ENV using PyEnv and Venv
export WORK_DIR="$HOME/snet"
mkdir -p $WORK_DIR
ENV_NAME="venv-snet-3.11.6"
if ! pyenv versions | grep -q "3.11.6"; then
    pyenv install -v 3.11.6
fi

cd $WORK_DIR
pyenv local 3.11.6

if [ ! -d "$WORK_DIR/$ENV_NAME" ]; then
    python -m venv $ENV_NAME
fi

# 4. Install Docker image with ETCD
cd $WORK_DIR
mkdir -p etcd
if [ ! -f "$WORK_DIR/etcd/docker-etcd-setup.sh" ]; then
    git clone https://github.com/ishaan-ghosh/sNET-TUI.git
    cp $WORK_DIR/sNET-TUI/application/terminal/docker-etcd.sh $WORK_DIR/etcd/
    cd $WORK_DIR/etcd
    bash docker-etcd.sh
    sudo usermod -aG docker $USER
fi

# 5. Set Docker Local and Public ETCD addresses
export LOCAL_ETCD_NODE_URL=`hostname -I | awk '{print $1}'`+":2380"
export PUBLIC_ETCD_NODE_URL="https://13.48.190.33:2379"

# 6. Generating certificates for project
export SNET_CERT_FOLDER="/var/lib/etcd/cfssl"
if [ ! -d "$SNET_CERT_FOLDER" ]; then
    sudo mkdir -p $SNET_CERT_FOLDER
    # Assuming you have the JSON files for certificates in the correct place
    cfssl gencert -initca $SNET_CERT_FOLDER/ca-csr.json | cfssljson -bare ca -
    cfssl gencert -ca=$SNET_CERT_FOLDER/ca.pem -ca-key=$SNET_CERT_FOLDER/ca-key.pem -config=$SNET_CERT_FOLDER/ca-config.json -profile=server $SNET_CERT_FOLDER/server.json | cfssljson -bare server
    cfssl gencert -ca=$SNET_CERT_FOLDER/ca.pem -ca-key=$SNET_CERT_FOLDER/ca-key.pem -config=$SNET_CERT_FOLDER/ca-config.json -profile=peer $SNET_CERT_FOLDER/member-1.json | cfssljson -bare member-1
    cfssl gencert -ca=$SNET_CERT_FOLDER/ca.pem -ca-key=$SNET_CERT_FOLDER/ca-key.pem -config=$SNET_CERT_FOLDER/ca-config.json -profile=client $SNET_CERT_FOLDER/client.json | cfssljson -bare client
fi

sudo docker start docker-etcd-node-1 || sudo docker restart docker-etcd-node-1

# 7. Install daemon
if [ ! -f "$WORK_DIR/snetd" ]; then
    cd $WORK_DIR
    wget "https://github.com/singnet/snet-daemon/releases/download/v5.1.2/snetd-linux-amd64-v5.1.2" -O snetd
    sudo chmod +x snetd
fi

if [ ! -f "$WORK_DIR/snetd.config.json" ]; then
    echo '{
    "blockchain_enabled":true,
    "blockchain_network_selected":"sepolia",
    "daemon_end_point":"0.0.0.0:<DAEMON_PORT>",
    "daemon_group_name":"<DAEMON_GROUP>",
    "ipfs_end_point":"http://ipfs.singularitynet.io:80",
    "organization_id":"<ORGANIZATION_ID>",
    "service_id":"<SERVICE_ID>",
    "passthrough_enabled":true,
    "passthrough_endpoint":"http://<SERVICE_HOST>:<SERVICE_PORT>",
    "payment_channel_cert_path":"'$SNET_CERT_FOLDER'/client.pem",
    "payment_channel_ca_path":"'$SNET_CERT_FOLDER'/ca.pem",
    "payment_channel_key_path":"'$SNET_CERT_FOLDER'/client-key.pem",
    "log":{"level":"debug","output":{"type":"stdout"}}
}' > $HOME/snet/snetd.config.json
fi

# 8. Install snet-cli
if [ ! -d "$WORK_DIR/snet-cli" ]; then
    cd $WORK_DIR
    source $ENV_NAME/bin/activate
    git clone https://github.com/singnet/snet-cli.git
    cd $HOME/snet/snet-cli/packages/snet_cli
    ./scripts/blockchain install
    python -m pip install -e .
fi

# Patch for deprecated RIPEMD160 (if necessary)
# echo "from Crypto.Hash.RIPEMD160 import RIPEMD160Hash, new" > $HOME/snet/$ENV_NAME/lib/python3.7/site-packages/Crypto/Hash/RIPEMD.py


# Check if CLI is able to run properly, it doesnt need to be an output check but you need to check something. 
cd "$WORK_DIR"
source $ENV_NAME/bin/activate
snet

echo "Installation and setup completed!"
# Reset shell for CLI
exec $SHELL
