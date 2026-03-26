from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "bambutui" / "config.json"


@dataclass
class PrinterConfig:
    printer_ip: str
    access_code: str
    serial_number: str
    printer_name: str = "My Printer"


def load_config() -> PrinterConfig | None:
    if not CONFIG_PATH.exists():
        return None
    try:
        data = json.loads(CONFIG_PATH.read_text())
        return PrinterConfig(**data)
    except (json.JSONDecodeError, TypeError, KeyError):
        return None


def save_config(config: PrinterConfig) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(asdict(config), indent=2))


def is_valid_ip(ip: str) -> bool:
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if not re.match(pattern, ip):
        return False
    return all(0 <= int(part) <= 255 for part in ip.split("."))


def is_valid_access_code(code: str) -> bool:
    return len(code) == 8 and code.isalnum()


def is_valid_serial(serial: str) -> bool:
    return len(serial) >= 10 and serial.isalnum()
