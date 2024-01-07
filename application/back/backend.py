import subprocess
# from web3 import Web3
# from eth_account import Account

class Wallet():
    def __init__(self) -> None:
        pass

# class Wallet:

#     def __init__(self):
#         self.w3 = Web3()

#     def create(self):
#         account = Account.create()
#         seed = account.seed_phrase()
#         private_key = account.privateKey.hex()
#         address = account.address
#         return private_key, address, seed

#     def import_from_seed(self, seed_phrase):
#         account = Account.from_mnemonic(seed_phrase)
#         private_key = account.privateKey.hex()
#         address = account.address
#         return private_key, address    

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
    

class Service():
    def __init__(self) -> None:
        pass

def run_shell_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr
    
# def check_daemon() -> bool:
#     # Check whether the daemon is installed
#     # Check whether the config has been edited
#     # Check whether the daemon can be run
#     return True

def check_cli() -> bool:
    return True

def check_wallet() -> bool:
    return True