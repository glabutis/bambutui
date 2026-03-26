from __future__ import annotations

import ftplib
import ssl
from collections.abc import Callable
from pathlib import Path


class FTPUploadError(Exception):
    pass


def upload_file(
    host: str,
    access_code: str,
    local_path: str | Path,
    progress_cb: Callable[[int, int], None] | None = None,
) -> str:
    """
    Upload a file to the printer via implicit FTPS (port 990).
    Returns the remote filename on the printer SD card.
    progress_cb(bytes_sent, total_bytes) is called periodically.
    """
    local_path = Path(local_path)
    if not local_path.exists():
        raise FTPUploadError(f"File not found: {local_path}")

    total_size = local_path.stat().st_size
    remote_name = local_path.name
    bytes_sent = 0

    # Implicit FTPS uses port 990 with TLS from the start
    tls_ctx = ssl.create_default_context()
    tls_ctx.check_hostname = False
    tls_ctx.verify_mode = ssl.CERT_NONE

    try:
        with ftplib.FTP_TLS(context=tls_ctx) as ftp:
            ftp.connect(host, 990, timeout=15)
            ftp.login("bblp", access_code)
            ftp.prot_p()  # Secure data channel

            chunk_size = 8192

            def _callback(data: bytes) -> None:
                nonlocal bytes_sent
                bytes_sent += len(data)
                if progress_cb:
                    progress_cb(bytes_sent, total_size)

            with local_path.open("rb") as f:
                ftp.storbinary(f"STOR {remote_name}", f, blocksize=chunk_size, callback=_callback)

    except ftplib.all_errors as e:
        raise FTPUploadError(f"FTP upload failed: {e}") from e

    return remote_name
