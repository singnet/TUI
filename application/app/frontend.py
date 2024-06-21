from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical, Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Header, Label, Input, Select, RadioButton, RichLog, Log, RadioSet
from rich_pixels import Pixels, FullcellRenderer
import back.backend as be
import sys
import os

# Unstable build v0.1.0
# Global variables for passing parameters between screens, as textual does not support this
error_exit_label: str
popup_output: str
conditional_output: str
conditional_command: str
load_screen_redirect: str

class WelcomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Grid(
                Label("Welcome to the SingularityNET TUI", id="welcome_label_1"),
                Label("A simple user interface overlay for the SingularityNET CLI", id="welcome_label_2"),
                Button("Login", id="start_button"),
                id = "welcome_screen_content"
            ),
            id = "welcome_screen"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect
        if event.button.id == "start_button":
            load_screen_redirect = "welcome"
            self.app.push_screen(loading_screen())

class loading_screen(Screen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Grid(
                Label("Loading...", id="loading_page_text"),
                id = "loading_screen_content"
            ),
            id = "loading_screen"
        )
        
    def on_show(self) -> None:
        global load_screen_redirect
        
        if load_screen_redirect == "organization":
            self.app.switch_screen(organization_page())
        elif load_screen_redirect == "account":
            self.app.switch_screen(account_page())
        elif load_screen_redirect == "welcome":
            identity_added, output, errCode = be.identity_check()
            if (identity_added):
                self.app.switch_screen(account_page())
            elif (not identity_added):
                self.app.switch_screen(create_identity_page())
        elif load_screen_redirect == "id_settings":
            self.app.switch_screen(identity_page())
        elif load_screen_redirect == "id_create":
            self.app.switch_screen(create_identity_page())
        elif load_screen_redirect == "account_popup":
            self.app.switch_screen(account_page())
            self.app.push_screen(popup_output_page())

class error_exit_page(Screen):
    def compose(self) -> ComposeResult:
        global error_exit_label
        if error_exit_label:
            yield Log(id="error_exit_log", auto_scroll=False).write(error_exit_label)
        else:
            yield Log(id="error_exit_log", auto_scroll=False).write("ERROR: Internal error, attempted to create popup without context")
        yield Button("Exit", id="error_exit_button")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "error_exit_button":
            self.app.exit()

class popup_output_page(Screen):
    def compose(self) -> ComposeResult:
        global popup_output
        if popup_output:
            yield Log(id="popup_output_log", auto_scroll=False).write(popup_output)
        else:
            yield Log(id="popup_output_log", auto_scroll=False).write("ERROR: Internal error, attempted to create popup without context.\nIf you are running a custom command, the CLI returned an empty string.")
        yield Button("OK", id="output_exit_button")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "output_exit_button":
            self.app.pop_screen()

class conditional_input_page(Screen):
    def compose(self) -> ComposeResult:
        global conditional_output
        global conditional_command
        global popup_output
        yield Log(id="conditional_input_log", auto_scroll=False).write(conditional_output)
        yield Horizontal(Button("Yes", id="conditional_input_accept_button"), Button("No", id="conditional_input_deny_button"), id="conditional_input_buttons")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global conditional_output
        global conditional_command
        global popup_output
        if event.button.id == "conditional_input_accept_button":
            output, errCode = be.run_shell_command(command=f"{conditional_command} --yes")
            popup_output = output
            self.app.switch_screen(popup_output_page())
        elif event.button.id == "conditional_input_deny_button":
            self.app.pop_screen()

class create_identity_page(Screen):
    def compose(self) -> ComposeResult:
        global error_exit_label
        network_list, errCode = be.network_list()
        img = Pixels.from_image_path("application/app/assets/snet_logo.png", renderer=FullcellRenderer(), resize=(32, 45))
        if errCode == 0:
            yield ScrollableContainer(
                Horizontal(
                    RichLog(id="create_identity_page_left_block").write(img, expand=True),
                    Vertical(
                        Label("Get started with the TUI", id="create_identity_page_info_label_1"),
                        Label("Fill in all the fields and connect your Web3 account", id="create_identity_page_info_label_2"),
                        Horizontal(
                            Label("Identity", id="create_identity_page_name_label"),
                            Input(placeholder="Identity Name", id="org_identity_input"),
                            id="create_identity_name_div",
                            classes="create_identity_div"
                        ),
                        Horizontal(
                            Label("Wallet Key", id="create_identity_page_wallet_label"),
                            Input(placeholder="Private Key", id="wallet_info_input", password=True),
                            id="create_identity_key_div",
                            classes="create_identity_div"
                        ),
                        Horizontal(
                            Label("Network", id="create_identity_page_network_label"),
                            Select(options=((line, line) for line in network_list), prompt="Select Network", id="network_select"),
                            id="create_identity_network_div",
                            classes="create_identity_div"
                        ),
                        Horizontal(
                            Button("Back", id="create_identity_back_button"),
                            Button("Create Identity", id="create_identity_button"),
                            id="create_identity_button_div",
                            classes="create_identity_div"
                        ),
                        id="create_identity_right_div",
                        classes="create_identity_right_div_class"
                    ),
                    id="create_identity_outer_div"
                ),
                id="create_identity",
                classes="create_identity_full_page"
            )
        else:
            error_exit_label = "ERROR: Could not find network list, please check CLI installation and run the command 'snet network list'"
            self.app.switch_screen(error_exit_page())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        if event.button.id == "create_identity_button":
            id_name = self.get_child_by_id("create_identity").get_child_by_id("create_identity_outer_div").get_child_by_id("create_identity_right_div").get_child_by_id("create_identity_name_div").get_child_by_id("org_identity_input").value
            network = self.get_child_by_id("create_identity").get_child_by_id("create_identity_outer_div").get_child_by_id("create_identity_right_div").get_child_by_id("create_identity_network_div").get_child_by_id("network_select").value
            wallet_info = self.get_child_by_id("create_identity").get_child_by_id("create_identity_outer_div").get_child_by_id("create_identity_right_div").get_child_by_id("create_identity_key_div").get_child_by_id("wallet_info_input").value
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
                self.create_identity(id_name, False, wallet_info, network)
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
        global error_exit_label
        wallet_dict, errCode = be.wallet_dict_create()
        log_output = f"Account: {wallet_dict['account']}\nETH: {wallet_dict['ETH']}\nAGIX: {wallet_dict['AGIX']}\nMPE: {wallet_dict['MPE']}"
        if errCode == 0:
            yield Header()
            yield Horizontal(
                be.nav_sidebar_vert("account"),
                ScrollableContainer(
                    Label("Account Page", id="account_page_title"),
                    Label("Account Info:", id="account_page_info_label"),
                    Label(log_output, id="account_page_info_log"),
                    Horizontal(
                        Button("Deposit", id="account_page_deposit_button"),
                        Button("Withdraw", id="account_page_withdraw_button"),
                        Button("Transfer", id="account_page_transfer_button"),
                        id="account_page_top_button_div",
                        classes="account_page_button_div"
                    ),
                    Horizontal(
                        Button("Treasurer", id="account_treasurer_button"),
                        Button("Identity Settings", id="account_page_identity_settings_button"),
                        id="account_page_bottom_button_div",
                        classes="account_page_button_div"
                    ),
                    id="account_page_content",
                    classes="content_page"
                ),
                id="account_page"
            )
        else:
            error_exit_label = "ERROR: Could not retrieve account information, please ensure you have created an identity and can access it through the CLI"
            self.app.push_screen(error_exit_page())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "account_page_identity_settings_button":
            load_screen_redirect = "id_settings"
            self.app.switch_screen(loading_screen())
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
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("account"),
            ScrollableContainer(
                Label("Treasurer Page", id="treasurer_page_title"),
                Horizontal(
                    Button("Claim", id="treasurer_claim_button"),
                    Button("Claim Expired", id="treasurer_claim_exp_button"),
                    id="treasurer_upper_button_div",
                    classes="treasurer_button_div"
                ),
                Horizontal(
                    Button("Claim All", id="treasurer_claim_all_button"),
                    id="treasurer_lower_button_div",
                    classes="treasurer_button_div"
                ),
                Button("Back", id="treasurer_back_button"),
                id="treasurer_page_content",
                classes="content_page"
            ),
            id="treasurer_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "treasurer_back_button":
            load_screen_redirect = "account"
            self.app.push_screen(loading_screen())
        elif event.button.id == "treasurer_claim_button":
            self.app.push_screen(treasurer_claim_page())
        elif event.button.id == "treasurer_claim_exp_button":
            self.app.push_screen(treasurer_claim_expr_page())
        elif event.button.id == "treasurer_claim_all_button":
            self.app.push_screen(treasurer_claim_all_page())


class treasurer_claim_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("account"),
            ScrollableContainer(
                Label("Payment Claim Page", id="treasurer_claim_page_title"),
                Horizontal(
                    Label("Channels to claim", id="treasurer_claim_channels_label", classes="treasurer_claim_page_label"),
                    Input(placeholder="Channels to claim", id="treasurer_claim_channels_input", classes="treasurer_claim_page_input"),
                    id="treasurer_claim_channels_div",
                    classes="treasurer_claim_page_div"
                ),
                Horizontal(
                    Label("Daemon Endpoint", id="treasurer_claim_endpoint_label", classes="treasurer_claim_page_label"),
                    Input(placeholder="Daemon Endpoint", id="treasurer_claim_endpoint_input", classes="treasurer_claim_page_input"),
                    id="treasurer_claim_endpoint_div",
                    classes="treasurer_claim_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="treasurer_claim_gas_label", classes="treasurer_claim_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="treasurer_claim_gas_input", classes="treasurer_claim_page_input"),
                    id="treasurer_claim_gas_div",
                    classes="treasurer_claim_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="treasurer_claim_index_label", classes="treasurer_claim_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="treasurer_claim_index_input", classes="treasurer_claim_page_input"),
                    id="treasurer_claim_index_div",
                    classes="treasurer_claim_page_div"
                ),
                RadioSet(
                    RadioButton(label="Quiet transaction printing", id="treasurer_claim_quiet_radio", classes="treasurer_claim_page_radio"),
                    RadioButton(label="Verbose transaction printing", id="treasurer_claim_verbose_radio", classes="treasurer_claim_page_radio"),
                    id="treasurer_claim_radio_set"
                ),
                Horizontal(
                    Button("Back", id="treasurer_claim_back_button"),
                    Button("Claim", id="treasurer_claim_confirm_button"),
                    id="treasurer_claim_page_button_div",
                    classes="treasurer_claim_page_div"
                ),
                id="treasurer_claim_page_content",
                classes="content_page"
            ),
            id="treasurer_claim_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "treasurer_claim_back_button":
            self.app.switch_screen(treasurer_page())
        elif event.button.id == "treasurer_claim_confirm_button":
            channels = self.get_child_by_id("treasurer_claim_page").get_child_by_id("treasurer_claim_page_content").get_child_by_id("treasurer_claim_channels_div").get_child_by_id("treasurer_claim_channels_input").value
            endpoint = self.get_child_by_id("treasurer_claim_page").get_child_by_id("treasurer_claim_page_content").get_child_by_id("treasurer_claim_endpoint_div").get_child_by_id("treasurer_claim_endpoint_input").value
            gas_price = self.get_child_by_id("treasurer_claim_page").get_child_by_id("treasurer_claim_page_content").get_child_by_id("treasurer_claim_gas_div").get_child_by_id("treasurer_claim_gas_input").value
            wallet_index = self.get_child_by_id("treasurer_claim_page").get_child_by_id("treasurer_claim_page_content").get_child_by_id("treasurer_claim_index_div").get_child_by_id("treasurer_claim_index_input").value
            quiet = self.get_child_by_id("treasurer_claim_page").get_child_by_id("treasurer_claim_page_content").get_child_by_id("treasurer_claim_radio_set").get_child_by_id("treasurer_claim_quiet_radio").value
            verbose = self.get_child_by_id("treasurer_claim_page").get_child_by_id("treasurer_claim_page_content").get_child_by_id("treasurer_claim_radio_set").get_child_by_id("treasurer_claim_verbose_radio").value

            output, errCode = be.treasurer_claim(channels, endpoint, gas_price, wallet_index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class treasurer_claim_all_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("account"),
            ScrollableContainer(
                Label("Claim All Payments Page", id="treasurer_claim_all_page_title"),
                Horizontal(
                    Label("Daemon Endpoint", id="treasurer_claim_all_endpoint_label", classes="treasurer_claim_all_page_label"),
                    Input(placeholder="Daemon Endpoint", id="treasurer_claim_all_endpoint_input", classes="treasurer_claim_all_page_input"),
                    id="treasurer_claim_all_endpoint_div",
                    classes="treasurer_claim_all_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="treasurer_claim_all_gas_label", classes="treasurer_claim_all_page_label"),
                    Input(placeholder="[OPTIONAL] In Wei or time based gas price strategy (defaults to session.default_gas_price)", id="treasurer_claim_all_gas_input", classes="treasurer_claim_all_page_input"),
                    id="treasurer_claim_all_gas_div",
                    classes="treasurer_claim_all_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="treasurer_claim_all_index_label", classes="treasurer_claim_all_page_label"),
                    Input(placeholder="[OPTIONAL] Account to use for signing (defaults to session.identity.default_wallet_index)", id="treasurer_claim_all_index_input", classes="treasurer_claim_all_page_input"),
                    id="treasurer_claim_all_index_div",
                    classes="treasurer_claim_all_page_div"
                ),
                RadioSet(
                    RadioButton(label="Quiet transaction printing", id="treasurer_claim_all_quiet_radio", classes="treasurer_claim_all_page_radio"),
                    RadioButton(label="Verbose transaction printing", id="treasurer_claim_all_verbose_radio", classes="treasurer_claim_all_page_radio"),
                    id="treasurer_claim_all_radio_set"
                ),
                Horizontal(
                    Button("Back", id="treasurer_claim_all_back_button"),
                    Button("Claim", id="treasurer_claim_all_confirm_button"),
                    id="treasurer_claim_all_page_button_div",
                    classes="treasurer_claim_all_page_div"
                ),
                id="treasurer_claim_all_page_content",
                classes="content_page"
            ),
            id="treasurer_claim_all_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "treasurer_claim_all_back_button":
            self.app.switch_screen(treasurer_page())
        elif event.button.id == "treasurer_claim_all_confirm_button":
            endpoint = self.get_child_by_id("treasurer_claim_all_page").get_child_by_id("treasurer_claim_all_page_content").get_child_by_id("treasurer_claim_all_endpoint_div").get_child_by_id("treasurer_claim_all_endpoint_input").value
            gas_price = self.get_child_by_id("treasurer_claim_all_page").get_child_by_id("treasurer_claim_all_page_content").get_child_by_id("treasurer_claim_all_gas_div").get_child_by_id("treasurer_claim_all_gas_input").value
            wallet_index = self.get_child_by_id("treasurer_claim_all_page").get_child_by_id("treasurer_claim_all_page_content").get_child_by_id("treasurer_claim_all_index_div").get_child_by_id("treasurer_claim_all_index_input").value
            quiet = self.get_child_by_id("treasurer_claim_all_page").get_child_by_id("treasurer_claim_all_page_content").get_child_by_id("treasurer_claim_all_radio_set").get_child_by_id("treasurer_claim_all_quiet_radio").value
            verbose = self.get_child_by_id("treasurer_claim_all_page").get_child_by_id("treasurer_claim_all_page_content").get_child_by_id("treasurer_claim_all_radio_set").get_child_by_id("treasurer_claim_all_verbose_radio").value

            output, errCode = be.treasurer_claim_all(endpoint, gas_price, wallet_index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class treasurer_claim_expr_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("account"),
            ScrollableContainer(
                Label("Claim expired payments Page", id="treasurer_claim_expr_page_title"),
                Horizontal(
                    Label("Daemon Endpoint", id="treasurer_claim_expr_endpoint_label", classes="treasurer_claim_expr_page_label"),
                    Input(placeholder="Daemon Endpoint", id="treasurer_claim_expr_endpoint_input", classes="treasurer_claim_expr_page_input"),
                    id="treasurer_claim_expr_endpoint_div",
                    classes="treasurer_claim_expr_page_div"
                ),
                Horizontal(
                    Label("Expir. Threshold", id="treasurer_claim_expr_threshold_label", classes="treasurer_claim_expr_page_label"),
                    Input(placeholder="[OPTIONAL] Service expiration threshold in blocks (default is 34560 ~ 6 days with 15s/block)", id="treasurer_claim_expr_threshold_input", classes="treasurer_claim_expr_page_input"),
                    id="treasurer_claim_expr_threshold_div",
                    classes="treasurer_claim_expr_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="treasurer_claim_expr_gas_label", classes="treasurer_claim_expr_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="treasurer_claim_expr_gas_input", classes="treasurer_claim_expr_page_input"),
                    id="treasurer_claim_expr_gas_div",
                    classes="treasurer_claim_expr_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="treasurer_claim_expr_index_label", classes="treasurer_claim_expr_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="treasurer_claim_expr_index_input", classes="treasurer_claim_expr_page_input"),
                    id="treasurer_claim_expr_index_div",
                    classes="treasurer_claim_expr_page_div"
                ),
                RadioSet(
                    RadioButton(label="Quiet transaction printing", id="treasurer_claim_expr_quiet_radio", classes="treasurer_claim_expr_page_radio"),
                    RadioButton(label="Verbose transaction printing", id="treasurer_claim_expr_verbose_radio", classes="treasurer_claim_expr_page_radio"),
                    id="treasurer_claim_expr_radio_set"
                ),
                Horizontal(
                    Button("Back", id="treasurer_claim_expr_back_button"),
                    Button("Claim", id="treasurer_claim_expr_confirm_button"),
                    id="treasurer_claim_expr_page_button_div",
                    classes="treasurer_claim_expr_page_div"
                ),
                id="treasurer_claim_expr_page_content",
                classes="content_page"
            ),
            id="treasurer_claim_expr_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "treasurer_claim_expr_back_button":
            self.app.switch_screen(treasurer_page())
        elif event.button.id == "treasurer_claim_expr_confirm_button":
            threshold = self.get_child_by_id("treasurer_claim_expr_page").get_child_by_id("treasurer_claim_expr_page_content").get_child_by_id("treasurer_claim_expr_threshold_div").get_child_by_id("treasurer_claim_expr_threshold_input").value
            endpoint = self.get_child_by_id("treasurer_claim_expr_page").get_child_by_id("treasurer_claim_expr_page_content").get_child_by_id("treasurer_claim_expr_endpoint_div").get_child_by_id("treasurer_claim_expr_endpoint_input").value
            gas_price = self.get_child_by_id("treasurer_claim_expr_page").get_child_by_id("treasurer_claim_expr_page_content").get_child_by_id("treasurer_claim_expr_gas_div").get_child_by_id("treasurer_claim_expr_gas_input").value
            wallet_index = self.get_child_by_id("treasurer_claim_expr_page").get_child_by_id("treasurer_claim_expr_page_content").get_child_by_id("treasurer_claim_expr_index_div").get_child_by_id("treasurer_claim_expr_index_input").value
            quiet = self.get_child_by_id("treasurer_claim_expr_page").get_child_by_id("treasurer_claim_expr_page_content").get_child_by_id("treasurer_claim_expr_radio_set").get_child_by_id("treasurer_claim_expr_quiet_radio").value
            verbose = self.get_child_by_id("treasurer_claim_expr_page").get_child_by_id("treasurer_claim_expr_page_content").get_child_by_id("treasurer_claim_expr_radio_set").get_child_by_id("treasurer_claim_expr_verbose_radio").value

            output, errCode = be.treasurer_claim_expr(threshold, endpoint, gas_price, wallet_index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class identity_page(Screen):
    def compose(self) -> ComposeResult:
        idList, listErrCode = be.run_shell_command("snet identity list")
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("account"),
            ScrollableContainer(
                Label("Identity Page", id="identity_page_title"),
                Label("Identity Info Section:", id="identity_page_log_label"),
                Log(id="identity_page_log", auto_scroll=False).write(f"Identity List:\n\n{idList}"),
                Button("Create Identity Page", id="identity_page_create_identity_button"),
                Label("Identity Delete Section:", id="identity_page_delete_label"),
                Input(placeholder="Identity name to delete", id="identity_page_delete_input"),
                Button("Delete Identity", id="identity_page_delete_identity_button"),
                Button("Back", id="identity_page_back_button"),
                id="identity_page_content",
                classes="content_page"
            ),
            id="identity_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "identity_page_create_identity_button":
            load_screen_redirect = "id_create"
            self.app.push_screen(loading_screen())
        elif event.button.id == "identity_page_back_button":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
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
            be.nav_sidebar_vert("account"),
            ScrollableContainer(
                Label("Deposit AGI Tokens", id="account_deposit_page_title"),
                Horizontal(
                    Label("Amount to Deposit", id="account_deposit_amount_label", classes="account_deposit_page_label"),
                    Input(placeholder="Amount of AGI tokens to deposit in MPE wallet", id="account_deposit_amount_input", classes="account_deposit_page_input"),
                    id="account_deposit_amount_div",
                    classes="account_deposit_page_div"
                ),
                Horizontal(
                    Label("Token Address", id="account_deposit_contract_label", classes="account_deposit_page_label"),
                    Input(placeholder="[OPTIONAL] Address of SingularityNetToken contract, if not specified we read address from 'networks'", id="account_deposit_contract_input", classes="account_deposit_page_input"),
                    id="account_deposit_contract_div",
                    classes="account_deposit_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="account_deposit_mpe_label", classes="account_deposit_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from 'networks'", id="account_deposit_mpe_input", classes="account_deposit_page_input"),
                    id="account_deposit_mpe_div",
                    classes="account_deposit_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="account_deposit_gas_label", classes="account_deposit_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="account_deposit_gas_input", classes="account_deposit_page_input"),
                    id="account_deposit_gas_div",
                    classes="account_deposit_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="account_deposit_index_label", classes="account_deposit_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="account_deposit_index_input", classes="account_deposit_page_input"),
                    id="account_deposit_index_div",
                    classes="account_deposit_page_div"
                ),
                RadioSet(
                    RadioButton(label="Quiet transaction printing", id="account_deposit_quiet_radio", classes="account_deposit_page_radio"),
                    RadioButton(label="Verbose transaction printing", id="account_deposit_verbose_radio", classes="account_deposit_page_radio"),
                    id="account_deposit_radio_set"
                ),
                Horizontal(
                    Button(label="Back", id="account_deposit_back_button"),
                    Button(label="Deposit", id="account_deposit_confirm_button"),
                    id="account_deposit_button_div",
                    classes="account_deposit_page_div"
                ),
                id="account_deposit_page_content",
                classes="content_page"
            ),
            id="account_deposit_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "account_deposit_back_button":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "account_deposit_confirm_button":
            agi_amount = self.get_child_by_id("account_deposit_page").get_child_by_id("account_deposit_page_content").get_child_by_id("account_deposit_amount_div").get_child_by_id("account_deposit_amount_input").value
            contract_address = self.get_child_by_id("account_deposit_page").get_child_by_id("account_deposit_page_content").get_child_by_id("account_deposit_contract_div").get_child_by_id("account_deposit_contract_input").value
            mpe_address = self.get_child_by_id("account_deposit_page").get_child_by_id("account_deposit_page_content").get_child_by_id("account_deposit_mpe_div").get_child_by_id("account_deposit_mpe_input").value
            gas_price = self.get_child_by_id("account_deposit_page").get_child_by_id("account_deposit_page_content").get_child_by_id("account_deposit_gas_div").get_child_by_id("account_deposit_gas_input").value
            wallet_index = self.get_child_by_id("account_deposit_page").get_child_by_id("account_deposit_page_content").get_child_by_id("account_deposit_index_div").get_child_by_id("account_deposit_index_input").value
            quiet = self.get_child_by_id("account_deposit_page").get_child_by_id("account_deposit_page_content").get_child_by_id("account_deposit_radio_set").get_child_by_id("account_deposit_quiet_radio").value
            verbose = self.get_child_by_id("account_deposit_page").get_child_by_id("account_deposit_page_content").get_child_by_id("account_deposit_radio_set").get_child_by_id("account_deposit_verbose_radio").value

            output, errCode = be.account_deposit(agi_amount, contract_address, mpe_address, gas_price, wallet_index, quiet, verbose)
            popup_output = output
            if errCode == 0:
                self.app.switch_screen(account_page())
            self.app.push_screen(popup_output_page())

class account_withdraw_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("account"),
            ScrollableContainer(
                Label("Withdraw AGI Tokens", id="account_withdraw_page_title"),
                Horizontal(
                    Label("Amount", id="account_withdraw_amount_label", classes="account_withdraw_page_label"),
                    Input(placeholder="Amount of AGI tokens to withdraw from MPE wallet", id="account_withdraw_amount_input", classes="account_withdraw_page_input"),
                    id="account_withdraw_amount_div",
                    classes="account_withdraw_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="account_withdraw_mpe_label", classes="account_withdraw_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from 'networks'", id="account_withdraw_mpe_input", classes="account_withdraw_page_input"),
                    id="account_withdraw_mpe_div",
                    classes="account_withdraw_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="account_withdraw_gas_label", classes="account_withdraw_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="account_withdraw_gas_input", classes="account_withdraw_page_input"),
                    id="account_withdraw_gas_div",
                    classes="account_withdraw_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="account_withdraw_index_label", classes="account_withdraw_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="account_withdraw_index_input", classes="account_withdraw_page_input"),
                    id="account_withdraw_index_div",
                    classes="account_withdraw_page_div"
                ),
                RadioSet(
                    RadioButton(label="Quiet transaction printing", id="account_withdraw_quiet_radio", classes="account_withdraw_page_radio"),
                    RadioButton(label="Verbose transaction printing", id="account_withdraw_verbose_radio", classes="account_withdraw_page_radio"),
                    id="account_withdraw_radio_set"
                ),
                Horizontal(
                    Button(label="Back", id="account_withdraw_back_button"),
                    Button(label="Withdraw", id="account_withdraw_confirm_button"),
                    id="account_withdraw_button_div",
                    classes="account_withdraw_page_div"
                ),
                id="account_withdraw_page_content",
                classes="content_page"
            ),
            id="account_withdraw_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "account_withdraw_back_button":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "account_withdraw_confirm_button":
            agi_amount = self.get_child_by_id("account_withdraw_page").get_child_by_id("account_withdraw_page_content").get_child_by_id("account_withdraw_amount_div").get_child_by_id("account_withdraw_amount_input").value
            mpe_address = self.get_child_by_id("account_withdraw_page").get_child_by_id("account_withdraw_page_content").get_child_by_id("account_withdraw_mpe_div").get_child_by_id("account_withdraw_mpe_input").value
            gas_price = self.get_child_by_id("account_withdraw_page").get_child_by_id("account_withdraw_page_content").get_child_by_id("account_withdraw_gas_div").get_child_by_id("account_withdraw_gas_input").value
            wallet_index = self.get_child_by_id("account_withdraw_page").get_child_by_id("account_withdraw_page_content").get_child_by_id("account_withdraw_index_div").get_child_by_id("account_withdraw_index_input").value
            quiet = self.get_child_by_id("account_withdraw_page").get_child_by_id("account_withdraw_page_content").get_child_by_id("account_withdraw_radio_set").get_child_by_id("account_withdraw_quiet_radio").value
            verbose = self.get_child_by_id("account_withdraw_page").get_child_by_id("account_withdraw_page_content").get_child_by_id("account_withdraw_radio_set").get_child_by_id("account_withdraw_verbose_radio").value

            output, errCode = be.account_withdraw(agi_amount, mpe_address, gas_price, wallet_index, quiet, verbose)
            popup_output = output
            if errCode == 0:
                self.app.switch_screen(account_page())
            self.app.push_screen(popup_output_page())

class account_transfer_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("account"),
            ScrollableContainer(
                Label("Transfer AGI Tokens", id="account_transfer_page_title"),
                Horizontal(
                    Label("Receiver Address", id="account_transfer_addr_label", classes="account_transfer_page_label"),
                    Input(placeholder="Address of the receiver", id="account_transfer_addr_input", classes="account_transfer_page_input"),
                    id="account_transfer_addr_div",
                    classes="account_transfer_page_div"
                ),
                Horizontal(
                    Label("Amount to Transfer", id="account_transfer_amount_label", classes="account_transfer_page_label"),
                    Input(placeholder="Amount of AGI tokens to be transferred to another account inside MPE wallet", id="account_transfer_amount_input", classes="account_transfer_page_input"),
                    id="account_transfer_amount_div",
                    classes="account_transfer_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="account_transfer_mpe_label", classes="account_transfer_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from 'networks'", id="account_transfer_mpe_input", classes="account_transfer_page_input"),
                    id="account_transfer_mpe_div",
                    classes="account_transfer_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="account_transfer_gas_label", classes="account_transfer_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="account_transfer_gas_input", classes="account_transfer_page_input"),
                    id="account_transfer_gas_div",
                    classes="account_transfer_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="account_transfer_index_label", classes="account_transfer_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="account_transfer_index_input", classes="account_transfer_page_input"),
                    id="account_transfer_index_div",
                    classes="account_transfer_page_div"
                ),
                RadioSet(
                    RadioButton(label="Quiet transaction printing", id="account_transfer_quiet_radio", classes="account_transfer_page_radio"),
                    RadioButton(label="Verbose transaction printing", id="account_transfer_verbose_radio", classes="account_transfer_page_radio"),
                    id="account_transfer_radio_set"
                ),
                Horizontal(
                    Button(label="Back", id="account_transfer_back_button"),
                    Button(label="Transfer", id="account_transfer_confirm_button"),
                    id="account_transfer_button_div",
                    classes="account_transfer_page_div"
                ),
                id="account_transfer_page_content",
                classes="content_page"
            ),
            id="account_transfer_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "account_transfer_back_button":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "account_transfer_confirm_button":
            agi_amount = self.get_child_by_id("account_transfer_page").get_child_by_id("account_transfer_page_content").get_child_by_id("account_transfer_amount_div").get_child_by_id("account_transfer_amount_input").value
            reciever_addr = self.get_child_by_id("account_transfer_page").get_child_by_id("account_transfer_page_content").get_child_by_id("account_transfer_addr_div").get_child_by_id("account_transfer_addr_input").value
            mpe_address = self.get_child_by_id("account_transfer_page").get_child_by_id("account_transfer_page_content").get_child_by_id("account_transfer_mpe_div").get_child_by_id("account_transfer_mpe_input").value
            gas_price = self.get_child_by_id("account_transfer_page").get_child_by_id("account_transfer_page_content").get_child_by_id("account_transfer_gas_div").get_child_by_id("account_transfer_gas_input").value
            wallet_index = self.get_child_by_id("account_transfer_page").get_child_by_id("account_transfer_page_content").get_child_by_id("account_transfer_index_div").get_child_by_id("account_transfer_index_input").value
            quiet = self.get_child_by_id("account_transfer_page").get_child_by_id("account_transfer_page_content").get_child_by_id("account_transfer_radio_set").get_child_by_id("account_transfer_quiet_radio").value
            verbose = self.get_child_by_id("account_transfer_page").get_child_by_id("account_transfer_page_content").get_child_by_id("account_transfer_radio_set").get_child_by_id("account_transfer_verbose_radio").value

            output, errCode = be.account_transfer(reciever_addr, agi_amount, mpe_address, gas_price, wallet_index, quiet, verbose)
            popup_output = output
            if errCode == 0:
                self.app.switch_screen(account_page())
            self.app.push_screen(popup_output_page())

