from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Header, Label, Input, Select, RadioButton, LoadingIndicator
import back.backend as be
import re

# Global variables for passing parameters between screens, as textual does not support this
error_exit_label: str
popup_output: str

# TODO Ensure all "command" screens are actually popups, and add back buttons.

class WelcomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Welcome to the SingularityNET text interface", id="welcome_label"),
            Button("Start", id="start_button"),
            id = "welcome_screen"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global error_exit_label
        if event.button.id == "start_button":
            cli_installed, output, errCode1 = be.check_cli()
            identity_added, output2, errCode2 = be.check_account_balance()
            if (cli_installed and identity_added):
                self.app.switch_screen(account_page())
            elif (not cli_installed):
                error_exit_label  = f"CLI not found, please double check installation and ensure you are running the TUI through the environment the CLI was installed in.\n\nCommand error output: {output}"
                self.app.switch_screen(error_exit_page())
            elif (not identity_added):
                self.app.push_screen(create_identity_page())

class error_exit_page(Screen):
    def compose(self) -> ComposeResult:
        global error_exit_label
        yield Grid(
            Label(f"{error_exit_label}", id="error_exit_label"),
            Button("Exit", id="error_exit_button"),
            id = "error_exit_screen"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "error_exit_button":
            self.app.exit()

class popup_output_page(Screen):
    def compose(self) -> ComposeResult:
        global popup_output
        yield Grid(
            Label(f"{popup_output}", id="popup_output_label"),
            Button("OK", id="output_exit_button"),
            id = "popup_output_screen"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "output_exit_button":
            self.app.pop_screen()

class create_identity_page(Screen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Input(placeholder="Identity Name", id="org_identity_input"),
            Input(placeholder="Wallet Private Key / Seed phrase (Mnemonic)", id="wallet_info_input"),
            Select(options=(("Goerli", "Goerli") for line in """Goerli""".splitlines()), prompt="Select Network", id="network_select"),
            RadioButton("Mnemonic Wallet", id="mnemonic_wallet_radio"),
            Button("Create Identity", id="create_identity_button"),
            Button("Back", id="create_identity_back_button"),
            id="create_identity"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        if event.button.id == "create_identity_button":
            id_name = self.get_child_by_id("create_identity").get_child_by_id("org_identity_input").value
            network = self.get_child_by_id("create_identity").get_child_by_id("network_select").value
            wallet_info = self.get_child_by_id("create_identity").get_child_by_id("wallet_info_input").value
            mnemonic = self.get_child_by_id("create_identity").get_child_by_type(RadioButton).value
            if not isinstance(id_name, str) or len(id_name) == 0:
                popup_output = "ERROR: Organization Identity cannot be blank."
                self.app.push_screen(popup_output_page())
            elif not isinstance(wallet_info, str):
                popup_output = "ERROR: Wallet private key / seed phrase must be entered"
                self.app.push_screen(popup_output_page())
            else:
                if network == Select.BLANK:
                    network = "goerli"
                else:
                    network = network.lower()
                self.create_identity(id_name, mnemonic, wallet_info, network)
        elif event.button.id == "create_identity_back_button":
            self.app.pop_screen()
                
    
    def create_identity(self, id_name, mnemonic, wallet_info = None, network_select = "goerli"):
        global popup_output
        global error_exit_label
        global cur_org
        
        output, errCode = be.create_identity_cli(id_name, wallet_info, network_select, mnemonic)
        if errCode == 0:
            popup_output = output
            if len(popup_output) == 0:
                popup_output = f"Identity '{id_name} created!'"
            self.app.switch_screen(identity_page())
            self.app.push_screen(popup_output_page())
        else:
            error_exit_label = output
            self.app.switch_screen(error_exit_page())

class account_page(Screen):
    def compose(self) -> ComposeResult:
        wallet_dict = be.wallet_dict_create()
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label(f"Account: {wallet_dict['account']}", id="account_page_account"),
                Label(f"ETH: {wallet_dict['ETH']}", id="account_page_eth"),
                Label(f"AGIX: {wallet_dict['AGI']}", id="account_page_agi"),
                Label(f"MPE: {wallet_dict['MPE']}", id="account_page_mpe"),
                Button("Deposit", id="account_page_deposit_button"),
                Button("Withdraw", id="account_page_withdraw_button"),
                Button("Transfer", id="account_page_transfer_button"),
                Button("Identity Settings", id="account_page_identity_settings_button"),
                id="account_page_content"
            ),
            id="account_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "account_page_identity_settings_button":
            self.app.switch_screen(identity_page())
        elif event.button.id == "account_page_deposit_button":
            self.app.switch_screen(account_deposit_page())
        elif event.button.id == "account_page_withdraw_button":
            self.app.switch_screen(account_withdraw_page())
        elif event.button.id == "account_page_transfer_button":
            self.app.switch_screen(account_transfer_page())

class identity_page(Screen):
    def compose(self) -> ComposeResult:
        idList, listErrCode = be.run_shell_command("snet identity list")
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label(f"Identity List:\n\n{idList}", id="identity_page_title"),
                Button("Create Identity Page", id="identity_page_create_identity_button"),
                Input(placeholder="Identity name to delete", id="identity_page_delete_input"),
                Button("Delete Identity", id="identity_page_delete_identity_button"),
                id="identity_page_content"
            ),
            id="identity_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "identity_page_create_identity_button":
            self.app.push_screen(create_identity_page())
        elif event.button.id == "identity_page_delete_identity_button":
            id_name = self.get_child_by_id("identity_page").get_child_by_id("identity_page_content").get_child_by_id("identity_page_delete_input").value
            if not isinstance(id_name, str) or len(id_name) == 0:
                popup_output = "ERROR: Please enter the name of the Identity to be deleted"
                self.app.push_screen(popup_output_page())
            else:
                output, errcode = be.delete_identity_cli(id_name)
                if len(output) == 0 and errcode == 0:
                    output = f"Identity '{id_name}' deleted!"
                popup_output = output
                self.app.switch_screen(identity_page())
                self.app.push_screen(popup_output_page())

class account_deposit_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Input(placeholder="Amount of AGI tokens to deposit in MPE wallet", id="account_deposit_amount_input"),
                Input(placeholder="[OPTIONAL] Address of SingularityNetToken contract, if not specified we read address from 'networks'", id="account_deposit_contract_input"),
                Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from 'networks'", id="account_deposit_mpe_input"),
                Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="account_deposit_gas_input"),
                Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="account_deposit_index_input"),
                RadioButton(label="Quiet transaction printing", id="account_deposit_quiet_radio"),
                RadioButton(label="Verbose transaction printing", id="account_deposit_verbose_radio"),
                Button(label="Deposit", id="account_deposit_confirm_button"),
                id="account_deposit_page_content"
            ),
            id="account_deposit_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        agi_amount = self.get_child_by_id("account_deposit_page").get_child_by_id("account_deposit_page_content").get_child_by_id("account_deposit_amount_input").value
        contract_address = self.get_child_by_id("account_deposit_page").get_child_by_id("account_deposit_page_content").get_child_by_id("account_deposit_contract_input").value
        mpe_address = self.get_child_by_id("account_deposit_page").get_child_by_id("account_deposit_page_content").get_child_by_id("account_deposit_mpe_input").value
        gas_price = self.get_child_by_id("account_deposit_page").get_child_by_id("account_deposit_page_content").get_child_by_id("account_deposit_gas_input").value
        wallet_index = self.get_child_by_id("account_deposit_page").get_child_by_id("account_deposit_page_content").get_child_by_id("account_deposit_index_input").value
        quiet = self.get_child_by_id("account_deposit_page").get_child_by_id("account_deposit_page_content").get_child_by_id("account_deposit_quiet_radio").value
        verbose = self.get_child_by_id("account_deposit_page").get_child_by_id("account_deposit_page_content").get_child_by_id("account_deposit_verbose_radio").value

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "account_deposit_confirm_button":
            output, errCode = be.account_deposit(agi_amount, contract_address, mpe_address, gas_price, wallet_index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class account_withdraw_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Input(placeholder="Amount of AGI tokens to deposit in MPE wallet", id="account_withdraw_amount_input"),
                Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from 'networks'", id="account_withdraw_mpe_input"),
                Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="account_withdraw_gas_input"),
                Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="account_withdraw_index_input"),
                RadioButton(label="Quiet transaction printing", id="account_withdraw_quiet_radio"),
                RadioButton(label="Verbose transaction printing", id="account_withdraw_verbose_radio"),
                Button(label="Withdraw", id="account_withdraw_confirm_button"),
                id="account_withdraw_page_content"
            ),
            id="account_withdraw_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        agi_amount = self.get_child_by_id("account_withdraw_page").get_child_by_id("account_withdraw_page_content").get_child_by_id("account_withdraw_amount_input").value
        mpe_address = self.get_child_by_id("account_withdraw_page").get_child_by_id("account_withdraw_page_content").get_child_by_id("account_withdraw_mpe_input").value
        gas_price = self.get_child_by_id("account_withdraw_page").get_child_by_id("account_withdraw_page_content").get_child_by_id("account_withdraw_gas_input").value
        wallet_index = self.get_child_by_id("account_withdraw_page").get_child_by_id("account_withdraw_page_content").get_child_by_id("account_withdraw_index_input").value
        quiet = self.get_child_by_id("account_withdraw_page").get_child_by_id("account_withdraw_page_content").get_child_by_id("account_withdraw_quiet_radio").value
        verbose = self.get_child_by_id("account_withdraw_page").get_child_by_id("account_withdraw_page_content").get_child_by_id("account_withdraw_verbose_radio").value

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "account_withdraw_confirm_button":
            output, errCode = be.account_withdraw(agi_amount, mpe_address, gas_price, wallet_index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class account_transfer_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Input(placeholder="Address of the receiver", id="account_transfer_addr_input"),
                Input(placeholder="Amount of AGI tokens to be transferred to another account inside MPE wallet", id="account_transfer_amount_input"),
                Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from 'networks'", id="account_transfer_mpe_input"),
                Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="account_transfer_gas_input"),
                Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="account_transfer_index_input"),
                RadioButton(label="Quiet transaction printing", id="account_transfer_quiet_radio"),
                RadioButton(label="Verbose transaction printing", id="account_transfer_verbose_radio"),
                Button(label="Transfer", id="account_transfer_confirm_button"),
                id="account_transfer_page_content"
            ),
            id="account_transfer_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        agi_amount = self.get_child_by_id("account_transfer_page").get_child_by_id("account_transfer_page_content").get_child_by_id("account_transfer_amount_input").value
        reciever_addr = self.get_child_by_id("account_transfer_page").get_child_by_id("account_transfer_page_content").get_child_by_id("account_transfer_addr_input").value
        mpe_address = self.get_child_by_id("account_transfer_page").get_child_by_id("account_transfer_page_content").get_child_by_id("account_transfer_mpe_input").value
        gas_price = self.get_child_by_id("account_transfer_page").get_child_by_id("account_transfer_page_content").get_child_by_id("account_transfer_gas_input").value
        wallet_index = self.get_child_by_id("account_transfer_page").get_child_by_id("account_transfer_page_content").get_child_by_id("account_transfer_index_input").value
        quiet = self.get_child_by_id("account_transfer_page").get_child_by_id("account_transfer_page_content").get_child_by_id("account_transfer_quiet_radio").value
        verbose = self.get_child_by_id("account_transfer_page").get_child_by_id("account_transfer_page_content").get_child_by_id("account_transfer_verbose_radio").value

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "account_transfer_confirm_button":
            output, errCode = be.account_transfer(reciever_addr, agi_amount, mpe_address, gas_price, wallet_index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())


