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

## Running Tests

Run the unit tests with:

```
pytest -q
```
