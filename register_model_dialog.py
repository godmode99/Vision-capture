from __future__ import annotations

from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
)

from serial_input import validate_prefix


class RegisterModelDialog(QDialog):
    """Dialog to register a serial prefix mapping."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Register Model")
        layout = QFormLayout(self)

        self.prefix_input = QLineEdit()
        self.model_input = QLineEdit()

        layout.addRow("Serial Prefix (4 chars):", self.prefix_input)
        layout.addRow("Model Name:", self.model_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self._on_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _on_accept(self) -> None:
        prefix = self.prefix_input.text().strip().upper()
        model = self.model_input.text().strip()
        if not validate_prefix(prefix):
            QMessageBox.warning(self, "Invalid Prefix", "Prefix must be 4 alphanumeric characters.")
            return
        if not model:
            QMessageBox.warning(self, "Invalid Model", "Model name is required.")
            return
        self.prefix_input.setText(prefix)
        self.accept()

    def get_data(self) -> tuple[str, str]:
        """Return the entered prefix and model."""
        return self.prefix_input.text(), self.model_input.text()
