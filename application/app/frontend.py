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
        output, errCode = be.print_organization_info()
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Organization Page", id="organization_page_title"),
                Label(f"My Organizations:\n{output}", id="org_metadata_info_label"),
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
            self.app.push_screen(org_metadata_page())
        elif event.button.id == "organization_page_groups_button":
            self.app.push_screen(org_groups_page())
        # elif event.button.id == "organization_page_members_button":
        #     self.app.push_screen()
        elif event.button.id == "organization_page_create_delete_button":
            self.app.push_screen(org_manage_page())

class org_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Organization Metadata Page", id="org_metadata_page_title"),
                Button(label="My Metadata", id="org_metadata_page_print_button"),
                Button(label="Initialize Metadata", id="org_metadata_page_init_button"),
                Button(label="Add Description", id="org_metadata_add_desc_button"),
                Button(label="Manage Assets", id="org_metadata_assets_button"),
                Button(label="Manage Contacts", id="org_metadata_contacts_button"),
                Button(label="Update Metadata", id="org_metadata_update_button"),
                Button(label="Back", id="org_metadata_back_button"),
                id="org_metadata_page_content"
            ),
            id="org_metadata_page"
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
        elif event.button.id == "org_metadata_back_button":
            self.app.switch_screen(organization_page())
        elif event.button.id == "org_metadata_page_print_button":
            self.app.push_screen(print_org_metadata_page())
        elif event.button.id == "org_metadata_page_init_button":
            self.app.push_screen(init_org_metadata_page())
        elif event.button.id == "org_metadata_add_desc_button":
            self.app.push_screen(add_org_metadata_desc_page())
        elif event.button.id == "org_metadata_assets_button":
            self.app.push_screen(manage_org_assets_page())
        elif event.button.id == "org_metadata_contacts_button":
            self.app.push_screen(manage_org_contacts_page())
        elif event.button.id == "org_metadata_update_button":
            self.app.push_screen(update_org_metadata_page())

# TODO Implement printing metadata page
class print_org_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        output, errCode = be.print_org_metadata()
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("My Metadata Page", id="print_org_metadata_page_title"),
                Label(f"\n\n{output}\n\n", id="print_org_metadata_metadata_content"),
                Button(label="Back", id="print_org_metadata_back_button"),
                id="print_org_metadata_page_content"
            ),
            id="print_org_metadata_page"
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
        elif event.button.id == "print_org_metadata_back_button":
            self.app.pop_screen()

# TODO Implement init metadata page
class init_org_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Initialize Metadata Page", id="init_org_metadata_page_title"),
                Input(placeholder="Input Organization name (The one you defined during the ETCD setup)", id="init_org_metadata_name_input"),
                Input(placeholder="Define your unique organization ID (You must reuse this in your Daemon configuration)", id="init_org_metadata_id_input"),
                Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from 'networks'", id="init_org_metadata_registry_input"),
                Select(options=((line, line) for line in """Individual\nOrganization""".splitlines()), prompt="Select Organization Type", id="init_org_metadata_type_select"),
                Button(label="Initialize", id="init_org_metadata_confirm_button"),
                Button(label="Back", id="init_org_metadata_back_button"),
                id="init_org_metadata_page_content"
            ),
            id="init_org_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        
        org_name = self.get_child_by_id("init_org_metadata_page").get_child_by_id("init_org_metadata_page_content").get_child_by_id("init_org_metadata_name_input").value
        org_id = self.get_child_by_id("init_org_metadata_page").get_child_by_id("init_org_metadata_page_content").get_child_by_id("init_org_metadata_id_input").value
        reg_addr = self.get_child_by_id("init_org_metadata_page").get_child_by_id("init_org_metadata_page_content").get_child_by_id("init_org_metadata_registry_input").value
        org_type = self.get_child_by_id("init_org_metadata_page").get_child_by_id("init_org_metadata_page_content").get_child_by_id("init_org_metadata_type_select").value

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "init_org_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "init_org_metadata_confirm_button":
            output, errCode = be.init_org_metadata(org_name, org_id, org_type, reg_addr)
            popup_output = output
            self.app.push_screen(popup_output_page())

