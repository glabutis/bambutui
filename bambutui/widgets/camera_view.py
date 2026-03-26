from __future__ import annotations

import threading
import time

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static


FRAME_INTERVAL = 1.0  # seconds between frames


class CameraView(Widget):
    """Renders an RTSP camera stream as ASCII art in a background thread."""

    DEFAULT_CSS = """
    CameraView {
        border: round $primary-darken-2;
        overflow: hidden;
    }
    CameraView Static {
        width: 100%;
        height: 100%;
    }
    """

    def __init__(self, ip: str, access_code: str, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._ip = ip
        self._access_code = access_code
        self._running = False
        self._thread: threading.Thread | None = None

    def compose(self) -> ComposeResult:
        yield Static("Connecting to camera...", id="camera-frame")

    def on_mount(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def on_unmount(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=3.0)

    def _capture_loop(self) -> None:
        from bambutui.camera import CameraStream

        stream = CameraStream(self._ip, self._access_code)

        self.app.call_from_thread(self._set_text, "Opening stream...")

        if not stream.open():
            self.app.call_from_thread(
                self._set_text,
                "Could not connect to camera.\n\n"
                "Make sure your printer is on and LAN mode is enabled.",
            )
            return

        while self._running:
            # Use content_size for accurate dimensions inside the border
            w = max(self.content_size.width, 20)
            h = max(self.content_size.height, 10)

            ascii_frame = stream.grab_ascii(w, h)
            if ascii_frame is not None:
                self.app.call_from_thread(self._set_text, ascii_frame)
            else:
                self.app.call_from_thread(self._set_text, "Frame read failed — retrying...")
                time.sleep(2.0)
                continue

            time.sleep(FRAME_INTERVAL)

        stream.close()

    def _set_text(self, text: str) -> None:
        try:
            self.query_one("#camera-frame", Static).update(text)
        except Exception:
            pass
