"""Manage runtime selection of serial input sources."""

from __future__ import annotations

from typing import Callable, Optional, TextIO, Tuple

from barcode_scanner import BarcodeScanner
from serial_input import get_serial


class InputManager:
    """Allow switching between manual input and barcode scanners.

    Parameters
    ----------
    com_port : str, optional
        Serial port used when ``scanner-COM`` is selected.
    baudrate : int, optional
        Baud rate for the COM scanner. Defaults to ``9600``.
    input_stream : TextIO, optional
        Stream object used for ``scanner-USB`` mode. Defaults to ``sys.stdin``.
    input_func : Callable[[str], str], optional
        Function used for manual input. Defaults to :func:`input`.
    serial_module : object, optional
        Module providing a ``Serial`` class, injected for testing.

    Example
    -------
    >>> mgr = InputManager(com_port="COM3")
    >>> mgr.set_source("scanner-USB")
    ('scanner-USB', 'available')
    >>> code = mgr.read_serial()
    """

    def __init__(
        self,
        *,
        com_port: Optional[str] = None,
        baudrate: int = 9600,
        input_stream: Optional[TextIO] = None,
        input_func: Callable[[str], str] = input,
        serial_module: object | None = None,
    ) -> None:
        self.com_port = com_port
        self.baudrate = baudrate
        self.input_stream = input_stream
        self.input_func = input_func
        self.serial_module = serial_module
        self._scanner: BarcodeScanner | None = None
        self._source = "manual"
        self.status = "available"

    # Public API -----------------------------------------------------
    def set_source(self, source: str) -> Tuple[str, str]:
        """Switch to ``source`` and return ``(current_source, status)``."""
        self.close()
        self.status = "available"
        if source == "manual":
            self._source = "manual"
            return self._source, self.status
        if source == "scanner-USB":
            self._scanner = BarcodeScanner(mode="usb", input_stream=self.input_stream)
            self._source = source
            return self._source, self.status
        if source == "scanner-COM":
            try:
                self._scanner = BarcodeScanner(
                    mode="com",
                    port=self.com_port,
                    baudrate=self.baudrate,
                    serial_module=self.serial_module,
                )
                # Attempt to open the port to verify availability
                self._scanner._open_serial()
            except Exception:
                self.status = "error"
            self._source = source
            return self._source, self.status
        raise ValueError(f"Unknown source: {source}")

    def read_serial(self, prompt: str = "Enter serial: ") -> str:
        """Read a serial using the currently selected source."""
        if self._source == "manual":
            return get_serial(prompt, input_func=self.input_func)
        if self._scanner is None:
            raise RuntimeError("Scanner not initialised")
        return self._scanner.scan()

    def close(self) -> None:
        """Close any active scanner."""
        if self._scanner is not None:
            self._scanner.close()
            self._scanner = None

    @property
    def current_source(self) -> str:
        return self._source
