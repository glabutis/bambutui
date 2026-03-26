from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label

from bambutui.printer.state import GcodeState, PrinterState


class StatusBar(Widget):
    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        layout: horizontal;
        background: $surface;
        padding: 0 1;
    }
    StatusBar Label {
        margin: 0 1;
    }
    StatusBar .connected { color: $success; }
    StatusBar .disconnected { color: $error; }
    StatusBar .state-idle { color: $text-muted; }
    StatusBar .state-running { color: $success; }
    StatusBar .state-pause { color: $warning; }
    StatusBar .state-failed { color: $error; }
    """

    connected: reactive[bool] = reactive(False)
    printer_state: reactive[GcodeState] = reactive(GcodeState.UNKNOWN)
    printer_name: reactive[str] = reactive("Printer")
    wifi_signal: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        yield Label(id="conn-label")
        yield Label(id="name-label")
        yield Label(id="state-label")
        yield Label(id="wifi-label")

    def watch_connected(self, value: bool) -> None:
        label = self.query_one("#conn-label", Label)
        if value:
            label.update("● Connected")
            label.set_classes("connected")
        else:
            label.update("○ Disconnected")
            label.set_classes("disconnected")

    def watch_printer_name(self, value: str) -> None:
        self.query_one("#name-label", Label).update(value)

    def watch_printer_state(self, value: GcodeState) -> None:
        label = self.query_one("#state-label", Label)
        state_map = {
            GcodeState.IDLE: ("IDLE", "state-idle"),
            GcodeState.RUNNING: ("PRINTING", "state-running"),
            GcodeState.PAUSE: ("PAUSED", "state-pause"),
            GcodeState.FINISH: ("FINISHED", "state-idle"),
            GcodeState.FAILED: ("FAILED", "state-failed"),
            GcodeState.UNKNOWN: ("", "state-idle"),
        }
        text, css_class = state_map.get(value, ("", "state-idle"))
        label.update(text)
        label.set_classes(css_class)

    def watch_wifi_signal(self, value: str) -> None:
        self.query_one("#wifi-label", Label).update(f"WiFi: {value}" if value else "")

    def update_from_state(self, state: PrinterState, connected: bool, name: str) -> None:
        self.connected = connected
        self.printer_name = name
        self.printer_state = state.gcode_state
        self.wifi_signal = state.wifi_signal
