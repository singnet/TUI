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
        return "Deposit amount must be greater than 0", 42
    if isinstance(contract_address, str):
        command += f" --singularitynettoken-at {contract_address}"
    if isinstance(mpe_address, str):
        command += f" --multipartyescrow-at {mpe_address}"
    if isinstance(gas_price, str):
        command += f" --gas-price {gas_price}"
    if isinstance(wallet_index, str):
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
        return "Withdraw amount must be greater than 0", 42
    if isinstance(mpe_address, str):
        command += f" --multipartyescrow-at {mpe_address}"
    if isinstance(gas_price, str):
        command += f" --gas-price {gas_price}"
    if isinstance(wallet_index, str):
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
    if not isinstance(reciever_addr, str):
        return "Please input the reciever address", 42
    if not isinstance(agi_amount, str) and agi_amount <= 0:
        return "Withdraw amount must be greater than 0", 42
    if isinstance(mpe_address, str):
        command += f" --multipartyescrow-at {mpe_address}"
    if isinstance(gas_price, str):
        command += f" --gas-price {gas_price}"
    if isinstance(wallet_index, str):
        command += f" --wallet-index {wallet_index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    command += " --yes"
    command += f" {reciever_addr}"
    command += f" {agi_amount}"

    return run_shell_command(command)
    