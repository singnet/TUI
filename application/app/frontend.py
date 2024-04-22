from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Header, Label, Input, Select, RadioButton, LoadingIndicator, Log
import back.backend as be
import re

# Stable build v0.1

# Global variables for passing parameters between screens, as textual does not support this
error_exit_label: str
popup_output: str

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
        yield Log(id="error_exit_log").write(error_exit_label)
        yield Button("Exit", id="error_exit_button")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "error_exit_button":
            self.app.exit()

class popup_output_page(Screen):
    def compose(self) -> ComposeResult:
        global popup_output
        yield Log(id="popup_output_log").write(popup_output)
        yield Button("OK", id="output_exit_button")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "output_exit_button":
            self.app.pop_screen()

class create_identity_page(Screen):
    def compose(self) -> ComposeResult:
        global error_exit_label
        network_list, errCode = be.network_list()
        if errCode == 0:
            yield Grid(
                Input(placeholder="Identity Name", id="org_identity_input"),
                Input(placeholder="Wallet Private Key / Seed phrase (Mnemonic)", id="wallet_info_input", password=True),
                Select(options=((line, line) for line in network_list), prompt="Select Network", id="network_select"),
                RadioButton("Mnemonic Wallet", id="mnemonic_wallet_radio"),
                Button("Create Identity", id="create_identity_button"),
                Button("Back", id="create_identity_back_button"),
                id="create_identity"
            )
        else:
            error_exit_label = "ERROR: Could not find network list, please check CLI installation and run the command 'snet network list'"
            self.app.switch_screen(error_exit_page())

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
            self.app.switch_screen(account_page())
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
                Label(f"AGIX: {wallet_dict['AGIX']}", id="account_page_agi"),
                Label(f"MPE: {wallet_dict['MPE']}", id="account_page_mpe"),
                Button("Deposit", id="account_page_deposit_button"),
                Button("Withdraw", id="account_page_withdraw_button"),
                Button("Transfer", id="account_page_transfer_button"),
                Button("Identity Settings", id="account_page_identity_settings_button"),
                Button("Treasurer", id="account_treasurer_button"),
                id="account_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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
        elif event.button.id == "account_treasurer_button":
            self.app.switch_screen(treasurer_page())


class treasurer_page(Screen):
    def compose(self) -> ComposeResult:
        global popup_output
        unclaimed_payments, errCode = be.print_unclaimed_payments()
        if errCode != 0:
            popup_output = unclaimed_payments
            self.app.switch_screen(account_page())
            self.app.push_screen(popup_output_page())
        else:
            yield Header()
            yield Horizontal(
                be.nav_sidebar_vert(),
                Grid(
                    Label("Treasurer Page", id="treasurer_page_title"),
                    Label(f"Unclaimed payments:\n\n{unclaimed_payments}", id="treasurer_unclaimed_label"),
                    Button("Claim", id="treasurer_claim_button"),
                    Button("Claim Expired", id="treasurer_claim_exp_button"),
                    Button("Claim All", id="treasurer_claim_all_button"),
                    Button("Back", id="treasurer_back_button"),
                    id="treasurer_page_content",
                    classes="content_page"
                ),
                id="treasurer_page"
            )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "treasurer_back_button":
            self.app.push_screen(exit_page())
        elif event.button.id == "treasurer_claim_button":
            self.app.push_screen(exit_page())
        elif event.button.id == "treasurer_claim_exp_button":
            self.app.push_screen(exit_page())
        elif event.button.id == "treasurer_claim_all_button":
            self.app.push_screen(exit_page())

class treasurer_claim_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Payment Claim Page", id="treasurer_claim_page_title"),
                Input(placeholder="Channels to claim", id="treasurer_claim_channels_input"),
                Input(placeholder="Daemon Endpoint", id="treasurer_claim_endpoint_input"),
                Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="treasurer_claim_gas_input"),
                Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="treasurer_claim_index_input"),
                RadioButton(label="Quiet transaction printing", id="treasurer_claim_quiet_radio"),
                RadioButton(label="Verbose transaction printing", id="treasurer_claim_verbose_radio"),
                Button("Claim", id="treasurer_claim_confirm_button"),
                Button("Back", id="treasurer_claim_back_button"),
                id="treasurer_claim_page_content",
                classes="content_page"
            ),
            id="treasurer_claim_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "treasurer_claim_back_button":
            self.app.switch_screen(treasurer_page())
        elif event.button.id == "treasurer_claim_confirm_button":
            channels = self.get_child_by_id("treasurer_claim_page").get_child_by_id("treasurer_claim_page_content").get_child_by_id("treasurer_claim_channels_input").value
            endpoint = self.get_child_by_id("treasurer_claim_page").get_child_by_id("treasurer_claim_page_content").get_child_by_id("treasurer_claim_endpoint_input").value
            gas_price = self.get_child_by_id("treasurer_claim_page").get_child_by_id("treasurer_claim_page_content").get_child_by_id("treasurer_claim_gas_input").value
            wallet_index = self.get_child_by_id("treasurer_claim_page").get_child_by_id("treasurer_claim_page_content").get_child_by_id("treasurer_claim_index_input").value
            quiet = self.get_child_by_id("treasurer_claim_page").get_child_by_id("treasurer_claim_page_content").get_child_by_id("treasurer_claim_quiet_radio").value
            verbose = self.get_child_by_id("treasurer_claim_page").get_child_by_id("treasurer_claim_page_content").get_child_by_id("treasurer_claim_verbose_radio").value

            output, errCode = be.treasurer_claim(channels, endpoint, gas_price, wallet_index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())   

