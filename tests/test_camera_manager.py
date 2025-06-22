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


def test_check_all_statuses(tmp_path: Path, caplog):
    cfg = tmp_path / "cfg.json"
    device = tmp_path / "video0"
    device.touch()
    missing = tmp_path / "missing"
    data = {
        "autoReconnect": True,
        "cameras": [
            {"id": 1, "type": "usb", "name": "USB1", "device": str(device)},
            {"id": 2, "type": "usb", "name": "USB2", "device": str(missing)},
            {
                "id": 3,
                "type": "keyence",
                "name": "Key",
                "ip": "1.2.3.4",
                "port": 8500,
            },
        ],
    }
    cfg.write_text(json.dumps(data))

    manager = CameraManager(config_path=cfg)
    statuses = manager.check_all_statuses()

    assert {d["id"]: d["status"] for d in statuses} == {
        1: "connected",
        2: "disconnected",
        3: "connected",
    }
    assert "Failed to connect camera 2" in caplog.text


def test_capture_single_and_all(tmp_path: Path):
    cfg = create_config(tmp_path)
    manager = CameraManager(config_path=cfg)
    manager.connect_all()

    single = manager.capture_images(1)
    assert set(single) == {1}
    assert single[1] is not None and single[1].is_file()

    all_caps = manager.capture_images()
    assert set(all_caps) == {1, 2}
    assert all(path is not None and path.is_file() for path in all_caps.values())


def test_capture_error_handling(tmp_path: Path):
    cfg = create_config(tmp_path)
    manager = CameraManager(config_path=cfg)
    manager.connect_camera(1)

    results = manager.capture_images()
    assert results[1] is not None
    assert results[2] is None
