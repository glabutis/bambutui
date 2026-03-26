from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding

from bambutui.config import PrinterConfig, load_config
from bambutui.printer.mqtt_client import MQTTClient
from bambutui.printer.state import PrinterState
from bambutui.screens.control import ControlScreen
from bambutui.screens.dashboard import DashboardScreen
from bambutui.screens.setup import SetupScreen


class BambuTUI(App):
    CSS_PATH = "bambutui.tcss"

    SCREENS = {
        "dashboard": DashboardScreen,
        "control": ControlScreen,
    }

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.config: PrinterConfig | None = None
        self.mqtt: MQTTClient | None = None

    def on_mount(self) -> None:
        self.config = load_config()
        if self.config is None:
            self.push_screen(SetupScreen(), self._on_setup_complete)
        else:
            self._connect(self.config)
            self.push_screen("dashboard")

    def _on_setup_complete(self, config: PrinterConfig) -> None:
        self.config = config
        self._connect(config)
        self.push_screen("dashboard")

    def _connect(self, config: PrinterConfig) -> None:
        if self.mqtt is not None:
            self.mqtt.disconnect()

        self.mqtt = MQTTClient(
            host=config.printer_ip,
            access_code=config.access_code,
            serial=config.serial_number,
            on_state_update=self._on_state_update,
            on_connect=self._on_connect_change,
        )
        self.mqtt.connect()

    def _on_state_update(self, state: PrinterState) -> None:
        try:
            dashboard = self.get_screen("dashboard")
            if isinstance(dashboard, DashboardScreen) and dashboard.is_current:
                dashboard.update_state(state, self.mqtt.is_connected, self.config.printer_name)
        except Exception:
            pass

        try:
            control = self.get_screen("control")
            if isinstance(control, ControlScreen) and control.is_current:
                control.update_state(state)
        except Exception:
            pass

    def _on_connect_change(self, connected: bool) -> None:
        try:
            dashboard = self.get_screen("dashboard")
            if isinstance(dashboard, DashboardScreen) and self.mqtt is not None and self.config is not None:
                dashboard.update_state(self.mqtt.state, connected, self.config.printer_name)
        except Exception:
            pass

    def action_refresh(self) -> None:
        if self.mqtt is not None:
            self.mqtt.request_full_status()


    def on_unmount(self) -> None:
        if self.mqtt is not None:
            self.mqtt.disconnect()