# TODO Implement add desc page
class add_org_metadata_desc_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Add Metadata Description Page", id="add_org_metadata_desc_title"),
                Input(placeholder="Description about organization", id="add_org_metadata_desc_long_input"),
                Input(placeholder="Short description about organization", id="add_org_metadata_desc_short_input"),
                Input(placeholder="URL for Organization", id="add_org_metadata_desc_url_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file name (default service_metadata.json)", id="add_org_metadata_desc_path_input"),
                Button(label="Add Description", id="add_org_metadata_desc_confirm_button"),
                Button(label="Back", id="add_org_metadata_desc_back_button"),
                id="add_org_metadata_desc_page_content"
            ),
            id="add_org_metadata_desc_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        
        long_desc = self.get_child_by_id("add_org_metadata_desc_page").get_child_by_id("add_org_metadata_desc_page_content").get_child_by_id("add_org_metadata_desc_long_input").value
        short_desc = self.get_child_by_id("add_org_metadata_desc_page").get_child_by_id("add_org_metadata_desc_page_content").get_child_by_id("add_org_metadata_desc_short_input").value
        url = self.get_child_by_id("add_org_metadata_desc_page").get_child_by_id("add_org_metadata_desc_page_content").get_child_by_id("add_org_metadata_desc_url_input").value
        meta_path = self.get_child_by_id("add_org_metadata_desc_page").get_child_by_id("add_org_metadata_desc_page_content").get_child_by_id("add_org_metadata_desc_path_input").value

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "add_org_metadata_desc_back_button":
            self.app.pop_screen()
        elif event.button.id == "add_org_metadata_desc_confirm_button":
            output, errCode = be.add_org_metadata_desc(long_desc, short_desc, url, meta_path)
            popup_output = output
            self.app.push_screen(popup_output_page())

# TODO Implement manage assets page
class manage_org_assets_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Manage Assets Page", id="manage_org_assets_title"),
                Input(placeholder="Hero_image Asset File Path", id="manage_org_assets_path_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json) Default: 'organization_metadata.json'", id="manage_org_assets_meta_input"),
                Button(label="Add Asset", id="manage_org_assets_confirm_button"),
                Button(label="Remove ALL Assets (No confirmation dialog, optionally add metadata file name)", id="manage_org_assets_remove_button"),
                Button(label="Back", id="manage_org_assets_back_button"),
                id="manage_org_assets_page_content"
            ),
            id="manage_org_assets_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        asset_file_path = self.get_child_by_id("manage_org_assets_page").get_child_by_id("manage_org_assets_page_content").get_child_by_id("manage_org_assets_path_input").value
        metadata_file_name = self.get_child_by_id("manage_org_assets_page").get_child_by_id("manage_org_assets_page_content").get_child_by_id("manage_org_assets_meta_input").value

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "manage_org_assets_back_button":
            self.app.pop_screen()
        elif event.button.id == "manage_org_assets_confirm_button":
            output, errCode = be.add_org_metadata_assets(asset_file_path, metadata_file_name)
            popup_output = output
            self.app.push_screen(popup_output_page())
        elif event.button.id == "manage_org_assets_remove_button":
            output, errCode = be.remove_all_org_metadata_assets(metadata_file_name)
            popup_output = output
            self.app.push_screen(popup_output_page())