class organization_page(Screen):
    def compose(self) -> ComposeResult:
        output, errCode = be.print_organization_info()
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Organization Page", id="organization_page_title"),
                Label("Organization Info:", id="organization_page_log_label"),
                Log(id="org_metadata_info_log", auto_scroll=False).write(f"My Organizations:\n\n{output}"),
                Horizontal(
                    Button(label="Metadata", id="organization_page_metadata_button"),
                    Button(label="Groups", id="organization_page_groups_button"),
                    id="organization_page_top_button_div",
                    classes="organization_page_button_div"
                ),
                Horizontal(
                    Button(label="Members", id="organization_page_members_button"),
                    Button(label="Manage", id="organization_page_create_delete_button"),
                    id="organization_page_bottom_button_div",
                    classes="organization_page_button_div"
                ),
                id="organization_page_content",
                classes="content_page"
            ),
            id="organization_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
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
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Organization Metadata Page", id="org_metadata_page_title"),
                Horizontal(
                    Button(label="Print Metadata", id="org_metadata_page_print_button"),
                    Button(label="Initialize Metadata", id="org_metadata_page_init_button"),
                    Button(label="Add Description", id="org_metadata_add_desc_button"),
                    id="org_metadata_page_upper_div",
                    classes="org_metadata_page_div"
                ),
                Horizontal(
                    Button(label="Manage Assets", id="org_metadata_assets_button"),
                    Button(label="Manage Contacts", id="org_metadata_contacts_button"),
                    Button(label="Update Metadata", id="org_metadata_update_button"),
                    id="org_metadata_page_lower_div",
                    classes="org_metadata_page_div"
                ),
                Button(label="Back", id="org_metadata_back_button"),
                id="org_metadata_page_content",
                classes="content_page"
            ),
            id="org_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "org_metadata_back_button":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
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
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Organization Metadata Page", id="print_org_metadata_page_title"),
                Horizontal(
                    Label("Organization ID", id="print_org_metadata_id_label", classes="print_org_metadata_page_label"),
                    Input(placeholder="Organization ID", id="print_org_metadata_id_input", classes="print_org_metadata_page_input"),
                    id="print_org_metadata_page_id_div",
                    classes="print_org_metadata_page_div"
                ),
                Horizontal(
                    Button(label="Back", id="print_org_metadata_back_button"),
                    Button(label="View Metadata", id="print_org_metadata_confirm_button"),
                    id="print_org_metadata_page_button_div",
                    classes="print_org_metadata_page_div"
                ),
                id="print_org_metadata_page_content",
                classes="content_page"
            ),
            id="print_org_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "print_org_metadata_confirm_button":
            org_id = self.get_child_by_id("print_org_metadata_page").get_child_by_id("print_org_metadata_page_content").get_child_by_id("print_org_metadata_page_id_div").get_child_by_id("print_org_metadata_id_input").value
            output, errCode = be.print_org_metadata(org_id)
            popup_output = output
            self.app.push_screen(popup_output_page())
        elif event.button.id == "print_org_metadata_back_button":
            self.app.pop_screen()

class init_org_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Initialize Metadata Page", id="init_org_metadata_page_title"),
                Horizontal(
                    Label("Organization Name", id="init_org_metadata_name_label", classes="init_org_metadata_page_label"),
                    Input(placeholder="Input Organization name (The one you defined during the ETCD setup)", id="init_org_metadata_name_input", classes="init_org_metadata_page_input"),
                    id="init_org_metadata_page_name_div",
                    classes="init_org_metadata_page_div"
                ),
                Horizontal(
                    Label("Organization ID", id="init_org_metadata_id_label", classes="init_org_metadata_page_label"),
                    Input(placeholder="Define your unique organization ID (You must reuse this in your Daemon configuration)", id="init_org_metadata_id_input", classes="init_org_metadata_page_input"),
                    id="init_org_metadata_page_id_div",
                    classes="init_org_metadata_page_div"
                ),
                Horizontal(
                    Label("Metadata Path", id="init_org_metadata_meta_path_label", classes="init_org_metadata_page_label"),
                    Input(placeholder="[OPTIONAL] Service metadata json file (default organization_metadata.json)", id="init_org_metadata_meta_path_input", classes="init_org_metadata_page_input"),
                    id="init_org_metadata_page_meta_path_div",
                    classes="init_org_metadata_page_div"
                ),
                Horizontal(
                    Label("Registry Address", id="init_org_metadata_registry_label", classes="init_org_metadata_page_label"),
                    Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from 'networks'", id="init_org_metadata_registry_input", classes="init_org_metadata_page_input"),
                    id="init_org_metadata_page_registry_div",
                    classes="init_org_metadata_page_div"
                ),
                Horizontal(
                    Label("Organization Type", id="init_org_metadata_type_label", classes="init_org_metadata_page_label"),
                    Select(options=((line, line) for line in """Individual\nOrganization""".splitlines()), prompt="Select Organization Type", id="init_org_metadata_type_select", classes="init_org_metadata_page_input"),
                    id="init_org_metadata_page_type_div",
                    classes="init_org_metadata_page_div"
                ),
                Horizontal(
                    Button(label="Back", id="init_org_metadata_back_button"),
                    Button(label="Initialize", id="init_org_metadata_confirm_button"),
                    id="init_org_metadata_page_button_div",
                    classes="init_org_metadata_page_div"
                ),
                id="init_org_metadata_page_content",
                classes="content_page"
            ),
            id="init_org_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "init_org_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "init_org_metadata_confirm_button":
            org_name = self.get_child_by_id("init_org_metadata_page").get_child_by_id("init_org_metadata_page_content").get_child_by_id("init_org_metadata_page_name_div").get_child_by_id("init_org_metadata_name_input").value
            org_id = self.get_child_by_id("init_org_metadata_page").get_child_by_id("init_org_metadata_page_content").get_child_by_id("init_org_metadata_page_id_div").get_child_by_id("init_org_metadata_id_input").value
            meta_file = self.get_child_by_id("init_org_metadata_page").get_child_by_id("init_org_metadata_page_content").get_child_by_id("init_org_metadata_page_meta_path_div").get_child_by_id("init_org_metadata_meta_path_input").value
            reg_addr = self.get_child_by_id("init_org_metadata_page").get_child_by_id("init_org_metadata_page_content").get_child_by_id("init_org_metadata_page_registry_div").get_child_by_id("init_org_metadata_registry_input").value
            org_type = self.get_child_by_id("init_org_metadata_page").get_child_by_id("init_org_metadata_page_content").get_child_by_id("init_org_metadata_page_type_div").get_child_by_id("init_org_metadata_type_select").value

            output, errCode = be.init_org_metadata(org_name, org_id, org_type, reg_addr, meta_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class add_org_metadata_desc_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Add Metadata Description Page", id="add_org_metadata_desc_title"),
                Horizontal(
                    Label("Long Description", id="add_org_metadata_desc_long_label", classes="add_org_metadata_desc_page_label"),
                    Input(placeholder="Description about organization", id="add_org_metadata_desc_long_input", classes="add_org_metadata_desc_page_input"),
                    id="add_org_metadata_desc_long_div",
                    classes="add_org_metadata_desc_page_div"
                ),
                Horizontal(
                    Label("Short Description", id="add_org_metadata_desc_short_label", classes="add_org_metadata_desc_page_label"),
                    Input(placeholder="Short description about organization", id="add_org_metadata_desc_short_input", classes="add_org_metadata_desc_page_input"),
                    id="add_org_metadata_desc_short_div",
                    classes="add_org_metadata_desc_page_div"
                ),
                Horizontal(
                    Label("Organization URL", id="add_org_metadata_desc_url_label", classes="add_org_metadata_desc_page_label"),
                    Input(placeholder="URL for Organization", id="add_org_metadata_desc_url_input", classes="add_org_metadata_desc_page_input"),
                    id="add_org_metadata_desc_url_div",
                    classes="add_org_metadata_desc_page_div"
                ),
                Horizontal(
                    Label("Metadata File Path", id="add_org_metadata_desc_path_label", classes="add_org_metadata_desc_page_label"),
                    Input(placeholder="[OPTIONAL] Service metadata json file name (default service_metadata.json)", id="add_org_metadata_desc_path_input", classes="add_org_metadata_desc_page_input"),
                    id="add_org_metadata_desc_path_div",
                    classes="add_org_metadata_desc_page_div"
                ),
                Horizontal(
                    Button(label="Back", id="add_org_metadata_desc_back_button"),
                    Button(label="Add Description", id="add_org_metadata_desc_confirm_button"),
                    id="add_org_metadata_desc_button_div",
                    classes="add_org_metadata_desc_page_div"
                ),
                id="add_org_metadata_desc_page_content",
                classes="content_page"
            ),
            id="add_org_metadata_desc_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "add_org_metadata_desc_back_button":
            self.app.pop_screen()
        elif event.button.id == "add_org_metadata_desc_confirm_button":
            long_desc = self.get_child_by_id("add_org_metadata_desc_page").get_child_by_id("add_org_metadata_desc_page_content").get_child_by_id("add_org_metadata_desc_long_div").get_child_by_id("add_org_metadata_desc_long_input").value
            short_desc = self.get_child_by_id("add_org_metadata_desc_page").get_child_by_id("add_org_metadata_desc_page_content").get_child_by_id("add_org_metadata_desc_short_div").get_child_by_id("add_org_metadata_desc_short_input").value
            url = self.get_child_by_id("add_org_metadata_desc_page").get_child_by_id("add_org_metadata_desc_page_content").get_child_by_id("add_org_metadata_desc_url_div").get_child_by_id("add_org_metadata_desc_url_input").value
            meta_path = self.get_child_by_id("add_org_metadata_desc_page").get_child_by_id("add_org_metadata_desc_page_content").get_child_by_id("add_org_metadata_desc_path_div").get_child_by_id("add_org_metadata_desc_path_input").value

            output, errCode = be.add_org_metadata_desc(long_desc, short_desc, url, meta_path)
            popup_output = output
            self.app.push_screen(popup_output_page())

class manage_org_assets_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Manage Assets Page", id="manage_org_assets_title"),
                Horizontal(
                    Label("Hero Image Path", id="manage_org_assets_path_label", classes="manage_org_assets_page_label"),
                    Input(placeholder="Hero_image Asset File Path", id="manage_org_assets_path_input", classes="manage_org_assets_page_input"),
                    id="manage_org_assets_path_div",
                    classes="manage_org_assets_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="manage_org_assets_meta_label", classes="manage_org_assets_page_label"),
                    Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json) Default: 'organization_metadata.json'", id="manage_org_assets_meta_input", classes="manage_org_assets_page_input"),
                    id="manage_org_assets_meta_div",
                    classes="manage_org_assets_page_div"
                ),
                Horizontal(
                    Button(label="Remove ALL Assets", id="manage_org_assets_remove_button"),
                    Button(label="Add Asset", id="manage_org_assets_confirm_button"),
                    id="manage_org_assets_button_div",
                    classes="manage_org_assets_page_div"
                ),
                Button(label="Back", id="manage_org_assets_back_button"),
                id="manage_org_assets_page_content",
                classes="content_page"
            ),
            id="manage_org_assets_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        asset_file_path = self.get_child_by_id("manage_org_assets_page").get_child_by_id("manage_org_assets_page_content").get_child_by_id("manage_org_assets_path_div").get_child_by_id("manage_org_assets_path_input").value
        metadata_file_name = self.get_child_by_id("manage_org_assets_page").get_child_by_id("manage_org_assets_page_content").get_child_by_id("manage_org_assets_meta_div").get_child_by_id("manage_org_assets_meta_input").value

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
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
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Manage Contacts Page", id="manage_org_contacts_page_title"),
                Horizontal(
                    Label("Contact Type", id="manage_org_contacts_type_label", classes="manage_org_contacts_page_label"),
                    Input(placeholder="Contact type of organization", id="manage_org_contacts_type_input", classes="manage_org_contacts_page_input"),
                    id="manage_org_contacts_type_div",
                    classes="manage_org_contacts_page_div"
                ),
                Horizontal(
                    Label("Phone Number", id="manage_org_contacts_phone_label", classes="manage_org_contacts_page_label"),
                    Input(placeholder="[Technically OPTIONAL] Phone number for contact with country code", id="manage_org_contacts_phone_input", classes="manage_org_contacts_page_input"),
                    id="manage_org_contacts_phone_div",
                    classes="manage_org_contacts_page_div"
                ),
                Horizontal(
                    Label("Email ID", id="manage_org_contacts_email_label", classes="manage_org_contacts_page_label"),
                    Input(placeholder="[Technically OPTIONAL] Email ID for contact", id="manage_org_contacts_email_input", classes="manage_org_contacts_page_input"),
                    id="manage_org_contacts_email_div",
                    classes="manage_org_contacts_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="manage_org_contacts_meta_label", classes="manage_org_contacts_page_label"),
                    Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json) Default: 'organization_metadata.json'", id="manage_org_contacts_meta_input", classes="manage_org_contacts_page_input"),
                    id="manage_org_contacts_meta_div",
                    classes="manage_org_contacts_page_div"
                ),
                Horizontal(
                    Button(label="Remove all contacts", id="manage_org_contacts_remove_button"),
                    Button(label="Add contact", id="manage_org_contacts_confirm_button"),
                    id="manage_org_contacts_button_div",
                    classes="manage_org_contacts_page_div"
                ),
                Button(label="Back", id="manage_org_contacts_back_button"),
                id="manage_org_contacts_page_content",
                classes="content_page"
            ),
            id="manage_org_contacts_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        contact_type = self.get_child_by_id("manage_org_contacts_page").get_child_by_id("manage_org_contacts_page_content").get_child_by_id("manage_org_contacts_type_div").get_child_by_id("manage_org_contacts_type_input").value
        phone = self.get_child_by_id("manage_org_contacts_page").get_child_by_id("manage_org_contacts_page_content").get_child_by_id("manage_org_contacts_phone_div").get_child_by_id("manage_org_contacts_phone_input").value
        email = self.get_child_by_id("manage_org_contacts_page").get_child_by_id("manage_org_contacts_page_content").get_child_by_id("manage_org_contacts_email_div").get_child_by_id("manage_org_contacts_email_input").value
        metadata_file = self.get_child_by_id("manage_org_contacts_page").get_child_by_id("manage_org_contacts_page_content").get_child_by_id("manage_org_contacts_meta_div").get_child_by_id("manage_org_contacts_meta_input").value

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen()) 
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen()) 
        elif event.button.id == "services_page_nav": 
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
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
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Update Metadata Page", id="update_org_metadata_page_title"),
                Horizontal(
                    Label("Organization ID", id="update_org_metadata_id_label", classes="update_org_metadata_page_label"),
                    Input(placeholder="Your Organization ID", id="update_org_metadata_id_input", classes="update_org_metadata_page_input"),
                    id="update_org_metadata_id_div",
                    classes="update_org_metadata_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="update_org_metadata_file_label", classes="update_org_metadata_page_label"),
                    Input(placeholder="Service metadata json file (default service_metadata.json) Default: 'organization_metadata.json'", id="update_org_metadata_file_input", classes="update_org_metadata_page_input"),
                    id="update_org_metadata_file_div",
                    classes="update_org_metadata_page_div"
                ),
                Horizontal(
                    Label("Members List", id="update_org_metadata_mems_label", classes="update_org_metadata_page_label"),
                    Input(placeholder="[OPTIONAL] List of members to be added to the organization", id="update_org_metadata_mems_input", classes="update_org_metadata_page_input"),
                    id="update_org_metadata_mems_div",
                    classes="update_org_metadata_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="update_org_metadata_gas_label", classes="update_org_metadata_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="update_org_metadata_gas_input", classes="update_org_metadata_page_input"),
                    id="update_org_metadata_gas_div",
                    classes="update_org_metadata_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="update_org_metadata_index_label", classes="update_org_metadata_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="update_org_metadata_index_input", classes="update_org_metadata_page_input"),
                    id="update_org_metadata_index_div",
                    classes="update_org_metadata_page_div"
                ),
                RadioSet(
                    RadioButton(label="Quiet transaction printing", id="update_org_metadata_quiet_radio", classes="update_org_metadata_page_radio"),
                    RadioButton(label="Verbose transaction printing", id="update_org_metadata_verbose_radio", classes="update_org_metadata_page_radio"),
                    id="update_org_metadata_radio_set"
                ),
                Horizontal(
                    Button(label="Back", id="update_org_metadata_back_button"),
                    Button(label="Update Metadata on Blockchain", id="update_org_metadata_confirm_button"),
                    id="update_org_metadata_page_button_div",
                    classes="update_org_metadata_page_div"
                ),
                id="update_org_metadata_page_content",
                classes="content_page"
            ),
            id="update_org_metadata_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "update_org_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "update_org_metadata_confirm_button":
            org_id = self.get_child_by_id("update_org_metadata_page").get_child_by_id("update_org_metadata_page_content").get_child_by_id("update_org_metadata_id_div").get_child_by_id("update_org_metadata_id_input").value
            file_name = self.get_child_by_id("update_org_metadata_page").get_child_by_id("update_org_metadata_page_content").get_child_by_id("update_org_metadata_file_div").get_child_by_id("update_org_metadata_file_input").value
            mem_list = self.get_child_by_id("update_org_metadata_page").get_child_by_id("update_org_metadata_page_content").get_child_by_id("update_org_metadata_mems_div").get_child_by_id("update_org_metadata_mems_input").value
            gas = self.get_child_by_id("update_org_metadata_page").get_child_by_id("update_org_metadata_page_content").get_child_by_id("update_org_metadata_gas_div").get_child_by_id("update_org_metadata_gas_input").value
            index = self.get_child_by_id("update_org_metadata_page").get_child_by_id("update_org_metadata_page_content").get_child_by_id("update_org_metadata_index_div").get_child_by_id("update_org_metadata_index_input").value
            quiet = self.get_child_by_id("update_org_metadata_page").get_child_by_id("update_org_metadata_page_content").get_child_by_id("update_org_metadata_radio_set").get_child_by_id("update_org_metadata_quiet_radio").value
            verbose = self.get_child_by_id("update_org_metadata_page").get_child_by_id("update_org_metadata_page_content").get_child_by_id("update_org_metadata_radio_set").get_child_by_id("update_org_metadata_verbose_radio").value

            output, errCode = be.update_org_metadata(org_id, file_name, mem_list, gas, index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class org_groups_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Organization Groups Page", id="org_groups_page_title"),
                Horizontal(
                    Button(label="Add a Group", id="org_groups_add_button"),
                    Button(label="Update Group", id="org_groups_update_button"),
                    id="org_groups_page_button_div"
                ),
                Button(label="Back", id="org_groups_back_button"),
                id="org_groups_page_content",
                classes="content_page"
            ),
            id="org_groups_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "org_groups_back_button":
            load_screen_redirect = "organization"
            self.app.push_screen(loading_screen())
        elif event.button.id == "org_groups_add_button":
            self.app.push_screen(add_org_group_page())
        elif event.button.id == "org_groups_update_button":
            self.app.push_screen(update_org_group_page())

class add_org_group_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Add Organization Group Page", id="add_org_group_title"),
                Horizontal(
                    Label("Group Name", id="add_org_group_name_label", classes="add_org_group_label"),
                    Input(placeholder="Group Name", id="add_org_group_name_input", classes="add_org_group_input"),
                    id="add_org_group_name_div",
                    classes="add_org_group_div"
                ),
                Horizontal(
                    Label("Payment Address", id="add_org_group_pay_addr_label", classes="add_org_group_label"),
                    Input(placeholder="Payment Address", id="add_org_group_pay_addr_input", classes="add_org_group_input"),
                    id="add_org_group_pay_addr_div",
                    classes="add_org_group_div"
                ),
                Horizontal(
                    Label("Endpoints", id="add_org_group_endpoint_label", classes="add_org_group_label"),
                    Input(placeholder="Endpoints (space separated if multiple, DO NOT add brackets '[]')", id="add_org_group_endpoint_input", classes="add_org_group_input"),
                    id="add_org_group_endpoint_div",
                    classes="add_org_group_div"
                ),
                Horizontal(
                    Label("Metadata File", id="add_org_group_metadata_file_label", classes="add_org_group_label"),
                    Input(placeholder="Service metadata json file", id="add_org_group_metadata_file_input", classes="add_org_group_input"),
                    id="add_org_group_metadata_file_div",
                    classes="add_org_group_div"
                ),
                Horizontal(
                    Label("Expir. Threshold", id="add_org_group_pay_expr_threshold_label", classes="add_org_group_label"),
                    Input(placeholder="[OPTIONAL] Payment Expiration threshold. Default: 100", id="add_org_group_pay_expr_threshold_input", classes="add_org_group_input"),
                    id="add_org_group_pay_expr_threshold_div",
                    classes="add_org_group_div"
                ),
                Horizontal(
                    Label("Channel Storage", id="add_org_group_pay_chann_storage_label", classes="add_org_group_label"),
                    Input(placeholder="[OPTIONAL] Storage channel for payment. Default: 'etcd'", id="add_org_group_pay_chann_storage_input", classes="add_org_group_input"),
                    id="add_org_group_pay_chann_storage_div",
                    classes="add_org_group_div"
                ),
                Horizontal(
                    Label("Connection Timeout", id="add_org_group_pay_chann_conn_to_label", classes="add_org_group_label"),
                    Input(placeholder="[OPTIONAL] Payment channel connection timeout. Default: '100s'", id="add_org_group_pay_chann_conn_to_input", classes="add_org_group_input"),
                    id="add_org_group_pay_chann_conn_to_div",
                    classes="add_org_group_div"
                ),
                Horizontal(
                    Label("Request Timeout", id="add_org_group_pay_chann_req_to_label", classes="add_org_group_label"),
                    Input(placeholder="[OPTIONAL] Payment channel request timeout. Default: '5s'", id="add_org_group_pay_chann_req_to_input", classes="add_org_group_input"),
                    id="add_org_group_pay_chann_req_to_div",
                    classes="add_org_group_div"
                ),
                Horizontal(
                    Label("Registry Address", id="add_org_group_registry_label", classes="add_org_group_label"),
                    Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from 'networks'", id="add_org_group_registry_input", classes="add_org_group_input"),
                    id="add_org_group_registry_div",
                    classes="add_org_group_div"
                ),
                Horizontal(
                    Button(label="Back", id="add_org_group_back_button"),
                    Button(label="Add Group", id="add_org_group_confirm_button"),
                    id="add_org_group_button_div",
                    classes="add_org_group_div"
                ),
                id="add_org_group_content",
                classes="content_page"
            ),
            id="add_org_group_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "add_org_group_back_button":
            self.app.pop_screen()
        elif event.button.id == "add_org_group_confirm_button":
            group_name = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_name_div").get_child_by_id("add_org_group_name_input").value
            pay_addr = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_pay_addr_div").get_child_by_id("add_org_group_pay_addr_input").value
            endpoints = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_endpoint_div").get_child_by_id("add_org_group_endpoint_input").value
            payment_expiration_threshold = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_pay_expr_threshold_div").get_child_by_id("add_org_group_pay_expr_threshold_input").value
            pay_chann_storage_type = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_pay_chann_storage_div").get_child_by_id("add_org_group_pay_chann_storage_input").value
            pay_chann_conn_to = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_pay_chann_conn_to_div").get_child_by_id("add_org_group_pay_chann_conn_to_input").value
            pay_chann_req_to = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_pay_chann_req_to_div").get_child_by_id("add_org_group_pay_chann_req_to_input").value
            reg_addr = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_registry_div").get_child_by_id("add_org_group_registry_input").value
            metadata_file = self.get_child_by_id("add_org_group_page").get_child_by_id("add_org_group_content").get_child_by_id("add_org_group_metadata_file_div").get_child_by_id("add_org_group_metadata_file_input").value

            output, errCode = be.add_org_metadata_group(group_name, pay_addr, endpoints, payment_expiration_threshold, pay_chann_storage_type, pay_chann_conn_to, pay_chann_req_to, metadata_file, reg_addr)
            popup_output = output
            if errCode == 0:
                self.app.switch_screen(organization_page())
            self.app.push_screen(popup_output_page())
        

class update_org_group_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Update Organization Group Page", id="update_org_group_title"),
                Horizontal(
                    Label("Group Id  ", id="update_org_group_name_label", classes="update_org_group_label"),
                    Input(placeholder="Group ID", id="update_org_group_name_input", classes="update_org_group_input"),
                    id="update_org_group_name_div",
                    classes="update_org_group_div"
                ),
                Horizontal(
                    Label("Metadata File", id="update_org_group_metadata_file_label", classes="update_org_group_label"),
                    Input(placeholder="Service metadata json file (default service_metadata.json) Default: 'organization_metadata.json'", id="update_org_group_metadata_file_input", classes="update_org_group_input"),
                    id="update_org_group_metadata_file_div",
                    classes="update_org_group_div"
                ),
                Horizontal(
                    Label("Payment Address", id="update_org_group_pay_addr_label", classes="update_org_group_label"),
                    Input(placeholder="[OPTIONAL] Payment Address", id="update_org_group_pay_addr_input", classes="update_org_group_input"),
                    id="update_org_group_pay_addr_div",
                    classes="update_org_group_div"
                ),
                Horizontal(
                    Label("Endpoints", id="update_org_group_endpoint_label", classes="update_org_group_label"),
                    Input(placeholder="[OPTIONAL] Endpoints (space separated if multiple, DO NOT add brackets '[]')", id="update_org_group_endpoint_input", classes="update_org_group_input"),
                    id="update_org_group_endpoint_div",
                    classes="update_org_group_div"
                ),
                Horizontal(
                    Label("Expir. Threshold", id="update_org_group_pay_expr_threshold_label", classes="update_org_group_label"),
                    Input(placeholder="[OPTIONAL] Payment Expiration threshold. Default: 100", id="update_org_group_pay_expr_threshold_input", classes="update_org_group_input"),
                    id="update_org_group_pay_expr_threshold_div",
                    classes="update_org_group_div"
                ),
                Horizontal(
                    Label("Storage Channel", id="update_org_group_pay_chann_storage_label", classes="update_org_group_label"),
                    Input(placeholder="[OPTIONAL] Storage channel for payment. Default: 'etcd'", id="update_org_group_pay_chann_storage_input", classes="update_org_group_input"),
                    id="update_org_group_pay_chann_storage_div",
                    classes="update_org_group_div"
                ),
                Horizontal(
                    Label("Connection Timeout", id="update_org_group_pay_chann_conn_to_label", classes="update_org_group_label"),
                    Input(placeholder="[OPTIONAL] Payment channel connection timeout. Default: '100s'", id="update_org_group_pay_chann_conn_to_input", classes="update_org_group_input"),
                    id="update_org_group_pay_chann_conn_to_div",
                    classes="update_org_group_div"
                ),
                Horizontal(
                    Label("Request Timeout", id="update_org_group_pay_chann_req_to_label", classes="update_org_group_label"),
                    Input(placeholder="[OPTIONAL] Payment channel request timeout. Default: '5s'", id="update_org_group_pay_chann_req_to_input", classes="update_org_group_input"),
                    id="update_org_group_pay_chann_req_to_div",
                    classes="update_org_group_div"
                ),
                Horizontal(
                    Label("Registry Address", id="update_org_group_registry_label", classes="update_org_group_label"),
                    Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from 'networks'", id="update_org_group_registry_input", classes="update_org_group_input"),
                    id="update_org_group_registry_div",
                    classes="update_org_group_div"
                ),
                Horizontal(
                    Button(label="Back", id="update_org_group_back_button"),
                    Button(label="Update Group", id="update_org_group_confirm_button"),
                    id="update_org_group_button_div",
                    classes="update_org_group_div"
                ),
                id="update_org_group_content",
                classes="content_page"
            ),
            id="update_org_group_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "update_org_group_back_button":
            self.app.pop_screen()
        elif event.button.id == "update_org_group_confirm_button":
            group_name = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_name_div").get_child_by_id("update_org_group_name_input").value
            pay_addr = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_pay_addr_div").get_child_by_id("update_org_group_pay_addr_input").value
            endpoints = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_endpoint_div").get_child_by_id("update_org_group_endpoint_input").value
            payment_expiration_threshold = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_pay_expr_threshold_div").get_child_by_id("update_org_group_pay_expr_threshold_input").value
            pay_chann_storage_type = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_pay_chann_storage_div").get_child_by_id("update_org_group_pay_chann_storage_input").value
            pay_chann_conn_to = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_pay_chann_conn_to_div").get_child_by_id("update_org_group_pay_chann_conn_to_input").value
            pay_chann_req_to = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_pay_chann_req_to_div").get_child_by_id("update_org_group_pay_chann_req_to_input").value
            reg_addr = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_registry_div").get_child_by_id("update_org_group_registry_input").value
            metadata_file = self.get_child_by_id("update_org_group_page").get_child_by_id("update_org_group_content").get_child_by_id("update_org_group_metadata_file_div").get_child_by_id("update_org_group_metadata_file_input").value

            output, errCode = be.update_org_metadata_group(group_name, pay_addr, endpoints, payment_expiration_threshold, pay_chann_storage_type, pay_chann_conn_to, pay_chann_req_to, metadata_file, reg_addr)
            popup_output = output
            if errCode == 0:
                self.app.switch_screen(organization_page())
            self.app.push_screen(popup_output_page())

class members_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Organization Members Page", id="members_page_title"),
                Horizontal(
                    Button(label="Manage Members", id="members_manage_button"),
                    Button(label="Change Organization Owner", id="members_change_owner_button"),
                    id="members_page_button_div"
                ),
                Button(label="Back", id="members_back_button"),
                id="members_page_content",
                classes="content_page"
            ),
            id="members_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "members_back_button":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "members_manage_button":
            self.app.push_screen(manage_members_page())
        elif event.button.id == "members_change_owner_button":
            self.app.push_screen(change_org_owner_page())

