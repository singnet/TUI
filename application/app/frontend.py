from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical, Horizontal
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, Label, ListView, ListItem, Input
import back.backend as be

class WelcomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Welcome to the installation tool"),
            Button("Start", id="start_button"),
            id = "welcome"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start_button":
            cli_installed: bool = be.check_cli()
            # daemon_installed: bool = be.check_daemon()
            wallet_added: bool = be.check_wallet()
            if (cli_installed and wallet_added):
                self.app.switch_screen(wallet_page())
            elif (not cli_installed):
                self.app.switch_screen(cli_error_page())
            elif (not wallet_added):
                self.app.switch_screen(import_wallet_page())
                

# class wallet_setup_page(Screen):
#     def compose(self) -> ComposeResult:
#         yield Grid(
#             Button("Create Wallet", id="create_wallet_button"),
#             Button("Import Wallet", id="import_wallet_button"),
#             id="wallet_setup"
#         )

#     def on_button_pressed(self, event: Button.Pressed) -> None:
#         if event.button.id == "create_wallet_button":
#             self.app.switch_screen(create_wallet_page())
#         elif event.button.id == "import_wallet_button":
#             self.app.switch_screen(import_wallet_page())

# class create_wallet_page(Screen):
#     def compose(self) -> ComposeResult:
#         yield Grid(
#             id="create_wallet"
#         )

#     def on_button_pressed(self, event: Button.Pressed) -> None:
#         if event.button.id == "create_wallet_button":
#             self.app.switch_screen(wallet_page())
#         elif event.button.id == "import_wallet_button":
#             self.app.switch_screen(organization_page())
                
class cli_error_page(Screen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Label("There appears to be an error with your CLI installation, please ensure you are running the TUI within the environment you have installed the CLI in and try again."),
            Button("Exit", id="exit_button"),
            id = "cli_error"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit_button":
            quit(1)

class import_wallet_page(Screen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Input(placeholder="Wallet Address", id="wallet_addr_input"),
            Input(placeholder="Wallet Private Key", id="wallet_priv_input"),
            Button("Import", id="import_wallet_confirm"),
            id="import_wallet"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "import_wallet_confirm":
            # NOTE: Save wallet information to cache file
            self.app.switch_screen(wallet_page())

def nav_sidebar_vert() -> Vertical:
    ret_vert = Vertical(
                Button("Wallet", id="wallet_page", classes="nav_sidebar_button"),
                Button("Organization", id="organization_page", classes="nav_sidebar_button"),
                Button("Services", id="services_page", classes="nav_sidebar_button"),
                Button("Settings", id="settings_page", classes="nav_sidebar_button"),
                classes="nav_sidebar",
                name="nav_sidebar_name",
                id="nav_sidebar_id"
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
        if event.button.id == "wallet_page":
            self.app.switch_screen(wallet_page())
        elif event.button.id == "organization_page":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page":
            self.app.switch_screen(services_page())
        elif event.button.id == "settings_page":
            self.app.switch_screen(settings_page())

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
        if event.button.id == "wallet_page":
            self.app.switch_screen(wallet_page())
        elif event.button.id == "organization_page":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page":
            self.app.switch_screen(services_page())
        elif event.button.id == "settings_page":
            self.app.switch_screen(settings_page())

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
        if event.button.id == "wallet_page":
            self.app.switch_screen(wallet_page())
        elif event.button.id == "organization_page":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page":
            self.app.switch_screen(services_page())
        elif event.button.id == "settings_page":
            self.app.switch_screen(settings_page())

class settings_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            nav_sidebar_vert(),
            Grid(
                Label("Settings Page", id="settings_page_title"),
                id="settings_page_content"
            ),
            id="settings_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "wallet_page":
            self.app.switch_screen(wallet_page())
        elif event.button.id == "organization_page":
            self.app.switch_screen(organization_page())
        elif event.button.id == "services_page":
            self.app.switch_screen(services_page())
        elif event.button.id == "settings_page":
            self.app.switch_screen(settings_page())

class Singularity_Net_TUI(App):

    CSS_PATH = "style.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        self.push_screen(WelcomeScreen())