class treasurer_claim_all_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Claim All Payments Page", id="treasurer_claim_all_page_title"),
                Input(placeholder="Daemon Endpoint", id="treasurer_claim_all_endpoint_input"),
                Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="treasurer_claim_all_gas_input"),
                Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="treasurer_claim_all_index_input"),
                RadioButton(label="Quiet transaction printing", id="treasurer_claim_all_quiet_radio"),
                RadioButton(label="Verbose transaction printing", id="treasurer_claim_all_verbose_radio"),
                Button("Claim", id="treasurer_claim_all_confirm_button"),
                Button("Back", id="treasurer_claim_all_back_button"),
                id="treasurer_claim_all_page_content",
                classes="content_page"
            ),
            id="treasurer_claim_all_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "treasurer_claim_all_back_button":
            self.app.switch_screen(treasurer_page())
        elif event.button.id == "treasurer_claim_all_confirm_button":
            endpoint = self.get_child_by_id("treasurer_claim_all_page").get_child_by_id("treasurer_claim_all_page_content").get_child_by_id("treasurer_claim_all_endpoint_input").value
            gas_price = self.get_child_by_id("treasurer_claim_all_page").get_child_by_id("treasurer_claim_all_page_content").get_child_by_id("treasurer_claim_all_gas_input").value
            wallet_index = self.get_child_by_id("treasurer_claim_all_page").get_child_by_id("treasurer_claim_all_page_content").get_child_by_id("treasurer_claim_all_index_input").value
            quiet = self.get_child_by_id("treasurer_claim_all_page").get_child_by_id("treasurer_claim_all_page_content").get_child_by_id("treasurer_claim_all_quiet_radio").value
            verbose = self.get_child_by_id("treasurer_claim_all_page").get_child_by_id("treasurer_claim_all_page_content").get_child_by_id("treasurer_claim_all_verbose_radio").value

            output, errCode = be.treasurer_claim_all(endpoint, gas_price, wallet_index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class treasurer_claim_expr_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Claim expired payments Page", id="treasurer_claim_expr_page_title"),
                Input(placeholder="[OPTIONAL] Service expiration threshold in blocks (default is 34560 ~ 6 days with 15s/block)", id="treasurer_claim_expr_threshold_input"),
                Input(placeholder="Daemon Endpoint", id="treasurer_claim_expr_endpoint_input"),
                Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="treasurer_claim_expr_gas_input"),
                Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="treasurer_claim_expr_index_input"),
                RadioButton(label="Quiet transaction printing", id="treasurer_claim_expr_quiet_radio"),
                RadioButton(label="Verbose transaction printing", id="treasurer_claim_expr_verbose_radio"),
                Button("Claim", id="treasurer_claim_expr_confirm_button"),
                Button("Back", id="treasurer_claim_expr_back_button"),
                id="treasurer_claim_expr_page_content",
                classes="content_page"
            ),
            id="treasurer_claim_expr_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "treasurer_claim_expr_back_button":
            self.app.switch_screen(treasurer_page())
        elif event.button.id == "treasurer_claim_expr_confirm_button":
            threshold = self.get_child_by_id("treasurer_claim_expr_page").get_child_by_id("treasurer_claim_expr_page_content").get_child_by_id("treasurer_claim_expr_threshold_input").value
            endpoint = self.get_child_by_id("treasurer_claim_expr_page").get_child_by_id("treasurer_claim_expr_page_content").get_child_by_id("treasurer_claim_expr_endpoint_input").value
            gas_price = self.get_child_by_id("treasurer_claim_expr_page").get_child_by_id("treasurer_claim_expr_page_content").get_child_by_id("treasurer_claim_expr_gas_input").value
            wallet_index = self.get_child_by_id("treasurer_claim_expr_page").get_child_by_id("treasurer_claim_expr_page_content").get_child_by_id("treasurer_claim_expr_index_input").value
            quiet = self.get_child_by_id("treasurer_claim_expr_page").get_child_by_id("treasurer_claim_expr_page_content").get_child_by_id("treasurer_claim_expr_quiet_radio").value
            verbose = self.get_child_by_id("treasurer_claim_expr_page").get_child_by_id("treasurer_claim_expr_page_content").get_child_by_id("treasurer_claim_expr_verbose_radio").value

            output, errCode = be.treasurer_claim_expr(threshold, endpoint, gas_price, wallet_index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())
        


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
                id="identity_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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
                id="account_deposit_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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
                id="account_withdraw_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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
                id="account_transfer_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "account_transfer_confirm_button":
            output, errCode = be.account_transfer(reciever_addr, agi_amount, mpe_address, gas_price, wallet_index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())


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
                id="organization_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "organization_page_metadata_button":
            self.app.push_screen(org_metadata_page())
        elif event.button.id == "organization_page_groups_button":
            self.app.push_screen(org_groups_page())
        elif event.button.id == "organization_page_members_button":
            self.app.push_screen(members_page())
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
                id="org_metadata_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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
                id="print_org_metadata_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "print_org_metadata_back_button":
            self.app.pop_screen()

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
                id="init_org_metadata_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "init_org_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "init_org_metadata_confirm_button":
            output, errCode = be.init_org_metadata(org_name, org_id, org_type, reg_addr)
            popup_output = output
            self.app.push_screen(popup_output_page())

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
                id="add_org_metadata_desc_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "add_org_metadata_desc_back_button":
            self.app.pop_screen()
        elif event.button.id == "add_org_metadata_desc_confirm_button":
            output, errCode = be.add_org_metadata_desc(long_desc, short_desc, url, meta_path)
            popup_output = output
            self.app.push_screen(popup_output_page())

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
                id="manage_org_assets_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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
                id="manage_org_contacts_page_content",
                classes="content_page"
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
                id="update_org_metadata_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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
                id="org_groups_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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
                id="add_org_group_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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
                id="update_org_group_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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

class members_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Organization Members Page", id="members_page_title"),
                Button(label="Manage Members", id="members_manage_button"),
                Button(label="Change Organization Owner", id="members_change_owner_button"),
                Button(label="Back", id="members_back_button"),
                id="members_page_content",
                classes="content_page"
            ),
            id="members_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "members_back_button":
            self.app.switch_screen(organization_page())
        elif event.button.id == "members_manage_button":
            self.app.push_screen(manage_members_page())
        elif event.button.id == "members_change_owner_button":
            self.app.push_screen(change_org_owner_page())


