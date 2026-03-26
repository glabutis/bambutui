from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static

from bambutui.config import (
    PrinterConfig,
    is_valid_access_code,
    is_valid_ip,
    is_valid_serial,
    save_config,
)


class SetupScreen(Screen[PrinterConfig]):
    """First-run setup screen to configure printer connection details."""

    TITLE = "BambuTUI — Printer Setup"
    BINDINGS = [Binding("escape", "app.quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "Enter your printer's local network details.\n"
            "Find the access code and serial on your printer:\n"
            "Settings → Network (LCD screen)",
            id="setup-intro",
        )
        yield Label("Printer Name (optional)", classes="field-label")
        yield Input(placeholder="My P1S", id="input-name")

        yield Label("Printer IP Address", classes="field-label")
        yield Input(placeholder="192.168.1.100", id="input-ip")

        yield Label("LAN Access Code (8 characters)", classes="field-label")
        yield Input(placeholder="12345678", id="input-access-code", password=True)

        yield Label("Serial Number", classes="field-label")
        yield Input(placeholder="00A00A123456789", id="input-serial")

        yield Label("", id="error-msg")
        yield Button("Save & Connect", variant="primary", id="btn-save")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            self._save()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._save()

    def _save(self) -> None:
        error = self.query_one("#error-msg", Label)

        name = self.query_one("#input-name", Input).value.strip() or "My Printer"
        ip = self.query_one("#input-ip", Input).value.strip()
        code = self.query_one("#input-access-code", Input).value.strip()
        serial = self.query_one("#input-serial", Input).value.strip().upper()

        if not is_valid_ip(ip):
            error.update("Invalid IP address")
            return
        if not is_valid_access_code(code):
            error.update("Access code must be 8 alphanumeric characters")
            return
        if not is_valid_serial(serial):
            error.update("Serial number must be at least 10 alphanumeric characters")
            return

        config = PrinterConfig(
            printer_name=name,
            printer_ip=ip,
            access_code=code,
            serial_number=serial,
        )
        save_config(config)
        error.update("")
        self.dismiss(config)
