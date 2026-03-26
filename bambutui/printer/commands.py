from __future__ import annotations

import itertools
import json
from pathlib import Path

_seq = itertools.count(1)


def _seq_id() -> str:
    return str(next(_seq))


def pushall() -> str:
    return json.dumps({"pushing": {"sequence_id": _seq_id(), "command": "pushall", "version": 1, "push_target": 1}})


def stop_print() -> str:
    return json.dumps({"print": {"sequence_id": _seq_id(), "command": "stop", "param": ""}})


def pause_print() -> str:
    return json.dumps({"print": {"sequence_id": _seq_id(), "command": "pause", "param": ""}})


def resume_print() -> str:
    return json.dumps({"print": {"sequence_id": _seq_id(), "command": "resume", "param": ""}})


def set_print_speed(level: int) -> str:
    """level: 1=silent, 2=standard, 3=sport, 4=ludicrous"""
    level = max(1, min(4, level))
    return json.dumps({"print": {"sequence_id": _seq_id(), "command": "print_speed", "param": str(level)}})


def start_print(
    filename: str,
    plate_number: int = 1,
    bed_leveling: bool = True,
    flow_cali: bool = False,
    vibration_cali: bool = False,
    layer_inspect: bool = False,
    timelapse: bool = False,
    use_ams: bool = False,
    ams_mapping: list[int] | None = None,
) -> str:
    """Build the project_file command to start printing an uploaded .3mf file."""
    name = Path(filename).name
    payload = {
        "print": {
            "sequence_id": _seq_id(),
            "command": "project_file",
            "param": f"Metadata/plate_{plate_number}.gcode",
            "subtask_name": name,
            "url": f"file:///sdcard/{name}",
            "timelapse": timelapse,
            "bed_leveling": bed_leveling,
            "flow_cali": flow_cali,
            "vibration_cali": vibration_cali,
            "layer_inspect": layer_inspect,
            "use_ams": use_ams,
            "ams_mapping": ams_mapping or [],
        }
    }
    return json.dumps(payload)


def set_chamber_light(on: bool) -> str:
    mode = "on" if on else "off"
    return json.dumps({
        "system": {
            "sequence_id": _seq_id(),
            "command": "ledctrl",
            "led_node": "chamber_light",
            "led_mode": mode,
            "led_on_time": 500,
            "led_off_time": 500,
            "loop_times": 0,
            "interval_time": 0,
        }
    })


def send_gcode(gcode: str) -> str:
    if not gcode.endswith("\n"):
        gcode += "\n"
    return json.dumps({"print": {"sequence_id": _seq_id(), "command": "gcode_line", "param": gcode, "layer_num": 0}})