class manage_members_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Manage Members Page", id="manage_members_page_title"),
                Input(placeholder="Id of the Organization", id="manage_members_id_input"),
                Input(placeholder="List of members to be added to/removed from the organization", id="manage_members_mem_list_input"),
                Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="manage_members_gas_input"),
                Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="manage_members_index_input"),
                RadioButton(label="Quiet transaction printing", id="manage_members_quiet_radio"),
                RadioButton(label="Verbose transaction printing", id="manage_members_verbose_radio"),
                Button(label="Add Member(s)", id="manage_members_add_button"),
                Button(label="Remove Member(s)", id="manage_members_remove_button"),
                Button(label="Back", id="manage_members_back_button"),
                id="manage_members_page_content",
                classes="content_page"
            ),
            id="manage_members_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        org_id = self.get_child_by_id("manage_members_page").get_child_by_id("manage_members_page_content").get_child_by_id("manage_members_id_input").value
        mem_list = self.get_child_by_id("manage_members_page").get_child_by_id("manage_members_page_content").get_child_by_id("manage_members_mem_list_input").value
        gas = self.get_child_by_id("manage_members_page").get_child_by_id("manage_members_page_content").get_child_by_id("manage_members_gas_input").value
        index = self.get_child_by_id("manage_members_page").get_child_by_id("manage_members_page_content").get_child_by_id("manage_members_index_input").value
        quiet = self.get_child_by_id("manage_members_page").get_child_by_id("manage_members_page_content").get_child_by_id("manage_members_quiet_radio").value
        verbose = self.get_child_by_id("manage_members_page").get_child_by_id("manage_members_page_content").get_child_by_id("manage_members_verbose_radio").value
            
        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "manage_members_back_button":
            self.app.pop_screen()
        elif event.button.id == "manage_members_add_button":
            output, errCode = be.add_org_members(org_id, mem_list, gas, index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())
        elif event.button.id == "manage_members_add_button":
            output, errCode = be.remove_org_members(org_id, mem_list, gas, index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())



class change_org_owner_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Organization Owner Page", id="change_org_owner_page_title"),
                Input(placeholder="Id of the Organization", id="change_org_owner_id_input"),
                Input(placeholder="Address of the new Organization's owner", id="change_org_owner_new_addr_input"),
                Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="change_org_owner_gas_input"),
                Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="change_org_owner_index_input"),
                RadioButton(label="Quiet transaction printing", id="change_org_owner_quiet_radio"),
                RadioButton(label="Verbose transaction printing", id="change_org_owner_verbose_radio"),
                Button(label="Change Owner", id="change_org_owner_confirm_button"),
                Button(label="Back", id="change_org_owner_back_button"),
                id="change_org_owner_page_content",
                classes="content_page"
            ),
            id="change_org_owner_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "change_org_owner_back_button":
            self.app.pop_screen()
        elif event.button.id == "change_org_owner_confirm_button":
            org_id = self.get_child_by_id("change_org_owner_page").get_child_by_id("change_org_owner_page_content").get_child_by_id("change_org_owner_id_input").value
            new_addr = self.get_child_by_id("change_org_owner_page").get_child_by_id("change_org_owner_page_content").get_child_by_id("change_org_owner_new_addr_input").value
            gas = self.get_child_by_id("change_org_owner_page").get_child_by_id("change_org_owner_page_content").get_child_by_id("change_org_owner_gas_input").value
            index = self.get_child_by_id("change_org_owner_page").get_child_by_id("change_org_owner_page_content").get_child_by_id("change_org_owner_index_input").value
            quiet = self.get_child_by_id("change_org_owner_page").get_child_by_id("change_org_owner_page_content").get_child_by_id("change_org_owner_quiet_radio").value
            verbose = self.get_child_by_id("change_org_owner_page").get_child_by_id("change_org_owner_page_content").get_child_by_id("change_org_owner_verbose_radio").value

            output, errCode = be.change_org_owner(org_id, new_addr, gas, index, quiet, verbose)
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
                id="org_manage_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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
                Input(placeholder="[OPTIONAL] Registery contract address", id="org_reg_addr_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json) Default: 'organization_metadata.json'", id="org_manage_create_file_input"),
                Input(placeholder="[OPTIONAL] List of members to be added to the organization", id="org_manage_create_mems_input"),
                Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="org_manage_create_gas_input"),
                Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="org_manage_create_index_input"),
                RadioButton(label="Quiet transaction printing", id="org_manage_create_quiet_radio"),
                RadioButton(label="Verbose transaction printing", id="org_manage_create_verbose_radio"),
                Button(label="Create Organization", id="org_manage_create_confirm_button"),
                Button(label="Back", id="org_manage_create_back_button"),
                id="org_manage_create_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "org_manage_create_back_button":
            self.app.pop_screen()
        elif event.button.id == "org_manage_create_confirm_button":
            org_id = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_id_input").value
            reg_addr = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_reg_addr_input").value
            file_name = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_file_input").value
            mem_list = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_mems_input").value
            gas = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_gas_input").value
            index = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_index_input").value
            quiet = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_quiet_radio").value
            verbose = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_verbose_radio").value

            output, errCode = be.create_organization(org_id, file_name, mem_list, gas, index, quiet, verbose, reg_addr)
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
                id="org_manage_delete_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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

class services_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Services Page", id="services_page_title"),
                Button(label="Metadata", id="services_metadata_button"),
                Button(label="Manage", id="services_page_manage_button"),
                id="services_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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
                Button(label="Set", id="services_set_button"),
                Button(label="Add/Remove", id="services_add_remove_button"),
                Button(label="Update", id="services_update_button"),
                Button(label="Get", id="services_get_button"),
                Button("Back", id="services_metadata_back_button"),
                id="manage_services_metadata_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "services_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "services_metadata_init_button":
            self.app.push_screen(init_service_metadata_page())
        elif event.button.id == "services_set_button":
            self.app.push_screen(service_metadata_set_page())
        elif event.button.id == "services_add_remove_button":
            self.app.push_screen(service_metadata_add_remove_page())
        elif event.button.id == "services_update_button":
            self.app.push_screen(service_metadata_update_page())
        elif event.button.id == "services_get_button":
            self.app.push_screen(service_metadata_get_page())

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
                id="init_service_metadata_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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

class service_metadata_set_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Service Metadata Set Page", id="service_metadata_set_page_title"),
                Button("Set model", id="service_metadata_set_model_button"),
                Button("Set fixed price", id="service_metadata_set_fixed_price_button"),
                Button("Set method price", id="service_metadata_set_method_price_button"),
                Button("Set free calls", id="service_metadata_set_free_calls_button"),
                Button("Set freecall signer address", id="service_metadata_set_freecall_signer_button"),
                Button("Back", id="service_metadata_set_back_button"),
                id="service_metadata_set_page_content",
                classes="content_page"
            ),
            id="service_metadata_set_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_set_model_button":
            self.app.push_screen(service_metadata_set_model_page())
        elif event.button.id == "service_metadata_set_fixed_price_button":
            self.app.push_screen(service_metadata_set_fixed_price_page())
        elif event.button.id == "service_metadata_set_method_price_button":
            self.app.push_screen(service_metadata_set_method_price_page())
        elif event.button.id == "service_metadata_set_free_calls_button":
            self.app.push_screen(service_metadata_set_free_calls_page())
        elif event.button.id == "service_metadata_set_freecall_signer_button":
            self.app.push_screen(service_metadata_set_freecall_signer_page())
        elif event.button.id == "service_metadata_set_back_button":
            self.app.pop_screen()