# TODO Implement manage contacts page
class manage_org_contacts_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Manage Contacts Page", id="manage_org_contacts_page_title"),
                Input(placeholder="Contact type of organization", id="manage_org_contacts_type_input"),
                Input(placeholder="[Technically OPTIONAL] Phone number for contact with country code", id="manage_org_contacts_phone_input"),
                Input(placeholder="[Technically OPTIONAL] Email ID for contact", id="manage_org_contacts_email_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json) Default: 'organization_metadata.json'", id="manage_org_contacts_meta_input"),
                Button(label="Add contact", id="manage_org_contacts_confirm_button"),
                Button(label="Remove all contacts", id="manage_org_contacts_remove_button"),
                Button(label="Back", id="manage_org_contacts_back_button"),
                id="manage_org_contacts_page_content"
            ),
            id="manage_org_contacts_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        contact_type = self.get_child_by_id("manage_org_contacts_page").get_child_by_id("manage_org_contacts_page_content").get_child_by_id("manage_org_contacts_type_input").value
        phone = self.get_child_by_id("manage_org_contacts_page").get_child_by_id("manage_org_contacts_page_content").get_child_by_id("manage_org_contacts_phone_input").value
        email = self.get_child_by_id("manage_org_contacts_page").get_child_by_id("manage_org_contacts_page_content").get_child_by_id("manage_org_contacts_email_input").value
        metadata_file = self.get_child_by_id("manage_org_contacts_page").get_child_by_id("manage_org_contacts_page_content").get_child_by_id("manage_org_contacts_meta_input").value

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page()) 
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav": 
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav": 
            self.app.push_screen(exit_page())
        elif event.button.id == "manage_org_contacts_back_button":
            self.app.pop_screen()
        elif event.button.id == "manage_org_contacts_confirm_button":
            output, errCode = be.add_org_metadata_contact(contact_type, phone, email, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())
        elif event.button.id == "manage_org_contacts_remove_button":
            output, errCode = be.remove_org_metadata_contacts(metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

# TODO update metadata org
class update_org_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Update Metadata Page", id="update_org_metadata_page_title"),
                Input(placeholder="Your Organization ID", id="update_org_metadata_id_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json) Default: 'organization_metadata.json'", id="update_org_metadata_file_input"),
                Input(placeholder="[OPTIONAL] List of members to be added to the organization", id="update_org_metadata_mems_input"),
                Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="update_org_metadata_gas_input"),
                Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="update_org_metadata_index_input"),
                RadioButton(label="Quiet transaction printing", id="update_org_metadata_quiet_radio"),
                RadioButton(label="Verbose transaction printing", id="update_org_metadata_verbose_radio"),
                Button(label="Update Metadata on Blockchain", id="update_org_metadata_confirm_button"),
                Button(label="Back", id="update_org_metadata_back_button"),
                id="update_org_metadata_page_content"
            ),
            id="update_org_metadata_page"
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
        elif event.button.id == "update_org_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "update_org_metadata_confirm_button":
            org_id = self.get_child_by_id("update_org_metadata_page").get_child_by_id("update_org_metadata_page_content").get_child_by_id("update_org_metadata_id_input").value
            file_name = self.get_child_by_id("update_org_metadata_page").get_child_by_id("update_org_metadata_page_content").get_child_by_id("update_org_metadata_file_input").value
            mem_list = self.get_child_by_id("update_org_metadata_page").get_child_by_id("update_org_metadata_page_content").get_child_by_id("update_org_metadata_mems_input").value
            gas = self.get_child_by_id("update_org_metadata_page").get_child_by_id("update_org_metadata_page_content").get_child_by_id("update_org_metadata_gas_input").value
            index = self.get_child_by_id("update_org_metadata_page").get_child_by_id("update_org_metadata_page_content").get_child_by_id("update_org_metadata_index_input").value
            quiet = self.get_child_by_id("update_org_metadata_page").get_child_by_id("update_org_metadata_page_content").get_child_by_id("update_org_metadata_quiet_radio").value
            verbose = self.get_child_by_id("update_org_metadata_page").get_child_by_id("update_org_metadata_page_content").get_child_by_id("update_org_metadata_verbose_radio").value

            output, errCode = be.update_org_metadata(org_id, file_name, mem_list, gas, index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class org_groups_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Organization Groups Page", id="org_groups_page_title"),
                Button(label="Add a Group", id="org_groups_add_button"),
                Button(label="Update Group", id="org_groups_update_button"),
                Button(label="Back", id="org_groups_back_button"),
                id="org_groups_page_content"
            ),
            id="org_groups_page"
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
        elif event.button.id == "org_groups_back_button":
            self.app.switch_screen(organization_page())
        elif event.button.id == "org_groups_add_button":
            self.app.switch_screen(add_org_group_page())
        elif event.button.id == "org_groups_update_button":
            self.app.switch_screen(update_org_group_page())

