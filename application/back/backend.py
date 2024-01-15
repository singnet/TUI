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

snet_dir = f"{os.environ['HOME']}/snet"
serv_path: str
serv_path_set = False

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

def run_shell_command(command, cwd=None):
    try:

        if cwd != None:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd)
        else:
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
    # snet account deposit [-h] [--singularitynettoken-at SINGULARITYNETTOKEN_AT]
    #                  [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                  [--gas-price GAS_PRICE] [--wallet-index WALLET_INDEX]
    #                  [--yes] [--quiet | --verbose]
    #                  AMOUNT
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
    # snet account withdraw [-h] [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                   [--gas-price GAS_PRICE] [--wallet-index WALLET_INDEX]
    #                   [--yes] [--quiet | --verbose]
    #                   AMOUNT
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
    # snet account transfer [-h] [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                   [--gas-price GAS_PRICE] [--wallet-index WALLET_INDEX]
    #                   [--yes] [--quiet | --verbose]
    #                   RECEIVER AMOUNT
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

def print_org_metadata():
    global snet_dir
    if os.path.exists(f"{snet_dir}/organization_metadata.json"):
        output, errCode = run_shell_command(f"cat {snet_dir}/organization_metadata.json")
        return output, errCode
    else:
        return f"ERROR: Organization metdata not found at '{snet_dir}', please initialize metadata first", 42

def init_org_metadata(org_name, org_id, org_type, reg_addr):
    # snet organization metadata-init [-h] [--registry-at REGISTRY_AT]
    #                             [--metadata-file METADATA_FILE]
    #                             ORG_NAME ORG_ID ORG_TYPE
    global snet_dir
    if os.path.exists(f"{snet_dir}/organization_metadata.json"):
        return f"ERROR: Organization metdata already exists at {snet_dir}/organization_metadata.json'", 42
    elif os.path.exists(snet_dir):
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
        output, errCode = run_shell_command(command, cwd=snet_dir)
        if len(output) == 0 and errCode == 0:
            output = f"Successfully initialized organization metadata at '{snet_dir}'"
        return output, errCode
    else:
        return f"ERROR: Cannot find work directory '{snet_dir}'", 1

def add_org_metadata_desc(long_desc, short_desc, url, meta_path):
    # snet organization metadata-add-description [-h] [--description DESCRIPTION]
    #                                        [--short-description SHORT_DESCRIPTION]
    #                                        [--url URL]
    #                                        [--metadata-file METADATA_FILE]
    global snet_dir

    command = "snet organization metadata-add-description"
    if long_desc and len(long_desc) > 0:
        command += f" --description \"{long_desc}\""
    if short_desc and len(short_desc) > 0:
        command += f" --short-description \"{short_desc}\""
    if url and len(url) > 0:
        command += f" --url {url}"
    if meta_path and len(meta_path) > 0:
        command += f" --metadata-file {meta_path}"

    output, errCode = run_shell_command(command, cwd=snet_dir)
    if len(output) == 0 and errCode == 0:
        return "Description successfully added!", 0
    return output, errCode

def add_org_metadata_assets(asset_file_path, metadata_file_name):
    # snet organization metadata-add-assets [-h] [--metadata-file METADATA_FILE]
    #                                   ASSET_FILE_PATH hero_image
    global snet_dir

    if not asset_file_path:
        return "ERROR: Asset file path is required", 42

    command = "snet organization metadata-add-assets"
    command += f" {asset_file_path} hero_image"  # Assuming the asset type is always 'hero_image'

    if metadata_file_name and len(metadata_file_name) > 0:
        command += f" --metadata-file {metadata_file_name}"

    output, errCode = run_shell_command(command, cwd=snet_dir)
    return output, errCode

def remove_all_org_metadata_assets(metadata_file_name):
    # snet organization metadata-remove-all-assets [-h]
    #                                          [--metadata-file METADATA_FILE]
    global snet_dir

    command = "snet organization metadata-remove-all-assets"
    if metadata_file_name and len(metadata_file_name) > 0:
        command += f" --metadata-file {metadata_file_name}"

    output, errCode = run_shell_command(command, cwd=snet_dir)
    if len(output) == 0 and errCode == 0:
        output = "Successfully deleted all assets!"

    return output, errCode