class service_metadata_set_model_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Set Service Model Page", id="service_metadata_set_model_page_title"),
                Input(placeholder="Directory which contains protobuf files", id="service_metadata_set_model_proto_dir_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json)", id="service_metadata_set_model_file_input"),
                Button("Set Model", id="service_metadata_set_model_confirm_button"),
                Button("Back", id="service_metadata_set_model_back_button"),
                id="service_metadata_set_model_page_content",
                classes="content_page"
            ),
            id="service_metadata_set_model_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_set_model_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_set_model_confirm_button":
            proto_dir = self.get_child_by_id("service_metadata_set_model_page").get_child_by_id("service_metadata_set_model_page_content").get_child_by_id("service_metadata_set_model_proto_dir_input").value
            metadata_file = self.get_child_by_id("service_metadata_set_model_page").get_child_by_id("service_metadata_set_model_page_content").get_child_by_id("service_metadata_set_model_file_input").value
            
            output, errCode = be.service_metadata_set_model(proto_dir, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_set_fixed_price_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Set Service Fixed Price Page", id="service_metadata_set_fixed_price_page_title"),
                Input(placeholder="Group name for fixed price method", id="service_metadata_set_fixed_price_group_input"),
                Input(placeholder="Fixed price in AGI token for all methods", id="service_metadata_set_fixed_price_amount_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json)", id="service_metadata_set_fixed_price_file_input"),
                Button("Set Fixed Price", id="service_metadata_set_fixed_price_confirm_button"),
                Button("Back", id="service_metadata_set_fixed_price_back_button"),
                id="service_metadata_set_fixed_price_page_content",
                classes="content_page"
            ),
            id="service_metadata_set_fixed_price_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_set_fixed_price_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_set_fixed_price_confirm_button":
            group_name = self.get_child_by_id("service_metadata_set_fixed_price_page").get_child_by_id("service_metadata_set_fixed_price_page_content").get_child_by_id("service_metadata_set_fixed_price_group_input").value
            price = self.get_child_by_id("service_metadata_set_fixed_price_page").get_child_by_id("service_metadata_set_fixed_price_page_content").get_child_by_id("service_metadata_set_fixed_price_amount_input").value
            metadata_file = self.get_child_by_id("service_metadata_set_fixed_price_page").get_child_by_id("service_metadata_set_fixed_price_page_content").get_child_by_id("service_metadata_set_fixed_price_file_input").value
            
            output, errCode = be.service_metadata_set_fixed_price(group_name, price, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_set_method_price_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Set Service Method Price Page", id="service_metadata_set_method_price_page_title"),
                Input(placeholder="Group Name", id="service_metadata_set_method_price_group_input"),
                Input(placeholder="Package Name", id="service_metadata_set_method_price_package_input"),
                Input(placeholder="Service Name", id="service_metadata_set_method_price_service_input"),
                Input(placeholder="Method Name", id="service_metadata_set_method_price_method_input"),
                Input(placeholder="Set fixed price in AGI token for all methods", id="service_metadata_set_method_price_amount_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json)", id="service_metadata_set_method_price_file_input"),
                Button("Set Method Price", id="service_metadata_set_method_price_confirm_button"),
                Button("Back", id="service_metadata_set_method_price_back_button"),
                id="service_metadata_set_method_price_page_content",
                classes="content_page"
            ),
            id="service_metadata_set_method_price_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_set_method_price_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_set_method_price_confirm_button":
            group_name = self.get_child_by_id("service_metadata_set_method_price_page").get_child_by_id("service_metadata_set_method_price_page_content").get_child_by_id("service_metadata_set_method_price_group_input").value
            package_name = self.get_child_by_id("service_metadata_set_method_price_page").get_child_by_id("service_metadata_set_method_price_page_content").get_child_by_id("service_metadata_set_method_price_package_input").value
            service_name = self.get_child_by_id("service_metadata_set_method_price_page").get_child_by_id("service_metadata_set_method_price_page_content").get_child_by_id("service_metadata_set_method_price_service_input").value
            method_name = self.get_child_by_id("service_metadata_set_method_price_page").get_child_by_id("service_metadata_set_method_price_page_content").get_child_by_id("service_metadata_set_method_price_method_input").value
            price = self.get_child_by_id("service_metadata_set_method_price_page").get_child_by_id("service_metadata_set_method_price_page_content").get_child_by_id("service_metadata_set_method_price_amount_input").value
            metadata_file = self.get_child_by_id("service_metadata_set_method_price_page").get_child_by_id("service_metadata_set_method_price_page_content").get_child_by_id("service_metadata_set_method_price_file_input").value
            
            output, errCode = be.service_metadata_set_method_price(group_name, package_name, service_name, method_name, price, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_set_free_calls_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Service Set Free Calls Page", id="service_metadata_set_free_calls_page_title"),
                Input(placeholder="Group Name", id="service_metadata_set_free_calls_group_input"),
                Input(placeholder="Number of free calls", id="service_metadata_set_free_calls_num_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json)", id="service_metadata_set_free_calls_file_input"),
                Button("Set Free Calls", id="service_metadata_set_free_calls_confirm_button"),
                Button("Back", id="service_metadata_set_free_calls_back_button"),
                id="service_metadata_set_free_calls_page_content",
                classes="content_page"
            ),
            id="service_metadata_set_free_calls_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_set_free_calls_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_set_free_calls_confirm_button":
            group_name = self.get_child_by_id("service_metadata_set_free_calls_page").get_child_by_id("service_metadata_set_free_calls_page_content").get_child_by_id("service_metadata_set_free_calls_group_input").value
            free_calls = self.get_child_by_id("service_metadata_set_free_calls_page").get_child_by_id("service_metadata_set_free_calls_page_content").get_child_by_id("service_metadata_set_free_calls_num_input").value
            metadata_file = self.get_child_by_id("service_metadata_set_free_calls_page").get_child_by_id("service_metadata_set_free_calls_page_content").get_child_by_id("service_metadata_set_free_calls_file_input").value
            
            output, errCode = be.service_metadata_set_method_price(group_name, free_calls, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_set_freecall_signer_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Service Freecall Signer Page", id="service_metadata_set_freecall_signer_page_title"),
                Input(placeholder="Name of the payment group to which we want to set freecalls", id="service_metadata_set_freecall_signer_group_input"),
                Input(placeholder="Signer Address - This is used to define the public key address used for validating signatures requested specially for free call. To be obtained as part of curation process", id="service_metadata_set_freecall_signer_addr_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json)", id="service_metadata_set_freecall_signer_file_input"),
                Button("Set Signer Address", id="service_metadata_set_freecall_signer_confirm_button"),
                Button("Back", id="service_metadata_set_freecall_signer_back_button"),
                id="service_metadata_set_freecall_signer_page_content",
                classes="content_page"
            ),
            id="service_metadata_set_freecall_signer_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_set_freecall_signer_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_set_freecall_signer_confirm_button":
            group_name = self.get_child_by_id("service_metadata_set_freecall_signer_page").get_child_by_id("service_metadata_set_freecall_signer_page_content").get_child_by_id("service_metadata_set_freecall_signer_group_input").value
            signer_addr = self.get_child_by_id("service_metadata_set_freecall_signer_page").get_child_by_id("service_metadata_set_freecall_signer_page_content").get_child_by_id("service_metadata_set_freecall_signer_addr_input").value
            metadata_file = self.get_child_by_id("service_metadata_set_freecall_signer_page").get_child_by_id("service_metadata_set_freecall_signer_page_content").get_child_by_id("service_metadata_set_freecall_signer_file_input").value
            
            output, errCode = be.service_metadata_set_freecall_signer_addr(group_name, signer_addr, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_add_remove_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Service Metadata Add/Remove Page", id="service_metadata_add_remove_page_title"),
                Button(label="Add Service Description", id="services_metadata_add_desc_button"),
                Button("Add/Remove Service Metadata Groups", id="services_metadata_add_remove_groups_button"),
                Button("Add/Remove Service Metadata Daemon Address", id="services_metadata_add_remove_daemon_button"),
                Button("Add/Remove Service Metadata Assets", id="services_metadata_add_remove_assets_button"),
                Button("Add/Remove Service Metadata Media", id="services_metadata_add_remove_media_button"),
                Button("Back", id="service_metadata_add_remove_back_button"),
                id="service_metadata_add_remove_page_content",
                classes="content_page"
            ),
            id="service_metadata_add_remove_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_add_remove_back_button":
            self.app.pop_screen()
        elif event.button.id == "services_metadata_add_desc_button":
            self.app.push_screen(add_desc_service_metadata_page())
        elif event.button.id == "services_metadata_add_remove_groups_button":
            self.app.push_screen(service_metadata_add_remove_group_page())
        elif event.button.id == "services_metadata_add_remove_daemon_button":
            self.app.push_screen(service_metadata_add_remove_daemon_addr_page())
        elif event.button.id == "services_metadata_add_remove_assets_button":
            self.app.push_screen(service_metadata_add_remove_assets_page())
        elif event.button.id == "services_metadata_add_remove_media_button":
            self.app.push_screen(service_metadata_add_remove_media_page())

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
                id="add_desc_service_metadata_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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