class manage_members_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Manage Members Page", id="manage_members_page_title"),
                Horizontal(
                    Label("Organization ID", id="manage_members_id_label", classes="manage_members_page_label"),
                    Input(placeholder="Id of the Organization", id="manage_members_id_input", classes="manage_members_page_input"),
                    id="manage_members_id_div",
                    classes="manage_members_page_div"
                ),
                Horizontal(
                    Label("Member List", id="manage_members_mem_list_label", classes="manage_members_page_label"),
                    Input(placeholder="List of members to be added to/removed from the organization", id="manage_members_mem_list_input", classes="manage_members_page_input"),
                    id="manage_members_mem_list_div",
                    classes="manage_members_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="manage_members_gas_label", classes="manage_members_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="manage_members_gas_input", classes="manage_members_page_input"),
                    id="manage_members_gas_div",
                    classes="manage_members_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="manage_members_index_label", classes="manage_members_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="manage_members_index_input", classes="manage_members_page_input"),
                    id="manage_members_index_div",
                    classes="manage_members_page_div"
                ),
                RadioSet(
                    RadioButton(label="Quiet transaction printing", id="manage_members_quiet_radio", classes="manage_members_radio"),
                    RadioButton(label="Verbose transaction printing", id="manage_members_verbose_radio", classes="manage_members_radio"),
                    id="manage_members_radio_set"
                ),
                Horizontal(
                    Button(label="Remove Member(s)", id="manage_members_remove_button"),
                    Button(label="Add Member(s)", id="manage_members_add_button"),
                    id="manage_members_page_button_div",
                    classes="manage_members_page_div"
                ),
                Button(label="Back", id="manage_members_back_button"),
                id="manage_members_page_content",
                classes="content_page"
            ),
            id="manage_members_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        org_id = self.get_child_by_id("manage_members_page").get_child_by_id("manage_members_page_content").get_child_by_id("manage_members_id_div").get_child_by_id("manage_members_id_input").value
        mem_list = self.get_child_by_id("manage_members_page").get_child_by_id("manage_members_page_content").get_child_by_id("manage_members_mem_list_div").get_child_by_id("manage_members_mem_list_input").value
        gas = self.get_child_by_id("manage_members_page").get_child_by_id("manage_members_page_content").get_child_by_id("manage_members_gas_div").get_child_by_id("manage_members_gas_input").value
        index = self.get_child_by_id("manage_members_page").get_child_by_id("manage_members_page_content").get_child_by_id("manage_members_index_div").get_child_by_id("manage_members_index_input").value
        quiet = self.get_child_by_id("manage_members_page").get_child_by_id("manage_members_page_content").get_child_by_id("manage_members_radio_set").get_child_by_id("manage_members_quiet_radio").value
        verbose = self.get_child_by_id("manage_members_page").get_child_by_id("manage_members_page_content").get_child_by_id("manage_members_radio_set").get_child_by_id("manage_members_verbose_radio").value

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
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
        elif event.button.id == "manage_members_remove_button":
            output, errCode = be.remove_org_members(org_id, mem_list, gas, index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class change_org_owner_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Organization Owner Page", id="change_org_owner_page_title"),
                Horizontal(
                    Label("Organization ID", id="change_org_owner_id_label", classes="change_org_owner_page_label"),
                    Input(placeholder="Id of the Organization", id="change_org_owner_id_input", classes="change_org_owner_page_input"),
                    id="change_org_owner_page_id_div",
                    classes="change_org_owner_page_div"
                ),
                Horizontal(
                    Label("New Owner Address", id="change_org_owner_new_addr_label", classes="change_org_owner_page_label"),
                    Input(placeholder="Address of the new Organization's owner", id="change_org_owner_new_addr_input", classes="change_org_owner_page_input"),
                    id="change_org_owner_page_new_addr_div",
                    classes="change_org_owner_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="change_org_owner_gas_label", classes="change_org_owner_page_label"),
                    Input(placeholder="[OPTIONAL] In Wei or time based gas price strategy (defaults to session.default_gas_price)", id="change_org_owner_gas_input", classes="change_org_owner_page_input"),
                    id="change_org_owner_page_gas_div",
                    classes="change_org_owner_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="change_org_owner_index_label", classes="change_org_owner_page_label"),
                    Input(placeholder="[OPTIONAL] Account to use for signing (defaults to session.identity.default_wallet_index)", id="change_org_owner_index_input", classes="change_org_owner_page_input"),
                    id="change_org_owner_page_index_div",
                    classes="change_org_owner_page_div"
                ),
                RadioSet(
                    RadioButton(label="Quiet transaction printing", id="change_org_owner_quiet_radio"),
                    RadioButton(label="Verbose transaction printing", id="change_org_owner_verbose_radio"),
                    id="change_org_owner_radio_set"
                ),
                Horizontal(
                    Button(label="Back", id="change_org_owner_back_button"),
                    Button(label="Change Owner", id="change_org_owner_confirm_button"),
                    id="change_org_owner_page_button_div",
                    classes="change_org_owner_page_div"
                ),
                id="change_org_owner_page_content",
                classes="content_page"
            ),
            id="change_org_owner_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "change_org_owner_back_button":
            self.app.pop_screen()
        elif event.button.id == "change_org_owner_confirm_button":
            org_id = self.get_child_by_id("change_org_owner_page").get_child_by_id("change_org_owner_page_content").get_child_by_id("change_org_owner_page_id_div").get_child_by_id("change_org_owner_id_input").value
            new_addr = self.get_child_by_id("change_org_owner_page").get_child_by_id("change_org_owner_page_content").get_child_by_id("change_org_owner_page_new_addr_div").get_child_by_id("change_org_owner_new_addr_input").value
            gas = self.get_child_by_id("change_org_owner_page").get_child_by_id("change_org_owner_page_content").get_child_by_id("change_org_owner_page_gas_div").get_child_by_id("change_org_owner_gas_input").value
            index = self.get_child_by_id("change_org_owner_page").get_child_by_id("change_org_owner_page_content").get_child_by_id("change_org_owner_page_index_div").get_child_by_id("change_org_owner_index_input").value
            quiet = self.get_child_by_id("change_org_owner_page").get_child_by_id("change_org_owner_page_content").get_child_by_id("change_org_owner_radio_set").get_child_by_id("change_org_owner_quiet_radio").value
            verbose = self.get_child_by_id("change_org_owner_page").get_child_by_id("change_org_owner_page_content").get_child_by_id("change_org_owner_radio_set").get_child_by_id("change_org_owner_verbose_radio").value

            output, errCode = be.change_org_owner(org_id, new_addr, gas, index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class org_manage_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Organization Management Page", id="org_manage_page_title"),
                Horizontal(
                    Button(label="Create Organization", id="org_manage_add_button"),
                    Button(label="Delete Organization", id="org_manage_delete_button"),
                    id="org_manage_page_button_div"
                ),
                Button(label="Back", id="org_manage_back_button"),
                id="org_manage_page_content",
                classes="content_page"
            ),
            id="org_manage_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "org_manage_back_button":
            load_screen_redirect = "organization"
            self.app.push_screen(loading_screen())
        elif event.button.id == "org_manage_add_button":
            self.app.push_screen(org_manage_create_page())
        elif event.button.id == "org_manage_delete_button":
            self.app.push_screen(org_manage_delete_page())

class org_manage_create_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Create Organization Page", id="org_manage_create_page_title"),
                Horizontal(
                    Label("Organization ID", id="org_manage_create_id_label", classes="org_manage_create_page_label"),
                    Input(placeholder="Your Organization ID", id="org_manage_create_id_input", classes="org_manage_create_page_input"),
                    id="org_manage_create_id_div",
                    classes="org_manage_create_page_div"
                ),
                Horizontal(
                    Label("Metadata File Path", id="org_manage_create_file_label", classes="org_manage_create_page_label"),
                    Input(placeholder="Organization metadata json file path", id="org_manage_create_file_input", classes="org_manage_create_page_input"),
                    id="org_manage_create_file_div",
                    classes="org_manage_create_page_div"
                ),
                Horizontal(
                    Label("Registry Address", id="org_reg_addr_label", classes="org_manage_create_page_label"),
                    Input(placeholder="[OPTIONAL] Registry contract address", id="org_reg_addr_input", classes="org_manage_create_page_input"),
                    id="org_reg_addr_div",
                    classes="org_manage_create_page_div"
                ),
                Horizontal(
                    Label("Member List", id="org_manage_create_mems_label", classes="org_manage_create_page_label"),
                    Input(placeholder="[OPTIONAL] List of members to be added to the organization", id="org_manage_create_mems_input", classes="org_manage_create_page_input"),
                    id="org_manage_create_mems_div",
                    classes="org_manage_create_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="org_manage_create_gas_label", classes="org_manage_create_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="org_manage_create_gas_input", classes="org_manage_create_page_input"),
                    id="org_manage_create_gas_div",
                    classes="org_manage_create_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="org_manage_create_index_label", classes="org_manage_create_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="org_manage_create_index_input", classes="org_manage_create_page_input"),
                    id="org_manage_create_index_div",
                    classes="org_manage_create_page_div"
                ),
                RadioSet(
                    RadioButton(label="Quiet transaction printing", id="org_manage_create_quiet_radio", classes="org_manage_create_page_radio"),
                    RadioButton(label="Verbose transaction printing", id="org_manage_create_verbose_radio", classes="org_manage_create_page_radio"),
                    id="org_manage_create_radio_set"
                ),
                Horizontal(
                    Button(label="Back", id="org_manage_create_back_button"),
                    Button(label="Create Organization", id="org_manage_create_confirm_button"),
                    id="org_manage_create_page_button_div",
                    classes="org_manage_create_page_div"
                ),
                id="org_manage_create_page_content",
                classes="content_page"
            ),
            id="org_manage_create_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "org_manage_create_back_button":
            self.app.pop_screen()
        elif event.button.id == "org_manage_create_confirm_button":
            org_id = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_id_div").get_child_by_id("org_manage_create_id_input").value
            reg_addr = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_reg_addr_div").get_child_by_id("org_reg_addr_input").value
            file_name = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_file_div").get_child_by_id("org_manage_create_file_input").value
            mem_list = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_mems_div").get_child_by_id("org_manage_create_mems_input").value
            gas = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_gas_div").get_child_by_id("org_manage_create_gas_input").value
            index = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_index_div").get_child_by_id("org_manage_create_index_input").value
            quiet = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_radio_set").get_child_by_id("org_manage_create_quiet_radio").value
            verbose = self.get_child_by_id("org_manage_create_page").get_child_by_id("org_manage_create_page_content").get_child_by_id("org_manage_create_radio_set").get_child_by_id("org_manage_create_verbose_radio").value

            output, errCode = be.create_organization(org_id, file_name, mem_list, gas, index, quiet, verbose, reg_addr)
            popup_output = output
            self.app.push_screen(popup_output_page())

class org_manage_delete_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("org"),
            ScrollableContainer(
                Label("Delete Organization Page", id="org_manage_delete_page_title"),
                Horizontal(
                    Label("Organization ID", id="org_manage_delete_id_label", classes="org_manage_delete_page_label"),
                    Input(placeholder="Your Organization ID", id="org_manage_delete_id_input", classes="org_manage_delete_page_input"),
                    id="org_manage_delete_id_div",
                    classes="org_manage_delete_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="org_manage_delete_gas_label", classes="org_manage_delete_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="org_manage_delete_gas_input", classes="org_manage_delete_page_input"),
                    id="org_manage_delete_gas_div",
                    classes="org_manage_delete_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="org_manage_delete_index_label", classes="org_manage_delete_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="org_manage_delete_index_input", classes="org_manage_delete_page_input"),
                    id="org_manage_delete_index_div",
                    classes="org_manage_delete_page_div"
                ),
                Horizontal(
                    Label("Contract Address", id="org_manage_reg_addr_label", classes="org_manage_delete_page_label"),
                    Input(placeholder="[OPTIONAL] registry contract address (defaults to session.current_registry_at)", id="org_manage_delete_reg_addr_input", classes="org_manage_delete_page_input"),
                    id="org_manage_delete_reg_addr_div",
                    classes="org_manage_delete_page_div"
                ),
                RadioSet(
                    RadioButton(label="Quiet transaction printing", id="org_manage_delete_quiet_radio", classes="org_manage_delete_page_radio"),
                    RadioButton(label="Verbose transaction printing", id="org_manage_delete_verbose_radio", classes="org_manage_delete_page_radio"),
                    id="org_manage_delete_radio_set"
                ),
                Horizontal(
                    Button(label="Back", id="org_manage_delete_back_button"),
                    Button(label="Delete Organization", id="org_manage_delete_confirm_button"),
                    id="org_manage_delete_page_button_div",
                    classes="org_manage_delete_page_div"
                ),
                id="org_manage_delete_page_content",
                classes="content_page"
            ),
            id="org_manage_delete_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "org_manage_delete_back_button":
            self.app.pop_screen()
        elif event.button.id == "org_manage_delete_confirm_button":
            org_id = self.get_child_by_id("org_manage_delete_page").get_child_by_id("org_manage_delete_page_content").get_child_by_id("org_manage_delete_id_div").get_child_by_id("org_manage_delete_id_input").value
            gas = self.get_child_by_id("org_manage_delete_page").get_child_by_id("org_manage_delete_page_content").get_child_by_id("org_manage_delete_gas_div").get_child_by_id("org_manage_delete_gas_input").value
            index = self.get_child_by_id("org_manage_delete_page").get_child_by_id("org_manage_delete_page_content").get_child_by_id("org_manage_delete_index_div").get_child_by_id("org_manage_delete_index_input").value
            reg_addr = self.get_child_by_id("org_manage_delete_page").get_child_by_id("org_manage_delete_page_content").get_child_by_id("org_manage_delete_reg_addr_div").get_child_by_id("org_manage_delete_reg_addr_input").value
            quiet = self.get_child_by_id("org_manage_delete_page").get_child_by_id("org_manage_delete_page_content").get_child_by_id("org_manage_delete_radio_set").get_child_by_id("org_manage_delete_quiet_radio").value
            verbose = self.get_child_by_id("org_manage_delete_page").get_child_by_id("org_manage_delete_page_content").get_child_by_id("org_manage_delete_radio_set").get_child_by_id("org_manage_delete_verbose_radio").value

            output, errCode = be.delete_organization(org_id, gas, index, quiet, verbose, reg_addr)
            popup_output = output
            self.app.push_screen(popup_output_page())


class services_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Services Page", id="services_page_title"),
                Horizontal(
                    Button(label="Metadata", id="services_metadata_button"),
                    Button(label="Manage", id="services_page_manage_button"),
                    id="services_page_button_div"
                ),
                id="services_page_content",
                classes="content_page"
            ),
            id="services_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect
        
        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
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
            be.nav_sidebar_vert("serv"),
            Grid(
                Label("Service Metadata Page", id="manage_services_metadata_page_title"),
                Horizontal(
                    Button(label="Initialize Service Metadata", id="services_metadata_init_button", classes="manage_services_metadata_page_button"),
                    Button(label="Set", id="services_set_button", classes="manage_services_metadata_page_button"),
                    Button(label="Add/Remove", id="services_add_remove_button", classes="manage_services_metadata_page_button"),
                    id="manage_services_metadata_page_upper_div",
                    classes="manage_services_metadata_page_div"
                ),
                Horizontal(
                    Button(label="Update", id="services_update_button", classes="manage_services_metadata_page_button"),
                    Button(label="Get", id="services_get_button", classes="manage_services_metadata_page_button"),  
                    id="manage_services_metadata_page_lower_div",
                    classes="manage_services_metadata_page_div"
                ),
                Button("Back", id="services_metadata_back_button"),
                id="manage_services_metadata_page_content",
                classes="content_page"
            ),
            id="manage_services_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect
        
        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
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
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Service Metadata Initialization Page", id="init_service_metadata_page_title"),
                Horizontal(
                    Label("Service Path", id="init_service_metadata_service_path_label", classes="init_service_metadata_page_label"),
                    Input(placeholder="Service directory (Path to Service)", id="init_service_metadata_service_path_input", classes="init_service_metadata_page_input"),
                    id="init_service_metadata_service_path_div",
                    classes="init_service_metadata_page_div"
                ),
                Horizontal(
                    Label("Proto Directory", id="init_service_metadata_proto_dir_label", classes="init_service_metadata_page_label"),
                    Input(placeholder="Directory which contains protobuf files", id="init_service_metadata_proto_dir_input", classes="init_service_metadata_page_input"),
                    id="init_service_metadata_proto_dir_div",
                    classes="init_service_metadata_page_div"
                ),
                Horizontal(
                    Label("Display Name", id="init_service_metadata_display_name_label", classes="init_service_metadata_page_label"),
                    Input(placeholder="Service display name", id="init_service_metadata_display_name_input", classes="init_service_metadata_page_input"),
                    id="init_service_metadata_display_name_div",
                    classes="init_service_metadata_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="init_service_metadata_file_name_label", classes="init_service_metadata_page_label"),
                    Input(placeholder="[OPTIONAL] Service metadata json file (default service_metadata.json)", id="init_service_metadata_file_name_input", classes="init_service_metadata_page_input"),
                    id="init_service_metadata_file_name_div",
                    classes="init_service_metadata_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="init_service_metadata_mpe_addr_label", classes="init_service_metadata_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from “networks”", id="init_service_metadata_mpe_addr_input", classes="init_service_metadata_page_input"),
                    id="init_service_metadata_mpe_addr_div",
                    classes="init_service_metadata_page_div"
                ),
                Horizontal(
                    Label("Payment Group Name", id="init_service_metadata_pay_group_name_label", classes="init_service_metadata_page_label"),
                    Input(placeholder="Name of the first payment group", id="init_service_metadata_pay_group_name_input", classes="init_service_metadata_page_input"),
                    id="init_service_metadata_pay_group_name_div",
                    classes="init_service_metadata_page_div"
                ),
                Horizontal(
                    Label("Endpoints", id="init_service_metadata_endpoints_label", classes="init_service_metadata_page_label"),
                    Input(placeholder="[OPTIONAL] Endpoints for the first group. Default: []", id="init_service_metadata_endpoints_input", classes="init_service_metadata_page_input"),
                    id="init_service_metadata_endpoints_div",
                    classes="init_service_metadata_page_div"
                ),
                Horizontal(
                    Label("Fixed Price", id="init_service_metadata_price_label", classes="init_service_metadata_page_label"),
                    Input(placeholder="Set fixed price in AGI token for all methods", id="init_service_metadata_price_input", classes="init_service_metadata_page_input"),
                    id="init_service_metadata_price_div",
                    classes="init_service_metadata_page_div"
                ),
                Horizontal(
                    Label("Encoding Type", id="init_service_metadata_enc_type_label", classes="init_service_metadata_page_label"),
                    Select(options=((line, line) for line in """proto\njson""".splitlines()), prompt="Select Encoding Type", id="init_service_metadata_enc_type_select", classes="init_service_metadata_page_input"),
                    id="init_service_metadata_enc_type_div",
                    classes="init_service_metadata_page_div"
                ),
                Horizontal(
                    Label("Service Type", id="init_service_metadata_serv_type_label", classes="init_service_metadata_page_label"),
                    Select(options=((line, line) for line in """grpc\njsonrpc\nprocess""".splitlines()), prompt="Select Service Type", id="init_service_metadata_serv_type_select", classes="init_service_metadata_page_input"),
                    id="init_service_metadata_serv_type_div",
                    classes="init_service_metadata_page_div"
                ),
                Horizontal(
                    Button(label="Back", id="init_service_metadata_back_button"),
                    Button(label="Initialize Service Metadata", id="init_service_metadata_confirm_button"),
                    id="init_service_metadata_page_button_div",
                    classes="init_service_metadata_page_div"
                ),
                id="init_service_metadata_page_content",
                classes="content_page"
            ),
            id="init_service_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "init_service_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "init_service_metadata_confirm_button":
            service_path = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_service_path_div").get_child_by_id("init_service_metadata_service_path_input").value
            proto_path = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_proto_dir_div").get_child_by_id("init_service_metadata_proto_dir_input").value
            service_display = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_display_name_div").get_child_by_id("init_service_metadata_display_name_input").value
            metadata_file = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_file_name_div").get_child_by_id("init_service_metadata_file_name_input").value
            mpe_addr = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_mpe_addr_div").get_child_by_id("init_service_metadata_mpe_addr_input").value
            pay_group_name = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_pay_group_name_div").get_child_by_id("init_service_metadata_pay_group_name_input").value
            endpoints = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_endpoints_div").get_child_by_id("init_service_metadata_endpoints_input").value
            fixed_price = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_price_div").get_child_by_id("init_service_metadata_price_input").value
            enc_type = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_enc_type_div").get_child_by_id("init_service_metadata_enc_type_select").value
            serv_type = self.get_child_by_id("init_service_metadata_page").get_child_by_id("init_service_metadata_page_content").get_child_by_id("init_service_metadata_serv_type_div").get_child_by_id("init_service_metadata_serv_type_select").value
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
            be.nav_sidebar_vert("serv"),
            Grid(
                Label("Service Metadata Set Page", id="service_metadata_set_page_title"),
                Horizontal(
                    Button("Set model", id="service_metadata_set_model_button", classes="services_metadata_set_page_button"),
                    Button("Set fixed price", id="service_metadata_set_fixed_price_button", classes="services_metadata_set_page_button"),
                    Button("Set method price", id="service_metadata_set_method_price_button", classes="services_metadata_set_page_button"),
                    id="service_metadata_set_upper_div",
                    classes="service_metadata_set_div"
                ),
                Horizontal(
                    Button("Set free calls", id="service_metadata_set_free_calls_button", classes="services_metadata_set_page_button"),
                    Button("Set freecall signer address", id="service_metadata_set_freecall_signer_button", classes="services_metadata_set_page_button"),
                    id="service_metadata_set_lower_div",
                    classes="service_metadata_set_div"
                ),
                Button("Back", id="service_metadata_set_back_button"),
                id="service_metadata_set_page_content",
                classes="content_page"
            ),
            id="service_metadata_set_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
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
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Set Service Model Page", id="service_metadata_set_model_page_title"),
                Horizontal(
                    Label("Proto Directory", id="service_metadata_set_model_proto_dir_label", classes="service_metadata_set_model_page_label"),
                    Input(placeholder="Directory which contains protobuf files", id="service_metadata_set_model_proto_dir_input", classes="service_metadata_set_model_page_input"),
                    id="service_metadata_set_model_proto_dir_div",
                    classes="service_metadata_set_model_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="service_metadata_set_model_file_label", classes="service_metadata_set_model_page_label"),
                    Input(placeholder="Service metadata json file path", id="service_metadata_set_model_file_input", classes="service_metadata_set_model_page_input"),
                    id="service_metadata_set_model_file_div",
                    classes="service_metadata_set_model_page_div"
                ),
                Horizontal(
                    Button("Back", id="service_metadata_set_model_back_button"),
                    Button("Set Model", id="service_metadata_set_model_confirm_button"),
                    id="service_metadata_set_model_page_button_div",
                    classes="service_metadata_set_model_page_div"
                ),
                id="service_metadata_set_model_page_content",
                classes="content_page"
            ),
            id="service_metadata_set_model_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_set_model_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_set_model_confirm_button":
            proto_dir = self.get_child_by_id("service_metadata_set_model_page").get_child_by_id("service_metadata_set_model_page_content").get_child_by_id("service_metadata_set_model_proto_dir_div").get_child_by_id("service_metadata_set_model_proto_dir_input").value
            metadata_file = self.get_child_by_id("service_metadata_set_model_page").get_child_by_id("service_metadata_set_model_page_content").get_child_by_id("service_metadata_set_model_file_div").get_child_by_id("service_metadata_set_model_file_input").value

            output, errCode = be.service_metadata_set_model(proto_dir, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())