class add_org_group_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Add Organization Group Page", id="add_org_group_title"),
                Input(placeholder="Group Name", id="add_org_group_name_input"),
                Input(placeholder="Payment Address", id="add_org_group_pay_addr_input"),
                Input(placeholder="Endpoints (space seperated if multiple, DO NOT add brackets '[]')", id="add_org_group_endpoint_input"),
                Input(placeholder="[OPTIONAL] Payment Expiration threshold. Default: 100", id="add_org_group_pay_expr_threshold_input"),
                Input(placeholder="[OPTIONAL] Storage channel for payment. Default: 'etcd'", id="add_org_group_pay_chann_storage_input"),
                Input(placeholder="[OPTIONAL] Payment channel connection timeout. Default: '100s'", id="add_org_group_pay_chann_conn_to_input"),
                Input(placeholder="[OPTIONAL] Payment channel request timeout. Default: '5s'", id="add_org_group_pay_chann_req_to_input"),
                Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from 'networks'", id="add_org_group_registry_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json) Default: 'organization_metadata.json'", id="add_org_group_metadata_file_input"),
                Button(label="Add Group", id="add_org_group_confirm_button"),
                Button(label="Back", id="add_org_group_back_button"),
                id="add_org_group_content"
            ),
            id="add_org_group_page"
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
        elif event.button.id == "add_org_group_back_button":
            self.app.pop_screen()
        elif event.button.id == "add_org_group_confirm_button":
            group_name = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_name_input").value
            pay_addr = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_pay_addr_input").value
            endpoints = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_endpoint_input").value
            payment_expiration_threshold = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_pay_expr_threshold_input").value
            pay_chann_storage_type = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_pay_chann_storage_input").value
            pay_chann_conn_to = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_pay_chann_conn_to_input").value
            pay_chann_req_to = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_pay_chann_req_to_input").value
            reg_addr = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_registry_input").value
            metadata_file = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_metadata_file_input").value

            output, errCode = be.add_org_metadata_group(group_name, pay_addr, endpoints, payment_expiration_threshold, pay_chann_storage_type, pay_chann_conn_to, pay_chann_req_to, metadata_file, reg_addr)
            popup_output = output
            self.app.push_screen(popup_output_page())
        

class update_org_group_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Update Organization Group Page", id="update_org_group_title"),
                Input(placeholder="Group Name", id="update_org_group_name_input"),
                Input(placeholder="Payment Address", id="update_org_group_pay_addr_input"),
                Input(placeholder="Endpoints (space seperated if multiple, DO NOT add brackets '[]')", id="update_org_group_endpoint_input"),
                Input(placeholder="Payment Expiration threshold. Default: 100", id="update_org_group_pay_expr_threshold_input"),
                Input(placeholder="Storage channel for payment. Default: 'etcd'", id="update_org_group_pay_chann_storage_input"),
                Input(placeholder="Payment channel connection timeout. Default: '100s'", id="update_org_group_pay_chann_conn_to_input"),
                Input(placeholder="Payment channel request timeout. Default: '5s'", id="update_org_group_pay_chann_req_to_input"),
                Input(placeholder="Address of Registry contract, if not specified we read address from 'networks'", id="update_org_group_registry_input"),
                Input(placeholder="Service metadata json file (default service_metadata.json) Default: 'organization_metadata.json'", id="update_org_group_metadata_file_input"),
                Button(label="Update Group", id="update_org_group_confirm_button"),
                Button(label="Back", id="update_org_group_back_button"),
                id="update_org_group_content"
            ),
            id="update_org_group_page"
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
        elif event.button.id == "update_org_group_back_button":
            self.app.pop_screen()
        elif event.button.id == "update_org_group_confirm_button":
            group_name = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_name_input").value
            pay_addr = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_pay_addr_input").value
            endpoints = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_endpoint_input").value
            payment_expiration_threshold = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_pay_expr_threshold_input").value
            pay_chann_storage_type = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_pay_chann_storage_input").value
            pay_chann_conn_to = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_pay_chann_conn_to_input").value
            pay_chann_req_to = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_pay_chann_req_to_input").value
            reg_addr = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_registry_input").value
            metadata_file = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_metadata_file_input").value

            output, errCode = be.update_org_metadata_group(group_name, pay_addr, endpoints, payment_expiration_threshold, pay_chann_storage_type, pay_chann_conn_to, pay_chann_req_to, metadata_file, reg_addr)
            popup_output = output
            self.app.push_screen(popup_output_page())

class org_manage_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Organization Management Page", id="org_manage_page_title"),
                Button(label="Create Organization", id="org_manage_add_button"),
                Button(label="Delete Organization", id="org_manage_delete_button"),
                Button(label="Back", id="org_manage_back_button"),
                id="org_manage_page_content"
            ),
            id="org_manage_page"
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
        elif event.button.id == "org_manage_back_button":
            self.app.switch_screen(organization_page())
        elif event.button.id == "org_manage_add_button":
            self.app.switch_screen(org_manage_create_page())
        elif event.button.id == "org_manage_delete_button":
            self.app.switch_screen(org_manage_delete_page())

