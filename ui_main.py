import serial
from PyQt5.QtCore import QThread, pyqtSignal
import serial.tools.list_ports
from manager_cam import trigger_iv2_camera
from threading import Thread


from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QLineEdit,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QStatusBar,
    QFileDialog,
    QMessageBox,
    QDialog,
    QFormLayout,
    QDialogButtonBox,

)
class CameraStatusWidget(QGroupBox):
    def __init__(self, cam_models, cam_statuses, parent=None):
        super().__init__("Camera Status", parent)
        self.cam_models = cam_models
        self.cam_statuses = cam_statuses
        self.colors = {"OK": "green", "NG": "red", "OFF": "gray", "ERROR": "orange"}

        self.layout = QVBoxLayout()
        self.cam_select = QComboBox()
        self.cam_select.addItems([f"CAM #{i+1}" for i in range(len(cam_models))])
        self.cam_select.currentIndexChanged.connect(self.update_display)

        self.model_label = QLabel()
        self.status_label = QLabel()

        self.layout.addWidget(self.cam_select)
        self.layout.addWidget(self.model_label)
        self.layout.addWidget(self.status_label)
        self.setLayout(self.layout)

        self.update_display(0)  # Show cam #1 info on start

    def update_display(self, idx):
        model = self.cam_models[idx]
        status = self.cam_statuses[idx]
        color = self.colors.get(status, "black")
        self.model_label.setText(f"Model: {model}")
        self.status_label.setText(f"Status: {status}")
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.model_label.setStyleSheet("font-weight: bold;")

    def set_status(self, idx, status):
        self.cam_statuses[idx] = status
        if self.cam_select.currentIndex() == idx:
            self.update_display(idx)
    def set_model(self, idx, model):
        self.cam_models[idx] = model
        if self.cam_select.currentIndex() == idx:
            self.update_display(idx)

from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QPixmap


import sys
import datetime
import os
import serial.tools.list_ports
def is_usb_camera_connected(port_name):
    ports = [p.device for p in serial.tools.list_ports.comports()]
    return port_name in ports



def get_config_path():
    # รองรับรันจาก script ปกติ หรือ exe (pyinstaller)
    if getattr(sys, 'frozen', False):
        app_path = os.path.dirname(sys.executable)
    else:
        app_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(app_path, 'config', 'config.json')
class SerialReaderThread(QThread):
    received = pyqtSignal(str)

    def __init__(self, port='COM3', baudrate=9600, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate
        self._running = True

    def run(self):
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=1)
        except Exception as e:
            print(f"เปิดพอร์ตไม่ได้: {e}")
            return
        while self._running:
            try:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    self.received.emit(line)
            except Exception as e:
                print(f"Serial Error: {e}")

    def stop(self):
        self._running = False

class RegisterModelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register Model")
        layout = QFormLayout(self)
        self.prefix_input = QLineEdit()
        self.model_input = QLineEdit()
        layout.addRow("Serial Prefix (4 ตัว):", self.prefix_input)
        layout.addRow("Model Name:", self.model_input)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

class CameraMock:
    def __init__(self, id):
        self.id = id
        self.connected = True
    def trigger(self):
        print(f"Camera {self.id} triggered")
    def is_connected(self):
        return self.id == 1