class service_metadata_set_fixed_price_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Set Service Fixed Price Page", id="service_metadata_set_fixed_price_page_title"),
                Horizontal(
                    Label("Group Name", id="service_metadata_set_fixed_price_group_label", classes="service_metadata_set_fixed_price_page_label"),
                    Input(placeholder="Group name for fixed price method", id="service_metadata_set_fixed_price_group_input", classes="service_metadata_set_fixed_price_page_input"),
                    id="service_metadata_set_fixed_price_group_div",
                    classes="service_metadata_set_fixed_price_page_div"
                ),
                Horizontal(
                    Label("Fixed Price", id="service_metadata_set_fixed_price_amount_label", classes="service_metadata_set_fixed_price_page_label"),
                    Input(placeholder="Fixed price in AGI token for all methods", id="service_metadata_set_fixed_price_amount_input", classes="service_metadata_set_fixed_price_page_input"),
                    id="service_metadata_set_fixed_price_amount_div",
                    classes="service_metadata_set_fixed_price_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="service_metadata_set_fixed_price_file_label", classes="service_metadata_set_fixed_price_page_label"),
                    Input(placeholder="Service metadata json file path", id="service_metadata_set_fixed_price_file_input", classes="service_metadata_set_fixed_price_page_input"),
                    id="service_metadata_set_fixed_price_file_div",
                    classes="service_metadata_set_fixed_price_page_div"
                ),
                Horizontal(
                    Button("Back", id="service_metadata_set_fixed_price_back_button"),
                    Button("Set Fixed Price", id="service_metadata_set_fixed_price_confirm_button"),
                    id="service_metadata_set_fixed_price_page_button_div",
                    classes="service_metadata_set_fixed_price_page_div"
                ),
                id="service_metadata_set_fixed_price_page_content",
                classes="content_page"
            ),
            id="service_metadata_set_fixed_price_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_set_fixed_price_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_set_fixed_price_confirm_button":
            group_name = self.get_child_by_id("service_metadata_set_fixed_price_page").get_child_by_id("service_metadata_set_fixed_price_page_content").get_child_by_id("service_metadata_set_fixed_price_group_div").get_child_by_id("service_metadata_set_fixed_price_group_input").value
            price = self.get_child_by_id("service_metadata_set_fixed_price_page").get_child_by_id("service_metadata_set_fixed_price_page_content").get_child_by_id("service_metadata_set_fixed_price_amount_div").get_child_by_id("service_metadata_set_fixed_price_amount_input").value
            metadata_file = self.get_child_by_id("service_metadata_set_fixed_price_page").get_child_by_id("service_metadata_set_fixed_price_page_content").get_child_by_id("service_metadata_set_fixed_price_file_div").get_child_by_id("service_metadata_set_fixed_price_file_input").value

            output, errCode = be.service_metadata_set_fixed_price(group_name, price, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_set_method_price_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Set Service Method Price Page", id="service_metadata_set_method_price_page_title"),
                Horizontal(
                    Label("Group Name", id="service_metadata_set_method_price_group_label", classes="service_metadata_set_method_price_page_label"),
                    Input(placeholder="Group Name", id="service_metadata_set_method_price_group_input", classes="service_metadata_set_method_price_page_input"),
                    id="service_metadata_set_method_price_group_div",
                    classes="service_metadata_set_method_price_page_div"
                ),
                Horizontal(
                    Label("Package Name", id="service_metadata_set_method_price_package_label", classes="service_metadata_set_method_price_page_label"),
                    Input(placeholder="Package Name", id="service_metadata_set_method_price_package_input", classes="service_metadata_set_method_price_page_input"),
                    id="service_metadata_set_method_price_package_div",
                    classes="service_metadata_set_method_price_page_div"
                ),
                Horizontal(
                    Label("Service Name", id="service_metadata_set_method_price_service_label", classes="service_metadata_set_method_price_page_label"),
                    Input(placeholder="Service Name", id="service_metadata_set_method_price_service_input", classes="service_metadata_set_method_price_page_input"),
                    id="service_metadata_set_method_price_service_div",
                    classes="service_metadata_set_method_price_page_div"
                ),
                Horizontal(
                    Label("Method Name", id="service_metadata_set_method_price_method_label", classes="service_metadata_set_method_price_page_label"),
                    Input(placeholder="Method Name", id="service_metadata_set_method_price_method_input", classes="service_metadata_set_method_price_page_input"),
                    id="service_metadata_set_method_price_method_div",
                    classes="service_metadata_set_method_price_page_div"
                ),
                Horizontal(
                    Label("Fixed Price", id="service_metadata_set_method_price_amount_label", classes="service_metadata_set_method_price_page_label"),
                    Input(placeholder="Set fixed price in AGI token for all methods", id="service_metadata_set_method_price_amount_input", classes="service_metadata_set_method_price_page_input"),
                    id="service_metadata_set_method_price_amount_div",
                    classes="service_metadata_set_method_price_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="service_metadata_set_method_price_file_label", classes="service_metadata_set_method_price_page_label"),
                    Input(placeholder="Service metadata json file path", id="service_metadata_set_method_price_file_input", classes="service_metadata_set_method_price_page_input"),
                    id="service_metadata_set_method_price_file_div",
                    classes="service_metadata_set_method_price_page_div"
                ),
                Horizontal(
                    Button("Back", id="service_metadata_set_method_price_back_button"),
                    Button("Set Method Price", id="service_metadata_set_method_price_confirm_button"),
                    id="service_metadata_set_method_price_page_button_div",
                    classes="service_metadata_set_method_price_page_div"
                ),
                id="service_metadata_set_method_price_page_content",
                classes="content_page"
            ),
            id="service_metadata_set_method_price_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_set_method_price_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_set_method_price_confirm_button":
            group_name = self.get_child_by_id("service_metadata_set_method_price_page").get_child_by_id("service_metadata_set_method_price_page_content").get_child_by_id("service_metadata_set_method_price_group_div").get_child_by_id("service_metadata_set_method_price_group_input").value
            package_name = self.get_child_by_id("service_metadata_set_method_price_page").get_child_by_id("service_metadata_set_method_price_page_content").get_child_by_id("service_metadata_set_method_price_package_div").get_child_by_id("service_metadata_set_method_price_package_input").value
            service_name = self.get_child_by_id("service_metadata_set_method_price_page").get_child_by_id("service_metadata_set_method_price_page_content").get_child_by_id("service_metadata_set_method_price_service_div").get_child_by_id("service_metadata_set_method_price_service_input").value
            method_name = self.get_child_by_id("service_metadata_set_method_price_page").get_child_by_id("service_metadata_set_method_price_page_content").get_child_by_id("service_metadata_set_method_price_method_div").get_child_by_id("service_metadata_set_method_price_method_input").value
            price = self.get_child_by_id("service_metadata_set_method_price_page").get_child_by_id("service_metadata_set_method_price_page_content").get_child_by_id("service_metadata_set_method_price_amount_div").get_child_by_id("service_metadata_set_method_price_amount_input").value
            metadata_file = self.get_child_by_id("service_metadata_set_method_price_page").get_child_by_id("service_metadata_set_method_price_page_content").get_child_by_id("service_metadata_set_method_price_file_div").get_child_by_id("service_metadata_set_method_price_file_input").value
            
            output, errCode = be.service_metadata_set_method_price(group_name, package_name, service_name, method_name, price, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_set_free_calls_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Service Set Free Calls Page", id="service_metadata_set_free_calls_page_title"),
                Horizontal(
                    Label("Group Name", id="service_metadata_set_free_calls_group_label", classes="service_metadata_set_free_calls_page_label"),
                    Input(placeholder="Group Name", id="service_metadata_set_free_calls_group_input", classes="service_metadata_set_free_calls_page_input"),
                    id="service_metadata_set_free_calls_group_div",
                    classes="service_metadata_set_free_calls_page_div"
                ),
                Horizontal(
                    Label("Num. of Free Calls", id="service_metadata_set_free_calls_num_label", classes="service_metadata_set_free_calls_page_label"),
                    Input(placeholder="Number of free calls", id="service_metadata_set_free_calls_num_input", classes="service_metadata_set_free_calls_page_input"),
                    id="service_metadata_set_free_calls_num_div",
                    classes="service_metadata_set_free_calls_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="service_metadata_set_free_calls_file_label", classes="service_metadata_set_free_calls_page_label"),
                    Input(placeholder="Service metadata json file path", id="service_metadata_set_free_calls_file_input", classes="service_metadata_set_free_calls_page_input"),
                    id="service_metadata_set_free_calls_file_div",
                    classes="service_metadata_set_free_calls_page_div"
                ),
                Horizontal(
                    Button(label="Back", id="service_metadata_set_free_calls_back_button"),
                    Button(label="Set Free Calls", id="service_metadata_set_free_calls_confirm_button"),
                    id="service_metadata_set_free_calls_button_div",
                    classes="service_metadata_set_free_calls_page_div"
                ),
                id="service_metadata_set_free_calls_page_content",
                classes="content_page"
            ),
            id="service_metadata_set_free_calls_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_set_free_calls_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_set_free_calls_confirm_button":
            group_name = self.get_child_by_id("service_metadata_set_free_calls_page").get_child_by_id("service_metadata_set_free_calls_page_content").get_child_by_id("service_metadata_set_free_calls_group_div").get_child_by_id("service_metadata_set_free_calls_group_input").value
            free_calls = self.get_child_by_id("service_metadata_set_free_calls_page").get_child_by_id("service_metadata_set_free_calls_page_content").get_child_by_id("service_metadata_set_free_calls_num_div").get_child_by_id("service_metadata_set_free_calls_num_input").value
            metadata_file = self.get_child_by_id("service_metadata_set_free_calls_page").get_child_by_id("service_metadata_set_free_calls_page_content").get_child_by_id("service_metadata_set_free_calls_file_div").get_child_by_id("service_metadata_set_free_calls_file_input").value
            
            output, errCode = be.service_metadata_set_free_calls(group_name, free_calls, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_set_freecall_signer_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Service Freecall Signer Page", id="service_metadata_set_freecall_signer_page_title"),
                Horizontal(
                    Label("Payment Group", id="service_metadata_set_freecall_signer_group_label", classes="service_metadata_set_freecall_signer_page_label"),
                    Input(placeholder="Name of the payment group to which we want to set freecalls", id="service_metadata_set_freecall_signer_group_input", classes="service_metadata_set_freecall_signer_page_input"),
                    id="service_metadata_set_freecall_signer_group_div",
                    classes="service_metadata_set_freecall_signer_page_div"
                ),
                Horizontal(
                    Label("Signer Address", id="service_metadata_set_freecall_signer_addr_label", classes="service_metadata_set_freecall_signer_page_label"),
                    Input(placeholder="Signer Address - This is used to define the public key address used for validating signatures requested specially for free call. To be obtained as part of curation process", id="service_metadata_set_freecall_signer_addr_input", classes="service_metadata_set_freecall_signer_page_input"),
                    id="service_metadata_set_freecall_signer_addr_div",
                    classes="service_metadata_set_freecall_signer_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="service_metadata_set_freecall_signer_file_label", classes="service_metadata_set_freecall_signer_page_label"),
                    Input(placeholder="Service metadata json file path", id="service_metadata_set_freecall_signer_file_input", classes="service_metadata_set_freecall_signer_page_input"),
                    id="service_metadata_set_freecall_signer_file_div",
                    classes="service_metadata_set_freecall_signer_page_div"
                ),
                Horizontal(
                    Button(label="Back", id="service_metadata_set_freecall_signer_back_button"),
                    Button(label="Set Signer Address", id="service_metadata_set_freecall_signer_confirm_button"),
                    id="service_metadata_set_freecall_signer_button_div",
                    classes="service_metadata_set_freecall_signer_page_div"
                ),
                id="service_metadata_set_freecall_signer_page_content",
                classes="content_page"
            ),
            id="service_metadata_set_freecall_signer_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_set_freecall_signer_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_set_freecall_signer_confirm_button":
            group_name = self.get_child_by_id("service_metadata_set_freecall_signer_page").get_child_by_id("service_metadata_set_freecall_signer_page_content").get_child_by_id("service_metadata_set_freecall_signer_group_div").get_child_by_id("service_metadata_set_freecall_signer_group_input").value
            signer_addr = self.get_child_by_id("service_metadata_set_freecall_signer_page").get_child_by_id("service_metadata_set_freecall_signer_page_content").get_child_by_id("service_metadata_set_freecall_signer_addr_div").get_child_by_id("service_metadata_set_freecall_signer_addr_input").value
            metadata_file = self.get_child_by_id("service_metadata_set_freecall_signer_page").get_child_by_id("service_metadata_set_freecall_signer_page_content").get_child_by_id("service_metadata_set_freecall_signer_file_div").get_child_by_id("service_metadata_set_freecall_signer_file_input").value
            
            output, errCode = be.service_metadata_set_freecall_signer_addr(group_name, signer_addr, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_add_remove_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("serv"),
            Grid(
                Label("Service Metadata Add/Remove Page", id="service_metadata_add_remove_page_title"),
                Horizontal(
                    Button(label="Add Service Description", id="services_metadata_add_desc_button", classes="services_metadata_add_remove_button"),
                    Button("Add/Remove Service Metadata Groups", id="services_metadata_add_remove_groups_button", classes="services_metadata_add_remove_button"),
                    Button("Add/Remove Daemon Address", id="services_metadata_add_remove_daemon_button", classes="services_metadata_add_remove_button"),
                    id="services_metadata_add_remove_upper_div",
                    classes="services_metadata_add_remove_div"
                ),
                Horizontal(
                    Button("Add/Remove Service Metadata Assets", id="services_metadata_add_remove_assets_button", classes="services_metadata_add_remove_button"),
                    Button("Add/Remove Service Metadata Media", id="services_metadata_add_remove_media_button", classes="services_metadata_add_remove_button"),
                    id="services_metadata_add_remove_lower_div",
                    classes="services_metadata_add_remove_div"
                ),
                Button("Back", id="service_metadata_add_remove_back_button"),
                id="service_metadata_add_remove_page_content",
                classes="content_page"
            ),
            id="service_metadata_add_remove_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
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
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Add Description Page", id="add_desc_service_metadata_page_title"),
                Horizontal(
                    Label("Long Description", id="add_desc_service_metadata_long_label", classes="add_desc_service_metadata_page_label"),
                    Input(placeholder="Description of the service and what it does", id="add_desc_service_metadata_long_input", classes="add_desc_service_metadata_page_input"),
                    id="add_desc_service_metadata_long_div",
                    classes="add_desc_service_metadata_page_div"
                ),
                Horizontal(
                    Label("Short Description", id="add_desc_service_metadata_short_label", classes="add_desc_service_metadata_page_label"),
                    Input(placeholder="Short overview of the service", id="add_desc_service_metadata_short_input", classes="add_desc_service_metadata_page_input"),
                    id="add_desc_service_metadata_short_div",
                    classes="add_desc_service_metadata_page_div"
                ),
                Horizontal(
                    Label("URL", id="add_desc_service_metadata_url_label", classes="add_desc_service_metadata_page_label"),
                    Input(placeholder="URL to provide more details of the service", id="add_desc_service_metadata_url_input", classes="add_desc_service_metadata_page_input"),
                    id="add_desc_service_metadata_url_div",
                    classes="add_desc_service_metadata_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="add_desc_service_metadata_meta_file_label", classes="add_desc_service_metadata_page_label"),
                    Input(placeholder="Service metadata json file path", id="add_desc_service_metadata_meta_file_input", classes="add_desc_service_metadata_page_input"),
                    id="add_desc_service_metadata_meta_file_div",
                    classes="add_desc_service_metadata_page_div"
                ),
                Horizontal(
                    Button(label="Back", id="add_desc_service_metadata_back_button"),
                    Button(label="Add Service Description", id="add_desc_service_metadata_confirm_button"),
                    id="add_desc_service_metadata_button_div",
                    classes="add_desc_service_metadata_page_div"
                ),
                id="add_desc_service_metadata_page_content",
                classes="content_page"
            ),
            id="add_desc_service_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "add_desc_service_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "add_desc_service_metadata_confirm_button":
            long_desc = self.get_child_by_id("add_desc_service_metadata_page").get_child_by_id("add_desc_service_metadata_page_content").get_child_by_id("add_desc_service_metadata_long_div").get_child_by_id("add_desc_service_metadata_long_input").value
            short_desc = self.get_child_by_id("add_desc_service_metadata_page").get_child_by_id("add_desc_service_metadata_page_content").get_child_by_id("add_desc_service_metadata_short_div").get_child_by_id("add_desc_service_metadata_short_input").value
            url = self.get_child_by_id("add_desc_service_metadata_page").get_child_by_id("add_desc_service_metadata_page_content").get_child_by_id("add_desc_service_metadata_url_div").get_child_by_id("add_desc_service_metadata_url_input").value
            metadata_file = self.get_child_by_id("add_desc_service_metadata_page").get_child_by_id("add_desc_service_metadata_page_content").get_child_by_id("add_desc_service_metadata_meta_file_div").get_child_by_id("add_desc_service_metadata_meta_file_input").value
            
            output, errCode = be.add_service_metadata_desc(long_desc, short_desc, url, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_add_remove_group_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Manage Service Group Page", id="service_metadata_add_remove_group_page_title"),
                Horizontal(
                    Label("Payment Group", id="service_metadata_add_remove_group_group_label", classes="service_metadata_add_remove_group_page_label"),
                    Input(placeholder="Name of the payment group to be added/removed", id="service_metadata_add_remove_group_group_input", classes="service_metadata_add_remove_group_page_input"),
                    id="service_metadata_add_remove_group_group_div",
                    classes="service_metadata_add_remove_group_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="service_metadata_add_remove_group_file_label", classes="service_metadata_add_remove_group_page_label"),
                    Input(placeholder="Service metadata json file path", id="service_metadata_add_remove_group_file_input", classes="service_metadata_add_remove_group_page_input"),
                    id="service_metadata_add_remove_group_file_div",
                    classes="service_metadata_add_remove_group_page_div"
                ),
                Horizontal(
                    Button("Remove Group", id="service_metadata_add_remove_group_remove_button"),
                    Button("Add Group", id="service_metadata_add_remove_group_add_button"),
                    id="service_metadata_add_remove_group_button_div",
                    classes="service_metadata_add_remove_group_page_div"
                ),
                Button("Back", id="service_metadata_add_remove_group_back_button"),
                id="service_metadata_add_remove_group_page_content",
                classes="content_page"
            ),
            id="service_metadata_add_remove_group_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        group_name = self.get_child_by_id("service_metadata_add_remove_group_page").get_child_by_id("service_metadata_add_remove_group_page_content").get_child_by_id("service_metadata_add_remove_group_group_div").get_child_by_id("service_metadata_add_remove_group_group_input").value
        metadata_file = self.get_child_by_id("service_metadata_add_remove_group_page").get_child_by_id("service_metadata_add_remove_group_page_content").get_child_by_id("service_metadata_add_remove_group_file_div").get_child_by_id("service_metadata_add_remove_group_file_input").value

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
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
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Service Daemon Address Page", id="service_metadata_add_remove_daemon_addr_page_title"),
                Horizontal(
                    Label("Payment Group", id="service_metadata_add_remove_daemon_addr_group_label", classes="service_metadata_add_remove_daemon_addr_page_label"),
                    Input(placeholder="Name of the payment group to be added/removed", id="service_metadata_add_remove_daemon_addr_group_input", classes="service_metadata_add_remove_daemon_addr_page_input"),
                    id="service_metadata_add_remove_daemon_addr_group_div",
                    classes="service_metadata_add_remove_daemon_addr_page_div"
                ),
                Horizontal(
                    Label("Daemon Addresses", id="service_metadata_add_remove_daemon_addr_endpoint_label", classes="service_metadata_add_remove_daemon_addr_page_label"),
                    Input(placeholder="[NOT REQUIRED FOR DELETE] Ethereum public addresses of daemon", id="service_metadata_add_remove_daemon_addr_endpoint_input", classes="service_metadata_add_remove_daemon_addr_page_input"),
                    id="service_metadata_add_remove_daemon_addr_endpoint_div",
                    classes="service_metadata_add_remove_daemon_addr_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="service_metadata_add_remove_daemon_addr_file_label", classes="service_metadata_add_remove_daemon_addr_page_label"),
                    Input(placeholder="Service metadata json file path", id="service_metadata_add_remove_daemon_addr_file_input", classes="service_metadata_add_remove_daemon_addr_page_input"),
                    id="service_metadata_add_remove_daemon_addr_file_div",
                    classes="service_metadata_add_remove_daemon_addr_page_div"
                ),
                Horizontal(
                    Button("Remove ALL Daemon Addresses (NOTE: EVERY addr)", id="service_metadata_add_remove_daemon_addr_remove_button"),
                    Button("Add Daemon Address", id="service_metadata_add_remove_daemon_addr_add_button"),
                    id="service_metadata_add_remove_daemon_addr_button_div",
                    classes="service_metadata_add_remove_daemon_addr_page_div"
                ),
                Button("Back", id="service_metadata_add_remove_daemon_addr_back_button"),
                id="service_metadata_add_remove_daemon_addr_page_content",
                classes="content_page"
            ),
            id="service_metadata_add_remove_daemon_addr_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        group_name = self.get_child_by_id("service_metadata_add_remove_daemon_addr_page").get_child_by_id("service_metadata_add_remove_daemon_addr_page_content").get_child_by_id("service_metadata_add_remove_daemon_addr_group_div").get_child_by_id("service_metadata_add_remove_daemon_addr_group_input").value
        daemon_addr = self.get_child_by_id("service_metadata_add_remove_daemon_addr_page").get_child_by_id("service_metadata_add_remove_daemon_addr_page_content").get_child_by_id("service_metadata_add_remove_daemon_addr_endpoint_div").get_child_by_id("service_metadata_add_remove_daemon_addr_endpoint_input").value
        metadata_file = self.get_child_by_id("service_metadata_add_remove_daemon_addr_page").get_child_by_id("service_metadata_add_remove_daemon_addr_page_content").get_child_by_id("service_metadata_add_remove_daemon_addr_file_div").get_child_by_id("service_metadata_add_remove_daemon_addr_file_input").value

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
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
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Manage Service Assets Page", id="service_metadata_add_remove_assets_page_title"),
                Horizontal(
                    Label("Asset Path", id="service_metadata_add_remove_assets_path_label", classes="service_metadata_add_remove_assets_page_label"),
                    Input(placeholder="[NOT REQUIRED FOR DELETE ALL] Asset file path", id="service_metadata_add_remove_assets_path_input", classes="service_metadata_add_remove_assets_page_input"),
                    id="service_metadata_add_remove_assets_path_div",
                    classes="service_metadata_add_remove_assets_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="service_metadata_add_remove_assets_file_label", classes="service_metadata_add_remove_assets_page_label"),
                    Input(placeholder="Service metadata json file", id="service_metadata_add_remove_assets_file_input", classes="service_metadata_add_remove_assets_page_input"),
                    id="service_metadata_add_remove_assets_file_div",
                    classes="service_metadata_add_remove_assets_page_div"
                ),
                Horizontal(
                    Label("Asset Type", id="service_metadata_add_remove_assets_type_label", classes="service_metadata_add_remove_assets_page_label"),
                    Select(options=((line, line) for line in """hero_image\nimages""".splitlines()), prompt="Select Asset Type", id="service_metadata_add_remove_assets_type_select", classes="service_metadata_add_remove_assets_page_select"),
                    id="service_metadata_add_remove_assets_type_div",
                    classes="service_metadata_add_remove_assets_page_div"
                ),
                Horizontal(
                    Button("Remove ALL Assets of type (NOTE: EVERY asset)", id="service_metadata_add_remove_assets_remove_button"),
                    Button("Add Asset", id="service_metadata_add_remove_assets_add_button"),
                    id="service_metadata_add_remove_assets_button_div",
                    classes="service_metadata_add_remove_assets_page_div"
                ),
                Button("Back", id="service_metadata_add_remove_assets_back_button"),
                id="service_metadata_add_remove_assets_page_content",
                classes="content_page"
            ),
            id="service_metadata_add_remove_assets_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        asset_type = self.get_child_by_id("service_metadata_add_remove_assets_page").get_child_by_id("service_metadata_add_remove_assets_page_content").get_child_by_id("service_metadata_add_remove_assets_type_div").get_child_by_id("service_metadata_add_remove_assets_type_select").value
        metadata_file = self.get_child_by_id("service_metadata_add_remove_assets_page").get_child_by_id("service_metadata_add_remove_assets_page_content").get_child_by_id("service_metadata_add_remove_assets_file_div").get_child_by_id("service_metadata_add_remove_assets_file_input").value

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_add_remove_assets_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_add_remove_assets_add_button":
            asset_path = self.get_child_by_id("service_metadata_add_remove_assets_page").get_child_by_id("service_metadata_add_remove_assets_page_content").get_child_by_id("service_metadata_add_remove_assets_path_div").get_child_by_id("service_metadata_add_remove_assets_path_input").value
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
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Add/Remove Service Media Page", id="service_metadata_add_remove_media_page_title"),
                Horizontal(
                    Label("Media URL", id="service_metadata_add_media_url_label", classes="service_metadata_add_remove_media_page_label"),
                    Input(placeholder="Media url endpoint", id="service_metadata_add_media_url_input", classes="service_metadata_add_remove_media_page_input"),
                    id="service_metadata_add_remove_media_url_div",
                    classes="service_metadata_add_remove_media_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="service_metadata_add_media_file_label", classes="service_metadata_add_remove_media_page_label"),
                    Input(placeholder="Service metadata json file path", id="service_metadata_add_media_file_input", classes="service_metadata_add_remove_media_page_input"),
                    id="service_metadata_add_remove_media_file_div",
                    classes="service_metadata_add_remove_media_page_div"
                ),
                RadioButton(label="Media is hero-image", id="service_metadata_add_media_hero_radio", classes="service_metadata_add_remove_media_page_radio"),
                Horizontal(
                    Button("Remove ALL Media (NOTE: EVERY media file)", id="service_metadata_add_remove_media_remove_button"),
                    Button("Add Media", id="service_metadata_add_remove_media_add_button"),
                    id="service_metadata_add_remove_media_button_div",
                    classes="service_metadata_add_remove_media_page_div"
                ),
                Button("Back", id="service_metadata_add_remove_media_back_button"),
                id="service_metadata_add_remove_media_page_content",
                classes="content_page"
            ),
            id="service_metadata_add_remove_media_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        metadata_file = self.get_child_by_id("service_metadata_add_remove_media_page").get_child_by_id("service_metadata_add_remove_media_page_content").get_child_by_id("service_metadata_add_remove_media_file_div").get_child_by_id("service_metadata_add_media_file_input").value

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
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
            url = self.get_child_by_id("service_metadata_add_remove_media_page").get_child_by_id("service_metadata_add_remove_media_page_content").get_child_by_id("service_metadata_add_remove_media_url_div").get_child_by_id("service_metadata_add_media_url_input").value
            hero_image = self.get_child_by_id("service_metadata_add_remove_media_page").get_child_by_id("service_metadata_add_remove_media_page_content").get_child_by_id("service_metadata_add_remove_media_hero_div").get_child_by_id("service_metadata_add_media_hero_radio").value
            output, errCode = be.service_metadata_add_media(url, hero_image, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_update_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("serv"),
            Grid(
                Label("Service Metadata Blockchain Update Page", id="service_metadata_update_page_title"),
                Horizontal(
                    Button("Update Service Daemon Address", id="service_metadata_update_daemon_button", classes="service_metadata_update_button"),
                    Button("Validate Metadata", id="service_metadata_update_validate_button", classes="service_metadata_update_button"),
                    id="service_metadata_update_div"
                ),
                Button("Update Metadata", id="service_metadata_update_metadata_button", classes="service_metadata_update_button"),
                Button("Back", id="serivce_metadata_update_back_button"),
                id="service_metadata_update_page_content",
                classes="content_page"
            ),
            id="service_metadata_update_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
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
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Update Service Daemon Address Page", id="service_metadata_update_daemon_addr_page_title"),
                Horizontal(
                    Label("Payment Group", id="service_metadata_update_daemon_addr_group_label", classes="service_metadata_update_daemon_addr_page_label"),
                    Input(placeholder="Name of the payment group to which we want to update daemon addresses for", id="service_metadata_update_daemon_addr_group_input", classes="service_metadata_update_daemon_addr_page_input"),
                    id="service_metadata_update_daemon_addr_group_div",
                    classes="service_metadata_update_daemon_addr_page_div"
                ),
                Horizontal(
                    Label("Daemon Addresses", id="service_metadata_update_daemon_addr_endpoint_label", classes="service_metadata_update_daemon_addr_page_label"),
                    Input(placeholder="Daemon addresses", id="service_metadata_update_daemon_addr_endpoint_input", classes="service_metadata_update_daemon_addr_page_input"),
                    id="service_metadata_update_daemon_addr_endpoint_div",
                    classes="service_metadata_update_daemon_addr_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="service_metadata_update_daemon_addr_file_label", classes="service_metadata_update_daemon_addr_page_label"),
                    Input(placeholder="Service metadata json file path", id="service_metadata_update_daemon_addr_file_input", classes="service_metadata_update_daemon_addr_page_input"),
                    id="service_metadata_update_daemon_addr_file_div",
                    classes="service_metadata_update_daemon_addr_page_div"
                ),
                Horizontal(
                    Button("Back", id="service_metadata_update_daemon_addr_back_button"),
                    Button("Update Daemon Address", id="service_metadata_update_daemon_addr_update_button"),
                    id="service_metadata_update_daemon_addr_button_div",
                    classes="service_metadata_update_daemon_addr_page_div"
                ),
                id="service_metadata_update_daemon_addr_page_content",
                classes="content_page"
            ),
            id="service_metadata_update_daemon_addr_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_update_daemon_addr_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_update_daemon_addr_update_button":
            group_name = self.get_child_by_id("service_metadata_update_daemon_addr_page").get_child_by_id("service_metadata_update_daemon_addr_page_content").get_child_by_id("service_metadata_update_daemon_addr_group_div").get_child_by_id("service_metadata_update_daemon_addr_group_input").value
            daemon_addr = self.get_child_by_id("service_metadata_update_daemon_addr_page").get_child_by_id("service_metadata_update_daemon_addr_page_content").get_child_by_id("service_metadata_update_daemon_addr_endpoint_div").get_child_by_id("service_metadata_update_daemon_addr_endpoint_input").value
            metadata_file = self.get_child_by_id("service_metadata_update_daemon_addr_page").get_child_by_id("service_metadata_update_daemon_addr_page_content").get_child_by_id("service_metadata_update_daemon_addr_file_div").get_child_by_id("service_metadata_update_daemon_addr_file_input").value

            output, errCode = be.service_metadata_update_daemon_addr(group_name, daemon_addr, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_update_validate_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Validate Service Metadata Page", id="service_metadata_update_validate_metadata_page_title"),
                Horizontal(
                    Label("Metadata File", id="service_metadata_update_validate_metadata_file_label", classes="service_metadata_update_validate_metadata_page_label"),
                    Input(placeholder="Service metadata json file path", id="service_metadata_update_validate_metadata_file_input", classes="service_metadata_update_validate_metadata_page_input"),
                    id="service_metadata_update_validate_metadata_file_div",
                    classes="service_metadata_update_validate_metadata_page_div"
                ),
                Horizontal(
                    Button("Back", id="service_metadata_update_validate_metadata_back_button"),
                    Button("Validate Metadata", id="service_metadata_update_validate_metadata_validate_button"),
                    id="service_metadata_update_validate_metadata_button_div",
                    classes="service_metadata_update_validate_metadata_page_div"
                ),
                id="service_metadata_update_validate_metadata_page_content",
                classes="content_page"
            ),
            id="service_metadata_update_validate_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_update_validate_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_update_validate_metadata_validate_button":
            metadata_file = self.get_child_by_id("service_metadata_update_validate_metadata_page").get_child_by_id("service_metadata_update_validate_metadata_page_content").get_child_by_id("service_metadata_update_validate_metadata_file_div").get_child_by_id("service_metadata_update_validate_metadata_file_input").value
            output, errCode = be.service_metadata_update_validate_metadata(metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_update_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Update Service Metadata Page", id="service_metadata_update_metadata_page_title"),
                Horizontal(
                    Label("Organization ID", id="service_metadata_update_metadata_org_id_label", classes="service_metadata_update_metadata_page_label"),
                    Input(placeholder="Your Organization ID", id="service_metadata_update_metadata_org_id_input", classes="service_metadata_update_metadata_page_input"),
                    id="service_metadata_update_metadata_org_id_div",
                    classes="service_metadata_update_metadata_page_div"
                ),
                Horizontal(
                    Label("Service ID", id="service_metadata_update_metadata_service_id_label", classes="service_metadata_update_metadata_page_label"),
                    Input(placeholder="Your Service ID", id="service_metadata_update_metadata_service_id_input", classes="service_metadata_update_metadata_page_input"),
                    id="service_metadata_update_metadata_service_id_div",
                    classes="service_metadata_update_metadata_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="service_metadata_update_metadata_file_label", classes="service_metadata_update_metadata_page_label"),
                    Input(placeholder="Service metadata json file path", id="service_metadata_update_metadata_file_input", classes="service_metadata_update_metadata_page_input"),
                    id="service_metadata_update_metadata_file_div",
                    classes="service_metadata_update_metadata_page_div"
                ),
                Horizontal(
                    Label("Registry Contract", id="service_metadata_update_metadata_reg_contract_label", classes="service_metadata_update_metadata_page_label"),
                    Input(placeholder="[OPTIONAL] if not specified we read address from 'networks'", id="service_metadata_update_metadata_reg_contract_input", classes="service_metadata_update_metadata_page_input"),
                    id="service_metadata_update_metadata_reg_contract_div",
                    classes="service_metadata_update_metadata_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="service_metadata_update_metadata_mpe_label", classes="service_metadata_update_metadata_page_label"),
                    Input(placeholder="[OPTIONAL] if not specified we read address from 'networks'", id="service_metadata_update_metadata_mpe_input", classes="service_metadata_update_metadata_page_input"),
                    id="service_metadata_update_metadata_mpe_div",
                    classes="service_metadata_update_metadata_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="service_metadata_update_metadata_gas_label", classes="service_metadata_update_metadata_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="service_metadata_update_metadata_gas_input", classes="service_metadata_update_metadata_page_input"),
                    id="service_metadata_update_metadata_gas_div",
                    classes="service_metadata_update_metadata_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="service_metadata_update_metadata_index_label", classes="service_metadata_update_metadata_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="service_metadata_update_metadata_index_input", classes="service_metadata_update_metadata_page_input"),
                    id="service_metadata_update_metadata_index_div",
                    classes="service_metadata_update_metadata_page_div"
                ),
                RadioButton(label="Update MPE Address in metadata before publishing service", id="service_metadata_update_metadata_update_mpe_radio", classes="service_metadata_update_metadata_page_radio"),
                RadioSet(
                    RadioButton(label="Quiet transaction printing", id="service_metadata_update_metadata_quiet_radio", classes="service_metadata_update_metadata_page_radio"),
                    RadioButton(label="Verbose transaction printing", id="service_metadata_update_metadata_verbose_radio", classes="service_metadata_update_metadata_page_radio"),
                    id="service_metadata_update_metadata_radio_set"
                ),
                Horizontal(
                    Button(label="Back", id="service_metadata_update_metadata_back_button"),
                    Button(label="Update Metadata", id="service_metadata_update_metadata_confirm_button"),
                    id="service_metadata_update_metadata_button_div",
                    classes="service_metadata_update_metadata_page_div"
                ),
                id="service_metadata_update_metadata_page_content",
                classes="content_page"
            ),
            id="service_metadata_update_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_update_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_update_metadata_confirm_button":
            org_id = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_org_id_div").get_child_by_id("service_metadata_update_metadata_org_id_input").value
            service_id = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_service_id_div").get_child_by_id("service_metadata_update_metadata_service_id_input").value
            metadata_file = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_file_div").get_child_by_id("service_metadata_update_metadata_file_input").value
            reg_addr = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_reg_contract_div").get_child_by_id("service_metadata_update_metadata_reg_contract_input").value
            mpe_addr = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_mpe_div").get_child_by_id("service_metadata_update_metadata_mpe_input").value
            update_mpe = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_update_mpe_radio").value
            gas = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_gas_div").get_child_by_id("service_metadata_update_metadata_gas_input").value
            index = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_index_div").get_child_by_id("service_metadata_update_metadata_index_input").value
            quiet = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_radio_set").get_child_by_id("service_metadata_update_metadata_quiet_radio").value
            verbose = self.get_child_by_id("service_metadata_update_metadata_page").get_child_by_id("service_metadata_update_metadata_page_content").get_child_by_id("service_metadata_update_metadata_radio_set").get_child_by_id("service_metadata_update_metadata_verbose_radio").value
            
            output, errCode = be.service_metadata_update_update_metadata(org_id, service_id, metadata_file, reg_addr, mpe_addr, update_mpe, gas, index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_get_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("serv"),
            Grid(
                Label("Service Metadata Get Page", id="service_metadata_get_page_title"),
                Horizontal(
                    Button("Service Status", id="service_metadata_get_status_button", classes="service_metadata_get_page_button"),
                    Button("API Metadata", id="service_metadata_get_metadata_button", classes="service_metadata_get_page_button"),
                    id="service_metadata_get_page_div"
                ),
                Button("API Registry", id="service_metadata_get_registry_button", classes="service_metadata_get_page_button"),
                Button("Back", id="service_metadata_get_back_button"),
                id="service_metadata_get_page_content",
                classes="content_page"
            ),
            id="service_metadata_get_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
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
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Service Status Page", id="service_metadata_get_service_status_page_title"),
                Horizontal(
                    Label("Organization ID", id="service_metadata_get_service_status_org_id_label", classes="service_metadata_get_service_status_page_label"),
                    Input(placeholder="Organization ID", id="service_metadata_get_service_status_org_id_input", classes="service_metadata_get_service_status_page_input"),
                    id="service_metadata_get_service_status_org_id_div",
                    classes="service_metadata_get_service_status_page_div"
                ),
                Horizontal(
                    Label("Service ID", id="service_metadata_get_service_status_service_id_label", classes="service_metadata_get_service_status_page_label"),
                    Input(placeholder="Service ID", id="service_metadata_get_service_status_service_id_input", classes="service_metadata_get_service_status_page_input"),
                    id="service_metadata_get_service_status_service_id_div",
                    classes="service_metadata_get_service_status_page_div"
                ),
                Horizontal(
                    Label("Payment Group", id="service_metadata_get_service_status_group_label", classes="service_metadata_get_service_status_page_label"),
                    Input(placeholder="[OPTIONAL] Name of the payment group. Parameter should be specified only for services with several payment groups", id="service_metadata_get_service_status_group_input", classes="service_metadata_get_service_status_page_input"),
                    id="service_metadata_get_service_status_group_div",
                    classes="service_metadata_get_service_status_page_div"
                ),
                Horizontal(
                    Label("Registry Contract", id="service_metadata_get_service_status_reg_contract_label", classes="service_metadata_get_service_status_page_label"),
                    Input(placeholder="[OPTIONAL] if not specified we read address from 'networks'", id="service_metadata_get_service_status_reg_contract_input", classes="service_metadata_get_service_status_page_input"),
                    id="service_metadata_get_service_status_reg_contract_div",
                    classes="service_metadata_get_service_status_page_div"
                ),
                Horizontal(
                    Button(label="Back", id="service_metadata_get_service_status_back_button"),
                    Button(label="Get Service Status", id="service_metadata_get_service_status_confirm_button"),
                    id="service_metadata_get_service_status_button_div",
                    classes="service_metadata_get_service_status_page_div"
                ),
                id="service_metadata_get_service_status_page_content",
                classes="content_page"
            ),
            id="service_metadata_get_service_status_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_get_service_status_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_get_service_status_confirm_button":
            org_id = self.get_child_by_id("service_metadata_get_service_status_page").get_child_by_id("service_metadata_get_service_status_page_content").get_child_by_id("service_metadata_get_service_status_org_id_div").get_child_by_id("service_metadata_get_service_status_org_id_input").value
            service_id = self.get_child_by_id("service_metadata_get_service_status_page").get_child_by_id("service_metadata_get_service_status_page_content").get_child_by_id("service_metadata_get_service_status_service_id_div").get_child_by_id("service_metadata_get_service_status_service_id_input").value
            reg_addr = self.get_child_by_id("service_metadata_get_service_status_page").get_child_by_id("service_metadata_get_service_status_page_content").get_child_by_id("service_metadata_get_service_status_reg_contract_div").get_child_by_id("service_metadata_get_service_status_reg_contract_input").value
            pay_group = self.get_child_by_id("service_metadata_get_service_status_page").get_child_by_id("service_metadata_get_service_status_page_content").get_child_by_id("service_metadata_get_service_status_group_div").get_child_by_id("service_metadata_get_service_status_group_input").value
            
            output, errCode = be.print_service_status(org_id, service_id, pay_group, reg_addr)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_get_api_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Service API Metadata Page", id="service_metadata_get_api_metadata_page_title"),
                Horizontal(
                    Label("Proto Directory", id="service_metadata_get_api_metadata_proto_dir_label", classes="service_metadata_get_api_metadata_page_label"),
                    Input(placeholder="Directory to which extract api (model)", id="service_metadata_get_api_metadata_proto_dir_input", classes="service_metadata_get_api_metadata_page_input"),
                    id="service_metadata_get_api_metadata_proto_dir_div",
                    classes="service_metadata_get_api_metadata_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="service_metadata_get_api_metadata_file_label", classes="service_metadata_get_api_metadata_page_label"),
                    Input(placeholder="Service metadata json file path", id="service_metadata_get_api_metadata_file_input", classes="service_metadata_get_api_metadata_page_input"),
                    id="service_metadata_get_api_metadata_file_div",
                    classes="service_metadata_get_api_metadata_page_div"
                ),
                Horizontal(
                    Button("Back", id="service_metadata_get_api_metadata_back_button"),
                    Button("Get API Metadata", id="service_metadata_get_api_metadata_confirm_button"),
                    id="service_metadata_get_api_metadata_button_div",
                    classes="service_metadata_get_api_metadata_page_div"
                ),
                id="service_metadata_get_api_metadata_page_content",
                classes="content_page"
            ),
            id="service_metadata_get_api_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_get_api_metadata_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_get_api_metadata_confirm_button":
            proto_dir = self.get_child_by_id("service_metadata_get_api_metadata_page").get_child_by_id("service_metadata_get_api_metadata_page_content").get_child_by_id("service_metadata_get_api_metadata_proto_dir_div").get_child_by_id("service_metadata_get_api_metadata_proto_dir_input").value
            metadata_file = self.get_child_by_id("service_metadata_get_api_metadata_page").get_child_by_id("service_metadata_get_api_metadata_page_content").get_child_by_id("service_metadata_get_api_metadata_file_div").get_child_by_id("service_metadata_get_api_metadata_file_input").value
            
            output, errCode = be.print_service_api_metadata(proto_dir, metadata_file)
            popup_output = output
            self.app.push_screen(popup_output_page())

