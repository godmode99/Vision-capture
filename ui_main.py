from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QLineEdit, QComboBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit, QTableWidget,
    QTableWidgetItem, QGroupBox, QStatusBar, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QPixmap

import sys

class VisionInspectionUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Protocol Vision IV4")
        self.setGeometry(200, 200, 800, 450)
        self.init_ui()

    def init_ui(self):
        # Camera Status Section
        cam_status_box = QGroupBox("Camera Status")
        cam_status_layout = QVBoxLayout()
        self.cam_labels = []
        for i in range(1, 4):
            lbl = QLabel(f"CAM #{i}: OFF")
            lbl.setStyleSheet("color: gray;")
            self.cam_labels.append(lbl)
            cam_status_layout.addWidget(lbl)
        cam_status_box.setLayout(cam_status_layout)

        # Serial/Model Section
        serial_box = QGroupBox("Serial / Barcode")
        serial_layout = QVBoxLayout()
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("Serial Input")
        detect_btn = QPushButton("Detect Model")
        self.model_label = QLabel("Model: -")
        serial_layout.addWidget(self.serial_input)
        serial_layout.addWidget(detect_btn)
        serial_layout.addWidget(self.model_label)
        serial_box.setLayout(serial_layout)

        # Control Section
        control_box = QGroupBox("Control")
        control_layout = QVBoxLayout()
        self.trigger_btn = QPushButton("Trigger")
        self.auto_trigger_btn = QPushButton("Auto Trigger")
        self.auto_trigger_interval = QComboBox()
        self.auto_trigger_interval.addItems(["0 s", "1 s", "2 s", "5 s", "10 s"])
        control_layout.addWidget(self.trigger_btn)
        control_layout.addWidget(self.auto_trigger_btn)
        control_layout.addWidget(QLabel("Auto Trigger"))
        control_layout.addWidget(self.auto_trigger_interval)
        control_box.setLayout(control_layout)

        # Camera Preview Section
        preview_box = QGroupBox("Camera Preview")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(240, 180)
        self.preview_label.setStyleSheet("background-color: #222;")
        preview_layout.addWidget(self.preview_label)
        preview_box.setLayout(preview_layout)

        # Screenshot/Save Section
        screenshot_box = QVBoxLayout()
        self.screenshot_btn = QPushButton("Screenshot")
        self.save_btn = QPushButton("Save")
        screenshot_box.addWidget(self.screenshot_btn)
        screenshot_box.addWidget(self.save_btn)

        # Register/Config
        reg_config_layout = QHBoxLayout()
        self.register_btn = QPushButton("Register Model")
        self.config_btn = QPushButton("Config")
        reg_config_layout.addWidget(self.register_btn)
        reg_config_layout.addWidget(self.config_btn)

        # History Table
        history_box = QGroupBox("History")
        history_layout = QVBoxLayout()
        self.last_scan_label = QLabel("Last Scan: -")
        self.history_table = QTableWidget(0, 4)
        self.history_table.setHorizontalHeaderLabels(["Serial", "Model", "Time", "Status"])
        history_layout.addWidget(self.last_scan_label)
        history_layout.addWidget(self.history_table)
        history_box.setLayout(history_layout)

        # Export Log
        export_layout = QHBoxLayout()
        self.export_btn = QPushButton("Export Log")
        export_layout.addWidget(self.export_btn)

        # Status bar
        self.status = QStatusBar()
        self.status.showMessage("Connected x3   Error x0   NG x1")

        # Layout Grid
        grid = QGridLayout()
        grid.addWidget(cam_status_box, 0, 0)
        grid.addWidget(serial_box, 0, 1)
        grid.addWidget(control_box, 0, 2)
        grid.addWidget(preview_box, 1, 0)
        grid.addLayout(screenshot_box, 1, 1)
        grid.addWidget(history_box, 1, 2)
        grid.addLayout(reg_config_layout, 2, 0)
        grid.addLayout(export_layout, 2, 2)
        grid.addWidget(self.status, 3, 0, 1, 3)

        self.setLayout(grid)

        # Example event: update status camera 1 to OK
        self.cam_labels[0].setText("CAM #1: OK")
        self.cam_labels[0].setStyleSheet("color: green;")
        self.cam_labels[1].setText("CAM #2: NG")
        self.cam_labels[1].setStyleSheet("color: red;")
        self.cam_labels[2].setText("CAM #3: OFF")
        self.cam_labels[2].setStyleSheet("color: gray;")
        # ใส่ event handler จริงเพิ่มเองได้เลย

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VisionInspectionUI()
    window.show()
    sys.exit(app.exec_())
