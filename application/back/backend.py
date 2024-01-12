import subprocess
from typing import Union
from textual.widgets import Button, Header, Label, Input, Select, RadioButton, LoadingIndicator
from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical, Horizontal
from textual.screen import Screen
from time import sleep
import re
# from web3 import Web3
# from eth_account import Account

class Identity():
    def __init__(self, identity_name, network, wallet_priv_key=None, seed_phrase=None) -> None:
        self.identity_name = identity_name
        self.network = network
        self.seed = seed_phrase
        if wallet_priv_key == None:
            self.mnemonic = True
        else:
            self.mnemonic = False

def run_shell_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout, result.stderr, result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode
    
def run_shell_command_with_input(command, input_text):
    try:
        process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate(input=input_text)
        return output, error, process.returncode
    except Exception as e:
        return str(e)

def check_cli():
    stdout, stderr, errCode = run_shell_command('snet')
    if "error: the following arguments are required: COMMAND" in stderr:
        return True, stdout, stderr, errCode
    return False, stdout, stderr, errCode

def check_account_balance():
    stdout, stderr, errCode = run_shell_command('snet account balance')
    if "    account:" in stdout:
        return True, stdout, stderr, errCode
    return False, stdout, stderr, errCode

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
                Button("Exit", id="exit_page_nav", classes="nav_sidebar_button"),
                classes="nav_sidebar",
                name="nav_sidebar_name",
                id="nav_sidebar"
            )

    return ret_vert

def wallet_dict_create():
    check, stdout, stderr, errCode = check_account_balance()
    matches = re.findall(r'(\w+):\s*(\S+)', stdout)
    return {key: value for key, value in matches}

def mpw_wallet_deposit(agi_amount):
    stdout, stderr, errCode = run_shell_command('snet account deposit {}'.format(agi_amount))
    return stdout, stderr, errCode

def create_identity_cli(id_name, wallet_info, network, mnemonic):
    if mnemonic:
        stdout, stderr, errCode = run_shell_command(f"snet identity create {id_name} mnemonic --mnemonic {wallet_info} --network {network}")
    else:
        stdout, stderr, errCode = run_shell_command(f"snet identity create {id_name} mnemonic --mnemonic {wallet_info} --network {network}")
    return stdout, stderr, errCode

def delete_identity_cli(id_name):
    stdout, stderr, errCode = run_shell_command(f"snet identity delete {id_name}")
    return stdout, stderr, errCode