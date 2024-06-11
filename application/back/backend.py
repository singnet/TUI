import subprocess
from typing import Union
from textual.widgets import Button, Header, Label, Input, Select, RadioButton, LoadingIndicator
from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical, Horizontal
from textual.screen import Screen
from time import sleep
import re
import os
import json
# from web3 import Web3
# from eth_account import Account

# Stable build v0.1

condCommDict = set({
    "account deposit",
    "account withdraw", 
    "account transfer",
    "channel open-init",
    "channel open-init-metadata",
    "channel extend-add",
    "channel extend-add-for-org",
    "channel claim-timeout",
    "channel claim-timeout-all",
    "client call",
    "contract MultiPartyEscrow balances",
    "contract MultiPartyEscrow channels",
    "contract MultiPartyEscrow nextChannelId",
    "contract MultiPartyEscrow token",
    "contract MultiPartyEscrow usedMessages",
    "contract MultiPartyEscrow deposit",
    "contract MultiPartyEscrow withdraw",
    "contract MultiPartyEscrow transfer",
    "contract MultiPartyEscrow openChannel",
    "contract MultiPartyEscrow openChannelByThirdParty",
    "contract MultiPartyEscrow depositAndOpenChannel",
    "contract MultiPartyEscrow multiChannelClaim",
    "contract MultiPartyEscrow channelClaim",
    "contract MultiPartyEscrow channelExtend",
    "contract MultiPartyEscrow channelAddFunds",
    "contract MultiPartyEscrow channelExtendAndAddFunds",
    "contract MultiPartyEscrow channelClaimTimeout",
    "contract Registry supportsInterface",
    "contract Registry createOrganization",
    "contract Registry changeOrganizationOwner",
    "contract Registry changeOrganizationMetadataURI",
    "contract Registry addOrganizationMembers",
    "contract Registry removeOrganizationMembers",
    "contract Registry deleteOrganization",
    "contract Registry createServiceRegistration",
    "contract Registry updateServiceRegistration",
    "contract Registry deleteServiceRegistration",
    "contract Registry listOrganizations",
    "contract Registry getOrganizationById",
    "contract Registry listServicesForOrganization",
    "contract Registry getServiceRegistrationById",
    "contract SingularityNetToken DEFAULT_ADMIN_ROLE",
    "contract SingularityNetToken MINTER_ROLE",
    "contract SingularityNetToken PAUSER_ROLE",
    "contract SingularityNetToken allowance",
    "contract SingularityNetToken approve",
    "contract SingularityNetToken balanceOf",
    "contract SingularityNetToken burn",
    "contract SingularityNetToken burnFrom",
    "contract SingularityNetToken decimals",
    "contract SingularityNetToken decreaseAllowance",
    "contract SingularityNetToken getRoleAdmin",
    "contract SingularityNetToken getRoleMember",
    "contract SingularityNetToken getRoleMemberCount",
    "contract SingularityNetToken grantRole",
    "contract SingularityNetToken hasRole",
    "contract SingularityNetToken increaseAllowance",
    "contract SingularityNetToken name",
    "contract SingularityNetToken paused",
    "contract SingularityNetToken renounceRole",
    "contract SingularityNetToken revokeRole",
    "contract SingularityNetToken symbol",
    "contract SingularityNetToken totalSupply",
    "contract SingularityNetToken transfer",
    "contract SingularityNetToken transferFrom",
    "contract SingularityNetToken mint",
    "contract SingularityNetToken pause",
    "contract SingularityNetToken unpause",
    "organization create",
    "organization update-metadata",
    "organization change-owner",
    "organization add-members",
    "organization rem-members",
    "organization delete",
    "service publish",
    "service publish-in-ipfs",
    "service update-metadata",
    "service update-add-tags",
    "service update-remove-tags",
    "service delete",
    "treasurer claim",
    "treasurer claim-all",
    "treasurer claim-expired"
})

def run_shell_command(command, workdir=None):
    try:
        if workdir != None:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=workdir)
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
    
