"""Simple event controller for the vision inspection UI."""

from __future__ import annotations

import tkinter as tk

from ui_main import MainUI
from manager_cam import CameraManager
from input_manager import InputManager
from event_logger import EventLogger
import model_api
from pathlib import Path


class MainController:
    """Connect :class:`MainUI` widgets to application logic."""

    def __init__(
        self,
        ui: MainUI,
        *,
        camera_manager: CameraManager | None = None,
        input_manager: InputManager | None = None,
        event_logger: EventLogger | None = None,
        image_dir: str | Path = "images",
        log_file: str | Path = "logs/events.txt",
    ) -> None:
        self.ui = ui
        self.camera_manager = camera_manager or CameraManager()
        self.input_manager = input_manager or InputManager()
        self.event_logger = event_logger or EventLogger(log_file)
        self.image_dir = Path(image_dir)
        self.active_camera: int | None = None

        # Wire up button commands
        self.ui.trigger_btn.configure(command=self.on_trigger)
        self.ui.settings_btn.configure(command=self.on_settings)

        if hasattr(self.ui, "camera_select"):
            self.ui.camera_select.configure(command=self.on_change_camera)
        if hasattr(self.ui, "serial_entry"):
            self.ui.serial_entry.configure(command=self.on_serial_received)
        if hasattr(self.ui, "export_btn"):
            self.ui.export_btn.configure(command=self.on_export_logs)

    def log_and_status(self, msg: str, level: str = "info") -> None:
        """Log *msg* via :class:`EventLogger` and show it on the status bar."""
        self.event_logger.log_event(level, msg)
        self.ui.update_status(msg)

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------
    def on_trigger(self) -> None:
        """Handle trigger button clicks."""
        try:
            serial = self.input_manager.read_serial()
            model = model_api.select_model(serial) or ""
            self.ui.update_serial(serial)
            if model:
                self.ui.update_model(model)

            images = self.camera_manager.capture_images(self.active_camera)
            for cam_id, path in images.items():
                if path is not None:
                    saved = self.camera_manager.save_latest_image(
                        cam_id, self.image_dir, serial=serial, status="OK"
                    )
                    self.ui.add_log(str(saved))

            self.event_logger.log_event(
                "info", "capture complete", {"serial": serial, "model": model}
            )
            self.ui.update_status("Capture complete")
        except Exception as exc:  # pragma: no cover - error path
            self.log_and_status(f"Capture failed: {exc}", level="error")

    def on_settings(self) -> None:
        """Handle settings button clicks."""
        self.ui.update_status("Opening settings...")
        self.ui.add_log("Settings selected")

    # ------------------------------------------------------------------
    # Other event handlers
    # ------------------------------------------------------------------
    def on_change_camera(self, cam_id: int) -> None:
        """Switch the active camera."""
        self.active_camera = cam_id
        self.log_and_status(f"Camera {cam_id} selected")

    def on_serial_received(self, serial: str) -> None:
        """Update UI when a serial is received."""
        self.ui.update_serial(serial)
        model = model_api.select_model(serial) or ""
        if model:
            self.ui.update_model(model)
        self.event_logger.log_event("info", f"serial {serial}", {"model": model})

    def on_export_logs(self, path: str) -> None:
        """Export logs to ``path``."""
        try:
            if path.endswith(".csv"):
                self.event_logger.save_log_csv(path)
            else:
                self.event_logger.save_log_json(path)
            self.log_and_status(f"Logs exported to {path}")
        except Exception as exc:  # pragma: no cover - error path
            self.log_and_status(f"Failed to export logs: {exc}", level="error")


def run() -> None:
    """Entry point to start the application."""
    root = tk.Tk()
    ui = MainUI(root)
    MainController(ui)
    root.mainloop()


if __name__ == "__main__":
    run()
