from web3 import Web3
from eth_account import Account
import subprocess


class Wallet:

    def __init__(self):
        self.w3 = Web3()

    def create(self):
        account = Account.create()
        seed = account.seed_phrase()
        private_key = account.privateKey.hex()
        address = account.address
        return private_key, address, seed

    def import_from_seed(self, seed_phrase):
        account = Account.from_mnemonic(seed_phrase)
        private_key = account.privateKey.hex()
        address = account.address
        return private_key, address


class SingularityNetOrganization:

    def __init__(self, identity_name, private_key, network='goerli'):
        self.identity_name = identity_name
        self.private_key = private_key
        self.network = network

    def create_identity(self):
        return f"snet identity create {self.identity_name} key --private-key {self.private_key} --network {self.network}"

    def init_metadata(self, org_name, org_id, org_type):
        return f"snet organization metadata-init {org_name} {org_id} {org_type}"

    def add_description(self, description, short_description, url):
        return f"snet organization metadata-add-description --description \"{description}\" --short-description \"{short_description}\" --url \"{url}\""

    def add_group(self, group_name, wallet_address, etcd_endpoint):
        return f"snet organization add-group {group_name} {wallet_address} {etcd_endpoint}"

    def add_assets(self, asset_file_path, asset_type):
        return f"snet organization metadata-add-assets {asset_file_path} {asset_type}"

    def add_contact(self, contact_type, phone=None, email=None):
        contact_command = f"snet organization metadata-add-contact --phone {phone} --email {email} {contact_type}"
        return contact_command

    def create_organization(self, organization_name, member_addresses):
        return f"snet organization create {organization_name} {member_addresses}"


def run_shell_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr