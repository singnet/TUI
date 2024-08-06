import subprocess
from textual.widgets import Button, Select
from textual.containers import Vertical
import re

# Stable build v0.1

current_process = None

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
    
def run_shell_command(command, input_text=None, workdir=None):
    global current_process 
    
    try:
        if workdir != None:
            current_process = subprocess.Popen(args=command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=workdir)
        else:
            current_process = subprocess.Popen(args=command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if input_text != None:
            stdout, stderr = current_process.communicate(input=input_text)
        else:
           stdout, stderr = current_process.communicate() 
        
        if stdout:
            return stdout, 0
        elif stderr:
            return stderr, 1
        else:
            return stdout, 42

    except Exception as e:
        return str(e), 1

def cancel_current_process():
    global current_process
    if current_process:
        current_process.terminate()
        try:
            current_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            current_process.kill()
        current_process = None
        return "Process cancelled", 0
    return "No process to cancel", 1

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

def create_identity_cli(id_name, misc_inp, network, type):
    # snet identity create [-h] [--mnemonic MNEMONIC] [--private-key PRIVATE_KEY]
    #                  [--keystore-path KEYSTORE_PATH] [--network NETWORK]
    #                  [--wallet-index WALLET_INDEX]
    #                  IDENTITY_NAME IDENTITY_TYPE
    command = f"snet --print-traceback identity create {id_name} {type} --network {network}"

    if type == "mnemonic":
        command += f" --mnemonic {misc_inp}"
    elif type == "key":
        command += f" --private-key {misc_inp}"
    elif type == "keystore":
        command += f" --keystore-path {misc_inp}"

    output, errCode = run_shell_command(command)
    return output, errCode

def delete_identity_cli(id_name):
    output, errCode = run_shell_command(f"snet --print-traceback identity delete {id_name}")
    return output, errCode

def account_deposit(agi_amount, contract_address, mpe_address, wallet_index, quiet, verbose):
    # snet account deposit [-h] [--singularitynettoken-at SINGULARITYNETTOKEN_AT]
    #                  [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                  [--wallet-index WALLET_INDEX]
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
    if isinstance(wallet_index, str) and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    command += " --yes"
    command += f" {agi_amount}"

    return run_shell_command(command)

def account_withdraw(agi_amount, mpe_address, wallet_index, quiet, verbose):
    # snet account withdraw [-h] [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                   [--wallet-index WALLET_INDEX]
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
    if isinstance(wallet_index, str) and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"
    command += " --yes"
    command += f" {agi_amount}"

    return run_shell_command(command)

def account_transfer(reciever_addr, agi_amount, mpe_address, wallet_index, quiet, verbose):
    # snet account transfer [-h] [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                   [--wallet-index WALLET_INDEX]
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

def update_org_metadata(org_id, file_name, mem_list, index, quiet, verbose):
    # snet organization update-metadata [-h] [--metadata-file METADATA_FILE]
    #                               [--members ORG_MEMBERS]
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

def create_organization(org_id, metadata_file, members, index, quiet, verbose, registry_address):
    # snet organization create [-h] [--metadata-file METADATA_FILE]
    #                      [--members ORG_MEMBERS] 
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

def change_organization_owner(org_id, owner_address, wallet_index, quiet, verbose, registry_address):
    # snet organization change-owner [-h] 
    #                            [--wallet-index WALLET_INDEX] [--yes]
    #                            [--quiet | --verbose]
    #                            [--registry-at REGISTRY_ADDRESS]
    #                            ORG_ID OWNER_ADDRESS

    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    if not owner_address or len(owner_address) <= 0:
        return "ERROR: Must enter owner address", 42
    command = f"snet --print-traceback organization change-owner {org_id} {owner_address}"
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

def add_org_metadata_members(org_id, org_members, wallet_index, quiet, verbose, registry_address):
    # snet organization add-members [-h] 
    #                           [--wallet-index WALLET_INDEX] [--yes]
    #                           [--quiet | --verbose]
    #                           [--registry-at REGISTRY_ADDRESS]
    #                           ORG_ID ORG_MEMBERS
    
    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    if not org_members or len(org_members) <= 0:
        return "ERROR: Must enter organization members", 42
    command = f"snet --print-traceback organization add-members {org_id} [{org_members}]"
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

def remove_org_metadata_members(org_id, org_members, wallet_index, quiet, verbose, registry_address):
    # snet organization rem-members [-h] 
    #                           [--wallet-index WALLET_INDEX] [--yes]
    #                           [--quiet | --verbose]
    #                           [--registry-at REGISTRY_ADDRESS]
    #                           ORG_ID ORG_MEMBERS
    
    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    if not org_members or len(org_members) <= 0:
        return "ERROR: Must enter organization members", 42
    command = f"snet --print-traceback organization rem-members {org_id} [{org_members}]"
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

def delete_organization(org_id, wallet_index, quiet, verbose, registry_address):
    # snet organization delete [-h] 
    #                      [--wallet-index WALLET_INDEX] [--yes]
    #                      [--quiet | --verbose]
    #                      [--registry-at REGISTRY_ADDRESS]
    #                      ORG_ID

    if not org_id or len(org_id) <= 0:
        return "ERROR: Must enter organization identity", 42
    command = f"snet --print-traceback organization delete {org_id}"
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

def publish_service(org_id, service_id, metadata_file, reg_addr, mpe_addr, update_mpe, index, quiet, verbose):
    # snet service publish [-h] [--metadata-file METADATA_FILE]
    #                  [--update-mpe-address]
    #                  [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                  [--registry-at REGISTRY_AT] 
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

def delete_service(org_id, service_id, reg_addr, index, quiet, verbose):
    # snet service delete [-h] [--registry-at REGISTRY_AT] 
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

def get_all_organizations_and_services():
    org_list, err_code = run_shell_command("snet organization list")
    if err_code != 0:
        return f"Error fetching organizations: {org_list}", err_code

    org_ids = [line.strip() for line in org_list.split('\n')[1:]]

    marketplace_data = {}

    for org_id in org_ids:
        if len(org_id) > 0:
            services_list, err_code = run_shell_command(f"snet organization list-services {org_id}")
            if err_code != 0:
                marketplace_data[org_id] = f"Error fetching services: {services_list}"
            else:
                services = [line.strip() for line in services_list.split('\n')[1:]]
                marketplace_data[org_id] = services

    return marketplace_data, 0

def search_organizations_and_services(data, phrase):
    results = {}
    phrase = phrase.lower()

    for org_id, services in data.items():
        org_matches = phrase in org_id.lower()
        if isinstance(services, str):
            if org_matches or phrase in services.lower():
                results[org_id] = services
        else:
            matching_services = [service for service in services if phrase in service.lower()]
            if org_matches or matching_services:
                results[org_id] = services if org_matches else matching_services

    return results

def format_marketplace_data(data):
    output = []
    for org_id, services in data.items():
        output.append(f"Organization ID: {org_id}")
        if isinstance(services, str):
            output.append(f"  {services}")
        elif services:
            for service in services:
                output.append(f"  {service}")
        else:
            output.append("  No services found")
        output.append("")
    return "\n".join(output)

def add_org_members(org_id, mem_list, index, quiet, verbose):
    # snet organization add-members [-h] 
    #                           [--wallet-index WALLET_INDEX] [--yes]
    #                           [--quiet | --verbose]
    #                           [--registry-at REGISTRY_ADDRESS]
    #                           ORG_ID ORG_MEMBERS
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42
    if not mem_list or len(mem_list) == 0:
        return "ERROR: Members list is required", 42
    command = f"snet --print-traceback organization add-members {org_id} {mem_list}"
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

def remove_org_members(org_id, mem_list, index, quiet, verbose):
    # snet organization rem-members [-h] 
    #                           [--wallet-index WALLET_INDEX] [--yes]
    #                           [--quiet | --verbose]
    #                           [--registry-at REGISTRY_ADDRESS]
    #                           ORG_ID ORG_MEMBERS
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42
    if not mem_list or len(mem_list) == 0:
        return "ERROR: Members list is required", 42
    command = f"snet --print-traceback organization rem-members {org_id} {mem_list}"
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

def change_org_owner(org_id, new_addr, index, quiet, verbose):
    # snet organization change-owner [-h] 
    #                            [--wallet-index WALLET_INDEX] [--yes]
    #                            [--quiet | --verbose]
    #                            [--registry-at REGISTRY_ADDRESS]
    #                            ORG_ID OWNER_ADDRESS

    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42
    if not new_addr or len(new_addr) == 0:
        return "ERROR: New owner address is required", 42

    command = f"snet --print-traceback organization change-owner {org_id} {new_addr}"
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

def treasurer_claim(channels, endpoint, wallet_index, quiet, verbose):
    # snet treasurer claim [-h] --endpoint ENDPOINT 
    #                  [--wallet-index WALLET_INDEX] [--yes]
    #                  [--quiet | --verbose]
    #                  CHANNELS [CHANNELS ...]
    if not channels or len(channels) == 0:
        return "ERROR: Channels list is required", 42
    if not endpoint or len(endpoint) == 0:
        return "ERROR: Endpoint is required", 42

    command = f"snet --print-traceback treasurer claim --endpoint {endpoint} {channels}"
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

def treasurer_claim_all(endpoint, wallet_index, quiet, verbose):
    # snet treasurer claim-all [-h] --endpoint ENDPOINT 
    #                      [--wallet-index WALLET_INDEX] [--yes]
    #                      [--quiet | --verbose]
    if not endpoint or len(endpoint) == 0:
        return "ERROR: Endpoint is required", 42

    command = f"snet --print-traceback treasurer claim-all --endpoint {endpoint}"
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

def treasurer_claim_expr(threshold: str, endpoint, wallet_index, quiet, verbose):
    # snet treasurer claim-expired [-h]
    #                          [--expiration-threshold EXPIRATION_THRESHOLD]
    #                          --endpoint ENDPOINT 
    #                          [--wallet-index WALLET_INDEX] [--yes]
    #                          [--quiet | --verbose]

    if endpoint is None or len(endpoint) <= 0:
        return "ERROR: Endpoint is required", 42

    command = f"snet --print-traceback treasurer claim-expired  --endpoint {endpoint}"

    if threshold and len(threshold) > 0:
        try:
            if float(threshold) <= 0:
                return "ERROR: Invalid expiration threshold, must be a number > 0", 42
        except ValueError:
            return "ERROR: Invalid expiration threshold, must be a number > 0", 42
        
        command += f" --expiration-threshold {threshold}"
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

def service_metadata_update_update_metadata(org_id, service_id, metadata_file, reg_addr, mpe_addr, update_mpe, index, quiet, verbose):
    # snet service update-metadata [-h] [--metadata-file METADATA_FILE]
    #                          [--update-mpe-address]
    #                          [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                          [--registry-at REGISTRY_AT]
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
    if not group_name or len(group_name) == 0:
        return "ERROR: Payment group name is required", 42

    # Construct command
    command = f"snet --print-traceback client call {org_id} {serv_id} {group_name} {method} {params}"

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
        output, errCode = run_shell_command(command=command, input_text="n\n")
    else:
        output, errCode = run_shell_command(command=f"{command} --yes")

    return output, errCode, command

def client_low_call(org_id, serv_id, group_name, channel_id, nonce, cog_amt, method, params, proto_serv, mpe_addr, file_name, endpoint, wallet_index):
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
        return "ERROR: Organization ID is required", 42
    if not serv_id or len(serv_id) == 0:
        return "ERROR: Service ID is required", 42
    if not channel_id or len(channel_id) == 0:
        return "ERROR: Channel ID is required", 42
    if not group_name or len(group_name) == 0:
        return "ERROR: Payment group name is required", 42
    if not nonce or len(nonce) == 0:
        return "ERROR: Nonce is required", 42
    try:
        if not cog_amt or float(cog_amt) < 0:
            return "ERROR: Amount of cogs > 0 is required", 42
    except ValueError:
        return "ERROR: Amount of cogs > 0 is required", 42
    if not method or len(method) == 0:
        return "ERROR: Method name of target service is required", 42
    if not params or len(params) == 0:
        return "ERROR: Params file path is required", 42

    # Construct command
    command = f"snet --print-traceback client call-lowlevel {org_id} {serv_id} {group_name} {channel_id} {nonce} {cog_amt} {method} {params}"
    
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
    output, errCode = run_shell_command(command)
    return output, errCode

def get_channel_state(channel_id, endpoint, mpe_addr, wallet_index):
    # snet client get-channel-state [-h] [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                           [--wallet-index WALLET_INDEX]
    #                           CHANNEL_ID ENDPOINT

    # Check for required parameters
    if not channel_id or len(channel_id) == 0:
        return "ERROR: Channel ID is required", 42
    if not endpoint or len(endpoint) == 0:
        return "ERROR: Service endpoint is required", 42

    # Construct command
    command = f"snet --print-traceback client get-channel-state {channel_id} {endpoint}"

    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"

    # Run command
    output, errCode = run_shell_command(command)
    return output, errCode

def channel_init(org_id, group_name, channel_id, registry, mpe_addr):
    # snet channel init [-h] [--registry-at REGISTRY_AT]
    #               [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #               ORG_ID group_name CHANNEL_ID

    # Check for required parameters
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42
    if not channel_id or len(channel_id) == 0:
        return "ERROR: Channel ID is required", 42
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42

    # Construct command
    command = f"snet --print-traceback channel init {org_id} {group_name} {channel_id}"
    
    if registry and len(registry) > 0:
        command += f" --registry-at {registry}"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"

    # Run command
    output, errCode = run_shell_command(command)
    return output, errCode


def channel_init_metadata(org_id, group_name, channel_id, registry, mpe_addr, meta_file, wallet_index):
    # snet channel init-metadata [-h] [--registry-at REGISTRY_AT]
    #                        [--metadata-file METADATA_FILE]
    #                        [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                        [--wallet-index WALLET_INDEX]
    #                        ORG_ID group_name CHANNEL_ID

    # Check for required parameters
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42
    if not channel_id or len(channel_id) == 0:
        return "ERROR: Channel ID is required", 42
    if not meta_file or len(meta_file) == 0:
        return "ERROR: Metadata file path is required", 42
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42

    # Construct command
    command = f"snet --print-traceback channel init-metadata {org_id} {group_name} {channel_id} --metadata-file {meta_file}"
    
    if registry and len(registry) > 0:
        command += f" --registry-at {registry}"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"

    # Run command
    output, errCode = run_shell_command(command)
    return output, errCode

def channel_open_init(org_id, group_name, agi_amount, expr, registry, force, signer, mpe_addr, open_anyway, from_block, wallet_index, quiet, verbose, view):
    # snet channel open-init [-h] [--registry-at REGISTRY_AT] [--force]
    #                    [--signer SIGNER]
    #                    [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                    [--wallet-index WALLET_INDEX]
    #                    [--yes] [--quiet | --verbose] [--open-new-anyway]
    #                    [--from-block FROM_BLOCK]
    #                    ORG_ID group_name AMOUNT EXPIRATION

    # Check for required parameters
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42, None
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42
    if not expr or len(expr) <= 0:
            return "ERROR: Expiration time is required", 42, None
    
    try:
        if not agi_amount or float(agi_amount) <= 0:
            return "ERROR: Amount of AGI must be greater than 0", 42, None
    except ValueError:
        return "ERROR: Amount of AGI must be a valid number greater than 0", 42, None
    
    # try:
    #     if not expr or int(expr) <= 0:
    #         return "ERROR: Expiration must be a positive integer", 42, None
    # except ValueError:
    #     return "ERROR: Expiration must be a valid positive integer", 42, None

    # Construct command
    command = f"snet channel open-init {org_id} {group_name} {agi_amount} {expr}"
    
    if registry and len(registry) > 0:
        command += f" --registry-at {registry}"
    if force:
        command += " --force"
    if signer and len(signer) > 0:
        command += f" --signer {signer}"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if open_anyway:
        command += " --open-new-anyway"
    if from_block and len(from_block) > 0:
        command += f" --from-block {from_block}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"

    # Run command
    if view:
        output, errCode = run_shell_command(command=command, input_text="n\n")
    else:
        output, errCode = run_shell_command(command=f"{command} --yes") 

    return output, errCode, command

def channel_open_init_metadata(org_id, group_name, agi_amount, expr, registry, force, signer, mpe_addr, open_anyway, from_block, metadata_file, wallet_index, quiet, verbose, view):
    # snet channel open-init-metadata [-h] [--registry-at REGISTRY_AT] [--force]
    #                             [--signer SIGNER]
    #                             [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                             [--wallet-index WALLET_INDEX] [--yes]
    #                             [--quiet | --verbose] [--open-new-anyway]
    #                             [--from-block FROM_BLOCK]
    #                             [--metadata-file METADATA_FILE]
    #                             ORG_ID group_name AMOUNT EXPIRATION

    # Check for required parameters
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42, None
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42
    if not expr or len(expr) <= 0:
            return "ERROR: Expiration time is required", 42, None
    
    try:
        if not agi_amount or float(agi_amount) <= 0:
            return "ERROR: Amount of AGI must be greater than 0", 42, None
    except ValueError:
        return "ERROR: Amount of AGI must be a valid number greater than 0", 42, None
    
    # try:
    #     if not expr or int(expr) <= 0:
    #         return "ERROR: Expiration must be a positive integer", 42, None
    # except ValueError:
    #     return "ERROR: Expiration must be a valid positive integer", 42, None
    
    if not metadata_file or len(metadata_file) == 0:
        return "ERROR: Metadata file path is required", 42, None

    # Construct command
    command = f"snet channel open-init-metadata {org_id} {group_name} {agi_amount} {expr} --metadata-file {metadata_file}"
    
    if registry and len(registry) > 0:
        command += f" --registry-at {registry}"
    if force:
        command += " --force"
    if signer and len(signer) > 0:
        command += f" --signer {signer}"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if open_anyway:
        command += " --open-new-anyway"
    if from_block and len(from_block) > 0:
        command += f" --from-block {from_block}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"

    # Run command
    if view:
        output, errCode = run_shell_command(command=command, input_text="n\n")
    else:
        output, errCode = run_shell_command(command=f"{command} --yes") 

    return output, errCode, command


def channel_extend_add(channel_id, mpe_addr, expr, force, agi_amount, wallet_index, quiet, verbose, view):
    # snet channel extend-add [-h] [--expiration EXPIRATION] [--force]
    #                     [--amount AMOUNT]
    #                     [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                     [--wallet-index WALLET_INDEX]
    #                     [--yes] [--quiet | --verbose]
    #                     CHANNEL_ID

    # Check for required parameters
    if not channel_id or len(channel_id) == 0:
        return "ERROR: Channel ID is required", 42, None

    # Construct command
    command = f"snet --print-traceback channel extend-add {channel_id}"
    
    if expr and len(expr) > 0:
        command += f" --expiration {expr}"
    if force:
        command += " --force"
    if agi_amount and len(agi_amount) > 0:
        try:
            if agi_amount and float(agi_amount) < 0:
                return "ERROR: Amount of AGI must be greater than or equal to 0", 42, None
        except ValueError:
            return "ERROR: Amount of AGI must be a valid number", 42, None
        command += f" --amount {agi_amount}"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"

    # Run command
    if view:
        output, errCode = run_shell_command(command=command, input_text="n\n")
    else:
        output, errCode = run_shell_command(command=f"{command} --yes") 

    return output, errCode, command

def channel_extend_add_org(org_id, group_name, registry, mpe_addr, channel_id, from_block, expr, force, agi_amount, wallet_index, quiet, verbose, view):
    # snet channel extend-add-for-org [-h] [--registry-at REGISTRY_AT]
    #                             [--expiration EXPIRATION] [--force]
    #                             [--amount AMOUNT]
    #                             [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                             [--wallet-index WALLET_INDEX] [--yes]
    #                             [--quiet | --verbose]
    #                             [--group-name GROUP_NAME]
    #                             [--channel-id CHANNEL_ID]
    #                             [--from-block FROM_BLOCK]
    #                             ORG_ID group_name

    # Check for required parameters
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42, None
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42

    # Construct command
    command = f"snet --print-traceback channel extend-add-for-org {org_id} {group_name}"

    if registry and len(registry) > 0:
        command += f" --registry-at {registry}"
    if expr and len(expr) > 0:
        command += f" --expiration {expr}"
    if force:
        command += " --force"
    if agi_amount and len(agi_amount) > 0:
        try:
            if agi_amount and float(agi_amount) < 0:
                return "ERROR: Amount of AGI must be greater than or equal to 0", 42, None
        except ValueError:
            return "ERROR: Amount of AGI must be a valid number", 42, None
        command += f" --amount {agi_amount}"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if channel_id and len(channel_id) > 0:
        command += f" --channel-id {channel_id}"
    if from_block and len(from_block) > 0:
        command += f" --from-block {from_block}"
    
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"

    # Run command
    if view:
        output, errCode = run_shell_command(command=command, input_text="n\n")
    else:
        output, errCode = run_shell_command(command=f"{command} --yes") 

    return output, errCode, command

def channel_print_initialized(only_id=None, filter_sender=None, filter_signer=None, filter_my=None, mpe_addr=None, registry=None, wallet_index=None):
    # snet channel print-initialized [-h] [--only-id]
    #                            [--filter-sender | --filter-signer | --filter-my]
    #                            [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                            [--wallet-index WALLET_INDEX]
    #                            [--registry-at REGISTRY_AT]

    # Construct command
    command = "snet --print-traceback channel print-initialized"
    
    if only_id:
        command += " --only-id"
    if filter_sender:
        command += " --filter-sender"
    elif filter_signer:
        command += " --filter-signer"
    elif filter_my:
        command += " --filter-my"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if registry and len(registry) > 0:
        command += f" --registry-at {registry}"

    # Run command
    output, errCode = run_shell_command(command)
    return output, errCode

def channel_print_initialized_filter_org(org_id, group_name, registry, only_id, filter_sender, filter_signer, filter_my, mpe_addr, wallet_index):
    # snet channel print-initialized-filter-org [-h] [--registry-at REGISTRY_AT]
    #                                       [--only-id]
    #                                       [--filter-sender | --filter-signer | --filter-my]
    #                                       [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                                       [--wallet-index WALLET_INDEX]
    #                                       ORG_ID group_name

    # Check for required parameters
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42
    

    # Construct command
    command = f"snet --print-traceback channel print-initialized-filter-org {org_id} {group_name}"
    if registry and len(registry) > 0:
        command += f" --registry-at {registry}"
    if only_id:
        command += " --only-id"
    if filter_sender:
        command += " --filter-sender"
    elif filter_signer:
        command += " --filter-signer"
    elif filter_my:
        command += " --filter-my"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"

    # Run command
    output, errCode = run_shell_command(command)
    return output, errCode

def channel_print_all_filter_sender(only_id, mpe_addr, from_block, sender, wallet_index):
    # snet channel print-all-filter-sender [-h] [--only-id]
    #                                  [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                                  [--from-block FROM_BLOCK]
    #                                  [--wallet-index WALLET_INDEX]
    #                                  [--sender SENDER]

    # Construct command
    command = "snet --print-traceback channel print-all-filter-sender"

    if only_id:
        command += " --only-id"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if from_block and len(from_block) > 0:
        command += f" --from-block {from_block}"
    if sender and len(sender) > 0:
        command += f" --sender {sender}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"

    # Run command
    output, errCode = run_shell_command(command)
    return output, errCode

def channel_print_all_filter_recipient(only_id, mpe_addr, from_block, recipient, wallet_index):
    # snet channel print-all-filter-recipient [-h] [--only-id]
    #                                     [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                                     [--from-block FROM_BLOCK]
    #                                     [--wallet-index WALLET_INDEX]
    #                                     [--recipient RECIPIENT]

    # Construct command
    command = "snet --print-traceback channel print-all-filter-recipient"

    if only_id:
        command += " --only-id"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if from_block and len(from_block) > 0:
        command += f" --from-block {from_block}"
    if recipient and len(recipient) > 0:
        command += f" --recipient {recipient}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"

    # Run command
    output, errCode = run_shell_command(command)
    return output, errCode

def channel_print_all_filter_group(org_id, group_name, registry, only_id, mpe_addr, from_block, wallet_index):
    # snet channel print-all-filter-group [-h] [--registry-at REGISTRY_AT]
    #                                 [--only-id]
    #                                 [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                                 [--from-block FROM_BLOCK]
    #                                 [--wallet-index WALLET_INDEX]
    #                                 ORG_ID group_name

    # Check for required parameters
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42

    # Construct command
    command = f"snet --print-traceback channel print-all-filter-group {org_id} {group_name}"
    if registry and len(registry) > 0:
        command += f" --registry-at {registry}"
    if only_id:
        command += " --only-id"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if from_block and len(from_block) > 0:
        command += f" --from-block {from_block}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"

    # Run command
    output, errCode = run_shell_command(command)
    return output, errCode

def channel_print_all_filter_group_sender(org_id, group_name, registry, only_id, mpe_addr, from_block, sender, wallet_index):
    # snet channel print-all-filter-group-sender [-h] [--registry-at REGISTRY_AT]
    #                                        [--only-id]
    #                                        [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                                        [--from-block FROM_BLOCK]
    #                                        [--wallet-index WALLET_INDEX]
    #                                        [--sender SENDER]
    #                                        ORG_ID group_name

    # Check for required parameters
    if not org_id or len(org_id) == 0:
        return "ERROR: Organization ID is required", 42
    if not group_name or len(group_name) == 0:
        return "ERROR: Group name is required", 42

    # Construct command
    command = f"snet --print-traceback channel print-all-filter-group-sender {org_id} {group_name}"
    if registry and len(registry) > 0:
        command += f" --registry-at {registry}"
    if only_id:
        command += " --only-id"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if from_block and len(from_block) > 0:
        command += f" --from-block {from_block}"
    if sender and len(sender) > 0:
        command += f" --sender {sender}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"

    # Run command
    output, errCode = run_shell_command(command)
    return output, errCode

def channel_claim_timeout(channel_id, mpe_addr, wallet_index, quiet, verbose, view):
    # snet channel claim-timeout [-h] [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                        [--wallet-index WALLET_INDEX] [--yes]
    #                        [--quiet | --verbose]
    #                        CHANNEL_ID

    # Check for required parameters
    if not channel_id or len(channel_id) == 0:
        return "ERROR: Channel ID is required", 42, None

    # Construct command
    command = f"snet --print-traceback channel claim-timeout {channel_id}"
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"

    # Run command
    if view:
        output, errCode = run_shell_command(command=command, input_text="n\n")
    else:
        output, errCode = run_shell_command(command=f"{command} --yes") 

    return output, errCode, command

def channel_claim_timeout_all(mpe_addr, from_block, wallet_index, quiet, verbose, view):
    # snet channel claim-timeout-all [-h]
    #                            [--multipartyescrow-at MULTIPARTYESCROW_AT]
    #                            [--wallet-index WALLET_INDEX] [--yes]
    #                            [--quiet | --verbose] [--from-block FROM_BLOCK]

    # Construct command
    command = "snet --print-traceback channel claim-timeout-all"
    
    if mpe_addr and len(mpe_addr) > 0:
        command += f" --multipartyescrow-at {mpe_addr}"
    if from_block and len(from_block) > 0:
        command += f" --from-block {from_block}"
    if wallet_index and len(wallet_index) > 0:
        command += f" --wallet-index {wallet_index}"
    if quiet:
        command += " --quiet"
    elif verbose:
        command += " --verbose"

    # Run command
    if view:
        output, errCode = run_shell_command(command=command, input_text="n\n")
    else:
        output, errCode = run_shell_command(command=f"{command} --yes") 

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
            output, errCode = run_shell_command(cmd, input_text="n\n", workdir=cwd)
        else:
            output, errCode = run_shell_command(cmd, input_text="n\n")
    else:
        if cwd and len(cwd) > 0:
            output, errCode = run_shell_command(command=f"{command} --yes", workdir=cwd) 
        else:
            output, errCode = run_shell_command(command=f"{command} --yes")

    return output, errCode, cmd

def custom_conditional_check(root, sub):
    global condCommDict
    comm = root + " " + sub
    return comm in condCommDict