# TODO Implement entire organization CLI command
class organization_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Organization Page", id="organization_page_title"),
                Button(label="Metadata", id="organization_page_metadata_button"),
                Button(label="Groups", id="organization_page_groups_button"),
                Button(label="Members", id="organization_page_members_button"),
                Button(label="Manage", id="organization_page_create_delete_button"),
                id="organization_page_content"
            ),
            id="organization_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "organization_page_metadata_button":
            self.app.push_screen(metadata_page())
        # elif event.button.id == "organization_page_groups_button":
        #     self.app.push_screen()
        # elif event.button.id == "organization_page_members_button":
        #     self.app.push_screen()
        # elif event.button.id == "organization_page_create_delete_button":
        #     self.app.push_screen()

class metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Metadata Page", id="metadata_page_title"),
                Button(label="My Metadata", id="metadata_page_print_button"),
                Button(label="Initialize Metadata", id="metadata_page_init_button"),
                Button(label="Add Description", id="metadata_add_desc_button"),
                Button(label="Manage Assets", id="metadata_assets_button"),
                Button(label="Manage Contacts", id="metadata_contacts_button"),
                Button(label="Update Metadata", id="metadata_update_button"),
                Button(label="Back", id="metadata_back_button"),
                id="metadata_page_content"
            ),
            id="metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "metadata_page_print_button":
            self.app.push_screen(print_metadata_page())
        elif event.button.id == "metadata_page_init_button":
            self.app.push_screen(init_metadata_page())

