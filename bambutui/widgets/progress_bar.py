from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ProgressBar


class PrintProgress(Widget):
    """Print progress bar with percentage, layer info, and ETA."""

    DEFAULT_CSS = """
    PrintProgress {
        height: 6;
        border: round $primary-darken-2;
        padding: 0 1;
        margin: 0 0 1 0;
    }
    PrintProgress Label { margin: 0; }
    PrintProgress .filename { color: $text; text-style: bold; }
    PrintProgress .info { color: $text-muted; }
    PrintProgress ProgressBar { margin: 0 0; }
    """

    percent: reactive[int] = reactive(0)
    remaining_minutes: reactive[int] = reactive(0)
    current_layer: reactive[int] = reactive(0)
    total_layers: reactive[int] = reactive(0)
    filename: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        yield Label("", classes="filename", id="pb-filename")
        yield ProgressBar(total=100, show_eta=False, id="pb-bar")
        yield Label("", classes="info", id="pb-info")

    def watch_filename(self, value: str) -> None:
        self.query_one("#pb-filename", Label).update(value or "No active print")

    def watch_percent(self, value: int) -> None:
        self.query_one("#pb-bar", ProgressBar).progress = value
        self._refresh_info()

    def watch_remaining_minutes(self, _: int) -> None:
        self._refresh_info()

    def watch_current_layer(self, _: int) -> None:
        self._refresh_info()

    def watch_total_layers(self, _: int) -> None:
        self._refresh_info()

    def _refresh_info(self) -> None:
        h, m = divmod(self.remaining_minutes, 60)
        eta = f"{h}h {m}m" if h else f"{m}m"
        layers = (
            f"Layer {self.current_layer}/{self.total_layers}"
            if self.total_layers > 0
            else ""
        )
        parts = [f"{self.percent}%"]
        if self.remaining_minutes > 0:
            parts.append(f"ETA: {eta}")
        if layers:
            parts.append(layers)
        self.query_one("#pb-info", Label).update("  |  ".join(parts))

    def update_progress(self, percent: int, remaining: int, layer: int, total: int, name: str) -> None:
        self.filename = name
        self.percent = percent
        self.remaining_minutes = remaining
        self.current_layer = layer
        self.total_layers = total
