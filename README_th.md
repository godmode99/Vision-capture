# ชุดเครื่องมือ Vision Capture

คอลเล็กชันโมดูลตัวช่วยขนาดเล็กสำหรับตั้งค่าและใช้งานระบบบันทึกภาพ
ประกอบด้วยยูทิลิตีสำหรับโหลดการตั้งค่ากล้อง เลือกรุ่นตามหมายเลขซีเรียล
และจัดการเส้นทางไฟล์ที่ระบุไว้ในไฟล์กำหนดค่า JSON

## การใช้งาน

1. ตรวจสอบให้แน่ใจว่ามีไฟล์ `config/config.json` ตัวอย่างมีให้ในรีโพซิทอรีนี้

```python
from camera_config import load_cameras, validate_cameras
from model_selector import select_model
from path_manager import load_paths

cameras = load_cameras()          # Load camera definitions
validate_cameras(cameras)         # Raise if definitions are invalid
model = select_model("AB12XXXX")  # -> "ModelA"
paths = load_paths()              # Access configured directories
images_dir = paths["images"]
```

## แก้ไขแมปปิงหมายเลขซีเรียล

```python
from serial_mapping import SerialMappingManager

manager = SerialMappingManager(config_path="config/config.json")
manager.add_mapping("ZZ99", "ModelZ")
```

## API เลือกโมเดล

ฟังก์ชันอำนวยความสะดวกใน ``model_api`` ครอบคลุมตัวจัดการแมปปิงและ
ตัวเลือกโมเดลเพื่อใช้งานในโมดูลอื่น

```python
from model_api import (
    select_model,
    add_mapping,
    remove_mapping,
    reload_mapping,
)

reload_mapping("config/config.json")
model = select_model("AB12XXXX")
add_mapping("ZZ99", "ModelZ")
remove_mapping("AB12")
```

## ตัวบันทึกเหตุการณ์

เก็บรายการเหตุการณ์ไว้ในหน่วยความจำและส่งออกหรือนำกลับมาโหลดได้

```python
from event_logger import EventLogger

logger = EventLogger("logs/events.txt")
logger.log_event("info", "started", {"user": "abc"})

logger.save_log_json("events.json")
logger.save_log_csv("events.csv")

logger.load_log_json("events.json")
logger.load_log_csv("events.csv")

# Convert log list to a DataFrame or HTML table
from event_logger import logs_to_dataframe

df = logs_to_dataframe(logger.logs)
html = logs_to_dataframe(logger.logs, as_html=True)
```

## ยูทิลิตีจับภาพหน้าจอ

จับภาพเดสก์ท็อปด้วยคลาส :class:`ScreenCapture`.

```python
from screenshot import ScreenCapture

cap = ScreenCapture()

# Full screen capture as a PIL image
image = cap.capture()

# Capture a specific window by its title
window_image = cap.capture(window="Untitled - Notepad")

# Capture a custom region and return a NumPy array
array = cap.capture(region=(0, 0, 300, 200), as_numpy=True)

# Save the capture to a temporary file
path = cap.capture(to_file=True)
```

ใช้ :func:`make_screenshot_name` เพื่อสร้างชื่อไฟล์สำหรับภาพที่บันทึก

```python
from screenshot_namer import make_screenshot_name

name = make_screenshot_name("SN123", "pass")
```

บันทึกรูปทีละหลายภาพด้วย :func:`save_screenshot`:

```python
from screenshot import ScreenCapture, save_screenshot

cap = ScreenCapture()
for i in range(3):
    img = cap.capture()
    save_screenshot(img, "captures", f"shot_{i+1}.png")
```

## รันการทดสอบ

ติดตั้งไลบรารีที่จำเป็นก่อนแล้วรันการทดสอบหน่วยด้วยคำสั่ง:

```bash
pip install -r requirements.txt
pytest -q
```
