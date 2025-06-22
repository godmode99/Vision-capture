"""Serial processing utilities decoupling input from downstream logic."""

from __future__ import annotations

from typing import Callable, Iterable, Any

from serial_input import get_serial



def process_serials(
    process_func: Callable[[str], Any],
    prompts: Iterable[str] = ("Enter serial 1: ", "Enter serial 2: "),
    *,
    retries: int = 0,
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], Any] = print,
    log_func: Callable[[str], Any] = print,
) -> None:
    """Prompt for serial numbers and forward them to ``process_func``.

    Parameters
    ----------
    process_func : Callable[[str], Any]
        Function invoked with each validated serial.
    prompts : iterable of str, optional
        Prompts used when requesting serials. Defaults to two prompts.
    retries : int, optional
        Number of times to retry ``process_func`` when it raises an exception.
    input_func : Callable[[str], str], optional
        Function used to read user input. Defaults to ``input``.
    output_func : Callable[[str], Any], optional
        Function used to output validation messages. Defaults to ``print``.
    log_func : Callable[[str], Any], optional
        Function used to log processing errors. Defaults to ``print``.
    """

    for prompt in prompts:
        serial = get_serial(prompt, input_func=input_func, output_func=output_func)
        attempts = 0
        while True:
            try:
                process_func(serial)
                break
            except Exception as exc:  # pragma: no cover - error path
                log_func(f"Error processing {serial}: {exc}")
                if attempts >= retries:
                    break
                attempts += 1