def add_org_metadata_contact(contact_type, phone, email, metadata_file):
    # snet organization metadata-add-contact [-h] [--phone PHONE] [--email EMAIL]
    #                                    [--metadata-file METADATA_FILE]
    #                                    contact_type
    global snet_dir

    if not contact_type:
        return "ERROR: Contact type is required", 42
    command = f"snet organization metadata-add-contact {contact_type}"
    if phone and len(phone) > 0:
        command += f" --phone {phone}"
    if email and len(email) > 0:
        command += f" --email {email}"
    if metadata_file and len(metadata_file) > 0:
        command += f" --metadata-file {metadata_file}"

    output, errCode = run_shell_command(command, cwd=snet_dir)
    if len(output) == 0 and errCode == 0:
        output = "Successfully added contact!"
    return output, errCode

def remove_org_metadata_contacts(metadata_file):
    # snet organization metadata-remove-all-contacts [-h]
    #                                            [--metadata-file METADATA_FILE]
    global snet_dir

    command = "snet organization metadata-remove-all-contacts"
    if metadata_file and len(metadata_file) > 0:
        command += f" --metadata-file {metadata_file}"

    output, errCode = run_shell_command(command, cwd=snet_dir)
    if len(output) == 0 and errCode == 0:
        output = "Successfully deleted all contacts!"
    return output, errCode

def update_org_metadata(org_id, file_name, mem_list, gas, index, quiet, verbose):
    # snet organization update-metadata [-h] [--metadata-file METADATA_FILE]
    #                               [--members ORG_MEMBERS]
    #                               [--gas-price GAS_PRICE]
    #                               [--wallet-index WALLET_INDEX] [--yes]
    #                               [--quiet | --verbose]
    #                               [--registry-at REGISTRY_ADDRESS]
    #                               ORG_ID
    global snet_dir

    if org_id == None or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    command = f"snet organization update-metadata {org_id}"
    if file_name and len(file_name) > 0:
        command += f" --metadata-file {file_name}"
    if mem_list and len(mem_list) > 0:
        command += f" --members {mem_list}"
    if gas and len(gas) > 0:
        command += f" --gas-price {gas}"
    if index and len(index) > 0:
        command += f" --wallet-index {index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    command += " --yes"

    output, errCode = run_shell_command(command, cwd=snet_dir)
    if len(output) == 0 and errCode == 0:
        output = "Organization metadata successfully updated!"
    return output, errCode

def create_organization(org_id, metadata_file, members, gas, index, quiet, verbose, registry_address):
    # snet organization create [-h] [--metadata-file METADATA_FILE]
    #                      [--members ORG_MEMBERS] [--gas-price GAS_PRICE]
    #                      [--wallet-index WALLET_INDEX] [--yes]
    #                      [--quiet | --verbose]
    #                      [--registry-at REGISTRY_ADDRESS]
    #                      ORG_ID
    global snet_dir

    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    command = f"snet organization create {org_id}"
    if metadata_file and len(metadata_file) > 0:
        command += f" --metadata-file {metadata_file}"
    if members and len(members) > 0:
        command += f" --members {members}"
    if gas and len(gas) > 0:
        command += f" --gas-price {gas}"
    if index and len(index) > 0:
        command += f" --wallet-index {index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    if registry_address and len(registry_address) > 0:
        command += f" --registry-at {registry_address}"
    command += " --yes"

    output, errCode = run_shell_command(command, cwd=snet_dir)
    if len(output) == 0 and errCode == 0:
        output = "Organization successfully created!"
    return output, errCode

def change_organization_owner(org_id, owner_address, gas_price, wallet_index, quiet, verbose, registry_address):
    # snet organization change-owner [-h] [--gas-price GAS_PRICE]
    #                            [--wallet-index WALLET_INDEX] [--yes]
    #                            [--quiet | --verbose]
    #                            [--registry-at REGISTRY_ADDRESS]
    #                            ORG_ID OWNER_ADDRESS
    global snet_dir

    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    if not owner_address or len(owner_address) <= 0:
        return "ERROR: Must enter owner address", 42
    command = f"snet organization change-owner {org_id} {owner_address}"
    if gas_price and len(gas_price) > 0:
        command += f" --gas-price {gas_price}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    if registry_address and len(registry_address) > 0:
        command += f" --registry-at {registry_address}"
    command += " --yes"

    output, errCode = run_shell_command(command, cwd=snet_dir)
    if len(output) == 0 and errCode == 0:
        output = "Organization owner successfully changed!"
    return output, errCode

