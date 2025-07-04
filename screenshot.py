"""Cross-platform screenshot utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple, Optional, Union, Callable
import tempfile

from PIL import Image  # type: ignore    
import numpy as np  # type: ignore
    

try:
    import mss  # type: ignore
except Exception as exc:  # pragma: no cover - mss optional
    raise ImportError("mss is required for screenshot functionality") from exc

try:
    import pyautogui  # type: ignore
except Exception:
    pyautogui = None  # type: ignore


class ScreenCapture:
    """Capture screenshots of the desktop or application windows."""

    def __init__(self) -> None:
        self._sct = mss.mss()

    # Internal helpers -------------------------------------------------
    def _grab(self, region: dict) -> Image.Image:
        """Return a :class:`PIL.Image.Image` for ``region``."""
        img = self._sct.grab(region)
        return Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")

    def _get_window_box(self, title: str) -> dict:
        """Return bounding box for the first window matching ``title``."""
        if pyautogui is None:
            raise RuntimeError("pyautogui is required for window capture")
        wins = pyautogui.getWindowsWithTitle(title)
        if not wins:
            raise ValueError(f"Window not found: {title}")
        win = wins[0]
        return {"left": win.left, "top": win.top, "width": win.width, "height": win.height}

    # Public API -------------------------------------------------------
    def capture(
    self,
    *,
    window: Optional[str] = None,
    region: Optional[Tuple[int, int, int, int]] = None,
    as_numpy: bool = False,
    to_file: bool = False,
) -> Union[Image.Image, np.nadarray, Path]:
        """Capture the screen, a window, or a region.

        Parameters
        ----------
        window : str, optional
            Title of the window to capture.
        region : tuple[int, int, int, int], optional
            ``(x, y, width, height)`` region to capture.
        as_numpy : bool, optional
            When ``True`` return a NumPy array instead of :class:`~PIL.Image.Image`.
        to_file : bool, optional
            When ``True`` save the capture to a temporary PNG file and return the
            :class:`pathlib.Path`.
        """
        if window and region:
            raise ValueError("Specify only one of window or region")

        if window:
            box = self._get_window_box(window)
        elif region:
            x, y, w, h = region
            box = {"left": x, "top": y, "width": w, "height": h}
        else:
            box = self._sct.monitors[1]

        image = self._grab(box)

        if to_file:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                image.save(tmp.name)
            return Path(tmp.name)

        if as_numpy:
            if np is None:
                raise RuntimeError("NumPy is required for as_numpy=True")
            return np.array(image)
        return image


def save_screenshot(
    image: "Image.Image",
    directory: str | Path,
    filename: str,
    *,
    log_func: Callable[[str], object] | None = None,
) -> Path:
    """Save ``image`` to ``directory`` with ``filename``.

    The directory is created when it does not already exist. Any failure
    encountered while writing the file is logged via ``log_func`` when
    provided and then re-raised.

    Parameters
    ----------
    image : PIL.Image.Image
        Screenshot image to save.
    directory : str or Path
        Destination directory for the image file.
    filename : str
        Name of the output file.
    log_func : callable, optional
        Function used to log errors. It receives the error message as a
        single argument.

    Returns
    -------
    pathlib.Path
        Full path to the saved file.
    """

    dest = Path(directory)
    try:
        dest.mkdir(parents=True, exist_ok=True)
    except OSError as exc:  # pragma: no cover - unlikely in tests
        if log_func:
            log_func(f"Failed to create directory {dest}: {exc}")
        raise

    path = dest / filename
    try:
        image.save(path)
    except OSError as exc:
        if log_func:
            log_func(f"Failed to save image to {path}: {exc}")
        raise

    return path
