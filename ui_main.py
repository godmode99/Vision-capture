"""Tkinter UI for the vision inspection system."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from datetime import datetime


class MainUI:
    """Main application window for controlling vision inspection."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Vision Inspection")

        # --- Top control frame ---
        top = ttk.Frame(root)
        top.pack(side="top", fill="x", padx=10, pady=10)

        # Trigger button for starting capture/inspection
        self.trigger_btn = ttk.Button(top, text="Trigger")
        self.trigger_btn.pack(side="left")

        # Serial and model labels show the current device info
        self.serial_label = ttk.Label(top, text="Serial: -")
        self.serial_label.pack(side="left", padx=10)

        self.model_label = ttk.Label(top, text="Model: -")
        self.model_label.pack(side="left", padx=10)

        # --- Image preview ---
        # Placeholder label where a captured image would be shown
        self.image_label = ttk.Label(
            root,
            text="Image preview",
            borderwidth=1,
            relief="solid",
            width=40,
            height=10,
        )
        self.image_label.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Log table ---
        self.log_table = ttk.Treeview(root, columns=("time", "event"), show="headings", height=8)
        self.log_table.heading("time", text="Time")
        self.log_table.heading("event", text="Event")
        self.log_table.pack(fill="both", expand=True, padx=10, pady=5)

        # --- Bottom status and settings ---
        bottom = ttk.Frame(root)
        bottom.pack(side="bottom", fill="x", padx=10, pady=5)

        self.settings_btn = ttk.Button(bottom, text="Settings")
        self.settings_btn.pack(side="left")

        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(bottom, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_bar.pack(side="left", fill="x", expand=True, padx=(10, 0))

    # ------------------------------------------------------------------
    # UI update helpers
    # ------------------------------------------------------------------
    def set_image(self, image: tk.PhotoImage) -> None:
        """Display *image* in the preview area."""
        self.image_label.configure(image=image)
        self.image_label.image = image

    def update_serial(self, serial: str) -> None:
        """Update the serial display."""
        self.serial_label.configure(text=f"Serial: {serial}")

    def update_model(self, model: str) -> None:
        """Update the model display."""
        self.model_label.configure(text=f"Model: {model}")

    def update_status(self, text: str) -> None:
        """Set the text shown in the status bar."""
        self.status_var.set(text)

    def add_log(self, message: str) -> None:
        """Append a line with *message* to the log table."""
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_table.insert("", "end", values=(ts, message))
