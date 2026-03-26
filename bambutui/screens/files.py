from __future__ import annotations

import asyncio
import threading
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import (
    Button,
    DirectoryTree,
    Footer,
    Header,
    Label,
    ProgressBar,
    Static,
    Switch,
)

from bambutui.printer.ftp_client import FTPUploadError, upload_file


class FileScreen(Screen):
    """Browse local filesystem, select a .3mf file, and send to printer."""

    TITLE = "BambuTUI — Send File"
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._selected_path: Path | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Select a pre-sliced .3mf file to send to the printer:", id="files-header")

        yield DirectoryTree(str(Path.home()), id="file-tree")

        yield Label("", id="selected-label")
        yield Static("Print Options", classes="section-title")

        yield Static("Bed Leveling")
        yield Switch(value=True, id="sw-bed-level")

        yield Static("Use AMS")
        yield Switch(value=False, id="sw-use-ams")

        yield Static("Timelapse")
        yield Switch(value=False, id="sw-timelapse")

        yield Button("Upload & Print", id="btn-upload", variant="primary", disabled=True)
        yield Label("", id="upload-status")
        yield ProgressBar(total=100, show_eta=False, id="upload-progress")

        yield Footer()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        path = Path(event.path)
        if path.suffix.lower() == ".3mf":
            self._selected_path = path
            self.query_one("#selected-label", Label).update(f"Selected: {path.name}")
            self.query_one("#btn-upload", Button).disabled = False
        else:
            self._selected_path = None
            self.query_one("#selected-label", Label).update("Please select a .3mf file")
            self.query_one("#btn-upload", Button).disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-upload" and self._selected_path:
            self._start_upload()

    def _start_upload(self) -> None:
        if self._selected_path is None:
            return

        config = self.app.config  # type: ignore[attr-defined]
        mqtt = self.app.mqtt  # type: ignore[attr-defined]

        if config is None or mqtt is None:
            self.query_one("#upload-status", Label).update("Error: Not connected to printer")
            return

        bed_leveling = self.query_one("#sw-bed-level", Switch).value
        use_ams = self.query_one("#sw-use-ams", Switch).value
        timelapse = self.query_one("#sw-timelapse", Switch).value

        btn = self.query_one("#btn-upload", Button)
        btn.disabled = True
        status = self.query_one("#upload-status", Label)
        progress_bar = self.query_one("#upload-progress", ProgressBar)
        status.update("Uploading...")
        progress_bar.progress = 0

        loop = asyncio.get_event_loop()
        path = self._selected_path

        def _progress(sent: int, total: int) -> None:
            pct = int(sent / total * 100) if total > 0 else 0
            loop.call_soon_threadsafe(setattr, progress_bar, "progress", pct)

        def _run() -> None:
            try:
                remote_name = upload_file(
                    host=config.printer_ip,
                    access_code=config.access_code,
                    local_path=path,
                    progress_cb=_progress,
                )
                loop.call_soon_threadsafe(self._on_upload_success, remote_name, bed_leveling, use_ams, timelapse)
            except FTPUploadError as e:
                loop.call_soon_threadsafe(self._on_upload_error, str(e))

        threading.Thread(target=_run, daemon=True).start()

    def _on_upload_success(self, remote_name: str, bed_leveling: bool, use_ams: bool, timelapse: bool) -> None:
        mqtt = self.app.mqtt  # type: ignore[attr-defined]
        status = self.query_one("#upload-status", Label)
        progress_bar = self.query_one("#upload-progress", ProgressBar)

        progress_bar.progress = 100
        status.update(f"Upload complete. Starting print: {remote_name}")

        mqtt.start_print(
            remote_name,
            bed_leveling=bed_leveling,
            use_ams=use_ams,
            timelapse=timelapse,
        )
        # Return to dashboard after a short delay
        self.set_timer(1.5, self._go_back)

    def _on_upload_error(self, error: str) -> None:
        self.query_one("#upload-status", Label).update(f"Upload failed: {error}")
        self.query_one("#btn-upload", Button).disabled = False

    def _go_back(self) -> None:
        self.app.pop_screen()
