"""Camera management utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from camera_config import load_camera_objects, Camera as CameraConfig


@dataclass
class BaseCamera:
    """Base class for all camera implementations."""

    id: int
    name: str
    type: str
    status: str = "disconnected"
    last_image: Optional[object] = None

    def connect(self) -> bool:  # pragma: no cover - base
        """Connect to the camera. Should be implemented by subclasses."""
        raise NotImplementedError


class USBCamera(BaseCamera):
    """Mock implementation of a USB camera."""

    def __init__(self, *, device: str, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.device = device

    def connect(self) -> bool:
        """Pretend to connect to a USB device by checking if the path exists."""
        if Path(self.device).exists():
            self.status = "connected"
        else:
            self.status = "disconnected"
        return self.status == "connected"


class KeyenceCamera(BaseCamera):
    """Mock implementation of a Keyence network camera."""

    def __init__(self, *, ip: str, port: int, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.ip = ip
        self.port = port

    def connect(self) -> bool:
        """Pretend to connect to the camera via TCP/IP."""
        # Real implementation would open a socket here. Always succeed for now.
        self.status = "connected"
        return True


class CameraManager:
    """Manage multiple cameras defined in a configuration file."""

    def __init__(self, config_path: str | Path = "config/config.json") -> None:
        configs = load_camera_objects(config_path)
        self.cameras: List[BaseCamera] = [self._create_camera(cfg) for cfg in configs]

    @staticmethod
    def _create_camera(cfg: CameraConfig) -> BaseCamera:
        if cfg.type == "usb":
            return USBCamera(id=cfg.id, name=cfg.name, type=cfg.type, device=cfg.device or "")
        if cfg.type == "keyence":
            return KeyenceCamera(id=cfg.id, name=cfg.name, type=cfg.type, ip=cfg.ip or "", port=cfg.port or 0)
        raise ValueError(f"Unsupported camera type: {cfg.type}")

    def connect_all(self) -> None:
        """Connect every camera managed by this instance."""
        for cam in self.cameras:
            cam.connect()

    def connect_camera(self, cam_id: int) -> bool:
        """Connect the camera with the given ``cam_id`` if found."""
        cam = self.get_camera(cam_id)
        if cam is None:
            raise ValueError(f"Camera {cam_id} not found")
        return cam.connect()

    def get_camera(self, cam_id: int) -> Optional[BaseCamera]:
        """Return camera instance with ``cam_id`` or ``None``."""
        for cam in self.cameras:
            if cam.id == cam_id:
                return cam
        return None