class service_metadata_add_remove_group_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Manage Service Group Page", id="service_metadata_add_remove_group_page_title"),
                Input(placeholder="Name of the payment group to be added/removed", id="service_metadata_add_remove_group_group_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json)", id="service_metadata_add_remove_group_file_input"),
                Button("Add Group", id="service_metadata_add_remove_group_add_button"),
                Button("Remove Group", id="service_metadata_add_remove_group_remove_button"),
                Button("Back", id="service_metadata_add_remove_group_back_button"),
                id="service_metadata_add_remove_group_page_content",
                classes="content_page"
            ),
            id="service_metadata_add_remove_group_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        group_name = self.get_child_by_id("service_metadata_add_remove_group_page").get_child_by_id("service_metadata_add_remove_group_page_content").get_child_by_id("service_metadata_add_remove_group_group_input").value
        metadata_file = self.get_child_by_id("service_metadata_add_remove_group_page").get_child_by_id("service_metadata_add_remove_group_page_content").get_child_by_id("service_metadata_add_remove_group_file_input").value

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_add_remove_group_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_add_remove_group_add_button":
            output, errCode = be.service_metadata_add_group(group_name, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())
        elif event.button.id == "service_metadata_add_remove_group_remove_button":
            output, errCode = be.service_metadata_remove_group(group_name, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_add_remove_daemon_addr_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Service Daemon Address Page", id="service_metadata_add_remove_daemon_addr_page_title"),
                Input(placeholder="Name of the payment group to be added/removed", id="service_metadata_add_remove_daemon_addr_group_input"),
                Input(placeholder="[NOT REQUIRED FOR DELETE] Ethereum public addresses of daemon", id="service_metadata_add_remove_daemon_addr_endpoint_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json)", id="service_metadata_add_remove_daemon_addr_file_input"),
                Button("Add Daemon Address", id="service_metadata_add_remove_daemon_addr_add_button"),
                Button("Remove ALL Daemon Addresses", id="service_metadata_add_remove_daemon_addr_remove_button"),
                Button("Back", id="service_metadata_add_remove_daemon_addr_back_button"),
                id="service_metadata_add_remove_daemon_addr_page_content",
                classes="content_page"
            ),
            id="service_metadata_add_remove_daemon_addr_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        group_name = self.get_child_by_id("service_metadata_add_remove_daemon_addr_page").get_child_by_id("service_metadata_add_remove_daemon_addr_page_content").get_child_by_id("service_metadata_add_remove_daemon_addr_group_input").value
        daemon_addr = self.get_child_by_id("service_metadata_add_remove_daemon_addr_page").get_child_by_id("service_metadata_add_remove_daemon_addr_page_content").get_child_by_id("service_metadata_add_remove_daemon_addr_endpoint_input").value
        metadata_file = self.get_child_by_id("service_metadata_add_remove_daemon_addr_page").get_child_by_id("service_metadata_add_remove_daemon_addr_page_content").get_child_by_id("service_metadata_add_remove_daemon_addr_file_input").value

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_add_remove_daemon_addr_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_add_remove_daemon_addr_add_button":
            output, errCode = be.service_metadata_add_daemon_addr(group_name, daemon_addr, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())
        elif event.button.id == "service_metadata_add_remove_daemon_addr_remove_button":
            output, errCode = be.service_metadata_remove_daemon_addr(group_name, daemon_addr, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_add_remove_assets_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Manage Service Assets Page", id="service_metadata_add_remove_assets_page_title"),
                Input(placeholder="[NOT REQUIRED FOR DELETE ALL] Asset file path", id="service_metadata_add_remove_assets_path_input"),
                Select(options=((line, line) for line in """hero_image\nimages""".splitlines()), prompt="Select Organization Type", id="service_metadata_add_remove_assets_type_select"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json)", id="service_metadata_add_remove_assets_file_input"),
                Button("Add Asset", id="service_metadata_add_remove_assets_add_button"),
                Button("Remove ALL Assets of type", id="service_metadata_add_remove_assets_remove_button"),
                Button("Back", id="service_metadata_add_remove_assets_back_button"),
                id="service_metadata_add_remove_assets_page_content",
                classes="content_page"
            ),
            id="service_metadata_add_remove_assets_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        asset_type = self.get_child_by_id("service_metadata_add_remove_assets_page").get_child_by_id("service_metadata_add_remove_assets_page_content").get_child_by_id("service_metadata_add_remove_assets_type_select").value
        metadata_file = self.get_child_by_id("service_metadata_add_remove_assets_page").get_child_by_id("service_metadata_add_remove_assets_page_content").get_child_by_id("service_metadata_add_remove_assets_file_input").value

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_add_remove_assets_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_add_remove_assets_add_button":
            asset_path = self.get_child_by_id("service_metadata_add_remove_assets_page").get_child_by_id("service_metadata_add_remove_assets_page_content").get_child_by_id("service_metadata_add_remove_assets_path_input").value
            output, errCode = be.service_metadata_add_assets(asset_path, asset_type, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())
        elif event.button.id == "service_metadata_add_remove_assets_remove_button":
            output, errCode = be.service_metadata_remove_assets(asset_type, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_add_remove_media_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Add/Remove Service Media Page", id="service_metadata_add_remove_media_page_title"),
                Input(placeholder="Media url endpoint", id="service_metadata_add_media_url_input"),
                Input(placeholder="Service metadata json file (default service_metadata.json)", id="service_metadata_add_media_file_input"),
                RadioButton(label="Media is hero-image", id="service_metadata_add_media_hero_radio"),
                Button("Add Media", id="service_metadata_add_remove_media_add_button"),
                Button("Remove ALL Media", id="service_metadata_add_remove_media_remove_button"),
                Button("Back", id="service_metadata_add_remove_media_back_button"),
                id="service_metadata_add_remove_media_page_content",
                classes="content_page"
            ),
            id="service_metadata_add_remove_media_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        metadata_file = self.get_child_by_id("service_metadata_add_remove_media_page").get_child_by_id("service_metadata_add_remove_media_page_content").get_child_by_id("service_metadata_add_media_file_input").value
        
        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_add_remove_media_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_add_remove_media_remove_button":
            output, errCode = be.service_metadata_remove_media(metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())
        elif event.button.id == "service_metadata_add_remove_media_add_button":
            url = self.get_child_by_id("service_metadata_add_remove_media_page").get_child_by_id("service_metadata_add_remove_media_page_content").get_child_by_id("service_metadata_add_media_url_input").value
            hero_image = self.get_child_by_id("service_metadata_add_remove_media_page").get_child_by_id("service_metadata_add_remove_media_page_content").get_child_by_id("service_metadata_add_media_hero_radio").value
            output, errCode = be.service_metadata_add_media(url, hero_image, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_update_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Service Metadata Blockchain Update Page", id="service_metadata_update_page_title"),
                Button("Update Service Daemon Address", id="service_metadata_update_daemon_button"),
                Button("Validate Metadata", id="service_metadata_update_validate_button"),
                Button("Update Metadata", id="service_metadata_update_metadata_button"),
                Button("Back", id="serivce_metadata_update_back_button"),
                id="service_metadata_update_page_content",
                classes="content_page"
            ),
            id="service_metadata_update_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "serivce_metadata_update_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_update_daemon_button":
            self.app.push_screen(service_metadata_update_daemon_addr_page())
        elif event.button.id == "service_metadata_update_validate_button":
            self.app.push_screen(service_metadata_update_validate_metadata_page())
        elif event.button.id == "service_metadata_update_metadata_button":
            self.app.push_screen(service_metadata_update_metadata_page())

