# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
# Activate the virtual environment first
source .venv/bin/activate

# Run the app
python -m bambutui

# Or via the installed script
bambutui
```

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

The project uses Python 3.9+ (the macOS system Python). All files use `from __future__ import annotations` to enable `X | Y` union type syntax on 3.9. Avoid `match` statements (Python 3.10+ only).

## Architecture

**Entry point:** `bambutui/__main__.py` → `bambutui/app.py` (`BambuTUI` Textual App subclass)

**Config:** `bambutui/config.py` — loads/saves printer credentials from `~/.config/bambutui/config.json`. On first launch, the app pushes `SetupScreen` to collect IP, access code, and serial number.

**Printer layer** (`bambutui/printer/`):
- `state.py` — `PrinterState` dataclass updated by `update_from_mqtt()` on every MQTT push_status message
- `commands.py` — builds JSON payloads for each MQTT command with an auto-incrementing `sequence_id`
- `mqtt_client.py` — `MQTTClient` wraps paho-mqtt, connects via TLS to port 8883 using `bblp`/access-code credentials, subscribes to `device/{serial}/report`, publishes to `device/{serial}/request`. Runs paho's loop in a daemon thread; callbacks fire on the asyncio event loop via `call_soon_threadsafe`.
- `ftp_client.py` — uploads `.3mf` files via implicit FTPS (port 990) before a print job

**Screens** (`bambutui/screens/`):
- `setup.py` — first-run config form, dismisses with a `PrinterConfig`
- `dashboard.py` — main view: status bar + temperatures + progress; keybindings for p/s/f/c/r/q
- `control.py` — pause/resume/stop + speed levels (1–4) + chamber light
- `files.py` — `DirectoryTree` browser to pick a `.3mf`, then FTP upload + MQTT print start in a background thread

**Widgets** (`bambutui/widgets/`): `StatusBar`, `TempDisplay` (with `TempGauge`), `PrintProgress` — all use Textual `reactive` attributes for live updates.

**Stylesheet:** `bambutui/bambutui.tcss` — Textual CSS for all screens and widgets.

## BambuLab Protocol Notes

- MQTT port 8883, TLS with `verify=False` (self-signed cert on printer)
- Topics: `device/{serial}/report` (receive) and `device/{serial}/request` (send)
- P1 series sends delta updates only — call `pushall` after connect to get full state
- FTP is implicit FTPS on port 990; upload `.3mf` to `/` on the SD card, then send `project_file` MQTT command referencing `file:///sdcard/{filename}`
- Print speed levels: 1=Silent, 2=Standard, 3=Sport, 4=Ludicrous