class service_metadata_get_api_registry_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Service API Registry Page", id="service_metadata_get_api_registry_page_title"),
                Horizontal(
                    Label("Organization ID", id="service_metadata_get_api_registry_org_id_label", classes="service_metadata_get_api_registry_page_label"),
                    Input(placeholder="Your Organization ID", id="service_metadata_get_api_registry_org_id_input", classes="service_metadata_get_api_registry_page_input"),
                    id="service_metadata_get_api_registry_org_id_div",
                    classes="service_metadata_get_api_registry_page_div"
                ),
                Horizontal(
                    Label("Service ID", id="service_metadata_get_api_registry_service_id_label", classes="service_metadata_get_api_registry_page_label"),
                    Input(placeholder="Your Service ID", id="service_metadata_get_api_registry_service_id_input", classes="service_metadata_get_api_registry_page_input"),
                    id="service_metadata_get_api_registry_service_id_div",
                    classes="service_metadata_get_api_registry_page_div"
                ),
                Horizontal(
                    Label("Proto Directory", id="service_metadata_get_api_registry_proto_dir_label", classes="service_metadata_get_api_registry_page_label"),
                    Input(placeholder="Directory to which extract api (model)", id="service_metadata_get_api_registry_proto_dir_input", classes="service_metadata_get_api_registry_page_input"),
                    id="service_metadata_get_api_registry_proto_dir_div",
                    classes="service_metadata_get_api_registry_page_div"
                ),
                Horizontal(
                    Label("Registry Contract", id="service_metadata_get_api_registry_reg_contract_label", classes="service_metadata_get_api_registry_page_label"),
                    Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from 'networks'", id="service_metadata_get_api_registry_reg_contract_input", classes="service_metadata_get_api_registry_page_input"),
                    id="service_metadata_get_api_registry_reg_contract_div",
                    classes="service_metadata_get_api_registry_page_div"
                ),
                Horizontal(
                    Button(label="Back", id="service_metadata_get_api_registry_back_button"),
                    Button(label="Get API Registry", id="service_metadata_get_api_registry_confirm_button"),
                    id="service_metadata_get_api_registry_button_div",
                    classes="service_metadata_get_api_registry_page_div"
                ),
                id="service_metadata_get_api_registry_page_content",
                classes="content_page"
            ),
            id="service_metadata_get_api_registry_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "service_metadata_get_api_registry_back_button":
            self.app.pop_screen()
        elif event.button.id == "service_metadata_get_api_registry_confirm_button":
            org_id = self.get_child_by_id("service_metadata_get_api_registry_page").get_child_by_id("service_metadata_get_api_registry_page_content").get_child_by_id("service_metadata_get_api_registry_org_id_div").get_child_by_id("service_metadata_get_api_registry_org_id_input").value
            service_id = self.get_child_by_id("service_metadata_get_api_registry_page").get_child_by_id("service_metadata_get_api_registry_page_content").get_child_by_id("service_metadata_get_api_registry_service_id_div").get_child_by_id("service_metadata_get_api_registry_service_id_input").value
            proto_dir = self.get_child_by_id("service_metadata_get_api_registry_page").get_child_by_id("service_metadata_get_api_registry_page_content").get_child_by_id("service_metadata_get_api_registry_proto_dir_div").get_child_by_id("service_metadata_get_api_registry_proto_dir_input").value
            reg_addr = self.get_child_by_id("service_metadata_get_api_registry_page").get_child_by_id("service_metadata_get_api_registry_page_content").get_child_by_id("service_metadata_get_api_registry_reg_contract_div").get_child_by_id("service_metadata_get_api_registry_reg_contract_input").value
            
            output, errCode = be.print_service_api_registry(org_id, service_id, reg_addr, proto_dir)
            popup_output = output
            self.app.push_screen(popup_output_page())

class services_manage_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("serv"),
            Grid(
                Label("Manage Services Page", id="services_manage_page_title"),
                Horizontal(
                    Button(label="Publish Service", id="services_manage_create_button", classes="services_manage_page_button"),
                    Button(label="Delete Service", id="services_manage_delete_button", classes="services_manage_page_button"),
                    id="services_manage_page_div"
                ),
                Button("Back", id="services_manage_back_button", classes="services_manage_page_button"),
                id="services_manage_page_content",
                classes="content_page"
            ),
            id="services_manage_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
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
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Service Publishing Page", id="publish_service_page_title"),
                Horizontal(
                    Label("Organization ID", id="publish_service_org_id_label", classes="publish_service_page_label"),
                    Input(placeholder="Your Organization ID", id="publish_service_org_id_input", classes="publish_service_page_input"),
                    id="publish_service_org_id_div",
                    classes="publish_service_page_div"
                ),
                Horizontal(
                    Label("Service ID", id="publish_service_service_id_label", classes="publish_service_page_label"),
                    Input(placeholder="Your Service ID", id="publish_service_service_id_input", classes="publish_service_page_input"),
                    id="publish_service_service_id_div",
                    classes="publish_service_page_div"
                ),
                Horizontal(
                    Label("Metadata File", id="publish_service_file_label", classes="publish_service_page_label"),
                    Input(placeholder="Service metadata json file path", id="publish_service_file_input", classes="publish_service_page_input"),
                    id="publish_service_file_div",
                    classes="publish_service_page_div"
                ),
                Horizontal(
                    Label("Registry Contract", id="publish_service_reg_contract_label", classes="publish_service_page_label"),
                    Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from 'networks'", id="publish_service_reg_contract_input", classes="publish_service_page_input"),
                    id="publish_service_reg_contract_div",
                    classes="publish_service_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="publish_service_mpe_label", classes="publish_service_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from 'networks'", id="publish_service_mpe_input", classes="publish_service_page_input"),
                    id="publish_service_mpe_div",
                    classes="publish_service_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="publish_service_gas_label", classes="publish_service_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="publish_service_gas_input", classes="publish_service_page_input"),
                    id="publish_service_gas_div",
                    classes="publish_service_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="publish_service_index_label", classes="publish_service_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="publish_service_index_input", classes="publish_service_page_input"),
                    id="publish_service_index_div",
                    classes="publish_service_page_div"
                ),
                RadioButton(label="Update MPE Address in metadata before publishing service", id="publish_service_update_mpe_radio", classes="publish_service_page_radio"),
                RadioSet(
                    RadioButton(label="Quiet transaction printing", id="publish_service_quiet_radio", classes="publish_service_page_radio"),
                    RadioButton(label="Verbose transaction printing", id="publish_service_verbose_radio", classes="publish_service_page_radio"),
                    id="publish_service_radio_set"
                ),
                Horizontal(
                    Button(label="Back", id="publish_service_back_button"),
                    Button(label="Publish Service", id="publish_service_confirm_button"),
                    id="publish_service_button_div",
                    classes="publish_service_page_div"
                ),
                id="publish_service_page_content",
                classes="content_page"
            ),
            id="publish_service_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "publish_service_back_button":
            self.app.pop_screen()
        elif event.button.id == "publish_service_confirm_button":
            org_id = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_org_id_div").get_child_by_id("publish_service_org_id_input").value
            service_id = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_service_id_div").get_child_by_id("publish_service_service_id_input").value
            metadata_file = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_file_div").get_child_by_id("publish_service_file_input").value
            reg_addr = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_reg_contract_div").get_child_by_id("publish_service_reg_contract_input").value
            mpe_addr = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_mpe_div").get_child_by_id("publish_service_mpe_input").value
            update_mpe = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_update_mpe_radio").value
            gas = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_gas_div").get_child_by_id("publish_service_gas_input").value
            index = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_index_div").get_child_by_id("publish_service_index_input").value
            quiet = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_radio_set").get_child_by_id("publish_service_quiet_radio").value
            verbose = self.get_child_by_id("publish_service_page").get_child_by_id("publish_service_page_content").get_child_by_id("publish_service_radio_set").get_child_by_id("publish_service_verbose_radio").value
            
            output, errCode = be.publish_service(org_id, service_id, metadata_file, reg_addr, mpe_addr, update_mpe, gas, index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class delete_service_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("serv"),
            ScrollableContainer(
                Label("Delete a Service Page", id="delete_service_page_title"),
                Horizontal(
                    Label("Organization ID", id="delete_service_org_id_label", classes="delete_service_page_label"),
                    Input(placeholder="Your Organization ID", id="delete_service_org_id_input", classes="delete_service_page_input"),
                    id="delete_service_org_id_div",
                    classes="delete_service_page_div"
                ),
                Horizontal(
                    Label("Service ID", id="delete_service_service_id_label", classes="delete_service_page_label"),
                    Input(placeholder="Your Service ID", id="delete_service_service_id_input", classes="delete_service_page_input"),
                    id="delete_service_service_id_div",
                    classes="delete_service_page_div"
                ),
                Horizontal(
                    Label("Registry Contract", id="delete_service_reg_contract_label", classes="delete_service_page_label"),
                    Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from 'networks'", id="delete_service_reg_contract_input", classes="delete_service_page_input"),
                    id="delete_service_reg_contract_div",
                    classes="delete_service_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="delete_service_gas_label", classes="delete_service_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy ('fast' ~1min, 'medium' ~5min or 'slow' ~60min) (defaults to session.default_gas_price)", id="delete_service_gas_input", classes="delete_service_page_input"),
                    id="delete_service_gas_div",
                    classes="delete_service_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="delete_service_index_label", classes="delete_service_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="delete_service_index_input", classes="delete_service_page_input"),
                    id="delete_service_index_div",
                    classes="delete_service_page_div"
                ),
                RadioSet(
                    RadioButton(label="Quiet transaction printing", id="delete_service_quiet_radio", classes="delete_service_page_radio"),
                    RadioButton(label="Verbose transaction printing", id="delete_service_verbose_radio", classes="delete_service_page_radio"),
                    id="delete_service_radio_set"
                ),
                Horizontal(
                    Button(label="Back", id="delete_service_back_button"),
                    Button(label="Delete Service", id="delete_service_confirm_button"),
                    id="delete_service_button_div",
                    classes="delete_service_page_div"
                ),
                id="delete_service_page_content",
                classes="content_page"
            ),
            id="delete_service_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "delete_service_back_button":
            self.app.pop_screen()
        elif event.button.id == "delete_service_confirm_button":
            org_id = self.get_child_by_id("delete_service_page").get_child_by_id("delete_service_page_content").get_child_by_id("delete_service_org_id_div").get_child_by_id("delete_service_org_id_input").value
            service_id = self.get_child_by_id("delete_service_page").get_child_by_id("delete_service_page_content").get_child_by_id("delete_service_service_id_div").get_child_by_id("delete_service_service_id_input").value
            reg_addr = self.get_child_by_id("delete_service_page").get_child_by_id("delete_service_page_content").get_child_by_id("delete_service_reg_contract_div").get_child_by_id("delete_service_reg_contract_input").value
            gas = self.get_child_by_id("delete_service_page").get_child_by_id("delete_service_page_content").get_child_by_id("delete_service_gas_div").get_child_by_id("delete_service_gas_input").value
            index = self.get_child_by_id("delete_service_page").get_child_by_id("delete_service_page_content").get_child_by_id("delete_service_index_div").get_child_by_id("delete_service_index_input").value
            quiet = self.get_child_by_id("delete_service_page").get_child_by_id("delete_service_page_content").get_child_by_id("delete_service_radio_set").get_child_by_id("delete_service_quiet_radio").value
            verbose = self.get_child_by_id("delete_service_page").get_child_by_id("delete_service_page_content").get_child_by_id("delete_service_radio_set").get_child_by_id("delete_service_verbose_radio").value
            
            output, errCode = be.delete_service(org_id, service_id, reg_addr, gas, index, quiet, verbose)
            popup_output = output
            self.app.push_screen(popup_output_page())

class client_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Client Page", id="client_page_title"),
                Horizontal(
                    Button(label="Call", id="client_page_call_button", classes="client_page_button"),
                    Button(label="Call low level", id="client_page_call_low_button", classes="client_page_button"),
                    id="client_page_upper_button_div",
                    classes="client_page_div"
                ),
                Horizontal(
                    Button(label="Channels", id="client_page_channel_button", classes="client_page_button"),
                    Button(label="Get channel state", id="client_page_channel_state_button", classes="client_page_button"),
                    id="client_page_lower_button_div",
                    classes="client_page_div"
                ),
                id="client_page_content",
                classes="content_page"
            ),
            id="client_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "client_page_call_button":
            self.app.push_screen(client_call_page())
        elif event.button.id == "client_page_call_low_button":
            self.app.push_screen(client_call_low_page())
        elif event.button.id == "client_page_channel_state_button":
            self.app.push_screen(client_channel_state_page())
        elif event.button.id == "client_page_channel_button":
            self.app.push_screen(channel_page())

class client_call_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Client Call Server Page", id="client_call_page_title"),
                Horizontal(
                    Label("Organization ID", id="client_call_org_id_label", classes="client_call_page_label"),
                    Input(placeholder="Id of the organization", id="client_call_org_id_input", classes="client_call_page_input"),
                    id="client_call_page_org_id_div",
                    classes="client_call_page_div"
                ),
                Horizontal(
                    Label("Service ID", id="client_call_service_id_label", classes="client_call_page_label"),
                    Input(placeholder="Id of service", id="client_call_service_id_input", classes="client_call_page_input"),
                    id="client_call_page_service_id_div",
                    classes="client_call_page_div"
                ),
                Horizontal(
                    Label("Service Method", id="client_call_method_label", classes="client_call_page_label"),
                    Input(placeholder="Target service's method name to call", id="client_call_method_input", classes="client_call_page_input"),
                    id="client_call_page_method_div",
                    classes="client_call_page_div"
                ),
                Horizontal(
                    Label("Parameters", id="client_call_params_label", classes="client_call_page_label"),
                    Input(placeholder="Path to file containing JSON-serialized parameters object", id="client_call_params_input", classes="client_call_page_input"),
                    id="client_call_page_params_div",
                    classes="client_call_page_div"
                ),
                Horizontal(
                    Label("Payment Group", id="client_call_pay_group_label", classes="client_call_page_label"),
                    Input(placeholder="Payment group of the service", id="client_call_pay_group_input", classes="client_call_page_input"),
                    id="client_call_page_pay_group_div",
                    classes="client_call_page_div"
                ),
                Horizontal(
                    Label("Proto Service", id="client_call_service_label", classes="client_call_page_label"),
                    Input(placeholder="[OPTIONAL] It should be specified in case of method name conflict.", id="client_call_service_input", classes="client_call_page_input"),
                    id="client_call_page_service_div",
                    classes="client_call_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="client_call_mpe_addr_label", classes="client_call_page_label"),
                    Input(placeholder="[OPTIONAL] If not specified we read address from “networks”", id="client_call_mpe_addr_input", classes="client_call_page_input"),
                    id="client_call_page_mpe_addr_div",
                    classes="client_call_page_div"
                ),
                Horizontal(
                    Label("Save File Path", id="client_call_file_name_label", classes="client_call_page_label"),
                    Input(placeholder="[OPTIONAL] Name/Path of file to save response to", id="client_call_save_file_name_input", classes="client_call_page_input"),
                    id="client_call_page_file_name_div",
                    classes="client_call_page_div"
                ),
                Horizontal(
                    Label("Service Endpoint", id="client_call_endpoint_label", classes="client_call_page_label"),
                    Input(placeholder="[OPTIONAL] (by default we read it from metadata)", id="client_call_endpoint_input", classes="client_call_page_input"),
                    id="client_call_page_endpoint_div",
                    classes="client_call_page_div"
                ),
                Horizontal(
                    Label("Channel ID", id="client_call_channel_id_label", classes="client_call_page_label"),
                    Input(placeholder="[OPTIONAL] (in case of multiple initialized channels for same payment group)", id="client_call_channel_id_input", classes="client_call_page_input"),
                    id="client_call_page_channel_id_div",
                    classes="client_call_page_div"
                ),
                Horizontal(
                    Label("Block Number", id="client_call_from_block_label", classes="client_call_page_label"),
                    Input(placeholder="[OPTIONAL] Start searching from this block (for channel searching). Default = 0", id="client_call_from_block_input", classes="client_call_page_input"),
                    id="client_call_page_from_block_div",
                    classes="client_call_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="client_call_wallet_index_label", classes="client_call_page_label"),
                    Input(placeholder="[OPTIONAL] (defaults to session.identity.default_wallet_index)", id="client_call_wallet_index_input", classes="client_call_page_input"),
                    id="client_call_page_wallet_index_div",
                    classes="client_call_page_div"
                ),
                RadioButton(label="Skip check for service update", id="client_call_skip_update_check_radio"),
                Horizontal(
                    Button(label="Back", id="client_call_back_button"),
                    Button(label="View Server Call Price", id="client_call_view_price_button"),
                    id="client_call_page_button_div",
                    classes="client_call_page_div"
                ),
                id="client_call_page_content",
                classes="content_page"
            ),
            id="client_call_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global conditional_output
        global conditional_command
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "client_call_back_button":
            self.app.pop_screen()
        elif event.button.id == "client_call_view_price_button":
            org_id = self.get_child_by_id("client_call_page").get_child_by_id("client_call_page_content").get_child_by_id("client_call_page_org_id_div").get_child_by_id("client_call_org_id_input").value
            serv_id = self.get_child_by_id("client_call_page").get_child_by_id("client_call_page_content").get_child_by_id("client_call_page_service_id_div").get_child_by_id("client_call_service_id_input").value
            group_name = self.get_child_by_id("client_call_page").get_child_by_id("client_call_page_content").get_child_by_id("client_call_page_pay_group_div").get_child_by_id("client_call_pay_group_input").value
            method = self.get_child_by_id("client_call_page").get_child_by_id("client_call_page_content").get_child_by_id("client_call_page_method_div").get_child_by_id("client_call_method_input").value
            params = self.get_child_by_id("client_call_page").get_child_by_id("client_call_page_content").get_child_by_id("client_call_page_params_div").get_child_by_id("client_call_params_input").value
            proto_serv = self.get_child_by_id("client_call_page").get_child_by_id("client_call_page_content").get_child_by_id("client_call_page_service_div").get_child_by_id("client_call_service_input").value
            mpe_addr = self.get_child_by_id("client_call_page").get_child_by_id("client_call_page_content").get_child_by_id("client_call_page_mpe_addr_div").get_child_by_id("client_call_mpe_addr_input").value
            file_name = self.get_child_by_id("client_call_page").get_child_by_id("client_call_page_content").get_child_by_id("client_call_page_file_name_div").get_child_by_id("client_call_save_file_name_input").value
            endpoint = self.get_child_by_id("client_call_page").get_child_by_id("client_call_page_content").get_child_by_id("client_call_page_endpoint_div").get_child_by_id("client_call_endpoint_input").value
            channel_id = self.get_child_by_id("client_call_page").get_child_by_id("client_call_page_content").get_child_by_id("client_call_page_channel_id_div").get_child_by_id("client_call_channel_id_input").value
            from_block = self.get_child_by_id("client_call_page").get_child_by_id("client_call_page_content").get_child_by_id("client_call_page_from_block_div").get_child_by_id("client_call_from_block_input").value
            wallet_index = self.get_child_by_id("client_call_page").get_child_by_id("client_call_page_content").get_child_by_id("client_call_page_wallet_index_div").get_child_by_id("client_call_wallet_index_input").value
            skip_update = self.get_child_by_id("client_call_page").get_child_by_id("client_call_page_content").get_child_by_id("client_call_skip_update_check_radio").value

            output, errCode, command = be.client_call(org_id, serv_id, group_name, method, params, proto_serv, mpe_addr, file_name, endpoint, channel_id, from_block, skip_update, wallet_index, True)

            if errCode == 0:
                conditional_output = output
                conditional_command = command
                self.app.push_screen(conditional_input_page())
            else:
                popup_output = output
                self.app.push_screen(popup_output_page())

class client_call_low_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Client Call Server (Low Level function) Page", id="client_call_low_page_title"),
                Horizontal(
                    Label("Organization ID", id="client_call_low_page_org_id_label", classes="client_call_low_page_label"),
                    Input(placeholder="Id of the organization", id="client_call_low_org_id_input", classes="client_call_low_page_input"),
                    id="client_call_low_page_org_id_div",
                    classes="client_call_low_page_div"
                ),
                Horizontal(
                    Label("Service ID", id="client_call_low_page_service_id_label", classes="client_call_low_page_label"),
                    Input(placeholder="Id of service", id="client_call_low_service_id_input", classes="client_call_low_page_input"),
                    id="client_call_low_page_service_id_div",
                    classes="client_call_low_page_div"
                ),
                Horizontal(
                    Label("Channel ID", id="client_call_low_page_channel_id_label", classes="client_call_low_page_label"),
                    Input(placeholder="The Channel Id", id="client_call_low_channel_id_input", classes="client_call_low_page_input"),
                    id="client_call_low_page_channel_id_div",
                    classes="client_call_low_page_div"
                ),
                Horizontal(
                    Label("Nonce", id="client_call_low_page_nonce_label", classes="client_call_low_page_label"),
                    Input(placeholder="Nonce of the channel", id="client_call_low_nonce_input", classes="client_call_low_page_input"),
                    id="client_call_low_page_nonce_div",
                    classes="client_call_low_page_div"
                ),
                Horizontal(
                    Label("Amount of COGS", id="client_call_low_page_cogs_label", classes="client_call_low_page_label"),
                    Input(placeholder="Amount in cogs", id="client_call_low_cogs_input", classes="client_call_low_page_input"),
                    id="client_call_low_page_cogs_div",
                    classes="client_call_low_page_div"
                ),
                Horizontal(
                    Label("Service Method", id="client_call_low_page_method_label", classes="client_call_low_page_label"),
                    Input(placeholder="Target service's method name to call", id="client_call_low_method_input", classes="client_call_low_page_input"),
                    id="client_call_low_page_method_div",
                    classes="client_call_low_page_div"
                ),
                Horizontal(
                    Label("Parameters", id="client_call_low_page_params_label", classes="client_call_low_page_label"),
                    Input(placeholder="Path to file containing JSON-serialized parameters object", id="client_call_low_params_input", classes="client_call_low_page_input"),
                    id="client_call_low_page_params_div",
                    classes="client_call_low_page_div"
                ),
                Horizontal(
                    Label("Payment Group", id="client_call_low_page_pay_group_label", classes="client_call_low_page_label"),
                    Input(placeholder="Name of the payment group", id="client_call_low_pay_group_input", classes="client_call_low_page_input"),
                    id="client_call_low_page_pay_group_div",
                    classes="client_call_low_page_div"
                ),
                Horizontal(
                    Label("Proto Service", id="client_call_low_page_service_label", classes="client_call_low_page_label"),
                    Input(placeholder="[OPTIONAL] Name of protobuf service to call. It should be specified in case of method name conflict.", id="client_call_low_service_input", classes="client_call_low_page_input"),
                    id="client_call_low_page_service_div",
                    classes="client_call_low_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="client_call_low_page_mpe_addr_label", classes="client_call_low_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from “networks”", id="client_call_low_mpe_addr_input", classes="client_call_low_page_input"),
                    id="client_call_low_page_mpe_addr_div",
                    classes="client_call_low_page_div"
                ),
                Horizontal(
                    Label("File Path", id="client_call_low_page_file_name_label", classes="client_call_low_page_label"),
                    Input(placeholder="[OPTIONAL] Path/Name of file to save response to", id="client_call_low_save_file_name_input", classes="client_call_low_page_input"),
                    id="client_call_low_page_file_name_div",
                    classes="client_call_low_page_div"
                ),
                Horizontal(
                    Label("Service Endpoint", id="client_call_low_page_service_endpoint_label", classes="client_call_low_page_label"),
                    Input(placeholder="[OPTIONAL] Service endpoint (by default we read it from metadata)", id="client_call_low_endpoint_input", classes="client_call_low_page_input"),
                    id="client_call_low_page_endpoint_div",
                    classes="client_call_low_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="client_call_low_page_wallet_index_label", classes="client_call_low_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for calling (defaults to session.identity.default_wallet_index)", id="client_call_low_wallet_index_input", classes="client_call_low_page_input"),
                    id="client_call_low_page_wallet_index_div",
                    classes="client_call_low_page_div"
                ),
                Horizontal(
                    Button(label="Back", id="client_call_low_back_button"),
                    Button(label="View Server Low-Level Call Price", id="client_call_low_view_price_button"),
                    id="client_call_low_page_button_div",
                    classes="client_call_low_page_div"
                ),
                id="client_call_low_page_content",
                classes="content_page"
            ),
            id="client_call_low_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global conditional_command
        global conditional_output
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "client_call_low_back_button":
            self.app.pop_screen()
        elif event.button.id == "client_call_low_view_price_button":
            org_id = self.get_child_by_id("client_call_low_page").get_child_by_id("client_call_low_page_content").get_child_by_id("client_call_low_page_org_id_div").get_child_by_id("client_call_low_org_id_input").value
            serv_id = self.get_child_by_id("client_call_low_page").get_child_by_id("client_call_low_page_content").get_child_by_id("client_call_low_page_service_id_div").get_child_by_id("client_call_low_service_id_input").value
            group_name = self.get_child_by_id("client_call_low_page").get_child_by_id("client_call_low_page_content").get_child_by_id("client_call_low_page_pay_group_div").get_child_by_id("client_call_low_pay_group_input").value
            channel_id = self.get_child_by_id("client_call_low_page").get_child_by_id("client_call_low_page_content").get_child_by_id("client_call_low_page_channel_id_div").get_child_by_id("client_call_low_channel_id_input").value
            nonce = self.get_child_by_id("client_call_low_page").get_child_by_id("client_call_low_page_content").get_child_by_id("client_call_low_page_nonce_div").get_child_by_id("client_call_low_nonce_input").value
            cog_amt = self.get_child_by_id("client_call_low_page").get_child_by_id("client_call_low_page_content").get_child_by_id("client_call_low_page_cogs_div").get_child_by_id("client_call_low_cogs_input").value
            method = self.get_child_by_id("client_call_low_page").get_child_by_id("client_call_low_page_content").get_child_by_id("client_call_low_page_method_div").get_child_by_id("client_call_low_method_input").value
            params = self.get_child_by_id("client_call_low_page").get_child_by_id("client_call_low_page_content").get_child_by_id("client_call_low_page_params_div").get_child_by_id("client_call_low_params_input").value
            proto_serv = self.get_child_by_id("client_call_low_page").get_child_by_id("client_call_low_page_content").get_child_by_id("client_call_low_page_service_div").get_child_by_id("client_call_low_service_input").value
            mpe_addr = self.get_child_by_id("client_call_low_page").get_child_by_id("client_call_low_page_content").get_child_by_id("client_call_low_page_mpe_addr_div").get_child_by_id("client_call_low_mpe_addr_input").value
            file_name = self.get_child_by_id("client_call_low_page").get_child_by_id("client_call_low_page_content").get_child_by_id("client_call_low_page_file_name_div").get_child_by_id("client_call_low_save_file_name_input").value
            endpoint = self.get_child_by_id("client_call_low_page").get_child_by_id("client_call_low_page_content").get_child_by_id("client_call_low_page_endpoint_div").get_child_by_id("client_call_low_endpoint_input").value
            wallet_index = self.get_child_by_id("client_call_low_page").get_child_by_id("client_call_low_page_content").get_child_by_id("client_call_low_page_wallet_index_div").get_child_by_id("client_call_low_wallet_index_input").value

            output, errCode = be.client_low_call(org_id, serv_id, group_name, channel_id, nonce, cog_amt, method, params, proto_serv, mpe_addr, file_name, endpoint, wallet_index)
            popup_output = output
            self.app.push_screen(popup_output_page())