def run_shell_command_with_input(command, input_text, workdir=None):
    try:
        if workdir != None:
            process = subprocess.Popen(args=command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=workdir)
        else:
            process = subprocess.Popen(args=command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        stdout, stderr = process.communicate(input_text)
        
        if stdout:
            return stdout, 0
        elif stderr:
            return stderr, 1
        else:
            return stdout, 42

    except Exception as e:
        return str(e), 1

def check_cli():
    output, errCode = run_shell_command('snet')
    if "error: the following arguments are required: COMMAND" in output:
        return True, output, errCode
    return False, output, errCode

def network_list():
    output, errCode = run_shell_command('snet --print-traceback network list')
    if errCode == 0:
        network_list = re.findall(r'(?m)^\s*([a-zA-Z]+)\s*:$', output)
    else:
        network_list = ["Unable to find network list"]
    return network_list, errCode

def check_account_balance():
    output, errCode = run_shell_command('snet --print-traceback account balance')
    if "    account:" in output:
        return True, output, errCode
    return False, output, errCode

def identity_check():
    output, errCode = run_shell_command('snet --print-traceback account print')
    if errCode == 0:
        return True, output, errCode
    else:
        return False, output, errCode

def nav_sidebar_vert(focus_button) -> Vertical:
    ret_vert = Vertical(
                Button("Account", id="account_page_nav", classes="nav_sidebar_button"),
                Button("Organization", id="organization_page_nav", classes="nav_sidebar_button"),
                Button("Services", id="services_page_nav", classes="nav_sidebar_button"),
                Button("Client", id="client_page_nav", classes="nav_sidebar_button"),
                Button("Custom Command", id="custom_command_page_nav", classes="nav_sidebar_button"),
                Button("Exit", id="exit_page_nav", classes="nav_sidebar_button"),
                classes="nav_sidebar",
                name="nav_sidebar_name",
                id="nav_sidebar"
            )

    if focus_button == "account":
        ret_vert.get_child_by_id("account_page_nav").focus()
    elif focus_button == "org":
        ret_vert.get_child_by_id("organization_page_nav").focus()
    elif focus_button == "serv":
        ret_vert.get_child_by_id("services_page_nav").focus()
    elif focus_button == "client":
        ret_vert.get_child_by_id("client_page_nav").focus()
    elif focus_button == "custom":
        ret_vert.get_child_by_id("custom_command_page_nav").focus()

    return ret_vert

def wallet_dict_create():
    check, output, errCode = check_account_balance()
    if check:
        matches = re.findall(r'(\w+):\s*(\S+)', output)
        return {key: value for key, value in matches}, 0
    else:
        return {}, 1

def create_identity_cli(id_name, wallet_info, network, mnemonic):
    if mnemonic:
        output, errCode = run_shell_command(f"snet --print-traceback identity create {id_name} mnemonic --mnemonic {wallet_info} --network {network}")
    else:
        output, errCode = run_shell_command(f"snet --print-traceback identity create {id_name} key --private-key {wallet_info} --network {network}")
    return output, errCode

def delete_identity_cli(id_name):
    output, errCode = run_shell_command(f"snet --print-traceback identity delete {id_name}")
    return output, errCode

def account_deposit(agi_amount, contract_address, mpe_address, gas_price, wallet_index, quiet, verbose):
    # snet account deposit [-h] [--singularitynettoken-at SINGULARITYNETTOKEN_AT]
    #                  [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                  [--gas-price GAS_PRICE] [--wallet-index WALLET_INDEX]
    #                  [--yes] [--quiet | --verbose]
    #                  AMOUNT
    command = "snet --print-traceback account deposit"
    if not isinstance(agi_amount, str) or len(agi_amount) <= 0:
        return "ERROR: Please enter deposit amount", 42
    try:
        if float(agi_amount) <= 0:
            return "ERROR: Please enter deposit amount greater than 0", 42
    except ValueError:
        return "ERROR: Please enter deposit amount greater than 0", 42
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
    command = "snet --print-traceback account withdraw"
    if not isinstance(agi_amount, str) or len(agi_amount) <= 0:
        return "ERROR: Please enter deposit amount", 42
    try:
        if float(agi_amount) <= 0:
            return "ERROR: Please enter deposit amount greater than 0", 42
    except ValueError:
        return "ERROR: Please enter deposit amount greater than 0", 42
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
    command = "snet --print-traceback account transfer"
    if not isinstance(reciever_addr, str) or len(reciever_addr) <= 0:
        return "ERROR: Please input the reciever address", 42
    if not isinstance(agi_amount, str) or len(agi_amount) <= 0:
        return "ERROR: Please enter deposit amount", 42
    try:
        if float(agi_amount) <= 0:
            return "ERROR: Please enter deposit amount greater than 0", 42
    except ValueError:
        return "ERROR: Please enter deposit amount greater than 0", 42
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

def print_org_metadata(org_id):
    # snet organization print-metadata [-h] org_id
    command = "snet organization print-metadata"
    if not isinstance(org_id, str) or len(org_id) <= 0:
        return "ERROR: Organization identity is required", 42
    
    command += f" {org_id}"

    return run_shell_command(command)

def init_org_metadata(org_name, org_id, org_type, reg_addr, meta_file):
    # snet organization metadata-init [-h] [--registry-at REGISTRY_AT]
    #                             [--metadata-file METADATA_FILE]
    #                             ORG_NAME ORG_ID ORG_TYPE
    command = "snet --print-traceback organization metadata-init"
    if org_type == Select.BLANK or not isinstance(org_type, str):
        return "ERROR: Please select an organization type", 42
    else:
        org_type = org_type.lower()
    if not isinstance(org_name, str) or len(org_name) <= 0:
        return "ERROR: Organization name is required", 42
    if not isinstance(org_id, str) or len(org_id) <= 0:
        return "ERROR: Organization identity is required", 42
    if isinstance(reg_addr, str) and len(reg_addr) > 0:
        command += f" --registry-at {reg_addr}"
    if isinstance(meta_file, str) and len(meta_file) > 0:
        command += f" --metadata-file {meta_file}"
    command += f" {org_name}"
    command += f" {org_id}"
    command += f" {org_type}"
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = f"Successfully initialized organization metadata!"
    return output, errCode

def add_org_metadata_desc(long_desc, short_desc, url, meta_path):
    # snet organization metadata-add-description [-h] [--description DESCRIPTION]
    #                                        [--short-description SHORT_DESCRIPTION]
    #                                        [--url URL]
    #                                        [--metadata-file METADATA_FILE]
    command = "snet --print-traceback organization metadata-add-description"
    if not isinstance(meta_path, str) or len(meta_path) <= 0:
        return "ERROR: Organization metadata file path is required", 42
    if long_desc and len(long_desc) > 0:
        command += f" --description \"{long_desc}\""
    if short_desc and len(short_desc) > 0:
        command += f" --short-description \"{short_desc}\""
    if url and len(url) > 0:
        command += f" --url {url}"
    command += f" --metadata-file {meta_path}"

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        return "Description successfully added!", 0
    return output, errCode

def add_org_metadata_assets(asset_file_path, metadata_file_name):
    # snet organization metadata-add-assets [-h] [--metadata-file METADATA_FILE]
    #                                   ASSET_FILE_PATH hero_image

    if not asset_file_path or len(asset_file_path) <= 0:
        return "ERROR: Asset file path is required", 42
    if not isinstance(metadata_file_name, str) or len(metadata_file_name) <= 0:
        return "ERROR: Organization metadata file path is required", 42
    command = "snet --print-traceback organization metadata-add-assets"
    command += f" {asset_file_path} hero_image"  # Assuming the asset type is always 'hero_image'
    command += f" --metadata-file {metadata_file_name}"

    output, errCode = run_shell_command(command)
    return output, errCode

def remove_all_org_metadata_assets(metadata_file_name):
    # snet organization metadata-remove-all-assets [-h]
    #                                          [--metadata-file METADATA_FILE]
    command = "snet --print-traceback organization metadata-remove-all-assets"
    if not isinstance(metadata_file_name, str) or len(metadata_file_name) <= 0:
        return "ERROR: Organization metadata file path is required", 42
    command += f" --metadata-file {metadata_file_name}"

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Successfully deleted all assets!"

    return output, errCode

def add_org_metadata_contact(contact_type, phone, email, metadata_file):
    # snet organization metadata-add-contact [-h] [--phone PHONE] [--email EMAIL]
    #                                    [--metadata-file METADATA_FILE]
    #                                    contact_type

    if not contact_type or len(contact_type) <= 0:
        return "ERROR: Contact type is required", 42
    if not isinstance(metadata_file, str) or len(metadata_file) <= 0:
        return "ERROR: Organization metadata file path is required", 42
    command = f"snet --print-traceback organization metadata-add-contact {contact_type}"
    if phone and len(phone) > 0:
        command += f" --phone {phone}"
    if email and len(email) > 0:
        command += f" --email {email}"
    command += f" --metadata-file {metadata_file}"

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Successfully added contact!"
    return output, errCode

def remove_org_metadata_contacts(metadata_file):
    # snet organization metadata-remove-all-contacts [-h]
    #                                            [--metadata-file METADATA_FILE]

    command = "snet --print-traceback organization metadata-remove-all-contacts"
    if not isinstance(metadata_file, str) or len(metadata_file) <= 0:
        return "ERROR: Organization metadata file path is required", 42
    
    command += f" --metadata-file {metadata_file}"

    output, errCode = run_shell_command(command)
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

    if org_id == None or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    if not isinstance(file_name, str) or len(file_name) <= 0:
        return "ERROR: Organization metadata file path is required", 42
    command = f"snet --print-traceback organization update-metadata {org_id}"
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

    output, errCode = run_shell_command(command)
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

    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    if not isinstance(metadata_file, str) or len(metadata_file) <= 0:
        return "ERROR: Organization metadata file path is required", 42
    command = f"snet --print-traceback organization create {org_id}"
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

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Organization successfully created!"
    return output, errCode

def change_organization_owner(org_id, owner_address, gas_price, wallet_index, quiet, verbose, registry_address):
    # snet organization change-owner [-h] [--gas-price GAS_PRICE]
    #                            [--wallet-index WALLET_INDEX] [--yes]
    #                            [--quiet | --verbose]
    #                            [--registry-at REGISTRY_ADDRESS]
    #                            ORG_ID OWNER_ADDRESS

    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    if not owner_address or len(owner_address) <= 0:
        return "ERROR: Must enter owner address", 42
    command = f"snet --print-traceback organization change-owner {org_id} {owner_address}"
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
        output = "Organization owner successfully changed!"
    return output, errCode

def add_org_metadata_members(org_id, org_members, gas_price, wallet_index, quiet, verbose, registry_address):
    # snet organization add-members [-h] [--gas-price GAS_PRICE]
    #                           [--wallet-index WALLET_INDEX] [--yes]
    #                           [--quiet | --verbose]
    #                           [--registry-at REGISTRY_ADDRESS]
    #                           ORG_ID ORG_MEMBERS
    
    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    if not org_members or len(org_members) <= 0:
        return "ERROR: Must enter organization members", 42
    command = f"snet --print-traceback organization add-members {org_id} [{org_members}]"
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
        output = "Members successfully added to organization!"
    return output, errCode

def remove_org_metadata_members(org_id, org_members, gas_price, wallet_index, quiet, verbose, registry_address):
    # snet organization rem-members [-h] [--gas-price GAS_PRICE]
    #                           [--wallet-index WALLET_INDEX] [--yes]
    #                           [--quiet | --verbose]
    #                           [--registry-at REGISTRY_ADDRESS]
    #                           ORG_ID ORG_MEMBERS
    
    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    if not org_members or len(org_members) <= 0:
        return "ERROR: Must enter organization members", 42
    command = f"snet --print-traceback organization rem-members {org_id} [{org_members}]"
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
        output = "Members successfully removed from organization!"
    return output, errCode

def delete_organization(org_id, gas_price, wallet_index, quiet, verbose, registry_address):
    # snet organization delete [-h] [--gas-price GAS_PRICE]
    #                      [--wallet-index WALLET_INDEX] [--yes]
    #                      [--quiet | --verbose]
    #                      [--registry-at REGISTRY_ADDRESS]
    #                      ORG_ID

    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    command = f"snet --print-traceback organization delete {org_id}"
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
    command = "snet --print-traceback organization list-my"
    if registry_address and len(registry_address) > 0:
        command += f" --registry-at {registry_address}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode != 0:
        output = f"ERROR: Unable to find organizations, ensure you have created one\nCLI Output: {output}"
    return output, errCode

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
    
    if not group_name or len(group_name) <= 0:
        return "ERROR: Must enter group name", 42
    if not pay_addr or len(pay_addr) <= 0:
        return "ERROR: Must enter group payment address", 42
    if not endpoints or len(endpoints) <= 0:
        return "ERROR: Must enter group endpoints", 42
    if not isinstance(metadata_file, str) or len(metadata_file) <= 0:
        return "ERROR: Organization metadata path is required", 42
    command = f"snet --print-traceback organization add-group {group_name} {pay_addr} {endpoints}"
    if payment_expiration_threshold and len(payment_expiration_threshold) > 0:
        command += f" --payment-expiration-threshold {payment_expiration_threshold}"
    if pay_chann_storage_type and len(pay_chann_storage_type) > 0:
        command += f" --payment-channel-storage-type {pay_chann_storage_type}"
    if pay_chann_conn_to and len(pay_chann_conn_to) > 0: 
        command += f" --payment-channel-connection-timeout {pay_chann_conn_to}"
    if pay_chann_req_to and len(pay_chann_req_to) > 0:
        command += f" --payment-channel-request-timeout {pay_chann_req_to}"
    command += f" --metadata-file {metadata_file}"
    if reg_addr and len(reg_addr) > 0:
        command += f" --registry-at {reg_addr}"

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Group successfully added to organization!"
    return output, errCode

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

    if not group_name or len(group_name) <= 0:
        return "ERROR: Must enter group name", 42
    if not isinstance(metadata_file, str) or len(metadata_file) <= 0:
        return "ERROR: Organization metadata path is required", 42
    command = f"snet --print-traceback organization update-group {group_name}"
    if pay_addr:
        command += f" --payment-address {pay_addr}"
    if endpoints:
        command += f" --endpoints {endpoints}"
    if payment_expiration_threshold:
        command += f" --payment-expiration-threshold {payment_expiration_threshold}"
    if pay_chann_storage_type:
        command += f" --payment-channel-storage-type {pay_chann_storage_type}"
    if pay_chann_conn_to:
        command += f" --payment-channel-connection-timeout {pay_chann_conn_to}"
    if pay_chann_req_to:
        command += f" --payment-channel-request-timeout {pay_chann_req_to}"
    command += f" --metadata-file {metadata_file}"
    if reg_addr and len(reg_addr) > 0:
        command += f" --registry-at {reg_addr}"

    output, errCode = run_shell_command(command)
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

    if not service_path or len(service_path) <= 0:
        return "ERROR: Must enter service directory path", 42
    if not proto_path or len(proto_path) <= 0:
        return "ERROR: Must enter protobuf directory path", 42
    if not service_display or len(service_display) <= 0:
        return "ERROR: Must enter service display name", 42

    command = f"snet --print-traceback service metadata-init {proto_path} \"{service_display}\""
    if metadata_file and len(metadata_file) > 0:
        command += f" --metadata-file {metadata_file}"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if pay_group_name and len(pay_group_name) > 0:
        command += f" --group-name {pay_group_name}"
    if endpoints:
        command += " --endpoints " + (endpoints)
    if fixed_price:
        command += f" --fixed-price {fixed_price}"
    if enc_type:
        command += f" --encoding {enc_type}"
    if serv_type:
        command += f" --service-type {serv_type}"

    output, errCode = run_shell_command(command, workdir=service_path)
    if len(output) == 0 and errCode == 0:
        output = "Service metadata successfully initialized!"
    return output, errCode

def add_service_metadata_desc(long_desc, short_desc, url, metadata_file):
    # snet service metadata-add-description [-h] [--json JSON] [--url URL]
    #                                   [--description DESCRIPTION]
    #                                   [--short-description SHORT_DESCRIPTION]
    #                                   [--metadata-file METADATA_FILE]
    
    
    if not metadata_file or len(metadata_file) <= 0:
        return "ERROR: Must enter service metadata file path", 42
    
    command = f"snet --print-traceback service metadata-add-description  --metadata-file {metadata_file}"

    if long_desc and len(long_desc) > 0:
        command += f" --description \"{long_desc}\""
    if short_desc and len(short_desc) > 0:
        command += f" --short-description \"{short_desc}\""
    if url and len(url) > 0:
        command += f" --url {url}"

    output, errCode = run_shell_command(command)
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
    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization ID", 42
    if not service_id or len(service_id) <= 0:
        return "ERROR: Must enter service ID", 42
    if not metadata_file or len(metadata_file) <= 0:
        return "ERROR: Must enter Metadata File path", 42

    command = f"snet --print-traceback service publish {org_id} {service_id}  --metadata-file {metadata_file}"
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

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Service successfully published!"
    return output, errCode

def delete_service(org_id, service_id, reg_addr, gas, index, quiet, verbose):
    # snet service delete [-h] [--registry-at REGISTRY_AT] [--gas-price GAS_PRICE]
    #                 [--wallet-index WALLET_INDEX] [--yes]
    #                 [--quiet | --verbose]
    #                 ORG_ID SERVICE_ID

    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization ID", 42
    if not service_id or len(service_id) <= 0:
        return "ERROR: Must enter service ID", 42

    command = f"snet --print-traceback service delete {org_id} {service_id}"
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

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Service successfully deleted!"
    return output, errCode

def add_org_members(org_id, mem_list, gas, index, quiet, verbose):
    # snet organization add-members [-h] [--gas-price GAS_PRICE]
    #                           [--wallet-index WALLET_INDEX] [--yes]
    #                           [--quiet | --verbose]
    #                           [--registry-at REGISTRY_ADDRESS]
    #                           ORG_ID ORG_MEMBERS
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42
    if not mem_list or len(mem_list) == 0:
        return "ERROR: Members list is required", 42
    command = f"snet --print-traceback organization add-members {org_id} {mem_list}"
    if gas and len(gas) > 0:
        command += f" --gas-price {gas}"
    if index and len(index) > 0:
        command += f" --wallet-index {index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    command += " --yes"

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Members successfully added to the organization!"
    return output, errCode

def remove_org_members(org_id, mem_list, gas, index, quiet, verbose):
    # snet organization rem-members [-h] [--gas-price GAS_PRICE]
    #                           [--wallet-index WALLET_INDEX] [--yes]
    #                           [--quiet | --verbose]
    #                           [--registry-at REGISTRY_ADDRESS]
    #                           ORG_ID ORG_MEMBERS
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42
    if not mem_list or len(mem_list) == 0:
        return "ERROR: Members list is required", 42
    command = f"snet --print-traceback organization rem-members {org_id} {mem_list}"
    if gas and len(gas) > 0:
        command += f" --gas-price {gas}"
    if index and len(index) > 0:
        command += f" --wallet-index {index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    command += " --yes"

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Members successfully removed from the organization!"
    return output, errCode

def change_org_owner(org_id, new_addr, gas, index, quiet, verbose):
    # snet organization change-owner [-h] [--gas-price GAS_PRICE]
    #                            [--wallet-index WALLET_INDEX] [--yes]
    #                            [--quiet | --verbose]
    #                            [--registry-at REGISTRY_ADDRESS]
    #                            ORG_ID OWNER_ADDRESS

    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42
    if not new_addr or len(new_addr) == 0:
        return "ERROR: New owner address is required", 42

    command = f"snet --print-traceback organization change-owner {org_id} {new_addr}"
    if gas and len(gas) > 0:
        command += f" --gas-price {gas}"
    if index and len(index) > 0:
        command += f" --wallet-index {index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    command += " --yes"

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Organization owner successfully changed!"
    return output, errCode

# def print_unclaimed_payments(endpoint):
#     # snet treasurer print-unclaimed [-h] --endpoint ENDPOINT
#     #                            [--wallet-index WALLET_INDEX]
#     # URGENT: Redo snetd endpoint retrieval
    
#     command = f"snet --print-traceback treasurer print-unclaimed --endpoint {endpoint}"

#     output, errCode = run_shell_command(command)
#     return output, errCode

def treasurer_claim(channels, endpoint, gas_price, wallet_index, quiet, verbose):
    # snet treasurer claim [-h] --endpoint ENDPOINT [--gas-price GAS_PRICE]
    #                  [--wallet-index WALLET_INDEX] [--yes]
    #                  [--quiet | --verbose]
    #                  CHANNELS [CHANNELS ...]
    if not channels or len(channels) == 0:
        return "ERROR: Channels list is required", 42
    if not endpoint or len(endpoint) == 0:
        return "ERROR: Endpoint is required", 42

    command = f"snet --print-traceback treasurer claim --endpoint {endpoint} {channels}"
    if gas_price and len(gas_price) > 0:
        command += f" --gas-price {gas_price}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    command += " --yes"

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Payments successfully claimed from channels!"
    return output, errCode

def treasurer_claim_all(endpoint, gas_price, wallet_index, quiet, verbose):
    # snet treasurer claim-all [-h] --endpoint ENDPOINT [--gas-price GAS_PRICE]
    #                      [--wallet-index WALLET_INDEX] [--yes]
    #                      [--quiet | --verbose]
    if not endpoint or len(endpoint) == 0:
        return "ERROR: Endpoint is required", 42

    command = f"snet --print-traceback treasurer claim-all --endpoint {endpoint}"
    if gas_price and len(gas_price) > 0:
        command += f" --gas-price {gas_price}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    command += " --yes"

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "All available payments successfully claimed!"
    return output, errCode

def treasurer_claim_expr(threshold: str, endpoint, gas_price, wallet_index, quiet, verbose):
    # snet treasurer claim-expired [-h]
    #                          [--expiration-threshold EXPIRATION_THRESHOLD]
    #                          --endpoint ENDPOINT [--gas-price GAS_PRICE]
    #                          [--wallet-index WALLET_INDEX] [--yes]
    #                          [--quiet | --verbose]

    try:
        if threshold is None or float(threshold) <= 0:
            return "ERROR: Invalid expiration threshold, must be a number > 0", 42
    except ValueError:
        return "ERROR: Invalid expiration threshold, must be a number > 0", 42
    if endpoint is None or len(endpoint) <= 0:
        return "ERROR: Endpoint is required", 42

    command = f"snet --print-traceback treasurer claim-expired --expiration-threshold {threshold} --endpoint {endpoint}"
    if gas_price and len(gas_price) > 0:
        command += f" --gas-price {gas_price}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    command += " --yes"

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        return "Claimed expired payments!", errCode
    return output, errCode

def service_metadata_set_model(proto_dir, metadata_file):
    # snet service metadata-set-model [-h] [--metadata-file METADATA_FILE] PROTO_DIR

    # Check for required parameters
    if not proto_dir or len(proto_dir) == 0:
        return "ERROR: Protobuf directory path is required", 42
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata file path is required", 42

    # Construct the command
    command = f"snet --print-traceback service metadata-set-model {proto_dir} --metadata-file {metadata_file}"

    # Execute the command
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Model successfully set in service metadata!"

    return output, errCode

def service_metadata_set_fixed_price(group_name, price, metadata_file):
    # snet service metadata-set-fixed-price [-h] [--metadata-file METADATA_FILE]
    #                                   group_name PRICE

    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata file path is required", 42
    try:
        if price is None or float(price) <= 0:
            return "ERROR: Price must be greater than 0", 42
    except ValueError:
        return "ERROR: Price must be a number greater than 0", 42

    command = f"snet --print-traceback service metadata-set-fixed-price {group_name} {price} --metadata-file {metadata_file}"

    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Fixed price successfully set in service metadata!"

    return output, errCode

def service_metadata_set_method_price(group_name, package_name, service_name, method, price, metadata_file):
    # snet service metadata-set-method-price [-h] [--metadata-file METADATA_FILE]
    #                                    group_name package_name service_name
    #                                    method PRICE
    
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42
    if not package_name or len(package_name) == 0:
        return "ERROR: Package name is required", 42
    if not service_name or len(service_name) == 0:
        return "ERROR: Service name is required", 42
    if not method or len(method) == 0:
        return "ERROR: Method is required", 42
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata file path is required", 42
    try:
        if price is None or float(price) <= 0:
            return "ERROR: Price must be greater than 0", 42
    except ValueError:
        return "ERROR: Price must be a number greater than 0", 42

    # Construct the command
    command = f"snet --print-traceback service metadata-set-method-price {group_name} {package_name} {service_name} {method} {price} --metadata-file {metadata_file}"

    # Execute the command
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Method price successfully set in service metadata!"

    return output, errCode

def service_metadata_set_free_calls(group_name, free_calls: str, metadata_file):
    # snet service metadata-set-free-calls [-h] [--metadata-file METADATA_FILE]
    #                                  GROUP_NAME free_calls

    # Validate input parameters
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata file path is required", 42
    try:
        if free_calls is None or int(free_calls) < 0:
            return "ERROR: Free calls must be a non-negative integer", 42
    except ValueError:
        return "ERROR: Free calls must be a non-negative integer", 42

    # Construct the command
    command = f"snet --print-traceback service metadata-set-free-calls {group_name} {free_calls} --metadata-file {metadata_file}"

    # Execute the command
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Free calls successfully set in service metadata!"

    return output, errCode

def service_metadata_set_freecall_signer_addr(group_name, signer_addr, metadata_file):
    # snet service metadata-set-freecall-signer-address [-h]
    #                                               [--metadata-file METADATA_FILE]
    #                                               GROUP_NAME signer_address

    # Validate input parameters
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42
    if not signer_addr or len(signer_addr) == 0:
        return "ERROR: Signer address is required", 42
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata file path is required", 42

    # Construct the command
    command = f"snet --print-traceback service metadata-set-freecall-signer-address {group_name} {signer_addr} --metadata-file {metadata_file}"

    # Execute the command
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Freecall signer address successfully set in service metadata!"

    return output, errCode

def service_metadata_add_group(group_name, metadata_file):
    # snet service metadata-add-group [-h] [--metadata-file METADATA_FILE]
    #                             GROUP_NAME

    # Check for required parameters
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata path is required", 42
    
    # Construct the command
    command = f"snet --print-traceback service metadata-add-group {group_name} --metadata-file {metadata_file}"

    # Execute the command
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Group successfully added to service metadata!"

    return output, errCode

def service_metadata_remove_group(group_name, metadata_file):
    # snet service metadata-remove-group [-h] [--metadata-file METADATA_FILE]
    #                                GROUP_NAME

    # Check for required parameters
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata path is required", 42

    # Construct the command
    command = f"snet --print-traceback service metadata-remove-group {group_name} --metadata-file {metadata_file}"

    # Execute the command
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Group successfully removed from service metadata!"

    return output, errCode

def service_metadata_add_daemon_addr(group_name, daemon_addr, metadata_file):
    # snet service metadata-add-daemon-addresses [-h]
    #                                        [--metadata-file METADATA_FILE]
    #                                        group_name DAEMON ADDRESSES
    #                                        [DAEMON ADDRESSES ...]

    # Check for required parameters
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42
    if not daemon_addr or len(daemon_addr) == 0:
        return "ERROR: Daemon address is required", 42
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata path is required", 42
    
    # Construct the command
    command = f"snet --print-traceback service metadata-add-daemon-addresses {group_name} {daemon_addr} --metadata-file {metadata_file}"

    # Execute the command
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Daemon address successfully added to service metadata!"

    return output, errCode

def service_metadata_remove_daemon_addr(group_name, daemon_addr, metadata_file):
    # snet service metadata-remove-all-daemon-addresses [-h]
    #                                               [--metadata-file METADATA_FILE]
    #                                               group_name

    # Check for required parameters
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata path is required", 42
    
    # Construct the command
    command = f"snet --print-traceback service metadata-remove-all-daemon-addresses {group_name} --metadata-file {metadata_file}"

    # Execute the command
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Daemon address successfully removed from service metadata!"

    return output, errCode

def service_metadata_add_assets(asset_path, asset_type, metadata_file):
    # snet service metadata-add-assets [-h] [--metadata-file METADATA_FILE]
    #                              asset_file_path asset_type

    # Check for required parameters
    if not asset_path or len(asset_path) == 0:
        return "ERROR: Asset path is required", 42
    if not asset_type or len(asset_type) == 0:
        return "ERROR: Asset type is required", 42
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata path is required", 42

    # Construct the command
    command = f"snet --print-traceback service metadata-add-assets {asset_path} {asset_type} --metadata-file {metadata_file}"

    # Execute the command
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Asset successfully added to service metadata!"

    return output, errCode

def service_metadata_remove_assets(asset_type, metadata_file):
    # snet service metadata-remove-assets [-h] [--metadata-file METADATA_FILE]
    #                                 asset_type

    # Check for required parameters
    if not asset_type or len(asset_type) == 0:
        return "ERROR: Asset type is required", 42
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata path is required", 42

    # Construct the command
    command = f"snet --print-traceback service metadata-remove-assets {asset_type} --metadata-file {metadata_file}"

    # Execute the command
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Asset successfully removed from service metadata!"

    return output, errCode

def service_metadata_add_media(url, hero_image, metadata_file):
    # snet service metadata-add-media [-h] [--hero_image]
    #                             [--metadata-file METADATA_FILE]
    #                             MEDIA_URL

    # Check for required parameters
    if not url or len(url) == 0:
        return "ERROR: Media URL is required", 42
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata path is required", 42

    # Construct the command
    command = f"snet --print-traceback service metadata-add-media --metadata-file {metadata_file}  {url}"
    if hero_image:
        command += " --hero-image"

    # Execute the command
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Media successfully added to service metadata!"

    return output, errCode

def service_metadata_remove_media(metadata_file):
    # snet service metadata-remove-all-media [-h] [--metadata-file METADATA_FILE]

    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata path is required", 42
    
    # Construct the command
    command = f"snet --print-traceback service metadata-remove-all-media --metadata-file {metadata_file}"

    # Execute the command
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "All media successfully removed from service metadata!"

    return output, errCode

def service_metadata_update_daemon_addr(group_name, daemon_addr, metadata_file):
    # snet service metadata-update-daemon-addresses [-h]
    #                                           [--metadata-file METADATA_FILE]
    #                                           group_name DAEMON ADDRESSES
    #                                           [DAEMON ADDRESSES ...]

    # Check for required parameters
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42
    if not daemon_addr or len(daemon_addr) == 0:
        return "ERROR: New daemon address is required", 42
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata path is required", 42

    # Construct the command
    command = f"snet --print-traceback service metadata-update-daemon-addresses {group_name} {daemon_addr}  --metadata-file {metadata_file}"

    # Execute the command
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Daemon address successfully updated in service metadata!"

    return output, errCode

def service_metadata_update_validate_metadata(metadata_file):
    # snet service validate-metadata [-h] [--metadata-file METADATA_FILE]

    # Check for required parameters
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata file path is required", 42

    # Construct the command
    command = f"snet --print-traceback service validate-metadata --metadata-file {metadata_file}"

    # Execute the command
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Service metadata validation successful!"

    return output, errCode

def service_metadata_update_update_metadata(org_id, service_id, metadata_file, reg_addr, mpe_addr, update_mpe, gas, index, quiet, verbose):
    # snet service update-metadata [-h] [--metadata-file METADATA_FILE]
    #                          [--update-mpe-address]
    #                          [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                          [--registry-at REGISTRY_AT]
    #                          [--gas-price GAS_PRICE]
    #                          [--wallet-index WALLET_INDEX] [--yes]
    #                          [--quiet | --verbose]
    #                          ORG_ID SERVICE_ID

    # Check for required parameters
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42
    if not service_id or len(service_id) == 0:
        return "ERROR: Service ID is required", 42
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata file path is required", 42

    # Construct the command
    command = f"snet --print-traceback service update-metadata {org_id} {service_id}"
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

    # Execute the command
    output, errCode = run_shell_command(command)
    if len(output) == 0 and errCode == 0:
        output = "Service metadata successfully updated!"

    return output, errCode

def print_service_status(org_id, service_id, pay_group, reg_addr):
    # snet service print-service-status [-h] [--registry-at REGISTRY_AT]
    #                               [--group-name GROUP_NAME]
    #                               ORG_ID SERVICE_ID

    # Check for required parameters
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42
    if not service_id or len(service_id) == 0:
        return "ERROR: Service ID is required", 42

    # Construct the command
    command = f"snet --print-traceback service print-service-status {org_id} {service_id}"
    if pay_group and len(pay_group) > 0:
        command += f" --group-name {pay_group}"
    if reg_addr and len(reg_addr) > 0:
        command += f" --registry-at {reg_addr}"

    # Execute the command
    output, errCode = run_shell_command(command)
    return output, errCode

def print_service_api_metadata(proto_dir, metadata_file):
    # snet service get-api-metadata [-h] [--metadata-file METADATA_FILE] PROTO_DIR

    # Check for required parameters
    if not proto_dir or len(proto_dir) == 0:
        return "ERROR: Protobuf directory path is required", 42
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata file path is required", 42

    # Construct the command
    command = f"snet --print-traceback service get-api-metadata {proto_dir} --metadata-file {metadata_file}"

    # Execute the command
    output, errCode = run_shell_command(command)
    return output, errCode


def print_service_api_registry(org_id, service_id, reg_addr, proto_dir):
    # snet service get-api-registry [-h] [--registry-at REGISTRY_AT]
    #                           ORG_ID SERVICE_ID PROTO_DIR

    # Check for required parameters
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42
    if not service_id or len(service_id) == 0:
        return "ERROR: Service ID is required", 42
    if not proto_dir or len(proto_dir) == 0:
        return "ERROR: Protobuf directory path is required", 42

    # Construct the command
    command = f"snet --print-traceback service get-api-registry {org_id} {service_id} {proto_dir}"
    if reg_addr and len(reg_addr) > 0:
        command += f" --registry-at {reg_addr}"

    # Execute the command
    output, errCode = run_shell_command(command)
    return output, errCode

def client_call(org_id, serv_id, group_name, method, params, proto_serv=None, mpe_addr=None, file_name=None, endpoint=None, channel_id=None, from_block=None, skip_update=False, wallet_index=None, view=True):
    # snet client call [-h] [--service SERVICE] [--wallet-index WALLET_INDEX]
    #              [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #              [--save-response FILENAME]
    #              [--save-field SAVE_FIELD SAVE_FIELD] [--endpoint ENDPOINT]
    #              [--channel-id CHANNEL_ID] [--from-block FROM_BLOCK] [--yes]
    #              [--skip-update-check]
    #              ORG_ID SERVICE_ID group_name METHOD [PARAMS]

    # Check for required parameters
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42, None
    if not serv_id or len(serv_id) == 0:
        return "ERROR: Service ID is required", 42, None
    if not method or len(method) == 0:
        return "ERROR: Method name of target service is required", 42, None
    if not params or len(params) == 0:
        return "ERROR: Parameters file path for method call are required", 42, None

    # Construct command
    command = f"snet --print-traceback client call {org_id} {serv_id}"
    if group_name and len(group_name) > 0:
        command += f" {group_name}"
    command += f" {method} {params}"

    if proto_serv and len(proto_serv) > 0:
        command += f" --service {proto_serv}"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if file_name and len(file_name) > 0:
        command += f" --save-response {file_name}"
    if endpoint and len(endpoint) > 0:
        command += f" --endpoint {endpoint}"
    if channel_id and len(channel_id) > 0:
        command += f" --channel-id {channel_id}"
    if from_block and len(from_block) > 0:
        command += f" --from-block {from_block}"
    if skip_update:
        command += " --skip-update-check"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"

    # Run command
    if view:
        output, errCode = run_shell_command_with_input(command=command, input_text="n\n")
    else:
        output, errCode = run_shell_command_with_input(command=command, input_text="y\n")

    return output, errCode, command

def client_low_call(org_id, serv_id, group_name, channel_id, nonce, cog_amt, method, params, proto_serv, mpe_addr, file_name, endpoint, wallet_index, view):
    # snet client call-lowlevel [-h] [--service SERVICE]
    #                       [--wallet-index WALLET_INDEX]
    #                       [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                       [--save-response FILENAME]
    #                       [--save-field SAVE_FIELD SAVE_FIELD]
    #                       [--endpoint ENDPOINT]
    #                       ORG_ID SERVICE_ID group_name CHANNEL_ID NONCE
    #                       AMOUNT_IN_COGS METHOD [PARAMS]

    # Check for required parameters
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42, None
    if not serv_id or len(serv_id) == 0:
        return "ERROR: Service ID is required", 42, None
    if not channel_id or len(channel_id) == 0:
        return "ERROR: Channel ID is required", 42, None
    if not nonce or len(nonce) == 0:
        return "ERROR: Nonce is required", 42, None
    try:
        if not cog_amt or float(cog_amt) < 0:
            return "ERROR: Amount of cogs > 0 is required", 42, None
    except ValueError:
        return "ERROR: Amount of cogs > 0 is required", 42, None
    if not method or len(method) == 0:
        return "ERROR: Method name of target service is required", 42, None
    if not params or len(params) == 0:
        return "ERROR: Params file path is required", 42, None

    # Construct command
    command = f"snet --print-traceback client call-lowlevel {org_id} {serv_id}"
    if group_name and len(group_name) > 0:
        command += f" {group_name}"
    command += f" {channel_id} {nonce} {cog_amt} {method} {params}"
    

    if proto_serv and len(proto_serv) > 0:
        command += f" --service {proto_serv}"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if file_name and len(file_name) > 0:
        command += f" --save-response {file_name}"
    if endpoint and len(endpoint) > 0:
        command += f" --endpoint {endpoint}"
    if channel_id and len(channel_id) > 0:
        command += f" --channel-id {channel_id}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"

    # Run command
    if view:
        output, errCode = run_shell_command_with_input(command=command, input_text="n\n")
    else:
        output, errCode = run_shell_command_with_input(command=command, input_text="y\n")

    return output, errCode, command

def get_channel_state(channel_id, endpoint, mpe_addr, wallet_index, view):
    # snet client get-channel-state [-h] [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                           [--wallet-index WALLET_INDEX]
    #                           CHANNEL_ID ENDPOINT

    # Check for required parameters
    if not channel_id or len(channel_id) == 0:
        return "ERROR: Channel ID is required", 42, None
    if not endpoint or len(endpoint) == 0:
        return "ERROR: Service endpoint is required", 42, None

    # Construct command
    command = f"snet --print-traceback client call-lowlevel {channel_id} {endpoint}"

    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"

    # Run command
    if view:
        output, errCode = run_shell_command_with_input(command=command, input_text="n\n")
    else:
        output, errCode = run_shell_command_with_input(command=command, input_text="y\n")

    return output, errCode, command

def custom_command(root, sub, args, cwd, traceback):
    # snet [-h] COMMAND SUBCOMMAND ARGS

    command = root + " " + sub + " " + args
    
    if not command or len(command) <= 0:
        return "ERROR: Please input a command to run", 42
    if traceback:
        cmd = f"snet --print-traceback {command}"
    else:
        cmd = f"snet {command}"
    if cwd and len(cwd) > 0:
        output, errCode = run_shell_command(cmd, workdir=cwd)
    else:
        output, errCode = run_shell_command(cmd)

    return output, errCode

def custom_conditional_command(root, sub, args, cwd, traceback, view):
    # snet [-h] COMMAND SUBCOMMAND ARGS

    command = f"{root} {sub} {args}"

    if not command or len(command) <= 0:
        return "ERROR: Please input a command to run", 42
    if traceback:
        cmd = f"snet --print-traceback {command}"
    else:
        cmd = f"snet {command}"

    if view:
        if cwd and len(cwd) > 0:
            output, errCode = run_shell_command_with_input(cmd, input_text="n\n", workdir=cwd)
        else:
            output, errCode = run_shell_command_with_input(cmd, input_text="n\n")
    else:
        if cwd and len(cwd) > 0:
            output, errCode = run_shell_command_with_input(cmd, input_text="y\n", workdir=cwd)
        else:
            output, errCode = run_shell_command_with_input(cmd, input_text="y\n")

    return output, errCode, cmd

def custom_conditional_check(root, sub):
    global condCommDict
    comm = root + " " + sub
    return comm in condCommDict


