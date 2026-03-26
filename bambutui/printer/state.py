from dataclasses import dataclass, field
from enum import Enum


class GcodeState(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSE = "PAUSE"
    FINISH = "FINISH"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class PrintSpeed(int, Enum):
    SILENT = 1
    STANDARD = 2
    SPORT = 3
    LUDICROUS = 4


@dataclass
class PrinterState:
    # Temperatures
    bed_temp: float = 0.0
    bed_temp_target: float = 0.0
    nozzle_temp: float = 0.0
    nozzle_temp_target: float = 0.0
    chamber_temp: float = 0.0

    # Print progress
    gcode_state: GcodeState = GcodeState.UNKNOWN
    print_percent: int = 0
    remaining_time: int = 0  # minutes
    current_layer: int = 0
    total_layers: int = 0
    subtask_name: str = ""

    # Fan speeds (0-15 scale)
    part_fan_speed: int = 0
    aux_fan_speed: int = 0
    chamber_fan_speed: int = 0

    # Print speed level
    speed_level: int = 2

    # Connectivity
    wifi_signal: str = ""

    # Errors
    print_error: int = 0

    # Chamber light
    chamber_light: bool = False

    # AMS present
    ams_present: bool = False

    def update_from_mqtt(self, data: dict) -> None:
        """Update state from a push_status MQTT message dict."""
        if "bed_temper" in data:
            self.bed_temp = float(data["bed_temper"])
        if "bed_target_temper" in data:
            self.bed_temp_target = float(data["bed_target_temper"])
        if "nozzle_temper" in data:
            self.nozzle_temp = float(data["nozzle_temper"])
        if "nozzle_target_temper" in data:
            self.nozzle_temp_target = float(data["nozzle_target_temper"])
        if "chamber_temper" in data:
            self.chamber_temp = float(data["chamber_temper"])
        if "gcode_state" in data:
            try:
                self.gcode_state = GcodeState(data["gcode_state"].upper())
            except ValueError:
                self.gcode_state = GcodeState.UNKNOWN
        if "mc_percent" in data:
            self.print_percent = int(data["mc_percent"])
        if "mc_remaining_time" in data:
            self.remaining_time = int(data["mc_remaining_time"])
        if "layer_num" in data:
            self.current_layer = int(data["layer_num"])
        if "total_layer_num" in data:
            self.total_layers = int(data["total_layer_num"])
        if "subtask_name" in data:
            self.subtask_name = str(data["subtask_name"])
        if "wifi_signal" in data:
            self.wifi_signal = str(data["wifi_signal"])
        if "print_error" in data:
            self.print_error = int(data["print_error"])
        if "spd_lvl" in data:
            self.speed_level = int(data["spd_lvl"])

        # Fan speeds
        if "big_fan1_speed" in data:
            self.aux_fan_speed = int(data["big_fan1_speed"])
        if "big_fan2_speed" in data:
            self.chamber_fan_speed = int(data["big_fan2_speed"])
        if "cooling_fan_speed" in data:
            self.part_fan_speed = int(data["cooling_fan_speed"])

        # Chamber light from lights_report array
        if "lights_report" in data:
            for light in data["lights_report"]:
                if light.get("node") == "chamber_light":
                    self.chamber_light = light.get("mode") == "on"

        # AMS presence
        if "ams" in data:
            ams_data = data["ams"]
            self.ams_present = bool(ams_data.get("ams", []))

    @property
    def is_printing(self) -> bool:
        return self.gcode_state == GcodeState.RUNNING

    @property
    def is_paused(self) -> bool:
        return self.gcode_state == GcodeState.PAUSE

    @property
    def is_idle(self) -> bool:
        return self.gcode_state in (GcodeState.IDLE, GcodeState.FINISH, GcodeState.UNKNOWN)
