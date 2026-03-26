from __future__ import annotations

import os
from collections import deque


def check_camera_available() -> bool:
    try:
        import cv2  # noqa: F401
        return True
    except ImportError:
        return False


# ASCII density ramp — denser chars represent brighter pixels
_ASCII_RAMP = " .,:;i1tfLCG08@"
_RAMP_LEN = len(_ASCII_RAMP)


def _frame_to_ascii(frame: object, width: int, height: int) -> str:
    """Convert an OpenCV BGR frame to an ASCII string sized to (width x height)."""
    import cv2
    import numpy as np

    # Terminal chars are ~2x taller than wide, so halve height for resize target
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (width, height // 2), interpolation=cv2.INTER_AREA)
    rows, cols = resized.shape
    lines: list[str] = []
    for r in range(rows):
        row_chars: list[str] = []
        for c in range(cols):
            idx = int(resized[r, c] / 255 * (_RAMP_LEN - 1))
            row_chars.append(_ASCII_RAMP[idx])
        lines.append("".join(row_chars))
    return "\n".join(lines)


class CameraStream:
    """Wraps an RTSP capture from a BambuLab printer."""

    def __init__(self, ip: str, access_code: str) -> None:
        self._url = f"rtsps://bblp:{access_code}@{ip}:322/streaming/live/1"
        self._cap: object | None = None

    def open(self) -> bool:
        import cv2

        # Disable TLS verification for the printer's self-signed cert and use TCP
        os.environ.setdefault(
            "OPENCV_FFMPEG_CAPTURE_OPTIONS",
            "rtsp_transport;tcp|tls_verify;0",
        )
        self._cap = cv2.VideoCapture(self._url, cv2.CAP_FFMPEG)
        return self._cap.isOpened()

    def grab_ascii(self, width: int, height: int) -> str | None:
        if self._cap is None:
            return None
        import cv2

        ret, frame = self._cap.read()
        if not ret or frame is None:
            return None
        return _frame_to_ascii(frame, max(width, 1), max(height, 2))

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
