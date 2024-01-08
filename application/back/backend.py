import subprocess
# from web3 import Web3
# from eth_account import Account

class Organization():
    def __init__(self, org_identity, wallet_priv_key, network) -> None:
        self.identity_name = org_identity
        self.private_key = wallet_priv_key
        self.network = network
    
    def create_identity(self):
        return run_shell_command(f"snet identity create {self.identity_name} key --private-key {self.private_key} --network {self.network}")
    
    def init_metadata(self, org_name, org_id, org_type):
        return run_shell_command(f"snet organization metadata-init {org_name} {org_id} {org_type}")
    
    def add_description(self, description, short_description, url):
        return run_shell_command(f"snet organization metadata-add-description --description \"{description}\" --short-description \"{short_description}\" --url \"{url}\"")
    
    def add_group(self, group_name, wallet_address, etcd_endpoint):
        return run_shell_command(f"snet organization add-group {group_name} {wallet_address} {etcd_endpoint}")
    
    def add_assets(self, asset_file_path, asset_type):
        return run_shell_command(f"snet organization metadata-add-assets {asset_file_path} {asset_type}")
    
    def add_contact(self, contact_type, phone=None, email=None):
        contact_command = f"snet organization metadata-add-contact --phone {phone} --email {email} {contact_type}"
        return run_shell_command(contact_command)
    
    def create_organization(self, organization_name, member_addresses):
        return run_shell_command(f"snet organization create {organization_name} {member_addresses}")

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
        
        if process.returncode == 0:
            return output, process.returncode
        else:
            return error, process.returncode
    except Exception as e:
        return str(e)

def check_cli() -> bool:
    stdout, stderr = run_shell_command('snet')
    if "error: the following arguments are required: COMMAND" == stderr[0:53]:
        return True
    return False

def check_identity() -> bool:
    stdout, stderr = run_shell_command('snet account balance')
    # NOTE: Need to check for correct output, not incorrect. getting false positives
    if "Please create your first identity by running 'snet identity create'" == stdout[1:59]:
        return False
    return True