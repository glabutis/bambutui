from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label


class TempGauge(Widget):
    """Single temperature display: label, current → target."""

    DEFAULT_CSS = """
    TempGauge {
        height: 3;
        border: round $primary-darken-2;
        padding: 0 1;
        width: 1fr;
    }
    TempGauge .label { color: $text-muted; }
    TempGauge .temps { text-style: bold; }
    """

    current: reactive[float] = reactive(0.0)
    target: reactive[float] = reactive(0.0)
    label_text: reactive[str] = reactive("Temp")

    def compose(self) -> ComposeResult:
        yield Label("", classes="label", id="temp-label")
        yield Label("", classes="temps", id="temp-value")

    def watch_label_text(self, value: str) -> None:
        self.query_one("#temp-label", Label).update(value)
        self._refresh_value()

    def watch_current(self, _: float) -> None:
        self._refresh_value()

    def watch_target(self, _: float) -> None:
        self._refresh_value()

    def _refresh_value(self) -> None:
        label = self.query_one("#temp-value", Label)
        label.update(f"{self.current:.1f}° → {self.target:.1f}°")


class TempDisplay(Widget):
    """Shows bed, nozzle, and chamber temperatures."""

    DEFAULT_CSS = """
    TempDisplay {
        layout: horizontal;
        height: 5;
        margin: 0 0 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield TempGauge(id="temp-bed")
        yield TempGauge(id="temp-nozzle")
        yield TempGauge(id="temp-chamber")

    def on_mount(self) -> None:
        self.query_one("#temp-bed", TempGauge).label_text = "Bed"
        self.query_one("#temp-nozzle", TempGauge).label_text = "Nozzle"
        self.query_one("#temp-chamber", TempGauge).label_text = "Chamber"

    def update_temps(
        self,
        bed: float,
        bed_target: float,
        nozzle: float,
        nozzle_target: float,
        chamber: float,
    ) -> None:
        g = self.query_one("#temp-bed", TempGauge)
        g.current = bed
        g.target = bed_target

        g = self.query_one("#temp-nozzle", TempGauge)
        g.current = nozzle
        g.target = nozzle_target

        g = self.query_one("#temp-chamber", TempGauge)
        g.current = chamber
        g.target = 0.0
