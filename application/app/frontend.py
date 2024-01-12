from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Header, Label, Input, Select, RadioButton, LoadingIndicator
import back.backend as be
from back.backend import Identity
import re

# Global variables for passing parameters between screens, as textual does not support this
error_exit_label: str
popup_output: str
cur_org: Identity

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
            cli_installed, stdout1, stderr1, errCode1 = be.check_cli()
            identity_added, stdout2, stderr2, errCode2 = be.check_account_balance()
            if (cli_installed and identity_added):
                self.app.switch_screen(account_page())
            elif (not cli_installed):
                error_exit_label  = f"CLI not found, please double check installation and ensure you are running the TUI through the environment the CLI was installed in.\n\nCommand error output: {stderr1}"
                self.app.switch_screen(error_exit_page())
            elif (not identity_added):
                self.app.switch_screen(create_identity_page())

class error_exit_page(Screen):
    def compose(self) -> ComposeResult:
        global error_exit_label
        yield Grid(
            Label("ERROR - " + error_exit_label, id="error_exit_label"),
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
            Label("INFO - " + popup_output, id="popup_output_label"),
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
            Input(placeholder="Wallet Private Key / 24 word seed phrase (Mnemonic)", id="wallet_info_input"),
            Select(options=(("Goerli", "Goerli") for line in """Goerli""".splitlines()), prompt="Select Network", id="network_select"),
            RadioButton("Mnemonic Wallet", id="mnemonic_wallet_radio"),
            Button("Create Identity", id="create_identity_button"),
            id="create_identity"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        if event.button.id == "create_identity_button":
            id_name = self.get_child_by_id("create_identity").get_child_by_id("org_identity_input").value
            network = self.get_child_by_id("create_identity").get_child_by_id("network_select").value
            wallet_info = self.get_child_by_id("create_identity").get_child_by_id("wallet_info_input").value
            mnemonic = self.get_child_by_id("create_identity").get_child_by_type(RadioButton).value
            if not isinstance(id_name, str) or id_name == "":
                popup_output = "ERROR - Organization Identity cannot be blank."
                self.app.push_screen(popup_output_page())
            elif not isinstance(wallet_info, str):
                popup_output = "ERROR - Wallet private key / seed phrase must be entered"
                self.app.push_screen(popup_output_page())
            elif len(wallet_info) != 24 and mnemonic:
                popup_output = "ERROR - Seed phrase must be 24 single-word characters"
                self.app.push_screen(popup_output_page())
            else:
                if not isinstance(network, str):
                    network = "goerli"
                else:
                    network = network.lower()
                self.create_identity(id_name, mnemonic, wallet_info, network)
                
    
    def create_identity(self, id_name, mnemonic, wallet_info = None, network_select = "goerli"):
        global popup_output
        global error_exit_label
        global cur_org
        
        stdout, stderr, errCode = be.create_identity_cli(id_name, wallet_info, network_select, mnemonic)
        if errCode == 0:
            cur_org = Identity(identity_name=id_name, wallet_priv_key=wallet_info, network=network_select)
            popup_output = stdout
            self.app.switch_screen(account_page())
            self.app.push_screen(popup_output_page())
        else:
            out = stderr
            if len(out) == 0:
                out = stdout
            error_exit_label = out
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
            pass
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "account_page_identity_settings_button":
            self.app.switch_screen(identity_page())
        elif event.button.id == "account_page_deposit_button":
            # TODO Create deposit popup and push it
            pass
        elif event.button.id == "account_page_withdraw_button":
            # TODO Create withdraw popup and push it
            pass
        elif event.button.id == "account_page_transfer_button":
            # TODO Create transfer popup and push it
            pass

class identity_page(Screen):
    def compose(self) -> ComposeResult:
        idList, listErr, listErrCode = be.run_shell_command("snet identity list")
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label(f"Identity List:\n{idList}", id="identity_page_title"),
                Button("Create Identity Page", id="identity_page_create_identity_button"),
                Input("Identity name to delete", id="identity_page_delete_input"),
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
            self.app.switch_screen(create_identity_page())
        elif event.button.id == "identity_page_delete_identity_button":
            id_name = self.get_child_by_id("identity_page").get_child_by_id("identity_page_delete_input").value
            if not isinstance(id_name, str) or id_name == "":
                popup_output = "ERROR - Please enter the name of the Identity to be deleted"
                self.app.push_screen(popup_output_page())
            else:
                stdout, stderr, errcode = be.delete_identity_cli()
                if errcode == 0:
                    # TODO If identity deleted successfully
                    pass
                else:
                    # TODO If unsuccessful to delete identity
                    output = stderr
                    if output == "":
                        output = stdout
                    popup_output = output
                    self.app.switch_screen(identity_page())
                    self.app.push_screen(popup_output_page())
                    pass


# TODO Implement entire organization CLI command
class organization_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert(),
            Grid(
                Label("Organization Page", id="organization_page_title"),
                id="organization_page_content"
            ),
            id="organization_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "account_page_nav":
            self.app.switch_screen(account_page())
        elif event.button.id == "organization_page_nav":
            pass
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
            pass
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