class client_channel_state_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Client Channel State Page", id="client_channel_state_page_title"),
                Horizontal(
                    Label("Channel ID", id="client_channel_state_page_channel_id_label", classes="client_channel_state_page_label"),
                    Input(placeholder="The Channel Id", id="client_channel_state_id_input", classes="client_channel_state_page_input"),
                    id="client_channel_state_page_channel_id_div",
                    classes="client_channel_state_page_div"
                ),
                
                Horizontal(
                    Label("Service Endpoint", id="client_channel_state_page_endpoint_label", classes="client_channel_state_page_label"),
                    Input(placeholder="Service endpoint", id="client_channel_state_endpoint_input", classes="client_channel_state_page_input"),
                    id="client_channel_state_page_endpoint_div",
                    classes="client_channel_state_page_div"
                ),
                
                Horizontal(
                    Label("MPE Address", id="client_channel_state_page_mpe_addr_label", classes="client_channel_state_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from “networks”", id="client_channel_state_mpe_addr_input", classes="client_channel_state_page_input"),
                    id="client_channel_state_page_mpe_addr_div",
                    classes="client_channel_state_page_div"
                ),
                
                Horizontal(
                    Label("Wallet Index", id="client_channel_state_page_wallet_index_label", classes="client_channel_state_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for calling (defaults to session.identity.default_wallet_index)", id="client_channel_state_wallet_index_input", classes="client_channel_state_page_input"),
                    id="client_channel_state_page_wallet_index_div",
                    classes="client_channel_state_page_div"
                ),
                Horizontal(
                    Button(label="Back", id="client_channel_state_back_button"),
                    Button(label="Get Channel State", id="client_channel_state_submit_button"),
                    id="client_channel_state_page_button_div",
                    classes="client_channel_state_page_div"
                ),
                id="client_channel_state_page_content",
                classes="content_page"
            ),
            id="client_channel_state_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global conditional_command
        global conditional_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "client_channel_state_back_button":
            self.app.pop_screen()
        elif event.button.id == "client_channel_state_submit_button":
            channel_id = self.get_child_by_id("client_channel_state_page").get_child_by_id("client_channel_state_page_content").get_child_by_id("client_channel_state_page_channel_id_div").get_child_by_id("client_channel_state_id_input").value
            endpoint = self.get_child_by_id("client_channel_state_page").get_child_by_id("client_channel_state_page_content").get_child_by_id("client_channel_state_page_endpoint_div").get_child_by_id("client_channel_state_endpoint_input").value
            mpe_addr = self.get_child_by_id("client_channel_state_page").get_child_by_id("client_channel_state_page_content").get_child_by_id("client_channel_state_page_mpe_addr_div").get_child_by_id("client_channel_state_mpe_addr_input").value
            wallet_index = self.get_child_by_id("client_channel_state_page").get_child_by_id("client_channel_state_page_content").get_child_by_id("client_channel_state_page_wallet_index_div").get_child_by_id("client_channel_state_wallet_index_input").value

            output, errCode = be.get_channel_state(channel_id, endpoint, mpe_addr, wallet_index)
            popup_output = output
            self.app.push_screen(popup_output_page())

class channel_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Channel Page", id="channel_page_title"),
                Horizontal(
                    Button(label="Initialize/Open", id="channel_page_init_open_button", classes="channel_page_button"),
                    Button(label="Extend", id="channel_page_extend_button", classes="channel_page_button"),
                    id="channel_page_upper_button_div",
                    classes="channel_page_div"
                ),
                
                Horizontal(
                    Button(label="Print", id="channel_page_print_button", classes="channel_page_button"),
                    Button(label="Claim", id="channel_page_claim_button", classes="channel_page_button"),
                    id="channel_page_lower_button_div",
                    classes="channel_page_div"
                ),
                Button(label="Back", id="channel_page_back_button"),
                id="channel_page_content",
                classes="content_page"
            ),
            id="channel_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_page_init_open_button":
            self.app.push_screen(channel_init_open_page())
        elif event.button.id == "channel_page_extend_button":
            self.app.push_screen(channel_extend_page())
        elif event.button.id == "channel_page_print_button":
            self.app.push_screen(channel_print_page())
        elif event.button.id == "channel_page_claim_button":
            self.app.push_screen(channel_claim_page())
    
class channel_init_open_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Channel Initialize/Open Page", id="channel_init_open_page_title"),
                Horizontal(
                    Button(label="Initialize", id="channel_init_open_page_init_button", classes="channel_init_open_page_button"),
                    Button(label="Initialize Metadata", id="channel_init_open_page_init_meta_button", classes="channel_init_open_page_button"),
                    id="channel_init_open_page_upper_button_div",
                    classes="channel_init_open_page_div"
                ),
                Horizontal(
                    Button(label="Open Initialize", id="channel_init_open_page_open_init_button", classes="channel_init_open_page_button"),
                    Button(label="Open Initialize Metadata", id="channel_init_open_page_open_init_meta_button", classes="channel_init_open_page_button"),
                    id="channel_init_open_page_lower_button_div",
                    classes="channel_init_open_page_div"
                ),
                Button(label="Back", id="channel_init_open_page_back_button"),
                id="channel_init_open_page_content",
                classes="content_page"
            ),
            id="channel_init_open_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_init_open_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_init_open_page_init_button":
            self.app.push_screen(channel_init_page())
        elif event.button.id == "channel_init_open_page_init_meta_button":
            self.app.push_screen(channel_init_metadata_page())
        elif event.button.id == "channel_init_open_page_open_init_button":
            self.app.push_screen(channel_open_init_page())
        elif event.button.id == "channel_init_open_page_open_init_meta_button":
            self.app.push_screen(channel_open_init_meta_page())

class channel_init_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Channel Initialize Page", id="channel_init_page_title"),
                Horizontal(
                    Label("Organization ID", id="channel_init_page_org_id_label", classes="channel_init_page_label"),
                    Input(placeholder="Id of the Organization", id="channel_init_page_org_id_input", classes="channel_init_page_input"),
                    id="channel_init_page_org_id_div",
                    classes="channel_init_page_div"
                ),
                Horizontal(
                    Label("Channel ID", id="channel_init_page_channel_id_label", classes="channel_init_page_label"),
                    Input(placeholder="The Channel Id", id="channel_init_page_channel_id_input", classes="channel_init_page_input"),
                    id="channel_init_page_channel_id_div",
                    classes="channel_init_page_div"
                ),
                Horizontal(
                    Label("Payment Group", id="channel_init_page_group_label", classes="channel_init_page_label"),
                    Input(placeholder="Name of the payment group", id="channel_init_page_group_input", classes="channel_init_page_input"),
                    id="channel_init_page_group_div",
                    classes="channel_init_page_div"
                ),
                Horizontal(
                    Label("Registry Address", id="channel_init_page_registry_label", classes="channel_init_page_label"),
                    Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from “networks”", id="channel_init_page_registry_input", classes="channel_init_page_input"),
                    id="channel_init_page_registry_div",
                    classes="channel_init_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="channel_init_page_mpe_addr_label", classes="channel_init_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from “networks”", id="channel_init_page_mpe_addr_input", classes="channel_init_page_input"),
                    id="channel_init_page_mpe_addr_div",
                    classes="channel_init_page_div"
                ),
                Horizontal(
                    Button(label="Back", id="channel_init_page_back_button"),
                    Button(label="Initialize", id="channel_init_print_confirm_button"),
                    id="channel_init_page_button_div",
                    classes="channel_init_page_div"
                ),
                id="channel_init_content_page",
                classes="content_page"
            ),
            id="channel_init_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_init_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_init_print_confirm_button":
            org_id = self.get_child_by_id("channel_init_page").get_child_by_id("channel_init_content_page").get_child_by_id("channel_init_page_org_id_div").get_child_by_id("channel_init_page_org_id_input").value
            group = self.get_child_by_id("channel_init_page").get_child_by_id("channel_init_content_page").get_child_by_id("channel_init_page_group_div").get_child_by_id("channel_init_page_group_input").value
            channel_id = self.get_child_by_id("channel_init_page").get_child_by_id("channel_init_content_page").get_child_by_id("channel_init_page_channel_id_div").get_child_by_id("channel_init_page_channel_id_input").value
            registry = self.get_child_by_id("channel_init_page").get_child_by_id("channel_init_content_page").get_child_by_id("channel_init_page_registry_div").get_child_by_id("channel_init_page_registry_input").value
            mpe_addr = self.get_child_by_id("channel_init_page").get_child_by_id("channel_init_content_page").get_child_by_id("channel_init_page_mpe_addr_div").get_child_by_id("channel_init_page_mpe_addr_input").value

            client_nav_button = self.get_child_by_id("channel_init_page").get_child_by_id("nav_sidebar").get_child_by_id("client_page_nav")

            output, errCode = be.channel_init(org_id, group, channel_id, registry, mpe_addr)
            popup_output = output
            client_nav_button.focus()
            self.app.push_screen(popup_output_page())

class channel_init_metadata_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Channel Initialize Metadata Page", id="channel_init_metadata_page_title"),
                Horizontal(
                    Label("Organization ID", id="channel_init_metadata_page_org_id_label", classes="channel_init_metadata_page_label"),
                    Input(placeholder="Id of the Organization", id="channel_init_metadata_page_org_id_input", classes="channel_init_metadata_page_input"),
                    id="channel_init_metadata_page_org_id_div",
                    classes="channel_init_metadata_page_div"
                ),
                Horizontal(
                    Label("Channel ID", id="channel_init_metadata_page_channel_id_label", classes="channel_init_metadata_page_label"),
                    Input(placeholder="The Channel Id", id="channel_init_metadata_page_channel_id_input", classes="channel_init_metadata_page_input"),
                    id="channel_init_metadata_page_channel_id_div",
                    classes="channel_init_metadata_page_div"
                ),
                Horizontal(
                    Label("Metadata Path", id="channel_init_metadata_page_file_path_label", classes="channel_init_metadata_page_label"),
                    Input(placeholder="Service metadata json file path", id="channel_init_metadata_page_file_path_input", classes="channel_init_metadata_page_input"),
                    id="channel_init_metadata_page_file_path_div",
                    classes="channel_init_metadata_page_div"
                ),
                Horizontal(
                    Label("Payment Group", id="channel_init_metadata_page_group_label", classes="channel_init_metadata_page_label"),
                    Input(placeholder="Name of the payment group", id="channel_init_metadata_page_group_input", classes="channel_init_metadata_page_input"),
                    id="channel_init_metadata_page_group_div",
                    classes="channel_init_metadata_page_div"
                ),
                Horizontal(
                    Label("Registry Address", id="channel_init_metadata_page_registry_label", classes="channel_init_metadata_page_label"),
                    Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from “networks”", id="channel_init_metadata_page_registry_input", classes="channel_init_metadata_page_input"),
                    id="channel_init_metadata_page_registry_div",
                    classes="channel_init_metadata_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="channel_init_metadata_page_mpe_addr_label", classes="channel_init_metadata_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from “networks”", id="channel_init_metadata_page_mpe_addr_input", classes="channel_init_metadata_page_input"),
                    id="channel_init_metadata_page_mpe_addr_div",
                    classes="channel_init_metadata_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="channel_init_metadata_page_wallet_index_label", classes="channel_init_metadata_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for calling (defaults to session.identity.default_wallet_index)", id="channel_init_metadata_page_wallet_index_input", classes="channel_init_metadata_page_input"),
                    id="channel_init_metadata_page_wallet_index_div",
                    classes="channel_init_metadata_page_div"
                ),
                Horizontal(
                    Button(label="Back", id="channel_init_metadata_page_back_button"),
                    Button(label="Initialize", id="channel_init_metadata_print_confirm_button"),
                    id="channel_init_metadata_page_button_div",
                    classes="channel_init_metadata_page_div"
                ),
                id="channel_init_metadata_content_page",
                classes="content_page"
            ),
            id="channel_init_metadata_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_init_metadata_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_init_metadata_print_confirm_button":
            org_id = self.get_child_by_id("channel_init_metadata_page").get_child_by_id("channel_init_metadata_content_page").get_child_by_id("channel_init_metadata_page_org_id_div").get_child_by_id("channel_init_metadata_page_org_id_input").value
            group = self.get_child_by_id("channel_init_metadata_page").get_child_by_id("channel_init_metadata_content_page").get_child_by_id("channel_init_metadata_page_group_div").get_child_by_id("channel_init_metadata_page_group_input").value
            channel_id = self.get_child_by_id("channel_init_metadata_page").get_child_by_id("channel_init_metadata_content_page").get_child_by_id("channel_init_metadata_page_channel_id_div").get_child_by_id("channel_init_metadata_page_channel_id_input").value
            registry = self.get_child_by_id("channel_init_metadata_page").get_child_by_id("channel_init_metadata_content_page").get_child_by_id("channel_init_metadata_page_registry_div").get_child_by_id("channel_init_metadata_page_registry_input").value
            meta_file = self.get_child_by_id("channel_init_metadata_page").get_child_by_id("channel_init_metadata_content_page").get_child_by_id("channel_init_metadata_page_file_path_div").get_child_by_id("channel_init_metadata_page_file_path_input").value
            mpe_addr = self.get_child_by_id("channel_init_metadata_page").get_child_by_id("channel_init_metadata_content_page").get_child_by_id("channel_init_metadata_page_mpe_addr_div").get_child_by_id("channel_init_metadata_page_mpe_addr_input").value
            wallet_index = self.get_child_by_id("channel_init_metadata_page").get_child_by_id("channel_init_metadata_content_page").get_child_by_id("channel_init_metadata_page_wallet_index_div").get_child_by_id("channel_init_metadata_page_wallet_index_input").value

            client_nav_button = self.get_child_by_id("channel_init_metadata_page").get_child_by_id("nav_sidebar").get_child_by_id("client_page_nav")

            output, errCode = be.channel_init_metadata(org_id, group, channel_id, registry, mpe_addr, meta_file, wallet_index)
            popup_output = output
            client_nav_button.focus()
            self.app.push_screen(popup_output_page())

class channel_open_init_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Channel Open Initialize Page", id="channel_open_init_page_title"),
                Horizontal(
                    Label("Organization ID", id="channel_open_init_page_org_id_label", classes="channel_open_init_page_label"),
                    Input(placeholder="Id of the Organization", id="channel_open_init_page_org_id_input", classes="channel_open_init_page_input"),
                    id="channel_open_init_page_org_id_div",
                    classes="channel_open_init_page_div"
                ),
                Horizontal(
                    Label("Payment Group", id="channel_open_init_page_group_label", classes="channel_open_init_page_label"),
                    Input(placeholder="Name of the payment group", id="channel_open_init_page_group_input", classes="channel_open_init_page_input"),
                    id="channel_open_init_page_group_div",
                    classes="channel_open_init_page_div"
                ),
                Horizontal(
                    Label("AGI Amount", id="channel_open_init_page_agi_amount_label", classes="channel_open_init_page_label"),
                    Input(placeholder="Amount of AGI tokens to put in the new channel", id="channel_open_init_page_agi_amount_input", classes="channel_open_init_page_input"),
                    id="channel_open_init_page_agi_amount_div",
                    classes="channel_open_init_page_div"
                ),
                Horizontal(
                    Label("Expiration Time", id="channel_open_init_page_expr_label", classes="channel_open_init_page_label"),
                    Input(placeholder="Expiration time in blocks (<int>), or in blocks related to the current_block (+<int>blocks), or in days related to the current_block and assuming 15 sec/block (+<int>days)", id="channel_open_init_page_expr_input", classes="channel_open_init_page_input"),
                    id="channel_open_init_page_expr_div",
                    classes="channel_open_init_page_div"
                ),
                Horizontal(
                    Label("Registry Address", id="channel_open_init_page_registry_label", classes="channel_open_init_page_label"),
                    Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from “networks”", id="channel_open_init_page_registry_input", classes="channel_open_init_page_input"),
                    id="channel_open_init_page_registry_div",
                    classes="channel_open_init_page_div"
                ),
                Horizontal(
                    Label("Signer Address", id="channel_open_init_page_signer_label", classes="channel_open_init_page_label"),
                    Input(placeholder="[OPTIONAL] Signer for the channel (by default is equal to the sender)", id="channel_open_init_page_signer_input", classes="channel_open_init_page_input"),
                    id="channel_open_init_page_signer_div",
                    classes="channel_open_init_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="channel_open_init_page_mpe_addr_label", classes="channel_open_init_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from “networks”", id="channel_open_init_page_mpe_addr_input", classes="channel_open_init_page_input"),
                    id="channel_open_init_page_mpe_addr_div",
                    classes="channel_open_init_page_div"
                ),
                Horizontal(
                    Label("Block Number", id="channel_open_init_page_block_label", classes="channel_open_init_page_label"),
                    Input(placeholder="[OPTIONAL] Start searching from this block (for channel searching)", id="channel_open_init_page_block_input", classes="channel_open_init_page_input"),
                    id="channel_open_init_page_block_div",
                    classes="channel_open_init_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="channel_open_init_page_gas_label", classes="channel_open_init_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy (‘fast’ ~1min, ‘medium’ ~5min or ‘slow’ ~60min) (defaults to session.default_gas_price)", id="channel_open_init_page_gas_input", classes="channel_open_init_page_input"),
                    id="channel_open_init_page_gas_div",
                    classes="channel_open_init_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="channel_open_init_page_wallet_index_label", classes="channel_open_init_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="channel_open_init_page_wallet_index_input", classes="channel_open_init_page_input"),
                    id="channel_open_init_page_wallet_index_div",
                    classes="channel_open_init_page_div"
                ),
                RadioButton(label="Force", id="channel_open_init_page_force_radio"),
                RadioButton(label="Open New Anyway", id="channel_open_init_page_new_anyway_radio"),
                RadioSet(
                    RadioButton(label="Quiet Print", id="channel_open_init_page_quiet_radio"),
                    RadioButton(label="Verbose Print", id="channel_open_init_page_verbose_radio"),
                    id="channel_open_init_page_quiet_verbose_set"
                ),
                Horizontal(
                    Button(label="Back", id="channel_open_init_page_back_button"),
                    Button(label="Open and Initialize", id="channel_open_init_page_confirm_button"),
                    id="channel_open_init_page_button_div",
                    classes="channel_open_init_page_div"
                ),
                id="channel_open_init_content_page",
                classes="content_page"
            ),
            id="channel_open_init_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_open_init_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_open_init_page_confirm_button":
            global conditional_command
            global conditional_output
            global popup_output

            org_id = self.get_child_by_id("channel_open_init_page").get_child_by_id("channel_open_init_content_page").get_child_by_id("channel_open_init_page_org_id_div").get_child_by_id("channel_open_init_page_org_id_input").value
            group = self.get_child_by_id("channel_open_init_page").get_child_by_id("channel_open_init_content_page").get_child_by_id("channel_open_init_page_group_div").get_child_by_id("channel_open_init_page_group_input").value
            agi_amount = self.get_child_by_id("channel_open_init_page").get_child_by_id("channel_open_init_content_page").get_child_by_id("channel_open_init_page_agi_amount_div").get_child_by_id("channel_open_init_page_agi_amount_input").value
            expr = self.get_child_by_id("channel_open_init_page").get_child_by_id("channel_open_init_content_page").get_child_by_id("channel_open_init_page_expr_div").get_child_by_id("channel_open_init_page_expr_input").value
            registry = self.get_child_by_id("channel_open_init_page").get_child_by_id("channel_open_init_content_page").get_child_by_id("channel_open_init_page_registry_div").get_child_by_id("channel_open_init_page_registry_input").value
            mpe_addr = self.get_child_by_id("channel_open_init_page").get_child_by_id("channel_open_init_content_page").get_child_by_id("channel_open_init_page_mpe_addr_div").get_child_by_id("channel_open_init_page_mpe_addr_input").value
            signer = self.get_child_by_id("channel_open_init_page").get_child_by_id("channel_open_init_content_page").get_child_by_id("channel_open_init_page_signer_div").get_child_by_id("channel_open_init_page_signer_input").value
            block = self.get_child_by_id("channel_open_init_page").get_child_by_id("channel_open_init_content_page").get_child_by_id("channel_open_init_page_block_div").get_child_by_id("channel_open_init_page_block_input").value
            gas = self.get_child_by_id("channel_open_init_page").get_child_by_id("channel_open_init_content_page").get_child_by_id("channel_open_init_page_gas_div").get_child_by_id("channel_open_init_page_gas_input").value
            wallet_index = self.get_child_by_id("channel_open_init_page").get_child_by_id("channel_open_init_content_page").get_child_by_id("channel_open_init_page_wallet_index_div").get_child_by_id("channel_open_init_page_wallet_index_input").value
            force = self.get_child_by_id("channel_open_init_page").get_child_by_id("channel_open_init_content_page").get_child_by_id("channel_open_init_page_force_radio").value
            open_anyway = self.get_child_by_id("channel_open_init_page").get_child_by_id("channel_open_init_content_page").get_child_by_id("channel_open_init_page_new_anyway_radio").value
            quiet = self.get_child_by_id("channel_open_init_page").get_child_by_id("channel_open_init_content_page").get_child_by_id("channel_open_init_page_quiet_verbose_set").get_child_by_id("channel_open_init_page_quiet_radio").value
            verbose = self.get_child_by_id("channel_open_init_page").get_child_by_id("channel_open_init_content_page").get_child_by_id("channel_open_init_page_quiet_verbose_set").get_child_by_id("channel_open_init_page_verbose_radio").value

            client_nav_button = self.get_child_by_id("channel_open_init_page").get_child_by_id("nav_sidebar").get_child_by_id("client_page_nav")

            output, errCode, command = be.channel_open_init(org_id, group, agi_amount, expr, registry, force, signer, mpe_addr, open_anyway, block, gas, wallet_index, quiet, verbose, True)

            if errCode == 0:
                conditional_output = output
                conditional_command = command
                client_nav_button.focus()
                self.app.push_screen(conditional_input_page())
            else:
                popup_output = output
                client_nav_button.focus()
                self.app.push_screen(popup_output_page())

class channel_open_init_meta_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Channel Open Initialize Metadata Page", id="channel_open_init_meta_page_title"),
                Horizontal(
                    Label("Organization ID", id="channel_open_init_meta_page_org_id_label", classes="channel_open_init_meta_page_label"),
                    Input(placeholder="Id of the Organization", id="channel_open_init_meta_page_org_id_input", classes="channel_open_init_meta_page_input"),
                    id="channel_open_init_meta_page_org_id_div",
                    classes="channel_open_init_meta_page_div"
                ),
                Horizontal(
                    Label("Payment Group", id="channel_open_init_meta_page_group_label", classes="channel_open_init_meta_page_label"),
                    Input(placeholder="Name of the payment group.", id="channel_open_init_meta_page_group_input", classes="channel_open_init_meta_page_input"),
                    id="channel_open_init_meta_page_group_div",
                    classes="channel_open_init_meta_page_div"
                ),
                Horizontal(
                    Label("AGI Amount", id="channel_open_init_meta_page_agi_amount_label", classes="channel_open_init_meta_page_label"),
                    Input(placeholder="Amount of AGI tokens to put in the new channel", id="channel_open_init_meta_page_agi_amount_input", classes="channel_open_init_meta_page_input"),
                    id="channel_open_init_meta_page_agi_amount_div",
                    classes="channel_open_init_meta_page_div"
                ),
                Horizontal(
                    Label("Expiration Time", id="channel_open_init_meta_page_expr_label", classes="channel_open_init_meta_page_label"),
                    Input(placeholder="Expiration time in blocks (<int>), or in blocks related to the current_block (+<int>blocks), or in days related to the current_block and assuming 15 sec/block (+<int>days)", id="channel_open_init_meta_page_expr_input", classes="channel_open_init_meta_page_input"),
                    id="channel_open_init_meta_page_expr_div",
                    classes="channel_open_init_meta_page_div"
                ),
                Horizontal(
                    Label("Metadata Path", id="channel_open_init_meta_page_meta_path_label", classes="channel_open_init_meta_page_label"),
                    Input(placeholder="Service metadata json file path", id="channel_open_init_meta_page_meta_path_input", classes="channel_open_init_meta_page_input"),
                    id="channel_open_init_meta_page_meta_path_div",
                    classes="channel_open_init_meta_page_div"
                ),
                Horizontal(
                    Label("Registry Address", id="channel_open_init_meta_page_registry_label", classes="channel_open_init_meta_page_label"),
                    Input(placeholder="[OPTIONAL] Address of Registry contract, if not specified we read address from “networks”", id="channel_open_init_meta_page_registry_input", classes="channel_open_init_meta_page_input"),
                    id="channel_open_init_meta_page_registry_div",
                    classes="channel_open_init_meta_page_div"
                ),
                Horizontal(
                    Label("Signer Address", id="channel_open_init_meta_page_signer_label", classes="channel_open_init_meta_page_label"),
                    Input(placeholder="[OPTIONAL] Signer for the channel (by default is equal to the sender)", id="channel_open_init_meta_page_signer_input", classes="channel_open_init_meta_page_input"),
                    id="channel_open_init_meta_page_signer_div",
                    classes="channel_open_init_meta_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="channel_open_init_meta_page_mpe_addr_label", classes="channel_open_init_meta_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from “networks”", id="channel_open_init_meta_page_mpe_addr_input", classes="channel_open_init_meta_page_input"),
                    id="channel_open_init_meta_page_mpe_addr_div",
                    classes="channel_open_init_meta_page_div"
                ),
                Horizontal(
                    Label("Start Block", id="channel_open_init_meta_page_block_label", classes="channel_open_init_meta_page_label"),
                    Input(placeholder="[OPTIONAL] Start searching from this block (for channel searching)", id="channel_open_init_meta_page_block_input", classes="channel_open_init_meta_page_input"),
                    id="channel_open_init_meta_page_block_div",
                    classes="channel_open_init_meta_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="channel_open_init_meta_page_gas_label", classes="channel_open_init_meta_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy (‘fast’ ~1min, ‘medium’ ~5min or ‘slow’ ~60min) (defaults to session.default_gas_price)", id="channel_open_init_meta_page_gas_input", classes="channel_open_init_meta_page_input"),
                    id="channel_open_init_meta_page_gas_div",
                    classes="channel_open_init_meta_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="channel_open_init_meta_page_wallet_index_label", classes="channel_open_init_meta_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing (defaults to session.identity.default_wallet_index)", id="channel_open_init_meta_page_wallet_index_input", classes="channel_open_init_meta_page_input"),
                    id="channel_open_init_meta_page_wallet_index_div",
                    classes="channel_open_init_meta_page_div"
                ),
                RadioButton(label="Force", id="channel_open_init_meta_page_force_radio"),
                RadioButton(label="Open New Anyway", id="channel_open_init_meta_page_new_anyway_radio"),
                RadioSet(
                    RadioButton(label="Quiet Print", id="channel_open_init_meta_page_quiet_radio"),
                    RadioButton(label="Verbose Print", id="channel_open_init_meta_page_verbose_radio"),
                    id="channel_open_init_meta_page_quiet_verbose_set"
                ),
                Horizontal(
                    Button(label="Back", id="channel_open_init_meta_page_back_button"),
                    Button(label="Open and Initialize", id="channel_open_init_meta_page_confirm_button"),
                    id="channel_open_init_meta_page_button_div",
                    classes="channel_open_init_meta_page_div"
                ),
                id="channel_open_init_meta_content_page",
                classes="content_page"
            ),
            id="channel_open_init_meta_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_open_init_meta_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_open_init_meta_page_confirm_button":
            global conditional_command
            global conditional_output
            global popup_output

            org_id = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("channel_open_init_meta_content_page").get_child_by_id("channel_open_init_meta_page_org_id_div").get_child_by_id("channel_open_init_meta_page_org_id_input").value
            group = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("channel_open_init_meta_content_page").get_child_by_id("channel_open_init_meta_page_group_div").get_child_by_id("channel_open_init_meta_page_group_input").value
            agi_amount = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("channel_open_init_meta_content_page").get_child_by_id("channel_open_init_meta_page_agi_amount_div").get_child_by_id("channel_open_init_meta_page_agi_amount_input").value
            expr = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("channel_open_init_meta_content_page").get_child_by_id("channel_open_init_meta_page_expr_div").get_child_by_id("channel_open_init_meta_page_expr_input").value
            meta_path = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("channel_open_init_meta_content_page").get_child_by_id("channel_open_init_meta_page_meta_path_div").get_child_by_id("channel_open_init_meta_page_meta_path_input").value
            registry = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("channel_open_init_meta_content_page").get_child_by_id("channel_open_init_meta_page_registry_div").get_child_by_id("channel_open_init_meta_page_registry_input").value
            mpe_addr = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("channel_open_init_meta_content_page").get_child_by_id("channel_open_init_meta_page_mpe_addr_div").get_child_by_id("channel_open_init_meta_page_mpe_addr_input").value
            signer = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("channel_open_init_meta_content_page").get_child_by_id("channel_open_init_meta_page_signer_div").get_child_by_id("channel_open_init_meta_page_signer_input").value
            block = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("channel_open_init_meta_content_page").get_child_by_id("channel_open_init_meta_page_block_div").get_child_by_id("channel_open_init_meta_page_block_input").value
            gas = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("channel_open_init_meta_content_page").get_child_by_id("channel_open_init_meta_page_gas_div").get_child_by_id("channel_open_init_meta_page_gas_input").value
            wallet_index = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("channel_open_init_meta_content_page").get_child_by_id("channel_open_init_meta_page_wallet_index_div").get_child_by_id("channel_open_init_meta_page_wallet_index_input").value
            force = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("channel_open_init_meta_content_page").get_child_by_id("channel_open_init_meta_page_force_radio").value
            open_anyway = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("channel_open_init_meta_content_page").get_child_by_id("channel_open_init_meta_page_new_anyway_radio").value
            quiet = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("channel_open_init_meta_content_page").get_child_by_id("channel_open_init_meta_page_quiet_verbose_set").get_child_by_id("channel_open_init_meta_page_quiet_radio").value
            verbose = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("channel_open_init_meta_content_page").get_child_by_id("channel_open_init_meta_page_quiet_verbose_set").get_child_by_id("channel_open_init_meta_page_verbose_radio").value

            client_nav_button = self.get_child_by_id("channel_open_init_meta_page").get_child_by_id("nav_sidebar").get_child_by_id("client_page_nav")

            output, errCode, command = be.channel_open_init_metadata(org_id, group, agi_amount, expr, registry, force, signer, mpe_addr, open_anyway, block, meta_path, gas, wallet_index, quiet, verbose, True)

            if errCode == 0:
                conditional_output = output
                conditional_command = command
                client_nav_button.focus()
                self.app.push_screen(conditional_input_page())
            else:
                popup_output = output
                client_nav_button.focus()
                self.app.push_screen(popup_output_page())

