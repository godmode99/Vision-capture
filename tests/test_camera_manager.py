import json
from pathlib import Path

import pytest

from camera_manager import CameraManager, USBCamera, KeyenceCamera


def create_config(tmp_path: Path) -> Path:
    cfg = tmp_path / "cfg.json"
    device = tmp_path / "video0"
    device.touch()
    data = {
        "cameras": [
            {
                "id": 1,
                "type": "usb",
                "name": "USB",
                "device": str(device),
            },
            {
                "id": 2,
                "type": "keyence",
                "name": "Key",
                "ip": "1.2.3.4",
                "port": 8500,
            },
        ]
    }
    cfg.write_text(json.dumps(data))
    return cfg


def test_manager_loads_cameras(tmp_path: Path):
    cfg = create_config(tmp_path)
    manager = CameraManager(config_path=cfg)
    assert len(manager.cameras) == 2
    assert isinstance(manager.cameras[0], USBCamera)
    assert isinstance(manager.cameras[1], KeyenceCamera)


def test_connect_all(tmp_path: Path):
    cfg = create_config(tmp_path)
    manager = CameraManager(config_path=cfg)
    manager.connect_all()
    statuses = [cam.status for cam in manager.cameras]
    assert statuses == ["connected", "connected"]


def test_connect_single(tmp_path: Path):
    cfg = create_config(tmp_path)
    manager = CameraManager(config_path=cfg)
    assert manager.connect_camera(2) is True
    assert manager.get_camera(2).status == "connected"
    with pytest.raises(ValueError):
        manager.connect_camera(99)
