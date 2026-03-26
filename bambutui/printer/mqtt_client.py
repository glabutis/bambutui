from __future__ import annotations

import asyncio
import json
import ssl
import threading
from collections.abc import Callable
from typing import Any

import paho.mqtt.client as mqtt

from bambutui.printer import commands
from bambutui.printer.state import PrinterState


class MQTTClient:
    PORT = 8883
    USERNAME = "bblp"

    def __init__(
        self,
        host: str,
        access_code: str,
        serial: str,
        on_state_update: Callable[[PrinterState], None] | None = None,
        on_connect: Callable[[bool], None] | None = None,
    ) -> None:
        self.host = host
        self.access_code = access_code
        self.serial = serial
        self.on_state_update = on_state_update
        self.on_connect_cb = on_connect

        self.state = PrinterState()
        self._connected = False
        self._loop: asyncio.AbstractEventLoop | None = None

        self._report_topic = f"device/{serial}/report"
        self._request_topic = f"device/{serial}/request"

        self._client = self._build_client()

    def _build_client(self) -> mqtt.Client:
        client = mqtt.Client(
            client_id="bambutui",
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        )
        client.username_pw_set(self.USERNAME, self.access_code)

        tls_ctx = ssl.create_default_context()
        tls_ctx.check_hostname = False
        tls_ctx.verify_mode = ssl.CERT_NONE
        client.tls_set_context(tls_ctx)

        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        client.on_message = self._on_message
        return client

    def _on_connect(self, client: mqtt.Client, userdata: Any, flags: Any, reason_code: Any, properties: Any) -> None:
        if reason_code == 0:
            self._connected = True
            client.subscribe(self._report_topic, qos=1)
            client.publish(self._request_topic, commands.pushall(), qos=1)
        else:
            self._connected = False
        self._fire_connect_cb(self._connected)

    def _on_disconnect(self, client: mqtt.Client, userdata: Any, flags: Any, reason_code: Any, properties: Any) -> None:
        self._connected = False
        self._fire_connect_cb(False)

    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        try:
            payload = json.loads(msg.payload.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return

        # Messages arrive under different top-level keys
        for key in ("print", "system"):
            if key in payload:
                data = payload[key]
                command = data.get("command", "")
                if command == "push_status":
                    self.state.update_from_mqtt(data)
                    self._fire_state_cb()
                elif command == "pushall":
                    # pushall response also contains full state
                    self.state.update_from_mqtt(data)
                    self._fire_state_cb()

    def _fire_state_cb(self) -> None:
        if self.on_state_update and self._loop:
            self._loop.call_soon_threadsafe(self.on_state_update, self.state)

    def _fire_connect_cb(self, connected: bool) -> None:
        if self.on_connect_cb and self._loop:
            self._loop.call_soon_threadsafe(self.on_connect_cb, connected)

    def connect(self) -> None:
        self._loop = asyncio.get_event_loop()
        self._client.connect_async(self.host, self.PORT)
        thread = threading.Thread(target=self._client.loop_forever, daemon=True)
        thread.start()

    def disconnect(self) -> None:
        self._client.disconnect()

    @property
    def is_connected(self) -> bool:
        return self._connected

    def publish(self, payload: str) -> None:
        if self._connected:
            self._client.publish(self._request_topic, payload, qos=1)

    # Convenience wrappers

    def set_speed(self, level: int) -> None:
        self.publish(commands.set_print_speed(level))

    def set_light(self, on: bool) -> None:
        self.publish(commands.set_chamber_light(on))

    def request_full_status(self) -> None:
        self.publish(commands.pushall())
