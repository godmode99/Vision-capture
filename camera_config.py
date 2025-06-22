"""Utilities for loading and validating camera configuration."""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict

from config_loader import ConfigLoader


def load_cameras(config_path: str | Path = "config/config.json") -> List[Dict]:
    """Load the ``cameras`` section from a configuration file."""
    loader = ConfigLoader(config_path)
    config = loader.load_config()
    cameras = config.get("cameras", [])
    if not isinstance(cameras, list):
        raise TypeError("'cameras' section must be a list")
    return cameras


def validate_cameras(cameras: List[Dict]) -> None:
    """Validate that each camera has required fields based on its type."""
    for camera in cameras:
        camera_type = camera.get("type")
        if camera_type == "usb":
            if "device" not in camera:
                raise ValueError("USB camera missing 'device' field")
        elif camera_type == "keyence":
            if "ip" not in camera or "port" not in camera:
                raise ValueError("Keyence camera requires 'ip' and 'port'")
        else:
            raise ValueError("Unknown camera type")


def get_camera_status(camera: Dict) -> str:
    """Return a simple status string for *camera*.

    The logic here is intentionally minimal and acts as a placeholder. USB
    cameras check if the device path exists while Keyence cameras simply
    verify that ``ip`` and ``port`` are present.
    """
    camera_type = camera.get("type")
    if camera_type == "usb":
        device = camera.get("device")
        if device and Path(device).exists():
            return "connected"
        return "not found"
    if camera_type == "keyence":
        if camera.get("ip") and camera.get("port"):
            return "online"
        return "offline"
    return "unknown"
