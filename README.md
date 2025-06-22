# Vision Capture Utilities

A small collection of helper modules used to configure and operate a vision capture system.
It includes utilities for loading camera settings, selecting a model based on a serial
number, and handling filesystem paths described in a JSON configuration file.

## Usage

1. Ensure a `config/config.json` file exists. An example is provided in this
   repository.

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

## Editing Serial Mapping

```python
from serial_mapping import SerialMappingManager

manager = SerialMappingManager(config_path="config/config.json")
manager.add_mapping("ZZ99", "ModelZ")
```

## Model Selection API

Convenience functions in ``model_api`` wrap the mapping manager and
model selector for use in other modules.

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

## Event Logger

Keep a list of events in memory and export or reload them.

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

## Screenshot Utility

Capture desktop images using the :class:`ScreenCapture` class.

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

Use :func:`make_screenshot_name` to generate filenames for saved captures.

```python
from screenshot_namer import make_screenshot_name

name = make_screenshot_name("SN123", "pass")
```

## Running Tests

Run the unit tests with:

```
pytest -q
```
