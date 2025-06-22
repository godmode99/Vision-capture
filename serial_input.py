from __future__ import annotations

from typing import Callable, Any


def validate_serial(serial: str) -> bool:
    """Return ``True`` if ``serial`` is 4-20 alphanumeric characters."""
    return serial.isalnum() and 4 <= len(serial) <= 20


def get_serial(
    prompt: str = "Enter serial: ",
    *,
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], Any] = print,
) -> str:
    """Prompt for a serial number until a valid value is entered."""
    while True:
        value = input_func(prompt).strip()
        if validate_serial(value):
            return value
        output_func("Invalid serial. Please enter 4-20 alphanumeric characters.")
