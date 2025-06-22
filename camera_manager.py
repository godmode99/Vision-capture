"""Camera management utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import logging
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

from camera_config import load_camera_objects, Camera as CameraConfig
from config_loader import ConfigLoader


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

    def capture(self) -> Path:  # pragma: no cover - base
        """Capture an image and return the file path."""
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

    def capture(self) -> Path:
        """Simulate capturing an image from a USB camera."""
        if self.status != "connected":
            raise RuntimeError("Camera not connected")
        fd, path = tempfile.mkstemp(suffix=".jpg")
        Path(path).write_bytes(b"usb image")
        self.last_image = Path(path)
        return Path(path)


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

    def capture(self) -> Path:
        """Simulate capturing an image from a Keyence camera."""
        if self.status != "connected":
            raise RuntimeError("Camera not connected")
        fd, path = tempfile.mkstemp(suffix=".jpg")
        Path(path).write_bytes(b"keyence image")
        self.last_image = Path(path)
        return Path(path)


class CameraManager:
    """Manage multiple cameras defined in a configuration file."""

    def __init__(self, config_path: str | Path = "config/config.json") -> None:
        loader = ConfigLoader(config_path)
        config = loader.load_config()
        self.auto_reconnect = bool(config.get("autoReconnect", False))
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

    def check_all_statuses(self) -> List[Dict[str, str]]:
        """Return status information for all cameras.

        If ``auto_reconnect`` is enabled, attempt to reconnect any camera that
        is not currently connected. Errors are logged when a connection fails.
        """
        statuses: List[Dict[str, str]] = []
        for cam in self.cameras:
            if cam.status != "connected" and self.auto_reconnect:
                if not cam.connect():
                    logging.error("Failed to connect camera %s", cam.id)
            statuses.append({"id": cam.id, "status": cam.status})
        return statuses

    def capture_images(self, cam_id: Optional[int] = None) -> Dict[int, Optional[Path]]:
        """Capture an image from one camera or all cameras.

        Parameters
        ----------
        cam_id : int, optional
            When provided, only the camera matching ``cam_id`` will be used.
            When ``None``, all cameras are triggered.

        Returns
        -------
        dict
            Mapping of camera id to captured file path or ``None`` when the
            capture failed.
        """

        if cam_id is not None:
            cam = self.get_camera(cam_id)
            if cam is None:
                raise ValueError(f"Camera {cam_id} not found")
            cameras = [cam]
        else:
            cameras = list(self.cameras)

        results: Dict[int, Optional[Path]] = {}
        with ThreadPoolExecutor() as executor:
            future_map = {executor.submit(cam.capture): cam for cam in cameras}
            for future in as_completed(future_map):
                cam = future_map[future]
                try:
                    results[cam.id] = future.result()
                except Exception as exc:  # pragma: no cover - error path
                    logging.error("Failed to capture image from camera %s: %s", cam.id, exc)
                    results[cam.id] = None
        return results