# TODO Implement printing metadata page
class print_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        output, errCode = be.print_org_metadata()
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("My Metadata Page", id="print_metadata_page_title"),
                Label(f"\n\n{output}\n\n", id="print_metadata_metadata_content"),
                Button(label="Back", id="print_metadata_back_button"),
                id="print_metadata_page_content"
            ),
            id="print_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "print_metadata_back_button":
            self.app.pop_screen()

# TODO Implement init metadata page
class init_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Initialize Metadata Page", id="init_metadata_page_title"),
                Input(placeholder="Input Organization name (The one you defined during the ETCD setup)", id="init_metadata_org_name_input"),
                Input(placeholder="Define your unique organization ID (You must reuse this in your Daemon configuration)", id="init_metadata_org_id_input"),
                Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from 'networks'", id="init_metadata_registry_input"),
                Select(options=((line, line) for line in """Individual\nOrganization""".splitlines()), prompt="Select Organization Type", id="org_type_select"),
                Button(label="Initialize", id="init_metadata_confirm_button"),
                Button(label="Back", id="init_metadata_back_button"),
                id="init_metadata_page_content"
            ),
            id="init_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        
        org_name = self.get_child_by_id("init_metadata_page").get_child_by_id("init_metadata_page_content").get_child_by_id("init_metadata_org_name_input").value
        org_id = self.get_child_by_id("init_metadata_page").get_child_by_id("init_metadata_page_content").get_child_by_id("init_metadata_org_id_input").value
        reg_addr = self.get_child_by_id("init_metadata_page").get_child_by_id("init_metadata_page_content").get_child_by_id("init_metadata_registry_input").value
        org_type = self.get_child_by_id("init_metadata_page").get_child_by_id("init_metadata_page_content").get_child_by_id("org_type_select").value

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "init_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "init_metadata_confirm_button":
            output, errCode = be.init_org_metadata(org_name, org_id, org_type, reg_addr)
            popup_output = output
            self.app.push_screen(popup_output_page())