def add_org_metadata_members(org_id, org_members, gas_price, wallet_index, quiet, verbose, registry_address):
    # snet organization add-members [-h] [--gas-price GAS_PRICE]
    #                           [--wallet-index WALLET_INDEX] [--yes]
    #                           [--quiet | --verbose]
    #                           [--registry-at REGISTRY_ADDRESS]
    #                           ORG_ID ORG_MEMBERS
    global snet_dir
    
    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    if not org_members or len(org_members) <= 0:
        return "ERROR: Must enter organization members", 42
    command = f"snet organization add-members {org_id} [{org_members}]"
    if gas_price and len(gas_price) > 0:
        command += f" --gas-price {gas_price}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    if registry_address and len(registry_address) > 0:
        command += f" --registry-at {registry_address}"
    command += " --yes"

    output, errCode = run_shell_command(command, cwd=snet_dir)
    if len(output) == 0 and errCode == 0:
        output = "Members successfully added to organization metadata!"
    return output, errCode

def remove_org_metadata_members(org_id, org_members, gas_price, wallet_index, quiet, verbose, registry_address):
    # snet organization rem-members [-h] [--gas-price GAS_PRICE]
    #                           [--wallet-index WALLET_INDEX] [--yes]
    #                           [--quiet | --verbose]
    #                           [--registry-at REGISTRY_ADDRESS]
    #                           ORG_ID ORG_MEMBERS
    global snet_dir
    
    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    if not org_members or len(org_members) <= 0:
        return "ERROR: Must enter organization members", 42
    command = f"snet organization rem-members {org_id} [{org_members}]"
    if gas_price and len(gas_price) > 0:
        command += f" --gas-price {gas_price}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    if registry_address and len(registry_address) > 0:
        command += f" --registry-at {registry_address}"
    command += " --yes"

    output, errCode = run_shell_command(command, cwd=snet_dir)
    if len(output) == 0 and errCode == 0:
        output = "Members successfully removed from organization metadata!"
    return output, errCode

def delete_organization(org_id, gas_price, wallet_index, quiet, verbose, registry_address):
    # snet organization delete [-h] [--gas-price GAS_PRICE]
    #                      [--wallet-index WALLET_INDEX] [--yes]
    #                      [--quiet | --verbose]
    #                      [--registry-at REGISTRY_ADDRESS]
    #                      ORG_ID
    global snet_dir

    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    command = f"snet organization delete {org_id}"
    if gas_price and len(gas_price) > 0:
        command += f" --gas-price {gas_price}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    if registry_address and len(registry_address) > 0:
        command += f" --registry-at {registry_address}"
    command += " --yes"

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Organization successfully deleted!"
    return output, errCode

def print_organization_info(registry_address=None, wallet_index=None):
    # snet organization list-my [-h] [--registry-at REGISTRY_ADDRESS]
    #                       [--wallet-index WALLET_INDEX]
    command = "snet organization list-my"
    if registry_address and len(registry_address) > 0:
        command += f" --registry-at {registry_address}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"

    output, errCode = run_shell_command(command, cwd=snet_dir)
    if len(output) == 0:
        output = f"ERROR: Unable to find organizations, ensure you have created one\nCLI Output: {output}"
    return output, errCode

# TODO
def add_org_metadata_group(group_name, pay_addr, endpoints, payment_expiration_threshold, pay_chann_storage_type, pay_chann_conn_to, pay_chann_req_to, metadata_file, reg_addr):
    # snet organization add-group [-h]
    #                         [--payment-expiration-threshold PAYMENT_EXPIRATION_THRESHOLD]
    #                         [--payment-channel-storage-type PAYMENT_CHANNEL_STORAGE_TYPE]
    #                         [--payment-channel-connection-timeout PAYMENT_CHANNEL_CONNECTION_TIMEOUT]
    #                         [--payment-channel-request-timeout PAYMENT_CHANNEL_REQUEST_TIMEOUT]
    #                         [--metadata-file METADATA_FILE]
    #                         [--registry-at REGISTRY_AT]
    #                         group_name payment_address
    #                         [endpoints [endpoints ...]]
    global snet_dir
    
    if not group_name or len(group_name) <= 0:
        return "ERROR: Must enter group name", 42
    if not pay_addr or len(pay_addr) <= 0:
        return "ERROR: Must enter group payment address", 42
    if not endpoints or len(endpoints) <= 0:
        return "ERROR: Must enter group endpoints", 42
    command = f"snet organization add-group {group_name} {pay_addr} {endpoints}"
    if payment_expiration_threshold and len(payment_expiration_threshold) > 0:
        command += f" --payment-expiration-threshold {payment_expiration_threshold}"
    if pay_chann_storage_type and len(pay_chann_storage_type) > 0:
        command += f" --payment-channel-storage-type {pay_chann_storage_type}"
    if pay_chann_conn_to and len(pay_chann_conn_to) > 0: 
        command += f" --payment-channel-connection-timeout {pay_chann_conn_to}"
    if pay_chann_req_to and len(pay_chann_req_to) > 0:
        command += f" --payment-channel-request-timeout {pay_chann_req_to}"
    if metadata_file and len(metadata_file) > 0:
        command += f" --metadata-file {metadata_file}"
    if reg_addr and len(reg_addr) > 0:
        command += f" --registry-at {reg_addr}"

    output, errCode = run_shell_command(command, cwd=snet_dir)
    if len(output) == 0 and errCode == 0:
        output = "Group successfully added to organization metadata!"
    return output, errCode

# TODO
def update_org_metadata_group(group_name, pay_addr, endpoints, payment_expiration_threshold, pay_chann_storage_type, pay_chann_conn_to, pay_chann_req_to, metadata_file, reg_addr):
    # snet organization update-group [-h] [--payment-address PAYMENT_ADDRESS]
    #                            [--endpoints [ENDPOINTS [ENDPOINTS ...]]]
    #                            [--payment-expiration-threshold PAYMENT_EXPIRATION_THRESHOLD]
    #                            [--payment-channel-storage-type PAYMENT_CHANNEL_STORAGE_TYPE]
    #                            [--payment-channel-connection-timeout PAYMENT_CHANNEL_CONNECTION_TIMEOUT]
    #                            [--payment-channel-request-timeout PAYMENT_CHANNEL_REQUEST_TIMEOUT]
    #                            [--metadata-file METADATA_FILE]
    #                            [--registry-at REGISTRY_AT]
    #                            group_id
    global snet_dir

    if not group_name or len(group_name) <= 0:
        return "ERROR: Must enter group name", 42
    command = f"snet organization update-group {group_name}"
    if pay_addr:
        command += f" --payment-address {pay_addr}"
    if endpoints:
        command += " --endpoints " + " ".join(endpoints)
    if payment_expiration_threshold:
        command += f" --payment-expiration-threshold {payment_expiration_threshold}"
    if pay_chann_storage_type:
        command += f" --payment-channel-storage-type {pay_chann_storage_type}"
    if pay_chann_conn_to:
        command += f" --payment-channel-connection-timeout {pay_chann_conn_to}"
    if pay_chann_req_to:
        command += f" --payment-channel-request-timeout {pay_chann_req_to}"
    if metadata_file and len(metadata_file) > 0:
        command += f" --metadata-file {metadata_file}"
    if reg_addr and len(reg_addr) > 0:
        command += f" --registry-at {reg_addr}"

    output, errCode = run_shell_command(command, cwd=snet_dir)
    if len(output) == 0 and errCode == 0:
        output = "Group in organization metadata successfully updated!"
    return output, errCode

def init_service_metadata(service_path, proto_path, service_display, metadata_file, mpe_addr, pay_group_name, endpoints, fixed_price, enc_type, serv_type):
    # snet service metadata-init [-h] [--metadata-file METADATA_FILE]
    #                        [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                        [--group-name GROUP_NAME]
    #                        [--endpoints [ENDPOINTS [ENDPOINTS ...]]]
    #                        [--fixed-price FIXED_PRICE]
    #                        [--encoding {proto,json}]
    #                        [--service-type {grpc,jsonrpc,process}]
    #                        PROTO_DIR DISPLAY_NAME
    global serv_path
    global serv_path_set
    serv_path = service_path
    serv_path_set = True

    if not service_path or len(service_path) <= 0:
        return "ERROR: Must enter service directory path", 42
    if not proto_path or len(proto_path) <= 0:
        return "ERROR: Must enter protobuf directory path", 42
    if not service_display or len(service_display) <= 0:
        return "ERROR: Must enter service display name", 42

    command = f"snet service metadata-init {proto_path} \"{service_display}\""
    if metadata_file and len(metadata_file) > 0:
        command += f" --metadata-file {metadata_file}"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if pay_group_name and len(pay_group_name) > 0:
        command += f" --group-name {pay_group_name}"
    if endpoints:
        command += " --endpoints " + " ".join(endpoints)
    if fixed_price:
        command += f" --fixed-price {fixed_price}"
    if enc_type:
        command += f" --encoding {enc_type}"
    if serv_type:
        command += f" --service-type {serv_type}"

    output, errCode = run_shell_command(command, cwd=service_path)
    if len(output) == 0 and errCode == 0:
        output = "Service metadata successfully initialized!"
    return output, errCode