class org_manage_create_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Create Organization Page", id="org_manage_create_page_title"),
                Input(placeholder="Your Organization ID", id="org_manage_create_id_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json) Default: 'organization_metadata.json'", id="org_manage_create_file_input"),
                Input(placeholder="[OPTIONAL] List of members to be added to the organization", id="org_manage_create_mems_input"),
                Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="org_manage_create_gas_input"),
                Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="org_manage_create_index_input"),
                RadioButton(label="Quiet transaction printing", id="org_manage_create_quiet_radio"),
                RadioButton(label="Verbose transaction printing", id="org_manage_create_verbose_radio"),
                Button(label="Create Organization", id="org_manage_create_confirm_button"),
                Button(label="Back", id="org_manage_create_back_button"),
                id="org_manage_create_page_content"
            ),
            id="org_manage_create_page"
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
        elif event.button.id == "org_manage_create_back_button":
            self.app.pop_screen()
        elif event.button.id == "org_manage_create_confirm_button":
            org_id = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_id_input").value
            file_name = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_file_input").value
            mem_list = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_mems_input").value
            gas = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_gas_input").value
            index = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_index_input").value
            quiet = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_quiet_radio").value
            verbose = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_verbose_radio").value

            output, errCode = be.create_organization(org_id, file_name, mem_list, gas, index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class org_manage_delete_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Delete Organization Page", id="org_manage_delete_page_title"),
                Input(placeholder="Your Organization ID", id="org_manage_delete_id_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json) Default: 'organization_metadata.json'", id="org_manage_delete_file_input"),
                Input(placeholder="[OPTIONAL] List of members to be added to the organization", id="org_manage_delete_mems_input"),
                Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="org_manage_delete_gas_input"),
                Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="org_manage_delete_index_input"),
                RadioButton(label="Quiet transaction printing", id="org_manage_delete_quiet_radio"),
                RadioButton(label="Verbose transaction printing", id="org_manage_delete_verbose_radio"),
                Button(label="Create Organization", id="org_manage_delete_confirm_button"),
                Button(label="Back", id="org_manage_delete_back_button"),
                id="org_manage_delete_page_content"
            ),
            id="org_manage_delete_page"
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
        elif event.button.id == "org_manage_delete_back_button":
            self.app.pop_screen()
        elif event.button.id == "org_manage_delete_confirm_button":
            org_id = self.get_child_by_id("org_manage_delete_page").get_child_by_id("org_manage_delete_page_content").get_child_by_id("org_manage_delete_id_input").value
            file_name = self.get_child_by_id("org_manage_delete_page").get_child_by_id("org_manage_delete_page_content").get_child_by_id("org_manage_delete_file_input").value
            mem_list = self.get_child_by_id("org_manage_delete_page").get_child_by_id("org_manage_delete_page_content").get_child_by_id("org_manage_delete_mems_input").value
            gas = self.get_child_by_id("org_manage_delete_page").get_child_by_id("org_manage_delete_page_content").get_child_by_id("org_manage_delete_gas_input").value
            index = self.get_child_by_id("org_manage_delete_page").get_child_by_id("org_manage_delete_page_content").get_child_by_id("org_manage_delete_index_input").value
            quiet = self.get_child_by_id("org_manage_delete_page").get_child_by_id("org_manage_delete_page_content").get_child_by_id("org_manage_delete_quiet_radio").value
            verbose = self.get_child_by_id("org_manage_delete_page").get_child_by_id("org_manage_delete_page_content").get_child_by_id("org_manage_delete_verbose_radio").value

            output, errCode = be.delete_organization(org_id, file_name, mem_list, gas, index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

# TODO Implement entire service CLI command
class services_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Services Page", id="services_page_title"),
                Button(label="Metadata", id="services_metadata_button"),
                Button(label="Manage", id="services_page_manage_button"),
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
        elif event.button.id == "services_metadata_button":
            self.app.push_screen(services_metadata_page())
        elif event.button.id == "services_page_manage_button":
            self.app.push_screen(services_manage_page())

class services_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Service Metadata Page", id="manage_services_metadata_page_title"),
                Button(label="Initialize Service Metadata", id="services_metadata_init_button"),
                Button(label="Add Service Description", id="services_metadata_add_desc_button"),
                Button("Back", id="services_metadata_back_button"),
                id="manage_services_metadata_page_content"
            ),
            id="manage_services_metadata_page"
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
        elif event.button.id == "services_metadata_back_button":
            self.app.pop_screen()