# TODO Implement add desc page
class add_desc_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Add Metadata Description Page", id="add_desc_page_title"),
                Input(placeholder="Description about organization", id="add_desc_long_input"),
                Input(placeholder="Short description about organization", id="add_desc_short_input"),
                Input(placeholder="URL for Organization", id="add_desc_url_input"),
                Input("[OPTIONAL] Service metadata json file path (default $HOME/service_metadata.json)", id="add_desc_metadata_input"),
                Button(label="Add Description", id="add_desc_confirm_button"),
                Button(label="Back", id="add_desc_back_button"),
                id="add_desc_page_content"
            ),
            id="add_desc_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        
        long_desc = self.get_child_by_id("init_metadata_page").get_child_by_id("init_metadata_page_content").get_child_by_id("add_desc_long_input").value
        short_desc = self.get_child_by_id("init_metadata_page").get_child_by_id("init_metadata_page_content").get_child_by_id("add_desc_short_input").value
        url = self.get_child_by_id("init_metadata_page").get_child_by_id("init_metadata_page_content").get_child_by_id("add_desc_url_input").value
        meta_path = self.get_child_by_id("init_metadata_page").get_child_by_id("init_metadata_page_content").get_child_by_id("add_desc_metadata_input").value

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "init_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "init_metadata_confirm_button":
            output, errCode = be.add_org_metadata_desc(long_desc, short_desc, url, meta_path)
            popup_output = output
            self.app.push_screen(popup_output_page())

# TODO Implement manage assets page
class manage_assets_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Manage Assets Page", id="manage_assets_page_title"),
                id="manage_assets_page_content"
            ),
            id="manage_assets_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())

# TODO Implement manage contacts page
class manage_contacts_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Manage Contacts Page", id="manage_contacts_page_title"),
                id="manage_contacts_page_content"
            ),
            id="manage_contacts_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page()) 
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav": 
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav": 
            self.app.push_screen(exit_page())


# TODO Implement entire service CLI command
class services_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Services Page", id="services_page_title"),
                id="services_page_content"
            ),
            id="services_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())

# TODO Implement all other commands under "misc" nav page

class exit_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Grid(
            Label("Are you sure you want to exit?", id="exit_question"),
            Button("Exit", id="exit_button"),
            Button("Cancel", id="cancel_exit_button"),
            id="exit_page",
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit_button":
            self.app.exit()
        else:
            self.app.pop_screen()

class Singularity_Net_TUI(App):

    CSS_PATH = "style.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        self.push_screen(WelcomeScreen())