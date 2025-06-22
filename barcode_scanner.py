"""Utilities for reading a serial or barcode from a scanner.

The scanner can be attached either as a USB keyboard or via a COM
(RS232) serial port. In USB mode the scanner's input is read from a
file-like object which defaults to ``sys.stdin``. COM mode uses the
``pyserial`` package to read bytes from a serial port.

Example configuration for a COM scanner::

    {
        "scanner": {
            "port": "COM3",
            "baudrate": 9600
        }
    }

This module exposes :class:`BarcodeScanner` which provides a simple
``scan()`` method returning the scanned string once a newline or carriage
return is received.
"""

from __future__ import annotations

import sys
from typing import Optional, TextIO


class BarcodeScanner:
    """Read barcodes from a USB or COM scanner."""

    def __init__(
        self,
        *,
        mode: str = "usb",
        port: Optional[str] = None,
        baudrate: int = 9600,
        input_stream: Optional[TextIO] = None,
        serial_module: object | None = None,
    ) -> None:
        if mode not in {"usb", "com"}:
            raise ValueError("mode must be 'usb' or 'com'")
        self.mode = mode
        self.port = port
        self.baudrate = baudrate
        self.input_stream = input_stream or sys.stdin
        self.serial_module = serial_module
        self._serial = None

    def _open_serial(self) -> None:
        if self.serial_module is None:
            try:
                import serial  # type: ignore

                self.serial_module = serial
            except Exception as exc:  # pragma: no cover - optional dep
                raise ImportError("pyserial is required for COM mode") from exc
        Serial = getattr(self.serial_module, "Serial")
        self._serial = Serial(self.port, self.baudrate, timeout=1)

    def close(self) -> None:
        if self._serial is not None:
            try:
                self._serial.close()
            finally:
                self._serial = None

    def scan(self) -> str:
        """Return the next scanned barcode string."""

        if self.mode == "usb":
            line = self.input_stream.readline()
            return line.strip()

        if self._serial is None:
            self._open_serial()

        chars: list[str] = []
        while True:
            data = self._serial.read(1)
            if not data:
                continue
            ch = data.decode("utf-8", errors="ignore")
            if ch in "\r\n":
                if chars:
                    break
                continue
            chars.append(ch)
        return "".join(chars)