class channel_extend_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Channel Extend Page", id="channel_extend_page_title"),
                Horizontal(
                    Button(label="Extend Add", id="channel_extend_page_extend_add_button", classes="channel_extend_page_button"),
                    Button(label="Extend Add Org", id="channel_extend_page_extend_add_org_button", classes="channel_extend_page_button"),
                    id="channel_extend_page_button_div",
                    classes="channel_extend_page_div"
                ),
                Button(label="Back", id="channel_extend_page_back_button"),
                id="channel_extend_page_content",
                classes="content_page"
            ),
            id="channel_extend_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_extend_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_extend_page_extend_add_button":
            self.app.push_screen(channel_extend_add_page())
        elif event.button.id == "channel_extend_page_extend_add_org_button":
            self.app.push_screen(channel_extend_add_org_page())

class channel_extend_add_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Channel Extend Add Page", id="channel_extend_add_page_title"),
                Horizontal(
                    Label("Channel ID", id="channel_extend_add_page_channel_id_label", classes="channel_extend_add_page_label"),
                    Input(placeholder="The Channel Id", id="channel_extend_add_page_channel_id_input", classes="channel_extend_add_page_input"),
                    id="channel_extend_add_page_channel_id_div",
                    classes="channel_extend_add_page_div"
                ),
                Horizontal(
                    Label("Expiration Time", id="channel_extend_add_page_expr_label", classes="channel_extend_add_page_label"),
                    Input(placeholder="[OPTIONAL] Expiration time in blocks or days", id="channel_extend_add_page_expr_input", classes="channel_extend_add_page_input"),
                    id="channel_extend_add_page_expr_div",
                    classes="channel_extend_add_page_div"
                ),
                Horizontal(
                    Label("AGI Amount", id="channel_extend_add_page_agi_amount_label", classes="channel_extend_add_page_label"),
                    Input(placeholder="[OPTIONAL] Amount of AGI tokens to add", id="channel_extend_add_page_agi_amount_input", classes="channel_extend_add_page_input"),
                    id="channel_extend_add_page_agi_amount_div",
                    classes="channel_extend_add_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="channel_extend_add_page_mpe_addr_label", classes="channel_extend_add_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract", id="channel_extend_add_page_mpe_addr_input", classes="channel_extend_add_page_input"),
                    id="channel_extend_add_page_mpe_addr_div",
                    classes="channel_extend_add_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="channel_extend_add_page_gas_label", classes="channel_extend_add_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy", id="channel_extend_add_page_gas_input", classes="channel_extend_add_page_input"),
                    id="channel_extend_add_page_gas_div",
                    classes="channel_extend_add_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="channel_extend_add_page_wallet_index_label", classes="channel_extend_add_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing", id="channel_extend_add_page_wallet_index_input", classes="channel_extend_add_page_input"),
                    id="channel_extend_add_page_wallet_index_div",
                    classes="channel_extend_add_page_div"
                ),
                RadioButton(label="Force", id="channel_extend_add_page_force_radio"),
                RadioSet(
                    RadioButton(label="Quiet Print", id="channel_extend_add_page_quiet_radio"),
                    RadioButton(label="Verbose Print", id="channel_extend_add_page_verbose_radio"),
                    id="channel_extend_add_page_quiet_verbose_set"
                ),
                Horizontal(
                    Button(label="Back", id="channel_extend_add_page_back_button"),
                    Button(label="Extend and Add", id="channel_extend_add_page_confirm_button"),
                    id="channel_extend_add_page_button_div",
                    classes="channel_extend_add_page_div"
                ),
                id="channel_extend_add_content_page",
                classes="content_page"
            ),
            id="channel_extend_add_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global conditional_command
        global conditional_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_extend_add_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_extend_add_page_confirm_button":
            channel_id = self.get_child_by_id("channel_extend_add_page").get_child_by_id("channel_extend_add_content_page").get_child_by_id("channel_extend_add_page_channel_id_div").get_child_by_id("channel_extend_add_page_channel_id_input").value
            expr = self.get_child_by_id("channel_extend_add_page").get_child_by_id("channel_extend_add_content_page").get_child_by_id("channel_extend_add_page_expr_div").get_child_by_id("channel_extend_add_page_expr_input").value
            agi_amount = self.get_child_by_id("channel_extend_add_page").get_child_by_id("channel_extend_add_content_page").get_child_by_id("channel_extend_add_page_agi_amount_div").get_child_by_id("channel_extend_add_page_agi_amount_input").value
            mpe_addr = self.get_child_by_id("channel_extend_add_page").get_child_by_id("channel_extend_add_content_page").get_child_by_id("channel_extend_add_page_mpe_addr_div").get_child_by_id("channel_extend_add_page_mpe_addr_input").value
            gas = self.get_child_by_id("channel_extend_add_page").get_child_by_id("channel_extend_add_content_page").get_child_by_id("channel_extend_add_page_gas_div").get_child_by_id("channel_extend_add_page_gas_input").value
            wallet_index = self.get_child_by_id("channel_extend_add_page").get_child_by_id("channel_extend_add_content_page").get_child_by_id("channel_extend_add_page_wallet_index_div").get_child_by_id("channel_extend_add_page_wallet_index_input").value
            force = self.get_child_by_id("channel_extend_add_page").get_child_by_id("channel_extend_add_content_page").get_child_by_id("channel_extend_add_page_force_radio").value
            quiet = self.get_child_by_id("channel_extend_add_page").get_child_by_id("channel_extend_add_content_page").get_child_by_id("channel_extend_add_page_quiet_verbose_set").get_child_by_id("channel_extend_add_page_quiet_radio").value
            verbose = self.get_child_by_id("channel_extend_add_page").get_child_by_id("channel_extend_add_content_page").get_child_by_id("channel_extend_add_page_quiet_verbose_set").get_child_by_id("channel_extend_add_page_verbose_radio").value

            client_nav_button = self.get_child_by_id("channel_extend_add_page").get_child_by_id("nav_sidebar").get_child_by_id("client_page_nav")

            output, errCode, command = be.channel_extend_add(channel_id, mpe_addr, expr, force, agi_amount, gas, wallet_index, quiet, verbose, True)
            
            if errCode == 0:
                conditional_output = output
                conditional_command = command
                client_nav_button.focus()
                self.app.push_screen(conditional_input_page())
            else:
                popup_output = output
                client_nav_button.focus()
                self.app.push_screen(popup_output_page())

class channel_extend_add_org_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Channel Extend Add For Organization Page", id="channel_extend_add_org_page_title"),
                Horizontal(
                    Label("Organization ID", id="channel_extend_add_org_page_org_id_label", classes="channel_extend_add_org_page_label"),
                    Input(placeholder="Id of the Organization", id="channel_extend_add_org_page_org_id_input", classes="channel_extend_add_org_page_input"),
                    id="channel_extend_add_org_page_org_id_div",
                    classes="channel_extend_add_org_page_div"
                ),
                Horizontal(
                    Label("Payment Group Name", id="channel_extend_add_org_page_group_name_label", classes="channel_extend_add_org_page_label"),
                    Input(placeholder="Name of the payment group", id="channel_extend_add_org_page_group_name_input", classes="channel_extend_add_org_page_input"),
                    id="channel_extend_add_org_page_group_name_div",
                    classes="channel_extend_add_org_page_div"
                ),
                Horizontal(
                    Label("Registry Address", id="channel_extend_add_org_page_registry_label", classes="channel_extend_add_org_page_label"),
                    Input(placeholder="[OPTIONAL] Address of Registry contract", id="channel_extend_add_org_page_registry_input", classes="channel_extend_add_org_page_input"),
                    id="channel_extend_add_org_page_registry_div",
                    classes="channel_extend_add_org_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="channel_extend_add_org_page_mpe_addr_label", classes="channel_extend_add_org_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract", id="channel_extend_add_org_page_mpe_addr_input", classes="channel_extend_add_org_page_input"),
                    id="channel_extend_add_org_page_mpe_addr_div",
                    classes="channel_extend_add_org_page_div"
                ),
                Horizontal(
                    Label("Channel ID", id="channel_extend_add_org_page_channel_id_label", classes="channel_extend_add_org_page_label"),
                    Input(placeholder="[OPTIONAL] The Channel Id", id="channel_extend_add_org_page_channel_id_input", classes="channel_extend_add_org_page_input"),
                    id="channel_extend_add_org_page_channel_id_div",
                    classes="channel_extend_add_org_page_div"
                ),
                Horizontal(
                    Label("Start Block", id="channel_extend_add_org_page_from_block_label", classes="channel_extend_add_org_page_label"),
                    Input(placeholder="[OPTIONAL] Start searching from this block", id="channel_extend_add_org_page_from_block_input", classes="channel_extend_add_org_page_input"),
                    id="channel_extend_add_org_page_from_block_div",
                    classes="channel_extend_add_org_page_div"
                ),
                Horizontal(
                    Label("Expiration Time", id="channel_extend_add_org_page_expr_label", classes="channel_extend_add_org_page_label"),
                    Input(placeholder="[OPTIONAL] Expiration time in blocks or days", id="channel_extend_add_org_page_expr_input", classes="channel_extend_add_org_page_input"),
                    id="channel_extend_add_org_page_expr_div",
                    classes="channel_extend_add_org_page_div"
                ),
                Horizontal(
                    Label("AGI Tokens Amount", id="channel_extend_add_org_page_agi_amount_label", classes="channel_extend_add_org_page_label"),
                    Input(placeholder="[OPTIONAL] Amount of AGI tokens to add", id="channel_extend_add_org_page_agi_amount_input", classes="channel_extend_add_org_page_input"),
                    id="channel_extend_add_org_page_agi_amount_div",
                    classes="channel_extend_add_org_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="channel_extend_add_org_page_gas_label", classes="channel_extend_add_org_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy", id="channel_extend_add_org_page_gas_input", classes="channel_extend_add_org_page_input"),
                    id="channel_extend_add_org_page_gas_div",
                    classes="channel_extend_add_org_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="channel_extend_add_org_page_wallet_index_label", classes="channel_extend_add_org_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing", id="channel_extend_add_org_page_wallet_index_input", classes="channel_extend_add_org_page_input"),
                    id="channel_extend_add_org_page_wallet_index_div",
                    classes="channel_extend_add_org_page_div"
                ),
                RadioButton(label="Force", id="channel_extend_add_org_page_force_radio"),
                RadioSet(
                    RadioButton(label="Quiet Print", id="channel_extend_add_org_page_quiet_radio"),
                    RadioButton(label="Verbose Print", id="channel_extend_add_org_page_verbose_radio"),
                    id="channel_extend_add_org_page_quiet_verbose_set"
                ),
                Horizontal(
                    Button(label="Back", id="channel_extend_add_org_page_back_button"),
                    Button(label="Extend and Add", id="channel_extend_add_org_page_confirm_button"),
                    id="channel_extend_add_org_page_button_div",
                    classes="channel_extend_add_org_page_div"
                ),
                id="channel_extend_add_org_content_page",
                classes="content_page"
            ),
            id="channel_extend_add_org_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global conditional_command
        global conditional_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_extend_add_org_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_extend_add_org_page_confirm_button":
            org_id = self.get_child_by_id("channel_extend_add_org_page").get_child_by_id("channel_extend_add_org_content_page").get_child_by_id("channel_extend_add_org_page_org_id_div").get_child_by_id("channel_extend_add_org_page_org_id_input").value
            group_name = self.get_child_by_id("channel_extend_add_org_page").get_child_by_id("channel_extend_add_org_content_page").get_child_by_id("channel_extend_add_org_page_group_name_div").get_child_by_id("channel_extend_add_org_page_group_name_input").value
            registry = self.get_child_by_id("channel_extend_add_org_page").get_child_by_id("channel_extend_add_org_content_page").get_child_by_id("channel_extend_add_org_page_registry_div").get_child_by_id("channel_extend_add_org_page_registry_input").value
            mpe_addr = self.get_child_by_id("channel_extend_add_org_page").get_child_by_id("channel_extend_add_org_content_page").get_child_by_id("channel_extend_add_org_page_mpe_addr_div").get_child_by_id("channel_extend_add_org_page_mpe_addr_input").value
            channel_id = self.get_child_by_id("channel_extend_add_org_page").get_child_by_id("channel_extend_add_org_content_page").get_child_by_id("channel_extend_add_org_page_channel_id_div").get_child_by_id("channel_extend_add_org_page_channel_id_input").value
            from_block = self.get_child_by_id("channel_extend_add_org_page").get_child_by_id("channel_extend_add_org_content_page").get_child_by_id("channel_extend_add_org_page_from_block_div").get_child_by_id("channel_extend_add_org_page_from_block_input").value
            expr = self.get_child_by_id("channel_extend_add_org_page").get_child_by_id("channel_extend_add_org_content_page").get_child_by_id("channel_extend_add_org_page_expr_div").get_child_by_id("channel_extend_add_org_page_expr_input").value
            agi_amount = self.get_child_by_id("channel_extend_add_org_page").get_child_by_id("channel_extend_add_org_content_page").get_child_by_id("channel_extend_add_org_page_agi_amount_div").get_child_by_id("channel_extend_add_org_page_agi_amount_input").value
            gas = self.get_child_by_id("channel_extend_add_org_page").get_child_by_id("channel_extend_add_org_content_page").get_child_by_id("channel_extend_add_org_page_gas_div").get_child_by_id("channel_extend_add_org_page_gas_input").value
            wallet_index = self.get_child_by_id("channel_extend_add_org_page").get_child_by_id("channel_extend_add_org_content_page").get_child_by_id("channel_extend_add_org_page_wallet_index_div").get_child_by_id("channel_extend_add_org_page_wallet_index_input").value
            force = self.get_child_by_id("channel_extend_add_org_page").get_child_by_id("channel_extend_add_org_content_page").get_child_by_id("channel_extend_add_org_page_force_radio").value
            quiet = self.get_child_by_id("channel_extend_add_org_page").get_child_by_id("channel_extend_add_org_content_page").get_child_by_id("channel_extend_add_org_page_quiet_verbose_set").get_child_by_id("channel_extend_add_org_page_quiet_radio").value
            verbose = self.get_child_by_id("channel_extend_add_org_page").get_child_by_id("channel_extend_add_org_content_page").get_child_by_id("channel_extend_add_org_page_quiet_verbose_set").get_child_by_id("channel_extend_add_org_page_verbose_radio").value

            client_nav_button = self.get_child_by_id("channel_extend_add_org_page").get_child_by_id("nav_sidebar").get_child_by_id("client_page_nav")

            output, errCode, command = be.channel_extend_add_org(org_id, group_name, registry, mpe_addr, channel_id, from_block, expr, force, agi_amount, gas, wallet_index, quiet, verbose, True)

            if errCode == 0:
                conditional_output = output
                conditional_command = command
                client_nav_button.focus()
                self.app.push_screen(conditional_input_page())
            else:
                popup_output = output
                client_nav_button.focus()
                self.app.push_screen(popup_output_page())

class channel_print_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Channel Print Page", id="channel_print_page_title"),
                Horizontal(
                    Button(label="Print Initialized", id="channel_print_page_print_init_button", classes="channel_print_page_button"),
                    Button(label="Print Initialized Filter Org", id="channel_print_page_print_init_filter_org_button", classes="channel_print_page_button"),
                    Button(label="Print All Filter Sender", id="channel_print_page_print_all_filt_send_button", classes="channel_print_page_button"),
                    id="channel_print_page_upper_button_div",
                    classes="channel_print_page_div"
                ),
                Horizontal(
                    Button(label="Print All Filter Recipient", id="channel_print_page_print_all_filt_reci_button", classes="channel_print_page_button"),
                    Button(label="Print All Filter Group", id="channel_print_page_print_all_filt_group_button", classes="channel_print_page_button"),
                    Button(label="Print All Filter Group Sender", id="channel_print_page_print_all_filt_group_sender_button", classes="channel_print_page_button"),
                    id="channel_print_page_lower_button_div",
                    classes="channel_print_page_div"
                ),
                Button(label="Back", id="channel_print_page_back_button"),
                id="channel_print_page_content",
                classes="content_page"
            ),
            id="channel_ _page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_print_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_print_page_print_init_button":
            self.app.push_screen(channel_print_init_page())
        elif event.button.id == "channel_print_page_print_init_filter_org_button":
            self.app.push_screen(channel_print_init_filter_org_page())
        elif event.button.id == "channel_print_page_print_all_filt_send_button":
            self.app.push_screen(channel_print_all_filter_sender_page())
        elif event.button.id == "channel_print_page_print_all_filt_reci_button":
            self.app.push_screen(channel_print_all_filter_recipient_page())
        elif event.button.id == "channel_print_page_print_all_filt_group_button":
            self.app.push_screen(channel_print_all_filter_group_page())
        elif event.button.id == "channel_print_page_print_all_filt_group_sender_button":
            self.app.push_screen(channel_print_all_filter_group_sender_page())

class channel_print_init_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Channel Print Initialized Page", id="channel_print_initialized_page_title"),
                Horizontal(
                    Label("MPE Address", id="channel_print_initialized_page_mpe_addr_label", classes="channel_print_initialized_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract", id="channel_print_initialized_page_mpe_addr_input", classes="channel_print_initialized_page_input"),
                    id="channel_print_initialized_page_mpe_addr_div",
                    classes="channel_print_initialized_page_div"
                ),
                Horizontal(
                    Label("Registry Address", id="channel_print_initialized_page_registry_label", classes="channel_print_initialized_page_label"),
                    Input(placeholder="[OPTIONAL] Address of Registry contract", id="channel_print_initialized_page_registry_input", classes="channel_print_initialized_page_input"),
                    id="channel_print_initialized_page_registry_div",
                    classes="channel_print_initialized_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="channel_print_initialized_page_wallet_index_label", classes="channel_print_initialized_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use", id="channel_print_initialized_page_wallet_index_input", classes="channel_print_initialized_page_input"),
                    id="channel_print_initialized_page_wallet_index_div",
                    classes="channel_print_initialized_page_div"
                ),
                RadioButton(label="Only Print Ids", id="channel_print_initialized_page_only_id_radio"),
                RadioSet(
                    RadioButton(label="Filter by Sender", id="channel_print_initialized_page_filter_sender_radio"),
                    RadioButton(label="Filter by Signer", id="channel_print_initialized_page_filter_signer_radio"),
                    RadioButton(label="Filter by My Channels", id="channel_print_initialized_page_filter_my_radio"),
                    id="channel_print_initialized_page_filter_set"
                ),
                Horizontal(
                    Button(label="Back", id="channel_print_initialized_page_back_button"),
                    Button(label="Print", id="channel_print_initialized_page_confirm_button"),
                    id="channel_print_initialized_page_button_div",
                    classes="channel_print_initialized_page_div"
                ),
                id="channel_print_initialized_content_page",
                classes="content_page"
            ),
            id="channel_print_initialized_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_print_initialized_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_print_initialized_page_confirm_button":
            only_id = self.get_child_by_id("channel_print_initialized_page").get_child_by_id("channel_print_initialized_content_page").get_child_by_id("channel_print_initialized_page_only_id_radio").value
            filter_sender = self.get_child_by_id("channel_print_initialized_page").get_child_by_id("channel_print_initialized_content_page").get_child_by_id("channel_print_initialized_page_filter_set").get_child_by_id("channel_print_initialized_page_filter_sender_radio").value
            filter_signer = self.get_child_by_id("channel_print_initialized_page").get_child_by_id("channel_print_initialized_content_page").get_child_by_id("channel_print_initialized_page_filter_set").get_child_by_id("channel_print_initialized_page_filter_signer_radio").value
            filter_my = self.get_child_by_id("channel_print_initialized_page").get_child_by_id("channel_print_initialized_content_page").get_child_by_id("channel_print_initialized_page_filter_set").get_child_by_id("channel_print_initialized_page_filter_my_radio").value
            mpe_addr = self.get_child_by_id("channel_print_initialized_page").get_child_by_id("channel_print_initialized_content_page").get_child_by_id("channel_print_initialized_page_mpe_addr_div").get_child_by_id("channel_print_initialized_page_mpe_addr_input").value
            registry = self.get_child_by_id("channel_print_initialized_page").get_child_by_id("channel_print_initialized_content_page").get_child_by_id("channel_print_initialized_page_registry_div").get_child_by_id("channel_print_initialized_page_registry_input").value
            wallet_index = self.get_child_by_id("channel_print_initialized_page").get_child_by_id("channel_print_initialized_content_page").get_child_by_id("channel_print_initialized_page_wallet_index_div").get_child_by_id("channel_print_initialized_page_wallet_index_input").value

            client_nav_button = self.get_child_by_id("channel_print_initialized_page").get_child_by_id("nav_sidebar").get_child_by_id("client_page_nav")

            output, errCode = be.channel_print_initialized(only_id, filter_sender, filter_signer, filter_my, mpe_addr, registry, wallet_index)
            popup_output = output
            client_nav_button.focus()
            self.app.push_screen(popup_output_page())

class channel_print_init_filter_org_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Print Initialized Channels for Organization Page", id="channel_print_initialized_filter_org_page_title"),
                Horizontal(
                    Label("Organization ID", id="channel_print_initialized_filter_org_page_org_id_label", classes="channel_print_initialized_filter_org_page_label"),
                    Input(placeholder="Id of the Organization", id="channel_print_initialized_filter_org_page_org_id_input", classes="channel_print_initialized_filter_org_page_input"),
                    id="channel_print_initialized_filter_org_page_org_id_div",
                    classes="channel_print_initialized_filter_org_page_div"
                ),
                Horizontal(
                    Label("Payment Group", id="channel_print_initialized_filter_org_page_group_label", classes="channel_print_initialized_filter_org_page_label"),
                    Input(placeholder="Name of the payment group", id="channel_print_initialized_filter_org_page_group_input", classes="channel_print_initialized_filter_org_page_input"),
                    id="channel_print_initialized_filter_org_page_group_div",
                    classes="channel_print_initialized_filter_org_page_div"
                ),
                Horizontal(
                    Label("Registry Address", id="channel_print_initialized_filter_org_page_registry_label", classes="channel_print_initialized_filter_org_page_label"),
                    Input(placeholder="[OPTIONAL] Address of Registry contract", id="channel_print_initialized_filter_org_page_registry_input", classes="channel_print_initialized_filter_org_page_input"),
                    id="channel_print_initialized_filter_org_page_registry_div",
                    classes="channel_print_initialized_filter_org_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="channel_print_initialized_filter_org_page_mpe_addr_label", classes="channel_print_initialized_filter_org_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract", id="channel_print_initialized_filter_org_page_mpe_addr_input", classes="channel_print_initialized_filter_org_page_input"),
                    id="channel_print_initialized_filter_org_page_mpe_addr_div",
                    classes="channel_print_initialized_filter_org_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="channel_print_initialized_filter_org_page_wallet_index_label", classes="channel_print_initialized_filter_org_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for calling", id="channel_print_initialized_filter_org_page_wallet_index_input", classes="channel_print_initialized_filter_org_page_input"),
                    id="channel_print_initialized_filter_org_page_wallet_index_div",
                    classes="channel_print_initialized_filter_org_page_div"
                ),
                RadioButton(label="Only Print Ids", id="channel_print_initialized_filter_org_page_only_id_radio"),
                RadioSet(
                    RadioButton(label="Filter by Sender", id="channel_print_initialized_filter_org_page_filter_sender_radio"),
                    RadioButton(label="Filter by Signer", id="channel_print_initialized_filter_org_page_filter_signer_radio"),
                    RadioButton(label="Filter by My Channels", id="channel_print_initialized_filter_org_page_filter_my_radio"),
                    id="channel_print_initialized_filter_org_page_filter_set"
                ),
                Horizontal(
                    Button(label="Back", id="channel_print_initialized_filter_org_page_back_button"),
                    Button(label="Print", id="channel_print_initialized_filter_org_page_confirm_button"),
                    id="channel_print_initialized_filter_org_page_button_div",
                    classes="channel_print_initialized_filter_org_page_div"
                ),
                id="channel_print_initialized_filter_org_content_page",
                classes="content_page"
            ),
            id="channel_print_initialized_filter_org_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_print_initialized_filter_org_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_print_initialized_filter_org_page_confirm_button":
            org_id = self.get_child_by_id("channel_print_initialized_filter_org_page").get_child_by_id("channel_print_initialized_filter_org_content_page").get_child_by_id("channel_print_initialized_filter_org_page_org_id_div").get_child_by_id("channel_print_initialized_filter_org_page_org_id_input").value
            group = self.get_child_by_id("channel_print_initialized_filter_org_page").get_child_by_id("channel_print_initialized_filter_org_content_page").get_child_by_id("channel_print_initialized_filter_org_page_group_div").get_child_by_id("channel_print_initialized_filter_org_page_group_input").value
            registry = self.get_child_by_id("channel_print_initialized_filter_org_page").get_child_by_id("channel_print_initialized_filter_org_content_page").get_child_by_id("channel_print_initialized_filter_org_page_registry_div").get_child_by_id("channel_print_initialized_filter_org_page_registry_input").value
            mpe_addr = self.get_child_by_id("channel_print_initialized_filter_org_page").get_child_by_id("channel_print_initialized_filter_org_content_page").get_child_by_id("channel_print_initialized_filter_org_page_mpe_addr_div").get_child_by_id("channel_print_initialized_filter_org_page_mpe_addr_input").value
            wallet_index = self.get_child_by_id("channel_print_initialized_filter_org_page").get_child_by_id("channel_print_initialized_filter_org_content_page").get_child_by_id("channel_print_initialized_filter_org_page_wallet_index_div").get_child_by_id("channel_print_initialized_filter_org_page_wallet_index_input").value
            only_id = self.get_child_by_id("channel_print_initialized_filter_org_page").get_child_by_id("channel_print_initialized_filter_org_content_page").get_child_by_id("channel_print_initialized_filter_org_page_only_id_radio").value
            filter_sender = self.get_child_by_id("channel_print_initialized_filter_org_page").get_child_by_id("channel_print_initialized_filter_org_content_page").get_child_by_id("channel_print_initialized_filter_org_page_filter_set").get_child_by_id("channel_print_initialized_filter_org_page_filter_sender_radio").value
            filter_signer = self.get_child_by_id("channel_print_initialized_filter_org_page").get_child_by_id("channel_print_initialized_filter_org_content_page").get_child_by_id("channel_print_initialized_filter_org_page_filter_set").get_child_by_id("channel_print_initialized_filter_org_page_filter_signer_radio").value
            filter_my = self.get_child_by_id("channel_print_initialized_filter_org_page").get_child_by_id("channel_print_initialized_filter_org_content_page").get_child_by_id("channel_print_initialized_filter_org_page_filter_set").get_child_by_id("channel_print_initialized_filter_org_page_filter_my_radio").value

            client_nav_button = self.get_child_by_id("channel_print_initialized_filter_org_page").get_child_by_id("nav_sidebar").get_child_by_id("client_page_nav")

            output, errCode = be.channel_print_initialized_filter_org(org_id, group, registry, only_id, filter_sender, filter_signer, filter_my, mpe_addr, wallet_index)
            popup_output = output
            client_nav_button.focus()
            self.app.push_screen(popup_output_page())

class channel_print_all_filter_sender_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Print All Channels for Sender Page", id="channel_print_all_filter_sender_page_title"),
                Horizontal(
                    Label("MPE Address", id="channel_print_all_filter_sender_page_mpe_addr_label", classes="channel_print_all_filter_sender_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract", id="channel_print_all_filter_sender_page_mpe_addr_input", classes="channel_print_all_filter_sender_page_input"),
                    id="channel_print_all_filter_sender_page_mpe_addr_div",
                    classes="channel_print_all_filter_sender_page_div"
                ),
                Horizontal(
                    Label("Start Block", id="channel_print_all_filter_sender_page_block_label", classes="channel_print_all_filter_sender_page_label"),
                    Input(placeholder="[OPTIONAL] Start searching from this block", id="channel_print_all_filter_sender_page_block_input", classes="channel_print_all_filter_sender_page_input"),
                    id="channel_print_all_filter_sender_page_block_div",
                    classes="channel_print_all_filter_sender_page_div"
                ),
                Horizontal(
                    Label("Sender Account", id="channel_print_all_filter_sender_page_sender_label", classes="channel_print_all_filter_sender_page_label"),
                    Input(placeholder="[OPTIONAL] Account to set as sender", id="channel_print_all_filter_sender_page_sender_input", classes="channel_print_all_filter_sender_page_input"),
                    id="channel_print_all_filter_sender_page_sender_div",
                    classes="channel_print_all_filter_sender_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="channel_print_all_filter_sender_page_wallet_index_label", classes="channel_print_all_filter_sender_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for calling", id="channel_print_all_filter_sender_page_wallet_index_input", classes="channel_print_all_filter_sender_page_input"),
                    id="channel_print_all_filter_sender_page_wallet_index_div",
                    classes="channel_print_all_filter_sender_page_div"
                ),
                RadioButton(label="Only Print Ids", id="channel_print_all_filter_sender_page_only_id_radio"),
                Horizontal(
                    Button(label="Back", id="channel_print_all_filter_sender_page_back_button"),
                    Button(label="Print", id="channel_print_all_filter_sender_page_confirm_button"),
                    id="channel_print_all_filter_sender_page_button_div",
                    classes="channel_print_all_filter_sender_page_div"
                ),
                id="channel_print_all_filter_sender_content_page",
                classes="content_page"
            ),
            id="channel_print_all_filter_sender_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_print_all_filter_sender_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_print_all_filter_sender_page_confirm_button":
            only_id = self.get_child_by_id("channel_print_all_filter_sender_page").get_child_by_id("channel_print_all_filter_sender_content_page").get_child_by_id("channel_print_all_filter_sender_page_only_id_radio").value
            mpe_addr = self.get_child_by_id("channel_print_all_filter_sender_page").get_child_by_id("channel_print_all_filter_sender_content_page").get_child_by_id("channel_print_all_filter_sender_page_mpe_addr_div").get_child_by_id("channel_print_all_filter_sender_page_mpe_addr_input").value
            from_block = self.get_child_by_id("channel_print_all_filter_sender_page").get_child_by_id("channel_print_all_filter_sender_content_page").get_child_by_id("channel_print_all_filter_sender_page_block_div").get_child_by_id("channel_print_all_filter_sender_page_block_input").value
            sender = self.get_child_by_id("channel_print_all_filter_sender_page").get_child_by_id("channel_print_all_filter_sender_content_page").get_child_by_id("channel_print_all_filter_sender_page_sender_div").get_child_by_id("channel_print_all_filter_sender_page_sender_input").value
            wallet_index = self.get_child_by_id("channel_print_all_filter_sender_page").get_child_by_id("channel_print_all_filter_sender_content_page").get_child_by_id("channel_print_all_filter_sender_page_wallet_index_div").get_child_by_id("channel_print_all_filter_sender_page_wallet_index_input").value

            client_nav_button = self.get_child_by_id("channel_print_all_filter_sender_page").get_child_by_id("nav_sidebar").get_child_by_id("client_page_nav")

            output, errCode = be.channel_print_all_filter_sender(only_id, mpe_addr, from_block, sender, wallet_index)
            popup_output = output
            client_nav_button.focus()
            self.app.push_screen(popup_output_page())

