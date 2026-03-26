from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Static

from bambutui.printer.state import PrinterState


class ControlScreen(Screen):
    """Print control panel: speed, light."""

    TITLE = "BambuTUI — Controls"
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Print Control", id="control-header")
        yield Label("", id="state-label")

        yield Static("─" * 30, id="divider-1")
        yield Static("Print Speed", classes="section-title")
        yield Button("🐢  Silent (1)", id="btn-speed-1")
        yield Button("⚙  Standard (2)", id="btn-speed-2", variant="primary")
        yield Button("🏃  Sport (3)", id="btn-speed-3")
        yield Button("🚀  Ludicrous (4)", id="btn-speed-4", variant="warning")

        yield Static("─" * 30, id="divider-2")
        yield Static("Chamber", classes="section-title")
        yield Button("💡  Light On", id="btn-light-on", variant="success")
        yield Button("🌑  Light Off", id="btn-light-off")

        yield Footer()

    def on_screen_resume(self) -> None:
        app = self.app
        if app.mqtt is not None:  # type: ignore[attr-defined]
            self.update_state(app.mqtt.state)  # type: ignore[attr-defined]

    def update_state(self, state: PrinterState) -> None:
        self.query_one("#state-label", Label).update(
            f"Status: {state.gcode_state.value}  |  Speed: {state.speed_level}"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        mqtt = self.app.mqtt  # type: ignore[attr-defined]
        if mqtt is None:
            return
        btn_id = event.button.id
        if btn_id == "btn-speed-1":
            mqtt.set_speed(1)
        elif btn_id == "btn-speed-2":
            mqtt.set_speed(2)
        elif btn_id == "btn-speed-3":
            mqtt.set_speed(3)
        elif btn_id == "btn-speed-4":
            mqtt.set_speed(4)
        elif btn_id == "btn-light-on":
            mqtt.set_light(True)
        elif btn_id == "btn-light-off":
            mqtt.set_light(False)
