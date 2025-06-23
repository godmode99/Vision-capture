from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QLineEdit, QComboBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit, QTableWidget,
    QTableWidgetItem, QGroupBox, QStatusBar, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QPixmap

import sys
import datetime
import os

class VisionInspectionUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Protocol Vision IV4")
        self.setGeometry(200, 200, 800, 450)
        self.init_ui()
        self.log_data = []

    def init_ui(self):
        # Camera Status Section
        cam_status_box = QGroupBox("Camera Status")
        cam_status_layout = QVBoxLayout()
        self.cam_labels = []
        cam_status = ["OK", "NG", "OFF"]
        cam_colors = ["green", "red", "gray"]
        for i in range(3):
            lbl = QLabel(f"CAM #{i+1}: {cam_status[i]}")
            lbl.setStyleSheet(f"color: {cam_colors[i]};")
            self.cam_labels.append(lbl)
            cam_status_layout.addWidget(lbl)
        cam_status_box.setLayout(cam_status_layout)

        # Serial/Model Section
        serial_box = QGroupBox("Serial / Barcode")
        serial_layout = QVBoxLayout()
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("Serial Input")
        detect_btn = QPushButton("Detect Model")
        detect_btn.clicked.connect(self.handle_detect_model)
        self.model_label = QLabel("Model: -")
        serial_layout.addWidget(self.serial_input)
        serial_layout.addWidget(detect_btn)
        serial_layout.addWidget(self.model_label)
        serial_box.setLayout(serial_layout)

        # Control Section
        control_box = QGroupBox("Control")
        control_layout = QVBoxLayout()
        self.trigger_btn = QPushButton("Trigger")
        self.trigger_btn.clicked.connect(self.handle_trigger)
        self.auto_trigger_btn = QPushButton("Auto Trigger")
        self.auto_trigger_btn.clicked.connect(self.handle_auto_trigger)
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
        self.screenshot_btn.clicked.connect(self.handle_screenshot)
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.handle_save)
        screenshot_box.addWidget(self.screenshot_btn)
        screenshot_box.addWidget(self.save_btn)

        # Register/Config
        reg_config_layout = QHBoxLayout()
        self.register_btn = QPushButton("Register Model")
        self.register_btn.clicked.connect(self.handle_register_model)
        self.config_btn = QPushButton("Config")
        self.config_btn.clicked.connect(self.handle_config)
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
        self.export_btn.clicked.connect(self.handle_export_log)
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

        # Timer สำหรับ Auto Trigger
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.handle_trigger)

    ### --- Event Handler Functions (ใส่ logic mock ทุกปุ่ม) ---

    def handle_trigger(self):
        serial = self.serial_input.text() or "N/A"
        model = self.model_label.text().replace("Model: ", "")
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "OK"  # สมมุติผลลัพธ์
        # Mock: update preview image (สี random)
        import random
        color = random.choice(["#F88", "#8F8", "#88F", "#FF8", "#8FF", "#F8F"])
        pix = QPixmap(240, 180)
        pix.fill(Qt.transparent)
        pix.fill(Qt.GlobalColor.black)
        self.preview_label.setStyleSheet(f"background-color: {color};")
        # Update History Table
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        self.history_table.setItem(row, 0, QTableWidgetItem(serial))
        self.history_table.setItem(row, 1, QTableWidgetItem(model))
        self.history_table.setItem(row, 2, QTableWidgetItem(now))
        self.history_table.setItem(row, 3, QTableWidgetItem(status))
        self.last_scan_label.setText(f"Last Scan: {now}")
        self.log_data.append({"serial": serial, "model": model, "time": now, "status": status})
        self.status.showMessage(f"Triggered! Serial: {serial} Model: {model}")

    def handle_auto_trigger(self):
        interval_text = self.auto_trigger_interval.currentText()
        seconds = int(interval_text.split()[0])
        if seconds == 0:
            self.auto_timer.stop()
            self.status.showMessage("Auto Trigger stopped.")
        else:
            self.auto_timer.start(seconds * 1000)
            self.status.showMessage(f"Auto Trigger every {seconds} seconds.")

    def handle_save(self):
        # Mock: save to fake file
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        serial = self.serial_input.text() or "N/A"
        filename = f"{serial}_{now}.txt"
        with open(filename, "w") as f:
            f.write(f"Serial: {serial}\nTime: {now}\n")
        self.status.showMessage(f"Saved {filename}")
        QMessageBox.information(self, "Save", f"Saved file: {filename}")

    def handle_export_log(self):
        # Mock: export log as CSV
        fname, _ = QFileDialog.getSaveFileName(self, "Export Log", "", "CSV Files (*.csv)")
        if fname:
            import csv
            with open(fname, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=["serial", "model", "time", "status"])
                writer.writeheader()
                for row in self.log_data:
                    writer.writerow(row)
            self.status.showMessage(f"Exported log to {fname}")
            QMessageBox.information(self, "Export Log", f"Exported log to:\n{fname}")

    def handle_detect_model(self):
        # Mock: อ่าน serial แล้วเดา model จาก 4 ตัวหน้า
        serial = self.serial_input.text()
        if not serial or len(serial) < 4:
            self.model_label.setText("Model: -")
            QMessageBox.warning(self, "Detect Model", "Serial ต้องมีอย่างน้อย 4 ตัวอักษร")
            return
        prefix = serial[:4].upper()
        # สมมติ mapping (เปลี่ยนตามจริง)
        model_map = {"A123": "IV3-2202", "B543": "IV2-3000"}
        model = model_map.get(prefix, "Unknown")
        self.model_label.setText(f"Model: {model}")
        self.status.showMessage(f"Detected Model: {model}")

    def handle_screenshot(self):
        # Mock: สร้างรูป screenshot ปลอม
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"screenshot_{now}.png"
        pix = QPixmap(self.preview_label.size())
        self.preview_label.render(pix)
        pix.save(fname)
        self.status.showMessage(f"Screenshot saved: {fname}")
        QMessageBox.information(self, "Screenshot", f"Screenshot saved:\n{fname}")

    def handle_register_model(self):
        QMessageBox.information(self, "Register Model", "ยังไม่ implement (mock)")

    def handle_config(self):
        QMessageBox.information(self, "Config", "ยังไม่ implement (mock)")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VisionInspectionUI()
    window.show()
    sys.exit(app.exec_())