class channel_print_all_filter_recipient_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Print All Channels for Recipient Page", id="channel_print_all_filter_recipient_page_title"),
                Horizontal(
                    Label("MPE Address", id="channel_print_all_filter_recipient_page_mpe_addr_label", classes="channel_print_all_filter_recipient_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract", id="channel_print_all_filter_recipient_page_mpe_addr_input", classes="channel_print_all_filter_recipient_page_input"),
                    id="channel_print_all_filter_recipient_page_mpe_addr_div",
                    classes="channel_print_all_filter_recipient_page_div"
                ),
                Horizontal(
                    Label("Block Number", id="channel_print_all_filter_recipient_page_block_label", classes="channel_print_all_filter_recipient_page_label"),
                    Input(placeholder="[OPTIONAL] Start searching from this block", id="channel_print_all_filter_recipient_page_block_input", classes="channel_print_all_filter_recipient_page_input"),
                    id="channel_print_all_filter_recipient_page_block_div",
                    classes="channel_print_all_filter_recipient_page_div"
                ),
                Horizontal(
                    Label("Recipient", id="channel_print_all_filter_recipient_page_recipient_label", classes="channel_print_all_filter_recipient_page_label"),
                    Input(placeholder="[OPTIONAL] Account to set as recipient", id="channel_print_all_filter_recipient_page_recipient_input", classes="channel_print_all_filter_recipient_page_input"),
                    id="channel_print_all_filter_recipient_page_recipient_div",
                    classes="channel_print_all_filter_recipient_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="channel_print_all_filter_recipient_page_wallet_index_label", classes="channel_print_all_filter_recipient_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for calling", id="channel_print_all_filter_recipient_page_wallet_index_input", classes="channel_print_all_filter_recipient_page_input"),
                    id="channel_print_all_filter_recipient_page_wallet_index_div",
                    classes="channel_print_all_filter_recipient_page_div"
                ),
                RadioButton(label="Only Print Ids", id="channel_print_all_filter_recipient_page_only_id_radio"),
                Horizontal(
                    Button(label="Back", id="channel_print_all_filter_recipient_page_back_button"),
                    Button(label="Print", id="channel_print_all_filter_recipient_page_confirm_button"),
                    id="channel_print_all_filter_recipient_page_button_div",
                    classes="channel_print_all_filter_recipient_page_div"
                ),
                id="channel_print_all_filter_recipient_content_page",
                classes="content_page"
            ),
            id="channel_print_all_filter_recipient_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_print_all_filter_recipient_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_print_all_filter_recipient_page_confirm_button":
            only_id = self.get_child_by_id("channel_print_all_filter_recipient_page").get_child_by_id("channel_print_all_filter_recipient_content_page").get_child_by_id("channel_print_all_filter_recipient_page_only_id_radio").value
            mpe_addr = self.get_child_by_id("channel_print_all_filter_recipient_page").get_child_by_id("channel_print_all_filter_recipient_content_page").get_child_by_id("channel_print_all_filter_recipient_page_mpe_addr_div").get_child_by_id("channel_print_all_filter_recipient_page_mpe_addr_input").value
            from_block = self.get_child_by_id("channel_print_all_filter_recipient_page").get_child_by_id("channel_print_all_filter_recipient_content_page").get_child_by_id("channel_print_all_filter_recipient_page_block_div").get_child_by_id("channel_print_all_filter_recipient_page_block_input").value
            recipient = self.get_child_by_id("channel_print_all_filter_recipient_page").get_child_by_id("channel_print_all_filter_recipient_content_page").get_child_by_id("channel_print_all_filter_recipient_page_recipient_div").get_child_by_id("channel_print_all_filter_recipient_page_recipient_input").value
            wallet_index = self.get_child_by_id("channel_print_all_filter_recipient_page").get_child_by_id("channel_print_all_filter_recipient_content_page").get_child_by_id("channel_print_all_filter_recipient_page_wallet_index_div").get_child_by_id("channel_print_all_filter_recipient_page_wallet_index_input").value

            client_nav_button = self.get_child_by_id("channel_print_all_filter_recipient_page").get_child_by_id("nav_sidebar").get_child_by_id("client_page_nav")

            output, errCode = be.channel_print_all_filter_recipient(only_id, mpe_addr, from_block, recipient, wallet_index)
            popup_output = output
            client_nav_button.focus()
            self.app.push_screen(popup_output_page())

class channel_print_all_filter_group_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Print All Channels for Group Page", id="channel_print_all_filter_group_page_title"),
                Horizontal(
                    Label("Organization ID", id="channel_print_all_filter_group_page_org_id_label", classes="channel_print_all_filter_group_page_label"),
                    Input(placeholder="Id of the Organization", id="channel_print_all_filter_group_page_org_id_input", classes="channel_print_all_filter_group_page_input"),
                    id="channel_print_all_filter_group_page_org_id_div",
                    classes="channel_print_all_filter_group_page_div"
                ),
                Horizontal(
                    Label("Payment Group", id="channel_print_all_filter_group_page_group_label", classes="channel_print_all_filter_group_page_label"),
                    Input(placeholder="Name of the payment group", id="channel_print_all_filter_group_page_group_input", classes="channel_print_all_filter_group_page_input"),
                    id="channel_print_all_filter_group_page_group_div",
                    classes="channel_print_all_filter_group_page_div"
                ),
                Horizontal(
                    Label("Registry Address", id="channel_print_all_filter_group_page_registry_label", classes="channel_print_all_filter_group_page_label"),
                    Input(placeholder="[OPTIONAL] Address of Registry contract", id="channel_print_all_filter_group_page_registry_input", classes="channel_print_all_filter_group_page_input"),
                    id="channel_print_all_filter_group_page_registry_div",
                    classes="channel_print_all_filter_group_page_div"
                ),
                Horizontal(
                    Label("Start Block", id="channel_print_all_filter_group_page_block_label", classes="channel_print_all_filter_group_page_label"),
                    Input(placeholder="[OPTIONAL] Start searching from this block", id="channel_print_all_filter_group_page_block_input", classes="channel_print_all_filter_group_page_input"),
                    id="channel_print_all_filter_group_page_block_div",
                    classes="channel_print_all_filter_group_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="channel_print_all_filter_group_page_mpe_addr_label", classes="channel_print_all_filter_group_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract, if not specified we read address from “networks”", id="channel_print_all_filter_group_page_mpe_addr_input", classes="channel_print_all_filter_group_page_input"),
                    id="channel_print_all_filter_group_page_mpe_addr_div",
                    classes="channel_print_all_filter_group_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="channel_print_all_filter_group_page_wallet_index_label", classes="channel_print_all_filter_group_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for calling", id="channel_print_all_filter_group_page_wallet_index_input", classes="channel_print_all_filter_group_page_input"),
                    id="channel_print_all_filter_group_page_wallet_index_div",
                    classes="channel_print_all_filter_group_page_div"
                ),
                RadioButton(label="Only Print Ids", id="channel_print_all_filter_group_page_only_id_radio"),
                Horizontal(
                    Button(label="Back", id="channel_print_all_filter_group_page_back_button"),
                    Button(label="Print", id="channel_print_all_filter_group_page_confirm_button"),
                    id="channel_print_all_filter_group_page_button_div",
                    classes="channel_print_all_filter_group_page_div"
                ),
                id="channel_print_all_filter_group_content_page",
                classes="content_page"
            ),
            id="channel_print_all_filter_group_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_print_all_filter_group_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_print_all_filter_group_page_confirm_button":
            org_id = self.get_child_by_id("channel_print_all_filter_group_page").get_child_by_id("channel_print_all_filter_group_content_page").get_child_by_id("channel_print_all_filter_group_page_org_id_div").get_child_by_id("channel_print_all_filter_group_page_org_id_input").value
            group = self.get_child_by_id("channel_print_all_filter_group_page").get_child_by_id("channel_print_all_filter_group_content_page").get_child_by_id("channel_print_all_filter_group_page_group_div").get_child_by_id("channel_print_all_filter_group_page_group_input").value
            registry = self.get_child_by_id("channel_print_all_filter_group_page").get_child_by_id("channel_print_all_filter_group_content_page").get_child_by_id("channel_print_all_filter_group_page_registry_div").get_child_by_id("channel_print_all_filter_group_page_registry_input").value
            from_block = self.get_child_by_id("channel_print_all_filter_group_page").get_child_by_id("channel_print_all_filter_group_content_page").get_child_by_id("channel_print_all_filter_group_page_block_div").get_child_by_id("channel_print_all_filter_group_page_block_input").value
            wallet_index = self.get_child_by_id("channel_print_all_filter_group_page").get_child_by_id("channel_print_all_filter_group_content_page").get_child_by_id("channel_print_all_filter_group_page_wallet_index_div").get_child_by_id("channel_print_all_filter_group_page_wallet_index_input").value
            mpe_addr = self.get_child_by_id("channel_print_all_filter_group_page").get_child_by_id("channel_print_all_filter_group_content_page").get_child_by_id("channel_print_all_filter_group_page_mpe_addr_div").get_child_by_id("channel_print_all_filter_group_page_mpe_addr_input").value
            only_id = self.get_child_by_id("channel_print_all_filter_group_page").get_child_by_id("channel_print_all_filter_group_content_page").get_child_by_id("channel_print_all_filter_group_page_only_id_radio").value

            client_nav_button = self.get_child_by_id("channel_print_all_filter_group_page").get_child_by_id("nav_sidebar").get_child_by_id("client_page_nav")

            output, errCode = be.channel_print_all_filter_group(org_id, group, registry, only_id, mpe_addr, from_block, wallet_index)
            popup_output = output
            client_nav_button.focus()
            self.app.push_screen(popup_output_page())

class channel_print_all_filter_group_sender_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Print All Channels for Group and Sender Page", id="channel_print_all_filter_group_sender_page_title"),
                Horizontal(
                    Label("Organization ID", id="channel_print_all_filter_group_sender_page_org_id_label", classes="channel_print_all_filter_group_sender_page_label"),
                    Input(placeholder="Id of the Organization", id="channel_print_all_filter_group_sender_page_org_id_input", classes="channel_print_all_filter_group_sender_page_input"),
                    id="channel_print_all_filter_group_sender_page_org_id_div",
                    classes="channel_print_all_filter_group_sender_page_div"
                ),
                Horizontal(
                    Label("Payment Group", id="channel_print_all_filter_group_sender_page_group_label", classes="channel_print_all_filter_group_sender_page_label"),
                    Input(placeholder="Name of the payment group", id="channel_print_all_filter_group_sender_page_group_input", classes="channel_print_all_filter_group_sender_page_input"),
                    id="channel_print_all_filter_group_sender_page_group_div",
                    classes="channel_print_all_filter_group_sender_page_div"
                ),
                Horizontal(
                    Label("Registry Address", id="channel_print_all_filter_group_sender_page_registry_label", classes="channel_print_all_filter_group_sender_page_label"),
                    Input(placeholder="[OPTIONAL] Address of Registry contract", id="channel_print_all_filter_group_sender_page_registry_input", classes="channel_print_all_filter_group_sender_page_input"),
                    id="channel_print_all_filter_group_sender_page_registry_div",
                    classes="channel_print_all_filter_group_sender_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="channel_print_all_filter_group_sender_page_mpe_addr_label", classes="channel_print_all_filter_group_sender_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract", id="channel_print_all_filter_group_sender_page_mpe_addr_input", classes="channel_print_all_filter_group_sender_page_input"),
                    id="channel_print_all_filter_group_sender_page_mpe_addr_div",
                    classes="channel_print_all_filter_group_sender_page_div"
                ),
                Horizontal(
                    Label("Start Block", id="channel_print_all_filter_group_sender_page_block_label", classes="channel_print_all_filter_group_sender_page_label"),
                    Input(placeholder="[OPTIONAL] Start searching from this block", id="channel_print_all_filter_group_sender_page_block_input", classes="channel_print_all_filter_group_sender_page_input"),
                    id="channel_print_all_filter_group_sender_page_block_div",
                    classes="channel_print_all_filter_group_sender_page_div"
                ),
                Horizontal(
                    Label("Sender", id="channel_print_all_filter_group_sender_page_sender_label", classes="channel_print_all_filter_group_sender_page_label"),
                    Input(placeholder="[OPTIONAL] Account to set as sender", id="channel_print_all_filter_group_sender_page_sender_input", classes="channel_print_all_filter_group_sender_page_input"),
                    id="channel_print_all_filter_group_sender_page_sender_div",
                    classes="channel_print_all_filter_group_sender_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="channel_print_all_filter_group_sender_page_wallet_index_label", classes="channel_print_all_filter_group_sender_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for calling", id="channel_print_all_filter_group_sender_page_wallet_index_input", classes="channel_print_all_filter_group_sender_page_input"),
                    id="channel_print_all_filter_group_sender_page_wallet_index_div",
                    classes="channel_print_all_filter_group_sender_page_div"
                ),
                RadioButton(label="Only Print Ids", id="channel_print_all_filter_group_sender_page_only_id_radio"),
                Horizontal(
                    Button(label="Back", id="channel_print_all_filter_group_sender_page_back_button"),
                    Button(label="Print", id="channel_print_all_filter_group_sender_page_confirm_button"),
                    id="channel_print_all_filter_group_sender_page_button_div",
                    classes="channel_print_all_filter_group_sender_page_div"
                ),
                id="channel_print_all_filter_group_sender_content_page",
                classes="content_page"
            ),
            id="channel_print_all_filter_group_sender_page"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_print_all_filter_group_sender_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_print_all_filter_group_sender_page_confirm_button":
            org_id = self.get_child_by_id("channel_print_all_filter_group_sender_page").get_child_by_id("channel_print_all_filter_group_sender_content_page").get_child_by_id("channel_print_all_filter_group_sender_page_org_id_div").get_child_by_id("channel_print_all_filter_group_sender_page_org_id_input").value
            group = self.get_child_by_id("channel_print_all_filter_group_sender_page").get_child_by_id("channel_print_all_filter_group_sender_content_page").get_child_by_id("channel_print_all_filter_group_sender_page_group_div").get_child_by_id("channel_print_all_filter_group_sender_page_group_input").value
            registry = self.get_child_by_id("channel_print_all_filter_group_sender_page").get_child_by_id("channel_print_all_filter_group_sender_content_page").get_child_by_id("channel_print_all_filter_group_sender_page_registry_div").get_child_by_id("channel_print_all_filter_group_sender_page_registry_input").value
            mpe_addr = self.get_child_by_id("channel_print_all_filter_group_sender_page").get_child_by_id("channel_print_all_filter_group_sender_content_page").get_child_by_id("channel_print_all_filter_group_sender_page_mpe_addr_div").get_child_by_id("channel_print_all_filter_group_sender_page_mpe_addr_input").value
            from_block = self.get_child_by_id("channel_print_all_filter_group_sender_page").get_child_by_id("channel_print_all_filter_group_sender_content_page").get_child_by_id("channel_print_all_filter_group_sender_page_block_div").get_child_by_id("channel_print_all_filter_group_sender_page_block_input").value
            sender = self.get_child_by_id("channel_print_all_filter_group_sender_page").get_child_by_id("channel_print_all_filter_group_sender_content_page").get_child_by_id("channel_print_all_filter_group_sender_page_sender_div").get_child_by_id("channel_print_all_filter_group_sender_page_sender_input").value
            wallet_index = self.get_child_by_id("channel_print_all_filter_group_sender_page").get_child_by_id("channel_print_all_filter_group_sender_content_page").get_child_by_id("channel_print_all_filter_group_sender_page_wallet_index_div").get_child_by_id("channel_print_all_filter_group_sender_page_wallet_index_input").value
            only_id = self.get_child_by_id("channel_print_all_filter_group_sender_page").get_child_by_id("channel_print_all_filter_group_sender_content_page").get_child_by_id("channel_print_all_filter_group_sender_page_only_id_radio").value

            client_nav_button = self.get_child_by_id("channel_print_all_filter_group_sender_page").get_child_by_id("nav_sidebar").get_child_by_id("client_page_nav")

            output, errCode = be.channel_print_all_filter_group_sender(org_id, group, registry, only_id, mpe_addr, from_block, sender, wallet_index)
            popup_output = output
            client_nav_button.focus()
            self.app.push_screen(popup_output_page())

class channel_claim_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Channel Claim Page", id="channel_claim_page_title"),
                Horizontal(
                    Button(label="Claim Timeout", id="channel_claim_page_to_button", classes="channel_claim_page_button"),
                    Button(label="Claim ALL Timeout", id="channel_claim_page_to_all_button", classes="channel_claim_page_button"),
                    id="channel_claim_page_button_div",
                    classes="channel_claim_page_div"
                ),
                Button(label="Back", id="channel_claim_page_back_button"),
                id="channel_claim_page_content",
                classes="content_page"
            ),
            id="channel_claim_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_claim_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_claim_page_to_button":
            self.app.push_screen(channel_claim_to_page())
        elif event.button.id == "channel_claim_page_to_all_button":
            self.app.push_screen(channel_claim_to_all_page())

class channel_claim_to_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Channel Claim Timeout Page", id="channel_claim_timeout_page_title"),
                Horizontal(
                    Label("Channel ID", id="channel_claim_timeout_page_channel_id_label", classes="channel_claim_timeout_page_label"),
                    Input(placeholder="The Channel Id", id="channel_claim_timeout_page_channel_id_input", classes="channel_claim_timeout_page_input"),
                    id="channel_claim_timeout_page_channel_id_div",
                    classes="channel_claim_timeout_page_div"
                ),
                Horizontal(
                    Label("MPE Address", id="channel_claim_timeout_page_mpe_addr_label", classes="channel_claim_timeout_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract", id="channel_claim_timeout_page_mpe_addr_input", classes="channel_claim_timeout_page_input"),
                    id="channel_claim_timeout_page_mpe_addr_div",
                    classes="channel_claim_timeout_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="channel_claim_timeout_page_gas_label", classes="channel_claim_timeout_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy", id="channel_claim_timeout_page_gas_input", classes="channel_claim_timeout_page_input"),
                    id="channel_claim_timeout_page_gas_div",
                    classes="channel_claim_timeout_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="channel_claim_timeout_page_wallet_index_label", classes="channel_claim_timeout_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing", id="channel_claim_timeout_page_wallet_index_input", classes="channel_claim_timeout_page_input"),
                    id="channel_claim_timeout_page_wallet_index_div",
                    classes="channel_claim_timeout_page_div"
                ),
                RadioSet(
                    RadioButton(label="Quiet Print", id="channel_claim_timeout_page_quiet_radio"),
                    RadioButton(label="Verbose Print", id="channel_claim_timeout_page_verbose_radio"),
                    id="channel_claim_timeout_page_quiet_verbose_set"
                ),
                Horizontal(
                    Button(label="Back", id="channel_claim_timeout_page_back_button"),
                    Button(label="Claim", id="channel_claim_timeout_page_confirm_button"),
                    id="channel_claim_timeout_page_button_div",
                    classes="channel_claim_timeout_page_div"
                ),
                id="channel_claim_timeout_content_page",
                classes="content_page"
            ),
            id="channel_claim_timeout_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global conditional_command
        global conditional_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_claim_timeout_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_claim_timeout_page_confirm_button":
            channel_id = self.get_child_by_id("channel_claim_timeout_page").get_child_by_id("channel_claim_timeout_content_page").get_child_by_id("channel_claim_timeout_page_channel_id_div").get_child_by_id("channel_claim_timeout_page_channel_id_input").value
            mpe_addr = self.get_child_by_id("channel_claim_timeout_page").get_child_by_id("channel_claim_timeout_content_page").get_child_by_id("channel_claim_timeout_page_mpe_addr_div").get_child_by_id("channel_claim_timeout_page_mpe_addr_input").value
            gas = self.get_child_by_id("channel_claim_timeout_page").get_child_by_id("channel_claim_timeout_content_page").get_child_by_id("channel_claim_timeout_page_gas_div").get_child_by_id("channel_claim_timeout_page_gas_input").value
            wallet_index = self.get_child_by_id("channel_claim_timeout_page").get_child_by_id("channel_claim_timeout_content_page").get_child_by_id("channel_claim_timeout_page_wallet_index_div").get_child_by_id("channel_claim_timeout_page_wallet_index_input").value
            quiet = self.get_child_by_id("channel_claim_timeout_page").get_child_by_id("channel_claim_timeout_content_page").get_child_by_id("channel_claim_timeout_page_quiet_verbose_set").get_child_by_id("channel_claim_timeout_page_quiet_radio").value
            verbose = self.get_child_by_id("channel_claim_timeout_page").get_child_by_id("channel_claim_timeout_content_page").get_child_by_id("channel_claim_timeout_page_quiet_verbose_set").get_child_by_id("channel_claim_timeout_page_verbose_radio").value

            client_nav_button = self.get_child_by_id("channel_claim_timeout_page").get_child_by_id("nav_sidebar").get_child_by_id("client_page_nav")

            output, errCode, command = be.channel_claim_timeout(channel_id, mpe_addr, gas, wallet_index, quiet, verbose, True)
            
            if errCode == 0:
                conditional_output = output
                conditional_command = command
                client_nav_button.focus()
                self.app.push_screen(conditional_input_page())
            else:
                popup_output = output
                client_nav_button.focus()
                self.app.push_screen(popup_output_page())

class channel_claim_to_all_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("client"),
            ScrollableContainer(
                Label("Channel Claim Timeout All Page", id="channel_claim_timeout_all_page_title"),
                Horizontal(
                    Label("MPE Address", id="channel_claim_timeout_all_page_mpe_addr_label", classes="channel_claim_timeout_all_page_label"),
                    Input(placeholder="[OPTIONAL] Address of MultiPartyEscrow contract", id="channel_claim_timeout_all_page_mpe_addr_input", classes="channel_claim_timeout_all_page_input"),
                    id="channel_claim_timeout_all_page_mpe_addr_div",
                    classes="channel_claim_timeout_all_page_div"
                ),
                Horizontal(
                    Label("From Block", id="channel_claim_timeout_all_page_from_block_label", classes="channel_claim_timeout_all_page_label"),
                    Input(placeholder="[OPTIONAL] Start searching from this block", id="channel_claim_timeout_all_page_from_block_input", classes="channel_claim_timeout_all_page_input"),
                    id="channel_claim_timeout_all_page_from_block_div",
                    classes="channel_claim_timeout_all_page_div"
                ),
                Horizontal(
                    Label("Gas Price", id="channel_claim_timeout_all_page_gas_label", classes="channel_claim_timeout_all_page_label"),
                    Input(placeholder="[OPTIONAL] Ethereum gas price in Wei or time based gas price strategy", id="channel_claim_timeout_all_page_gas_input", classes="channel_claim_timeout_all_page_input"),
                    id="channel_claim_timeout_all_page_gas_div",
                    classes="channel_claim_timeout_all_page_div"
                ),
                Horizontal(
                    Label("Wallet Index", id="channel_claim_timeout_all_page_wallet_index_label", classes="channel_claim_timeout_all_page_label"),
                    Input(placeholder="[OPTIONAL] Wallet index of account to use for signing", id="channel_claim_timeout_all_page_wallet_index_input", classes="channel_claim_timeout_all_page_input"),
                    id="channel_claim_timeout_all_page_wallet_index_div",
                    classes="channel_claim_timeout_all_page_div"
                ),
                RadioSet(
                    RadioButton(label="Quiet Print", id="channel_claim_timeout_all_page_quiet_radio"),
                    RadioButton(label="Verbose Print", id="channel_claim_timeout_all_page_verbose_radio"),
                    id="channel_claim_timeout_all_page_quiet_verbose_set"
                ),
                Horizontal(
                    Button(label="Back", id="channel_claim_timeout_all_page_back_button"),
                    Button(label="Claim", id="channel_claim_timeout_all_page_confirm_button"),
                    id="channel_claim_timeout_all_page_button_div",
                    classes="channel_claim_timeout_all_page_div"
                ),
                id="channel_claim_timeout_all_content_page",
                classes="content_page"
            ),
            id="channel_claim_timeout_all_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global conditional_command
        global conditional_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "channel_claim_timeout_all_page_back_button":
            self.app.pop_screen()
        elif event.button.id == "channel_claim_timeout_all_page_confirm_button":
            mpe_addr = self.get_child_by_id("channel_claim_timeout_all_page").get_child_by_id("channel_claim_timeout_all_content_page").get_child_by_id("channel_claim_timeout_all_page_mpe_addr_div").get_child_by_id("channel_claim_timeout_all_page_mpe_addr_input").value
            from_block = self.get_child_by_id("channel_claim_timeout_all_page").get_child_by_id("channel_claim_timeout_all_content_page").get_child_by_id("channel_claim_timeout_all_page_from_block_div").get_child_by_id("channel_claim_timeout_all_page_from_block_input").value
            gas = self.get_child_by_id("channel_claim_timeout_all_page").get_child_by_id("channel_claim_timeout_all_content_page").get_child_by_id("channel_claim_timeout_all_page_gas_div").get_child_by_id("channel_claim_timeout_all_page_gas_input").value
            wallet_index = self.get_child_by_id("channel_claim_timeout_all_page").get_child_by_id("channel_claim_timeout_all_content_page").get_child_by_id("channel_claim_timeout_all_page_wallet_index_div").get_child_by_id("channel_claim_timeout_all_page_wallet_index_input").value
            quiet = self.get_child_by_id("channel_claim_timeout_all_page").get_child_by_id("channel_claim_timeout_all_content_page").get_child_by_id("channel_claim_timeout_all_page_quiet_verbose_set").get_child_by_id("channel_claim_timeout_all_page_quiet_radio").value
            verbose = self.get_child_by_id("channel_claim_timeout_all_page").get_child_by_id("channel_claim_timeout_all_content_page").get_child_by_id("channel_claim_timeout_all_page_quiet_verbose_set").get_child_by_id("channel_claim_timeout_all_page_verbose_radio").value

            client_nav_button = self.get_child_by_id("channel_claim_timeout_all_page").get_child_by_id("nav_sidebar").get_child_by_id("client_page_nav")

            output, errCode, command = be.channel_claim_timeout_all(mpe_addr, from_block, gas, wallet_index, quiet, verbose, True)
            
            if errCode == 0:
                conditional_output = output
                conditional_command = command
                client_nav_button.focus()
                self.app.push_screen(conditional_input_page())
            else:
                popup_output = output
                client_nav_button.focus()
                self.app.push_screen(popup_output_page())

class custom_command_page(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            be.nav_sidebar_vert("custom"),
            ScrollableContainer(
                Label("Custom CLI Command Page", id="custom_command_page_title"),
                Horizontal(
                    Label("Root Command", id="custom_command_root_label", classes="custom_command_page_label"),
                    Input(placeholder="Eg: account, channel, client, contract, sdk, etc.", id="custom_command_root_input", classes="custom_command_page_input"),
                    id="custom_command_root_div",
                    classes="custom_command_page_div"
                ),
                Horizontal(
                    Label("Sub-command", id="custom_command_sub_label", classes="custom_command_page_label"),
                    Input(placeholder="Eg: deposit, withdraw, MultiPartyEscrow balances, etc.", id="custom_command_sub_input", classes="custom_command_page_input"),
                    id="custom_command_sub_div",
                    classes="custom_command_page_div"
                ),
                Horizontal(
                    Label("Command Arguments", id="custom_command_args_label", classes="custom_command_page_label"),
                    Input(placeholder="Separated by spaces (In the order of: [POSITIONAL] [NAMED] [OPTIONAL])", id="custom_command_args_input", classes="custom_command_page_input"),
                    id="custom_command_args_div",
                    classes="custom_command_page_div"
                ),
                Horizontal(
                    Label("Working Directory", id="custom_command_dir_label", classes="custom_command_page_label"),
                    Input(placeholder="[OPTIONAL] (default: sNET-TUI directory)", id="custom_cwd_input", classes="custom_command_page_input"),
                    id="custom_command_dir_div",
                    classes="custom_command_page_div"
                ),
                RadioButton(label="Print Traceback", id="custom_command_traceback_radio"),
                Horizontal(
                    Button("Run Custom Command", id="custom_command_confirm_button"),
                    id="custom_command_run_div",
                    classes="custom_command_page_div"
                ),
                id="custom_command_page_content",
                classes="content_page"
            ),
            id="custom_command_page"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global popup_output
        global conditional_command
        global conditional_output
        global load_screen_redirect

        if event.button.id == "account_page_nav":
            load_screen_redirect = "account"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "organization_page_nav":
            load_screen_redirect = "organization"
            self.app.switch_screen(loading_screen())
        elif event.button.id == "services_page_nav":
            self.app.switch_screen(services_page())
        elif event.button.id == "client_page_nav":
            self.app.switch_screen(client_page())
        elif event.button.id == "custom_command_page_nav":
            self.app.switch_screen(custom_command_page())
        elif event.button.id == "exit_page_nav":
            self.app.push_screen(exit_page())
        elif event.button.id == "custom_command_confirm_button":
            root = self.get_child_by_id("custom_command_page").get_child_by_id("custom_command_page_content").get_child_by_id("custom_command_root_div").get_child_by_id("custom_command_root_input").value
            sub = self.get_child_by_id("custom_command_page").get_child_by_id("custom_command_page_content").get_child_by_id("custom_command_sub_div").get_child_by_id("custom_command_sub_input").value
            args = self.get_child_by_id("custom_command_page").get_child_by_id("custom_command_page_content").get_child_by_id("custom_command_args_div").get_child_by_id("custom_command_args_input").value
            cwd = self.get_child_by_id("custom_command_page").get_child_by_id("custom_command_page_content").get_child_by_id("custom_command_dir_div").get_child_by_id("custom_cwd_input").value
            traceback = self.get_child_by_id("custom_command_page").get_child_by_id("custom_command_page_content").get_child_by_id("custom_command_traceback_radio").value

            custom_comm_nav_button = self.get_child_by_id("custom_command_page").get_child_by_id("nav_sidebar").get_child_by_id("custom_command_page_nav")

            conditionalCheck = be.custom_conditional_check(root, sub)

            if conditionalCheck:
                output, errCode, command = be.custom_conditional_command(root, sub, args, cwd, traceback, True)

                if errCode == 0:
                    conditional_output = output
                    conditional_command = command
                    custom_comm_nav_button.focus()
                    self.app.push_screen(conditional_input_page())
                else:
                    popup_output = output
                    custom_comm_nav_button.focus()
                    self.app.push_screen(popup_output_page())
            else:
                output, errCode = be.custom_command(root, sub, args, cwd, traceback)
                popup_output = output
                custom_comm_nav_button.focus()
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

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class Singularity_Net_TUI(App):
    
    # CSS_PATH = resource_path('application/app/style.tcss')

    CSS_PATH = "style.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        self.push_screen(WelcomeScreen())