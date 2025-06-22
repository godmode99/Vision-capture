import json
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

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


def test_latest_image_helpers(tmp_path: Path):
    cfg = create_config(tmp_path)
    out_dir = tmp_path / "out"
    manager = CameraManager(config_path=cfg)
    manager.connect_all()

    # No capture yet
    assert manager.get_latest_image(1) is None

    caps = manager.capture_images()
    img_path = manager.get_latest_image(1)
    assert img_path == caps[1]
    assert isinstance(img_path, Path) and img_path.is_file()

    assert manager.get_latest_image(2) == caps[2]
    with pytest.raises(ValueError):
        manager.get_latest_image(99)

    fixed_time = datetime(2020, 1, 2, 3, 4, 5)
    saved = manager.save_latest_image(1, out_dir, serial="SN", status="OK", timestamp=fixed_time)
    expected = out_dir / "SN_OK_20200102_030405.jpg"
    assert saved == expected
    assert saved.is_file()


def test_disconnect_reconnect(tmp_path: Path):
    cfg = create_config(tmp_path)
    manager = CameraManager(config_path=cfg)
    manager.connect_all()

    assert manager.disconnect_camera(1) is True
    assert manager.get_camera(1).status == "disconnected"

    assert manager.reconnect_camera(1) is True
    assert manager.get_camera(1).status == "connected"


def test_parallel_reconnect(tmp_path: Path):
    cfg = create_config(tmp_path)
    manager = CameraManager(config_path=cfg)
    manager.connect_all()

    manager.disconnect_camera(1)
    manager.disconnect_camera(2)

    with ThreadPoolExecutor() as ex:
        futures = [ex.submit(manager.reconnect_camera, cid) for cid in (1, 2)]
        results = [f.result() for f in futures]

    assert results == [True, True]
    assert [cam.status for cam in manager.cameras] == ["connected", "connected"]


def test_reset_camera(tmp_path: Path):
    cfg = create_config(tmp_path)
    manager = CameraManager(config_path=cfg)
    manager.connect_all()

    new_device = tmp_path / "video1"
    new_device.touch()
    assert manager.reset_camera(1, device=str(new_device)) is True
    cam1 = manager.get_camera(1)
    assert isinstance(cam1, USBCamera)
    assert cam1.device == str(new_device)
    assert cam1.status == "connected"

    assert manager.reset_camera(2, port=8600) is True
    cam2 = manager.get_camera(2)
    assert isinstance(cam2, KeyenceCamera)
    assert cam2.port == 8600
    assert cam2.status == "connected"


def test_parallel_reset(tmp_path: Path):
    cfg = create_config(tmp_path)
    manager = CameraManager(config_path=cfg)
    manager.connect_all()

    dev1 = tmp_path / "v1"
    dev2 = tmp_path / "v2"
    dev1.touch()
    dev2.touch()

    with ThreadPoolExecutor() as ex:
        futures = [
            ex.submit(manager.reset_camera, 1, device=str(dev1)),
            ex.submit(manager.reset_camera, 2, port=8601),
        ]
        results = [f.result() for f in futures]

    assert results == [True, True]
    assert [cam.status for cam in manager.cameras] == ["connected", "connected"]