class service_metadata_update_daemon_addr_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Update Service Daemon Address Page", id="service_metadata_update_daemon_addr_page_title"),
                Input(placeholder="Name of the payment group to which we want to update daemon addresses for", id="service_metadata_update_daemon_addr_group_input"),
                Input(placeholder="Daemon addresses", id="service_metadata_update_daemon_addr_endpoint_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json)", id="service_metadata_update_daemon_addr_file_input"),
                Button("Update Daemon Address", id="service_metadata_update_daemon_addr_update_button"),
                Button("Back", id="service_metadata_update_daemon_addr_back_button"),
                id="service_metadata_update_daemon_addr_page_content",
                classes="content_page"
            ),
            id="service_metadata_update_daemon_addr_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_add_remove_media_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_add_remove_media_remove_button":
            group_name = self.get_child_by_id("service_metadata_update_daemon_addr_page").get_child_by_id("service_metadata_update_daemon_addr_page_content").get_child_by_id("service_metadata_update_daemon_addr_group_input").value
            daemon_addr = self.get_child_by_id("service_metadata_update_daemon_addr_page").get_child_by_id("service_metadata_update_daemon_addr_page_content").get_child_by_id("service_metadata_update_daemon_addr_endpoint_input").value
            metadata_file = self.get_child_by_id("service_metadata_update_daemon_addr_page").get_child_by_id("service_metadata_update_daemon_addr_page_content").get_child_by_id("service_metadata_update_daemon_addr_file_input").value

            output, errCode = be.service_metadata_update_daemon_addr(group_name, daemon_addr, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_update_validate_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Validate Service Metadata Page", id="service_metadata_update_validate_metadata_page_title"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json)", id="service_metadata_update_validate_metadata_file_input"),
                Button("Validate Metadata", id="service_metadata_update_validate_metadata_validate_button"),
                Button("Back", id="service_metadata_update_validate_metadata_back_button"),
                id="service_metadata_update_validate_metadata_page_content",
                classes="content_page"
            ),
            id="service_metadata_update_validate_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_update_validate_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_update_validate_metadata_validate_button":
            metadata_file = self.get_child_by_id("service_metadata_update_daemon_addr_page").get_child_by_id("service_metadata_update_daemon_addr_page_content").get_child_by_id("service_metadata_update_validate_metadata_file_input").value
            output, errCode = be.service_metadata_update_validate_metadata(metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_update_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Update Service Metadata Page", id="service_metadata_update_metadata_pagetitle"),
                Input(placeholder="Your Organization ID", id="service_metadata_update_metadata_org_id_input"),
                Input(placeholder="Your Service ID", id="service_metadata_update_metadata_service_id_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json) Default: 'organization_metadata.json'", id="service_metadata_update_metadata_file_input"),
                Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from 'networks'", id="service_metadata_update_metadata_reg_contract_input"),
                Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from 'networks'", id="service_metadata_update_metadata_mpe_input"),
                RadioButton(label="Update MPE Address in metadata before publishing service", id="service_metadata_update_metadata_update_mpe_radio"),
                Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="service_metadata_update_metadata_gas_input"),
                Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="service_metadata_update_metadata_index_input"),
                RadioButton(label="Quiet transaction printing", id="service_metadata_update_metadata_quiet_radio"),
                RadioButton(label="Verbose transaction printing", id="service_metadata_update_metadata_verbose_radio"),
                Button(label="Update Metadata", id="service_metadata_update_metadata_confirm_button"),
                Button(label="Back", id="service_metadata_update_metadata_back_button"),
                id="service_metadata_update_metadata_page_content",
                classes="content_page"
            ),
            id="service_metadata_update_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_update_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_update_metadata_confirm_button":
            org_id = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_org_id_input").value
            service_id = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_service_id_input").value
            metadata_file = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_file_input").value
            reg_addr = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_reg_contract_input").value
            mpe_addr = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_mpe_input").value
            update_mpe = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_update_mpe_radio").value
            gas = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_gas_input").value
            index = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_index_input").value
            quiet = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_quiet_radio").value
            verbose = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_verbose_radio").value
            
            output, errCode = be.service_metadata_update_update_metadata(org_id, service_id, metadata_file, reg_addr, mpe_addr, update_mpe, gas, index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_get_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Service Metadata Get Page", id="service_metadata_get_page_title"),
                Button("Service Status", id="service_metadata_get_status_button"),
                Button("API Metadata", id="service_metadata_get_metadata_button"),
                Button("API Registry", id="service_metadata_get_registry_button"),
                Button("Back", id="service_metadata_get_back_button"),
                id="service_metadata_get_page_content",
                classes="content_page"
            ),
            id="service_metadata_get_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_get_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_get_status_button":
            self.app.push_screen(service_metadata_get_service_status_page())
        elif event.button.id == "service_metadata_get_metadata_button":
            self.app.push_screen(service_metadata_get_api_metadata_page())
        elif event.button.id == "service_metadata_get_registry_button":
            self.app.push_screen(service_metadata_get_api_registry_page())