class init_service_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Service Metadata Initialization Page", id="init_service_metadata_page_title"),
                Input(placeholder="Service directory (Path to Service)", id="init_service_metadata_service_path_input"),
                Input(placeholder="Directory which contains protobuf files", id="init_service_metadata_proto_dir_input"),
                Input(placeholder="Service display name", id="init_service_metadata_display_name_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json). Default: “service_metadata.json”", id="init_service_metadata_file_name_input"),
                Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from “networks”", id="init_service_metadata_mpe_addr_input"),
                Input(placeholder="Name of the first payment group", id="init_service_metadata_pay_group_name_input"),
                Input(placeholder="[OPTIONAL] Endpoints for the first group. Default: []", id="init_service_metadata_endpoints_input"),
                Input(placeholder="Set fixed price in AGI token for all methods", id="init_service_metadata_price_input"),
                Select(options=((line, line) for line in """proto\njson""".splitlines()), prompt="Select Encoding Type", id="init_service_metadata_enc_type_select"),
                Select(options=((line, line) for line in """grpc\njsonrpc\nprocess""".splitlines()), prompt="Select Service Type", id="init_service_metadata_serv_type_select"),
                Button(label="Initialize Service Metadata", id="init_service_metadata_confirm_button"),
                Button(label="Back", id="init_service_metadata_back_button"),
                id="init_service_metadata_page_content"
            ),
            id="init_service_metadata_page"
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
        elif event.button.id == "init_service_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "init_service_metadata_confirm_button":
            service_path = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_service_path_input").value
            proto_path = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_proto_dir_input").value
            service_display = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_display_name_input").value
            metadata_file = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_file_name_input").value
            mpe_addr = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_mpe_addr_input").value
            pay_group_name = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_pay_group_name_input").value
            endpoints = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_endpoints_input").value
            fixed_price = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_price_input").value
            enc_type = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_enc_type_select").value
            serv_type = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_serv_type_select").value
            if enc_type == Select.BLANK:
                enc_type = "proto"
            if serv_type == Select.BLANK:
                serv_type = "grpc"
            
            output, errCode = be.init_service_metadata(service_path, proto_path, service_display, metadata_file, mpe_addr, pay_group_name, endpoints, fixed_price, enc_type, serv_type)
            popup_output = output
            self.app.push_screen(popup_output_page())
                    
class add_desc_service_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Add Description Page", id="add_desc_service_metadata_page_title"),
                Input(placeholder="Description of the service and what it does", id="add_desc_service_metadata_long_input"),
                Input(placeholder="Short overview of the service", id="add_desc_service_metadata_short_input"),
                Input(placeholder="URL to provide more details of the service", id="add_desc_service_metadata_url_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json)", id="add_desc_service_metadata_meta_file_input"),
                Button(label="Add Service Description", id="add_desc_service_metadata_confirm_button"),
                Button(label="Back", id="add_desc_service_metadata_back_button"),
                id="add_desc_service_metadata_page_content"
            ),
            id="add_desc_service_metadata_page"
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
        elif event.button.id == "add_desc_service_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "add_desc_service_metadata_confirm_button":
            long_desc = self.get_child_by_id("add_desc_service_metadata_page").get_child_by_id("add_desc_service_metadata_page_content").get_child_by_id("add_desc_service_metadata_long_input").value
            short_desc = self.get_child_by_id("add_desc_service_metadata_page").get_child_by_id("add_desc_service_metadata_page_content").get_child_by_id("add_desc_service_metadata_short_input").value
            url = self.get_child_by_id("add_desc_service_metadata_page").get_child_by_id("add_desc_service_metadata_page_content").get_child_by_id("add_desc_service_metadata_url_input").value
            metadata_file = self.get_child_by_id("add_desc_service_metadata_page").get_child_by_id("add_desc_service_metadata_page_content").get_child_by_id("add_desc_service_metadata_meta_file_input").value
            
            output, errCode = be.add_service_metadata_desc(long_desc, short_desc, url, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class services_manage_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Manage Services Page", id="services_manage_page_title"),
                id="services_manage_page_content"
            ),
            id="services_manage_page"
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