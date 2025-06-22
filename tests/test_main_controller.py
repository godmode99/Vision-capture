import io
from pathlib import Path

import pytest

from main import MainController
from event_logger import EventLogger


class DummyWidget:
    def configure(self, command=None):
        self.command = command

    def invoke(self):
        if self.command:
            self.command()


class DummyUI:
    def __init__(self):
        self.trigger_btn = DummyWidget()
        self.settings_btn = DummyWidget()
        self.serial = ""
        self.model = ""
        self.status = ""
        self.logs = []

    def update_serial(self, serial: str) -> None:
        self.serial = serial

    def update_model(self, model: str) -> None:
        self.model = model

    def update_status(self, text: str) -> None:
        self.status = text

    def add_log(self, msg: str) -> None:
        self.logs.append(msg)


class FakeInputManager:
    def __init__(self, serial: str = "SN1") -> None:
        self.serial = serial

    def read_serial(self):
        return self.serial


class FakeCameraManager:
    def __init__(self, base: Path):
        self.base = base
        (self.base / "raw.jpg").write_text("img")

    def capture_images(self, cam_id=None):
        return {1: self.base / "raw.jpg"}

    def save_latest_image(self, cam_id, dest_dir, **kwargs):
        dest = Path(dest_dir) / "saved.jpg"
        Path(dest_dir).mkdir(parents=True, exist_ok=True)
        dest.write_text("img")
        return dest


class ErrorCameraManager(FakeCameraManager):
    def capture_images(self, cam_id=None):
        raise RuntimeError("fail")


def test_on_trigger_success(tmp_path: Path):
    ui = DummyUI()
    logger = EventLogger(tmp_path / "log.txt")
    cam = FakeCameraManager(tmp_path)
    controller = MainController(
        ui,
        camera_manager=cam,
        input_manager=FakeInputManager("AB12XXXX"),
        event_logger=logger,
        image_dir=tmp_path / "images",
    )

    controller.on_trigger()

    assert ui.serial == "AB12XXXX"
    assert ui.status == "Capture complete"
    assert ui.logs and "saved.jpg" in ui.logs[0]
    assert logger.logs and logger.logs[-1].event_type == "info"
    saved = Path(ui.logs[0])
    assert saved.is_file()


def test_on_trigger_error(tmp_path: Path):
    ui = DummyUI()
    logger = EventLogger(tmp_path / "log.txt")
    cam = ErrorCameraManager(tmp_path)
    controller = MainController(
        ui,
        camera_manager=cam,
        input_manager=FakeInputManager(),
        event_logger=logger,
        image_dir=tmp_path / "images",
    )

    controller.on_trigger()

    assert "failed" in ui.status.lower()
    assert logger.logs and logger.logs[-1].event_type == "error"


def test_export_logs(tmp_path: Path):
    ui = DummyUI()
    logger = EventLogger(tmp_path / "log.txt")
    cam = FakeCameraManager(tmp_path)
    controller = MainController(
        ui,
        camera_manager=cam,
        input_manager=FakeInputManager(),
        event_logger=logger,
        image_dir=tmp_path / "images",
    )

    controller.event_logger.log_event("info", "something")
    out = tmp_path / "out.csv"
    controller.on_export_logs(str(out))

    assert out.is_file()
    assert "exported" in ui.status.lower()
