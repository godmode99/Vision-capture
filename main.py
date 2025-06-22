"""Simple event controller for the vision inspection UI."""

from __future__ import annotations

import tkinter as tk

from ui_main import MainUI


class MainController:
    """Connect :class:`MainUI` widgets to application logic."""

    def __init__(self, ui: MainUI) -> None:
        self.ui = ui
        # Wire up button commands
        self.ui.trigger_btn.configure(command=self.on_trigger)
        self.ui.settings_btn.configure(command=self.on_settings)

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------
    def on_trigger(self) -> None:
        """Handle trigger button clicks."""
        # Placeholder logic for a real capture routine
        serial = "SN123456"
        model = "ModelA"

        self.ui.update_serial(serial)
        self.ui.update_model(model)
        self.ui.update_status("Capture triggered")
        self.ui.add_log("Trigger pressed")

    def on_settings(self) -> None:
        """Handle settings button clicks."""
        self.ui.update_status("Opening settings...")
        self.ui.add_log("Settings selected")


def run() -> None:
    """Entry point to start the application."""
    root = tk.Tk()
    ui = MainUI(root)
    MainController(ui)
    root.mainloop()


if __name__ == "__main__":
    run()
