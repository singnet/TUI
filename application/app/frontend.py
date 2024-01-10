from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Header, Label, Input, Select, RadioButton
import back.backend as be
from back.backend import Organization
import pexpect

# Global variables for passing parameters between screens, as textual does not support this
error_exit_label: str
popup_output: str
cur_org: Organization

class WelcomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Welcome to the installation tool"),
            Button("Start", id="start_button"),
            id = "welcome"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global error_exit_label
        if event.button.id == "start_button":
            # Change the "start_button" to a textual loading bar

            cli_installed, stdout, stderr, errCode = be.check_cli()
            identity_added, stdout, stderr, errCode = be.check_identity()
            if (cli_installed and identity_added):
                self.app.switch_screen(wallet_page())
            elif (not cli_installed):
                error_exit_label  = stdout
                self.app.switch_screen(error_exit_page())
            elif (not identity_added):
                self.app.switch_screen(create_identity_page())

class error_exit_page(Screen):
    def compose(self) -> ComposeResult:
        global error_exit_label
        yield Grid(
            Label("ERROR - " + error_exit_label, id="error_exit_label"),
            Button("Exit", id="error_exit_button"),
            id = "error_exit"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "error_exit_button":
            self.app.exit()

class popup_output_page(Screen):
    def compose(self) -> ComposeResult:
        global popup_output
        yield Grid(
            Label(popup_output, id="popup_output_label"),
            Button("OK", id="output_exit_button"),
            id = "output"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "output_exit_button":
            self.app.pop_screen()

class create_identity_page(Screen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Input(placeholder="Organization Identity", id="org_identity_input"),
            Input(placeholder="Wallet Private Key / 24 character seed phrase (Mnemonic)", id="wallet_info_input"),
            Select(options=(("Goerli", "Goerli") for line in """Goerli""".splitlines()), prompt="Select Network", id="network_select"),
            RadioButton("Mnemonic Wallet", id="mnemonic_wallet_radio"),
            Button("Create Identity", id="create_identity_button"),
            id="create_identity"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        if event.button.id == "create_identity_button":
            org_id = self.get_child_by_id("create_identity").get_child_by_id("org_identity_input").value
            network = self.get_child_by_id("create_identity").get_child_by_id("network_select").value
            wallet_info = self.get_child_by_id("create_identity").get_child_by_id("wallet_info_input").value
            # NOTE: Add wallet info checks
            if not isinstance(org_id, str) or org_id == "":
                popup_output = "ERROR - Organization Identity cannot be blank."
                self.app.push_screen(popup_output_page())
            else:
                if not isinstance(network, str):
                    network = "goerli"
                if self.get_child_by_id("create_identity").get_child_by_type(RadioButton).value == True:
                    self.create_organization(org_id, True, wallet_info, network)
                else:
                    self.app.switch_screen(wallet_page())
                    self.create_organization(org_id, False, wallet_info, network)
                
    
    def create_organization(self, org_id, mnemonic = True, wallet_info = None, network_select = "goerli") -> Organization:
        global popup_output
        global error_exit_label
        global cur_org
        if mnemonic:
            command = f"snet identity create {org_id} mnemonic --network {network_select}"
            output, errCode = be.run_shell_command_with_input(command, wallet_info)
            if errCode == 0:
                cur_org = Organization(org_identity=org_id, wallet_priv_key=None, network=network_select)
                popup_output = stdOut
                self.app.push_screen(popup_output_page())
            else:
                error_exit_label = stdErr
                self.app.switch_screen(error_exit_page())
        else:
            command = f"snet identity create {org_id} key --private-key {wallet_info} --network {network_select.lower()}"
            stdOut, stdErr, errCode = be.run_shell_command(command)
            if errCode == 0:
                cur_org = Organization(org_identity=org_id, wallet_priv_key=wallet_info, network=network_select)
                popup_output = stdOut
                self.app.push_screen(popup_output_page())
            else:
                error_exit_label = stdErr
                self.app.switch_screen(error_exit_page())

def nav_sidebar_vert() -> Vertical:
    ret_vert = Vertical(
                Button("Wallet", id="wallet_page_nav", classes="nav_sidebar_button"),
                Button("Organization", id="organization_page_nav", classes="nav_sidebar_button"),
                Button("Services", id="services_page_nav", classes="nav_sidebar_button"),
                Button("Exit", id="exit_page_nav", classes="nav_sidebar_button"),
                classes="nav_sidebar",
                name="nav_sidebar_name",
                id="nav_sidebar"
            )

    return ret_vert

class wallet_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            nav_sidebar_vert(),
            Grid(
                Label("Wallet Page", id="wallet_page_title"),
                id="wallet_page_content"
            ),
            id="wallet_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "wallet_page_nav":
            pass
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())

class organization_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            nav_sidebar_vert(),
            Grid(
                Label("Organization Page", id="organization_page_title"),
                id="organization_page_content"
            ),
            id="organization_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "wallet_page_nav":
            self.app.switch_screen(wallet_page())
        elif event.button.id == "organization_page_nav":
            pass
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())

class services_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            nav_sidebar_vert(),
            Grid(
                Label("Services Page", id="services_page_title"),
                id="services_page_content"
            ),
            id="services_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "wallet_page_nav":
            self.app.switch_screen(wallet_page())
        elif event.button.id == "organization_page_nav":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page_nav":
            pass
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())

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