class VisionInspectionUI(QWidget):

    def on_serial_received(self, line): 
        self.serial_input.setText(line)
   
    
    def select_save_path(self):
     from PyQt5.QtWidgets import QFileDialog
     folder = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์เก็บไฟล์")
     if folder:
        self.save_path = folder
        self.path_label.setText(f"Path: {folder}")

    def trigger_all_cameras(self):
        print("DEBUG: cameras in trigger", self.cameras)
        from threading import Thread
        import traceback
        threads = []
        def run_trigger(cam):
            try:
                print(f"TRIGGER: {cam}")
                cam.trigger()
            except Exception as e:
                print(f"Camera {cam} error: {e}")
                traceback.print_exc()
        print("CAM LIST:", self.cameras)
        for cam in self.cameras:
            t = Thread(target=run_trigger, args=(cam,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        self.status.showMessage("Trigger All Done!")
   
    
    def __init__(self):
        super().__init__()
        self.cameras = [CameraMock(1), CameraMock(2)]
        print("DEBUG: cameras initialized", self.cameras)
        self.setWindowTitle("Protocol Vision IV4")
        self.setGeometry(200, 200, 800, 450)
        self.init_ui()
        self.log_data = []
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_camera_status)
        self.status_timer.start(1000)

    def update_camera_status(self):
        port = self.port_select.currentText()  # สมมุติเลือกพอร์ตใน UI หรือ mapping port จากกล้อง
        if not port:   # ยังไม่ได้เลือก port หรือไม่มี port ในเครื่อง
             status = "Disconnect"
             color = "red"
        else:
             connected = is_usb_camera_connected(port)
             status = "Connect" if connected else "Disconnect"
             color = "green" if connected else "red"
        self.cam_status_box.status_label.setText(f"Status: {status}")
        self.cam_status_box.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def init_ui(self):
        main_layout = QVBoxLayout()
         # --- Section Camera Status Widget ---
        cam_models = ["IV2", "IV3", "IV4"]
        cam_statuses = ["-", "-", "-"]
        self.cam_status_box = CameraStatusWidget(cam_models, cam_statuses)
        main_layout.addWidget(self.cam_status_box)
        
        serial_box = QGroupBox("Serial / Barcode")
        serial_layout = QVBoxLayout()
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("Serial Input")
        self.port_select = QComboBox()
        self.refresh_ports()
        serial_layout.addWidget(QLabel("Select Port:"))
        serial_layout.addWidget(self.port_select)
        detect_btn = QPushButton("Detect Model")
        serial_layout.addWidget(self.serial_input)
        serial_layout.addWidget(detect_btn)
        self.model_label = QLabel("Model: -")
        serial_layout.addWidget(self.model_label)
        serial_box.setLayout(serial_layout)
        main_layout.addWidget(serial_box)


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
        self.trigger_all_btn = QPushButton("Trigger All")
        self.trigger_all_btn.clicked.connect(self.trigger_all_cameras)
        control_layout.addWidget(self.trigger_all_btn)

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

        self.path_label = QLabel("Path: (ยังไม่ได้เลือก)")
        self.select_path_btn = QPushButton("เลือก Path เก็บไฟล์")
        self.select_path_btn.clicked.connect(self.select_save_path)
        screenshot_box.addWidget(self.select_path_btn)
        screenshot_box.addWidget(self.path_label)

        self.save_path = ""


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
        self.status.showMessage("")
        

        # Layout Grid
        grid = QGridLayout()
        grid.addWidget(self.cam_status_box, 0, 0)
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
    def refresh_ports(self):
        import serial.tools.list_ports
        ports = [port.device for port in serial.tools.list_ports.comports()]
        print("FOUND PORTS:", ports)
        self.port_select.clear()
        self.port_select.addItems(ports)

    def start_serial_thread(self):
        port = self.port_select.currentText()
        self.serial_thread = SerialReaderThread(port=port, baudrate=9600)
        self.serial_thread.received.connect(self.on_serial_received)
        self.serial_thread.start()
        self.port_select.currentTextChanged.connect(self.restart_serial_thread)

    def restart_serial_thread(self):
        if hasattr(self, 'serial_thread'):
           self.serial_thread.stop()
           self.serial_thread.wait()
           self.start_serial_thread()

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
        if  seconds == 0:
            self.auto_timer.stop()
            self.status.showMessage("Auto Trigger stopped.")
        else:
            self.auto_timer.start(seconds * 1000)
            self.status.showMessage(f"Auto Trigger every {seconds} seconds.")

    def handle_save(self):
      import os
      from PyQt5.QtWidgets import QMessageBox
      now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
      serial = self.serial_input.text() or "N/A"
      fname = f"{serial}_{now}.txt"
      folder = self.save_path if self.save_path else ""
      if not folder:
        QMessageBox.warning(self, "Error", "ยังไม่ได้เลือก Path เก็บไฟล์")
        return
      fpath = os.path.join(folder, fname)
      try:
         with open(fpath, "w", encoding="utf-8") as f:
            f.write(f"Serial: {serial}\nTime: {now}\n")
         self.status.showMessage(f"Saved {fpath}")
         QMessageBox.information(self, "Save", f"Saved file: {fpath}")
      except Exception as e:
        QMessageBox.critical(self, "Error", f"Save file failed: {e}")


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
     import os
     from PyQt5.QtWidgets import QMessageBox
     now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
     fname = f"screenshot_{now}.png"
     folder = self.save_path if self.save_path else ""
     if not folder:
        QMessageBox.warning(self, "Error", "ยังไม่ได้เลือก Path เก็บไฟล์")
        return
     fpath = os.path.join(folder, fname)
     pix = QPixmap(self.preview_label.size())
     self.preview_label.render(pix)
     pix.save(fpath)
     self.status.showMessage(f"Screenshot saved: {fpath}")
     QMessageBox.information(self, "Screenshot", f"Screenshot saved:\n{fpath}")

    def handle_register_model(self):
        import json
        dialog = RegisterModelDialog(self)
        if dialog.exec_() == QDialog.Accepted:
           prefix = dialog.prefix_input.text().strip().upper()
           model = dialog.model_input.text().strip()
           if len(prefix) != 4 or not model:
                QMessageBox.warning(self, "Error", "Serial Prefix ต้องมี 4 ตัวอักษร, Model ห้ามว่าง")
                return
           config_path = get_config_path()
           try:
                with open(config_path, "r") as f:
                  config = json.load(f)
           except Exception as e:
                QMessageBox.critical(self, "Error", f"อ่าน config ไม่ได้: {e}")
                return
           mapping = config.get("serial_mapping", {})
           mapping[prefix] = model
           config["serial_mapping"] = mapping
           try:
               with open(config_path, "w") as f:
                    json.dump(config, f, indent=4)
                    QMessageBox.information(self, "Register Model", f"เพิ่ม mapping {prefix} → {model} สำเร็จ!")
           except Exception as e:
                    QMessageBox.critical(self, "Error", f"บันทึก config ไม่ได้: {e}")


    def handle_config(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Config", "Test")
        
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VisionInspectionUI()
    window.show()
    sys.exit(app.exec_())

def closeEvent(self, event):
    if hasattr(self, 'serial_thread'):
        self.serial_thread.stop()
        self.serial_thread.wait()
    event.accept()


def handle_trigger(self):
    ip = "192.168.0.10"  
    try:
        ok, raw = trigger_iv2_camera(ip)
        if ok:
            self.status.showMessage("Result: OK")
        else:
            self.status.showMessage("Result: NG")
        print("Raw:", raw)
    except Exception as e:
        self.status.showMessage(f"Error: {e}")




