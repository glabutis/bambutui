from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header

from bambutui.printer.state import GcodeState, PrinterState
from bambutui.widgets.progress_bar import PrintProgress
from bambutui.widgets.status_bar import StatusBar
from bambutui.widgets.temp_display import TempDisplay


class DashboardScreen(Screen):
    """Main dashboard showing printer status, temperatures, and print progress."""

    TITLE = "BambuTUI"
    BINDINGS = [
        Binding("p", "pause_resume", "Pause/Resume", show=True),
        Binding("s", "stop", "Stop", show=True),
        Binding("f", "files", "Send File", show=True),
        Binding("c", "control", "Controls", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("v", "camera", "Camera [exp]", show=True),
        Binding("q", "app.quit", "Quit", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield StatusBar(id="status-bar")
        yield TempDisplay(id="temp-display")
        yield PrintProgress(id="print-progress")
        yield Footer()

    def update_state(self, state: PrinterState, connected: bool, name: str) -> None:
        self.query_one("#status-bar", StatusBar).update_from_state(state, connected, name)
        self.query_one("#temp-display", TempDisplay).update_temps(
            state.bed_temp,
            state.bed_temp_target,
            state.nozzle_temp,
            state.nozzle_temp_target,
            state.chamber_temp,
        )
        self.query_one("#print-progress", PrintProgress).update_progress(
            state.print_percent,
            state.remaining_time,
            state.current_layer,
            state.total_layers,
            state.subtask_name,
        )

    def action_pause_resume(self) -> None:
        self.app.action_pause_resume()

    def action_stop(self) -> None:
        self.app.action_stop()

    def action_files(self) -> None:
        self.app.push_screen("files")

    def action_control(self) -> None:
        self.app.push_screen("control")

    def action_refresh(self) -> None:
        self.app.action_refresh()

    def action_camera(self) -> None:
        self.app.action_camera()
