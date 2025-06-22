import json
from pathlib import Path

import pytest

from camera_config import load_cameras, validate_cameras, get_camera_status


def test_load_cameras(tmp_path: Path):
    cfg = tmp_path / "cfg.json"
    data = {"cameras": [{"type": "usb", "device": "/dev/null"}]}
    cfg.write_text(json.dumps(data))

    cams = load_cameras(cfg)
    assert cams == data["cameras"]


def test_validate_cameras_errors():
    with pytest.raises(ValueError):
        validate_cameras([{"type": "usb"}])
    with pytest.raises(ValueError):
        validate_cameras([{"type": "keyence", "ip": "1.2.3.4"}])
    with pytest.raises(ValueError):
        validate_cameras([{"type": "unknown"}])


def test_get_camera_status(tmp_path: Path):
    device = tmp_path / "cam"
    device.touch()
    usb_cam = {"type": "usb", "device": str(device)}
    assert get_camera_status(usb_cam) == "connected"
    assert get_camera_status({"type": "usb", "device": str(device) + "x"}) == "not found"

    keyence = {"type": "keyence", "ip": "1.2.3.4", "port": 8500}
    assert get_camera_status(keyence) == "online"