def add_service_metadata_desc(long_desc, short_desc, url, metadata_file):
    # snet service metadata-add-description [-h] [--json JSON] [--url URL]
    #                                   [--description DESCRIPTION]
    #                                   [--short-description SHORT_DESCRIPTION]
    #                                   [--metadata-file METADATA_FILE]
    global serv_path
    global serv_path_set
    if not serv_path_set:
        return "ERROR: Please initialize service metadata before attempting to add description", 42

    command = "snet service metadata-add-description"
    if long_desc and len(long_desc) > 0:
        command += f" --description \"{long_desc}\""
    if short_desc and len(short_desc) > 0:
        command += f" --short-description \"{short_desc}\""
    if url and len(url) > 0:
        command += f" --url {url}"
    if metadata_file and len(metadata_file) > 0:
        command += f" --metadata-file {metadata_file}"

    output, errCode = run_shell_command(command, cwd=serv_path)
    if len(output) == 0 and errCode == 0:
        output = "Service description successfully added!"
    return output, errCode

def publish_service(org_id, service_id, metadata_file, reg_addr, mpe_addr, update_mpe, gas, index, quiet, verbose):
    # snet service publish [-h] [--metadata-file METADATA_FILE]
    #                  [--update-mpe-address]
    #                  [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                  [--registry-at REGISTRY_AT] [--gas-price GAS_PRICE]
    #                  [--wallet-index WALLET_INDEX] [--yes]
    #                  [--quiet | --verbose]
    #                  ORG_ID SERVICE_ID
    global serv_path
    global serv_path_set

    if not serv_path_set:
        return "ERROR: Please initialize service metadata before publishing", 42

    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization ID", 42
    if not service_id or len(service_id) <= 0:
        return "ERROR: Must enter service ID", 42

    command = f"snet service publish {org_id} {service_id}"
    if metadata_file and len(metadata_file) > 0:
        command += f" --metadata-file {metadata_file}"
    if reg_addr and len(reg_addr) > 0:
        command += f" --registry-at {reg_addr}"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if update_mpe:
        command += " --update-mpe-address"
    if gas and len(gas) > 0:
        command += f" --gas-price {gas}"
    if index and len(index) > 0:
        command += f" --wallet-index {index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    command += " --yes"

    output, errCode = run_shell_command(command, cwd=serv_path)
    if len(output) == 0 and errCode == 0:
        output = "Service successfully published!"
    return output, errCode

# TODO
def delete_service(org_id, service_id, reg_addr, gas, index, quiet, verbose):
    # snet service delete [-h] [--registry-at REGISTRY_AT] [--gas-price GAS_PRICE]
    #                 [--wallet-index WALLET_INDEX] [--yes]
    #                 [--quiet | --verbose]
    #                 ORG_ID SERVICE_ID
    global serv_path

    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization ID", 42
    if not service_id or len(service_id) <= 0:
        return "ERROR: Must enter service ID", 42

    command = f"snet service delete {org_id} {service_id}"
    if reg_addr and len(reg_addr) > 0:
        command += f" --registry-at {reg_addr}"
    if gas and len(gas) > 0:
        command += f" --gas-price {gas}"
    if index and len(index) > 0:
        command += f" --wallet-index {index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    command += " --yes"

    output, errCode = run_shell_command(command, cwd=serv_path)
    if len(output) == 0 and errCode == 0:
        output = "Service successfully deleted!"
    return output, errCode

# TODO custom command
def custom_command(command):
    pass

