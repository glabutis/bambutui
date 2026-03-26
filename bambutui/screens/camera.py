from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


class CameraScreen(Screen):
    """[EXPERIMENTAL] Live ASCII camera feed from the printer's RTSP stream."""

    TITLE = "Camera Feed [Experimental]"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back", show=True),
    ]

    def __init__(self, ip: str, access_code: str) -> None:
        super().__init__()
        self._ip = ip
        self._access_code = access_code

    def compose(self) -> ComposeResult:
        from bambutui.camera import check_camera_available

        yield Header()
        yield Static(
            "[bold yellow]⚠ EXPERIMENTAL[/] — Live camera stream via RTSP",
            id="camera-header",
        )

        if check_camera_available():
            from bambutui.widgets.camera_view import CameraView
            yield CameraView(self._ip, self._access_code, id="camera-view")
        else:
            yield Static(
                "Camera requires [bold]opencv-python-headless[/].\n\n"
                "Install it with:\n\n"
                "    pip install \"bambutui[camera]\"\n\n"
                "Then restart bambutui.",
                id="camera-unavailable",
            )

        yield Footer()
