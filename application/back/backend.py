import subprocess
from typing import Union
from textual.widgets import Button, Header, Label, Input, Select, RadioButton, LoadingIndicator
from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical, Horizontal
from textual.screen import Screen
from time import sleep
import re
import os
# from web3 import Web3
# from eth_account import Account

work_dir = "$HOME/snet"

# TODO
class Identity():
    def __init__(self, identity_name, network, wallet_priv_key=None, seed_phrase=None) -> None:
        self.identity_name = identity_name
        self.network = network
        self.seed = seed_phrase
        if wallet_priv_key == None:
            self.mnemonic = True
        else:
            self.mnemonic = False
# TODO
class Organization():
    def __init__(self, org_name, org_id, org_type, org_email, org_website, org_description, org_assets, org_owner, org_members) -> None:
        self.org_name: str = org_name
        self.org_id: str = org_id
        self.org_type: str = org_type
        self.org_email: str = org_email
        self.org_website: str = org_website
        self.org_description: str = org_description
        self.org_assets: {str, str} = org_assets
        self.org_owner: Identity = org_owner
        self.org_members: [Identity] = org_members

def run_shell_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        stdout, stderr, errCode = result.stdout, result.stderr, result.returncode
        
        if errCode == 0:
            return stdout, errCode
        elif errCode == 42:
            return stdout, errCode
        else:
            return stderr, errCode 
        
    except subprocess.CalledProcessError as e:
        stdout, stderr, errCode = e.stdout, e.stderr, e.returncode

        if errCode == 0:
            return stdout, errCode
        elif errCode == 42:
            return stdout, errCode
        else:
            return stderr, errCode 
    
def run_shell_command_with_input(command, input_text):
    try:
        process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate(input=input_text)
        return output, error, process.returncode
    except Exception as e:
        return str(e)

def check_cli():
    output, errCode = run_shell_command('snet')
    if "error: the following arguments are required: COMMAND" in output:
        return True, output, errCode
    return False, output, errCode

def check_account_balance():
    output, errCode = run_shell_command('snet account balance')
    if "    account:" in output:
        return True, output, errCode
    return False, output, errCode

def dict_create(output: str):
    res = {}
    lines = output.split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            res[key] = value

    return res

def nav_sidebar_vert() -> Vertical:
    ret_vert = Vertical(
                Button("Account", id="account_page_nav", classes="nav_sidebar_button"),
                Button("Organization", id="organization_page_nav", classes="nav_sidebar_button"),
                Button("Services", id="services_page_nav", classes="nav_sidebar_button"),
                #Button("Misc.", id="misc_page_nav", classes="nav_sidebar_button"),
                Button("Exit", id="exit_page_nav", classes="nav_sidebar_button"),
                classes="nav_sidebar",
                name="nav_sidebar_name",
                id="nav_sidebar"
            )

    return ret_vert

def wallet_dict_create():
    check, output, errCode = check_account_balance()
    matches = re.findall(r'(\w+):\s*(\S+)', output)
    return {key: value for key, value in matches}

def create_identity_cli(id_name, wallet_info, network, mnemonic):
    if mnemonic:
        output, errCode = run_shell_command(f"snet identity create {id_name} mnemonic --mnemonic {wallet_info} --network {network}")
    else:
        output, errCode = run_shell_command(f"snet identity create {id_name} key --private-key {wallet_info} --network {network}")
    return output, errCode

def delete_identity_cli(id_name):
    output, errCode = run_shell_command(f"snet identity delete {id_name}")
    return output, errCode

def account_deposit(agi_amount, contract_address, mpe_address, gas_price, wallet_index, quiet, verbose):
    command = "snet account deposit"
    if not isinstance(agi_amount, str) and agi_amount <= 0:
        return "ERROR: Deposit amount must be greater than 0", 42
    if isinstance(contract_address, str) and len(contract_address) > 0:
        command += f" --singularitynettoken-at {contract_address}"
    if isinstance(mpe_address, str) and len(mpe_address) > 0:
        command += f" --multipartyescrow-at {mpe_address}"
    if isinstance(gas_price, str) and len(gas_price) > 0:
        command += f" --gas-price {gas_price}"
    if isinstance(wallet_index, str) and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    command += " --yes"
    command += f" {agi_amount}"

    return run_shell_command(command)

def account_withdraw(agi_amount, mpe_address, gas_price, wallet_index, quiet, verbose):
    command = "snet account withdraw"
    if not isinstance(agi_amount, str) and agi_amount <= 0:
        return "Error: Withdraw amount must be greater than 0", 42
    if isinstance(mpe_address, str) and len(mpe_address) > 0:
        command += f" --multipartyescrow-at {mpe_address}"
    if isinstance(gas_price, str) and len(gas_price) > 0:
        command += f" --gas-price {gas_price}"
    if isinstance(wallet_index, str) and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    command += " --yes"
    command += f" {agi_amount}"

    return run_shell_command(command)

def account_transfer(reciever_addr, agi_amount, mpe_address, gas_price, wallet_index, quiet, verbose):
    command = "snet account transfer"
    if not isinstance(reciever_addr, str) and len(reciever_addr) > 0:
        return "ERROR: Please input the reciever address", 42
    if not isinstance(agi_amount, str) and agi_amount <= 0:
        return "ERROR: Withdraw amount must be greater than 0", 42
    if isinstance(mpe_address, str) and len(mpe_address) > 0:
        command += f" --multipartyescrow-at {mpe_address}"
    if isinstance(gas_price, str) and len(gas_price) > 0:
        command += f" --gas-price {gas_price}"
    if isinstance(wallet_index, str) and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    command += " --yes"
    command += f" {reciever_addr}"
    command += f" {agi_amount}"

    return run_shell_command(command)

def print_metadata():
    global work_dir
    if os.path.exists(f"{work_dir}/organization_metadata.json"):
        output, errCode = run_shell_command(f"cat {work_dir}/organization_metadata.json")
        return output, errCode
    else:
        return f"ERROR: Organization metdata not found at '{work_dir}', please initialize metadata first", 42

def init_metadata(org_name, org_id, org_type, reg_addr):
    # snet organization metadata-init [-h] [--registry-at REGISTRY_AT]
    #                             [--metadata-file METADATA_FILE]
    #                             ORG_NAME ORG_ID ORG_TYPE
    global work_dir
    if os.path.exists(f"{work_dir}/organization_metadata.json"):
        return f"ERROR: Organization metdata already exists at '{work_dir}/organization_metadata.json'", 42
    elif os.path.exists(f"{work_dir}"):
        run_shell_command(f"cd {work_dir}")
        command = "snet organization metadata-init"
        if org_type == Select.BLANK or not isinstance(org_type, str):
            return "ERROR: Please select an organization type", 42
        else:
            org_type = org_type.lower()
        if org_name == None or len(org_name) == 0:
            return "ERROR: Organization name is required", 42
        if org_id == None or len(org_id) == 0:
            return "ERROR: Organization identity is required", 42
        if isinstance(reg_addr, str) and len(reg_addr) > 0:
            command += f" --registry-at {reg_addr}"
        command += f" {org_name}"
        command += f" {org_id}"
        command += f" {org_type}"
        output, errCode = run_shell_command(command)
        return output, errCode
    else:
        return f"ERROR: Cannot find work directory '{work_dir}", 1