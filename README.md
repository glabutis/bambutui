# bambutui

A terminal UI for monitoring BambuLab 3D printers over your local network.

![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)

## Features

- Live print status, temperatures, and progress
- Pause, resume, and stop prints
- Print speed control (Silent / Standard / Sport / Ludicrous)
- Chamber light toggle
- Upload pre-sliced `.3mf` files and start prints — no cloud required
- Works with all BambuLab printers (X1, P1, A1 series)

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/glabutis/bambutui/main/install.sh | bash
```

Then add `~/.local/bin` to your PATH if it isn't already:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

## Usage

```bash
bambutui
```

On first launch you'll be prompted for your printer's connection details:

| Field | Where to find it |
|-------|-----------------|
| IP Address | Router DHCP table, or printer LCD → Settings → WLAN |
| LAN Access Code | Printer LCD → Settings → Network (8-character code) |
| Serial Number | Printer LCD → Settings → Device |

Config is saved to `~/.config/bambutui/config.json`.

## Keyboard shortcuts

| Key | Action |
|-----|--------|
| `p` | Pause / Resume |
| `s` | Stop print |
| `f` | Send file |
| `c` | Controls (speed, light) |
| `r` | Refresh status |
| `q` | Quit |

## Requirements

- Python 3.9+
- BambuLab printer on the same local network
- LAN Mode enabled on the printer (Settings → Network → LAN Mode)

## Development

```bash
git clone https://github.com/glabutis/bambutui
cd bambutui
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
python -m bambutui
```
