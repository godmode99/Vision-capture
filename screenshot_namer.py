"""Filename helper for screenshots."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def make_screenshot_name(
    serial: str,
    result: str,
    timestamp: datetime | None = None,
    dest_dir: str | Path | None = None,
) -> str:
    """Return a screenshot filename.

    Parameters
    ----------
    serial : str
        Device serial number.
    result : str
        Result status for the capture.
    timestamp : datetime, optional
        Timestamp used for the filename. Defaults to :func:`datetime.now`.
    dest_dir : str or Path, optional
        Directory to prepend to the filename. When provided, "_1", "_2", ...
        is appended until a unique filename is found.
    """
    ts = (timestamp or datetime.now()).strftime("%Y%m%d_%H%M%S")
    base = f"{serial}_{result}_{ts}.jpg"
    if dest_dir is None:
        return base

    directory = Path(dest_dir)
    directory.mkdir(parents=True, exist_ok=True)
    name = directory / base
    counter = 1
    while name.exists():
        name = directory / f"{serial}_{result}_{ts}_{counter}.jpg"
        counter += 1
    return str(name)