class service_metadata_get_service_status_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Service Status Page", id="service_metadata_get_service_status_page_title"),
                Input(placeholder="Your Organization ID", id="service_metadata_get_service_status_org_id_input"),
                Input(placeholder="Your Service ID", id="service_metadata_get_service_status_service_id_input"),
                Input(placeholder="[OPTIONAL] Name of the payment group. Parameter should be specified only for services with several payment groups", id="service_metadata_get_service_status_group_input"),
                Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from 'networks'", id="service_metadata_get_service_status_reg_contract_input"),
                Button(label="Get Service Status", id="service_metadata_get_service_status_confirm_button"),
                Button(label="Back", id="service_metadata_get_service_status_back_button"),
                id="service_metadata_get_service_status_page_content",
                classes="content_page"
            ),
            id="service_metadata_get_service_status_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_get_service_status_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_get_service_status_confirm_button":
            org_id = self.get_child_by_id("service_metadata_get_service_status_page").get_child_by_id("service_metadata_get_service_status_page_content").get_child_by_id("service_metadata_get_service_status_org_id_input").value
            service_id = self.get_child_by_id("service_metadata_get_service_status_page").get_child_by_id("service_metadata_get_service_status_page_content").get_child_by_id("service_metadata_get_service_status_service_id_input").value
            reg_addr = self.get_child_by_id("service_metadata_get_service_status_page").get_child_by_id("service_metadata_get_service_status_page_content").get_child_by_id("service_metadata_get_service_status_reg_contract_input").value
            pay_group = self.get_child_by_id("service_metadata_get_service_status_page").get_child_by_id("service_metadata_get_service_status_page_content").get_child_by_id("service_metadata_get_service_status_group_input").value
            
            
            output, errCode = be.print_service_status(org_id, service_id, pay_group, reg_addr)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_get_api_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Service API Metadata Page", id="service_metadata_get_api_metadata_page_title"),
                Input(placeholder="Directory to which extract api (model)", id="service_metadata_get_api_metadata_proto_dir_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json)", id="service_metadata_get_api_metadata_file_input"),
                Button("Set Model", id="service_metadata_get_api_metadata_confirm_button"),
                Button("Back", id="service_metadata_get_api_metadata_back_button"),
                id="service_metadata_get_api_metadata_page_content",
                classes="content_page"
            ),
            id="service_metadata_get_api_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_get_api_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_get_api_metadata_confirm_button":
            proto_dir = self.get_child_by_id("service_metadata_get_api_metadata_page").get_child_by_id("service_metadata_get_api_metadata_page_content").get_child_by_id("service_metadata_get_api_metadata_proto_dir_input").value
            metadata_file = self.get_child_by_id("service_metadata_get_api_metadata_page").get_child_by_id("service_metadata_get_api_metadata_page_content").get_child_by_id("service_metadata_get_api_metadata_file_input").value
            
            output, errCode = be.print_service_api_metadata(proto_dir, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_get_api_registry_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Service API Registry Page", id="service_metadata_get_api_registry_page_title"),
                Input(placeholder="Your Organization ID", id="service_metadata_get_api_registry_org_id_input"),
                Input(placeholder="Your Service ID", id="service_metadata_get_api_registry_service_id_input"),
                Input(placeholder="Directory to which extract api (model)", id="service_metadata_get_api_registry_proto_dir_input"),
                Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from 'networks'", id="service_metadata_get_api_registry_reg_contract_input"),
                Button(label="Get Service Status", id="service_metadata_get_api_registry_confirm_button"),
                Button(label="Back", id="service_metadata_get_api_registry_back_button"),
                id="service_metadata_get_api_registry_page_content",
                classes="content_page"
            ),
            id="service_metadata_get_api_registry_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_get_api_registry_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_get_api_registry_confirm_button":
            org_id = self.get_child_by_id("service_metadata_get_api_registry_page").get_child_by_id("service_metadata_get_api_registry_page_content").get_child_by_id("service_metadata_get_api_registry_org_id_input").value
            service_id = self.get_child_by_id("service_metadata_get_api_registry_page").get_child_by_id("service_metadata_get_api_registry_page_content").get_child_by_id("service_metadata_get_api_registry_service_id_input").value
            proto_dir = self.get_child_by_id("service_metadata_get_api_registry_page").get_child_by_id("service_metadata_get_api_registry_page_content").get_child_by_id("service_metadata_get_api_registry_proto_dir_input").value
            reg_addr = self.get_child_by_id("service_metadata_get_api_registry_page").get_child_by_id("service_metadata_get_api_registry_page_content").get_child_by_id("service_metadata_get_api_registry_reg_contract_input").value
            
            output, errCode = be.print_service_api_registry(org_id, service_id, reg_addr, proto_dir)
            popup_output = output
            self.app.push_screen(popup_output_page())

class services_manage_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Manage Services Page", id="services_manage_page_title"),
                Button(label="Publish Service", id="services_manage_create_button"),
                Button(label="Delete Service", id="services_manage_delete_button"),
                Button("Back", id="services_manage_back_button"),
                id="services_manage_page_content",
                classes="content_page"
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
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "services_manage_back_button":
            self.app.pop_screen()
        elif event.button.id == "services_manage_create_button":
            self.app.push_screen(publish_service_page())
        elif event.button.id == "services_manage_delete_button":
            self.app.push_screen(delete_service_page())

class publish_service_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Service Publishing Page", id="publish_service_page_title"),
                Input(placeholder="Your Organization ID", id="publish_service_org_id_input"),
                Input(placeholder="Your Service ID", id="publish_service_service_id_input"),
                Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json) Default: 'organization_metadata.json'", id="publish_service_file_input"),
                Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from 'networks'", id="publish_service_reg_contract_input"),
                Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from 'networks'", id="publish_service_mpe_input"),
                RadioButton(label="Update MPE Address in metadata before publishing service", id="publish_service_update_mpe_radio"),
                Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="publish_service_gas_input"),
                Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="publish_service_index_input"),
                RadioButton(label="Quiet transaction printing", id="publish_service_quiet_radio"),
                RadioButton(label="Verbose transaction printing", id="publish_service_verbose_radio"),
                Button(label="Publish Service", id="publish_service_confirm_button"),
                Button(label="Back", id="publish_service_back_button"),
                id="publish_service_page_content",
                classes="content_page"
            ),
            id="publish_service_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "publish_service_back_button":
            self.app.pop_screen()
        elif event.button.id == "publish_service_confirm_button":
            org_id = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_org_id_input").value
            service_id = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_service_id_input").value
            metadata_file = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_file_input").value
            reg_addr = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_reg_contract_input").value
            mpe_addr = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_mpe_input").value
            update_mpe = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_update_mpe_radio").value
            gas = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_gas_input").value
            index = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_index_input").value
            quiet = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_quiet_radio").value
            verbose = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_verbose_radio").value
            
            output, errCode = be.publish_service(org_id, service_id, metadata_file, reg_addr, mpe_addr, update_mpe, gas, index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class delete_service_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Delete a Service Page", id="delete_service_page_title"),
                Input(placeholder="Your Organization ID", id="delete_service_org_id_input"),
                Input(placeholder="Your Service ID", id="delete_service_service_id_input"),
                Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from 'networks'", id="delete_service_reg_contract_input"),
                Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="delete_service_gas_input"),
                Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="delete_service_index_input"),
                RadioButton(label="Quiet transaction printing", id="delete_service_quiet_radio"),
                RadioButton(label="Verbose transaction printing", id="delete_service_verbose_radio"),
                Button(label="Delete Service", id="delete_service_confirm_button"),
                Button(label="Back", id="delete_service_back_button"),
                id="delete_service_page_content",
                classes="content_page"
            ),
            id="delete_service_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "delete_service_back_button":
            self.app.pop_screen()
        elif event.button.id == "delete_service_confirm_button":
            org_id = self.get_child_by_id("delete_service_page").get_child_by_id("delete_service_page_content").get_child_by_id("delete_service_org_id_input").value
            service_id = self.get_child_by_id("delete_service_page").get_child_by_id("delete_service_page_content").get_child_by_id("delete_service_service_id_input").value
            reg_addr = self.get_child_by_id("delete_service_page").get_child_by_id("delete_service_page_content").get_child_by_id("delete_service_reg_contract_input").value
            gas = self.get_child_by_id("delete_service_page").get_child_by_id("delete_service_page_content").get_child_by_id("delete_service_gas_input").value
            index = self.get_child_by_id("delete_service_page").get_child_by_id("delete_service_page_content").get_child_by_id("delete_service_index_input").value
            quiet = self.get_child_by_id("delete_service_page").get_child_by_id("delete_service_page_content").get_child_by_id("delete_service_quiet_radio").value
            verbose = self.get_child_by_id("delete_service_page").get_child_by_id("delete_service_page_content").get_child_by_id("delete_service_verbose_radio").value
            
            output, errCode = be.delete_service(org_id, service_id, reg_addr, gas, index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class custom_command_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Custom CLI Command Page", id="custom_command_page_title"),
                Input(placeholder="Input your custom command here. NOTE: omit the 'snet' prefix, this will be added automatically", id="custom_command_input"),
                Input(placeholder="[OPTIONAL] Input the working directory you would like the command to run from (default: $HOME/snet)", id="custom_cwd_input"),
                RadioButton(label="Print Traceback", id="custom_command_traceback_radio"),
                Button("Run Custom Command", id="custom_command_confirm_button"),
                id="custom_command_page_content",
                classes="content_page"
            ),
            id="custom_command_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output

        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "custom_command_confirm_button":
            command = self.get_child_by_id("custom_command_page").get_child_by_id("custom_command_page_content").get_child_by_id("custom_command_input").value
            cwd = self.get_child_by_id("custom_command_page").get_child_by_id("custom_command_page_content").get_child_by_id("custom_cwd_input").value
            traceback = self.get_child_by_id("custom_command_page").get_child_by_id("custom_command_page_content").get_child_by_id("custom_command_traceback_radio").value

            output, errCode = be.custom_command(command, cwd, traceback)
            popup_output = output
            self.app.push_screen(popup_output_page())



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