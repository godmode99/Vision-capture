import json
from pathlib import Path

import pytest

from serial_mapping import load_serial_mapping, SerialModelMap


def test_load_serial_mapping(tmp_path: Path):
    data = {"serialMapping": {"AB12": "ModelA"}}
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(data))

    mapping = load_serial_mapping(cfg)
    assert mapping == data["serialMapping"]


def test_load_serial_mapping_errors(tmp_path: Path):
    cfg = tmp_path / "cfg.json"

    cfg.write_text(json.dumps({}))
    with pytest.raises(ValueError):
        load_serial_mapping(cfg)

    cfg.write_text(json.dumps({"serialMapping": []}))
    with pytest.raises(TypeError):
        load_serial_mapping(cfg)

    cfg.write_text(json.dumps({"serialMapping": {}}))
    with pytest.raises(ValueError):
        load_serial_mapping(cfg)


def test_serial_model_map_get(tmp_path: Path):
    data = {"serialMapping": {"CD34": "ModelB"}}
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(data))

    mapper = SerialModelMap(config_path=cfg)
    assert mapper.get_model("CD34XXXX") == "ModelB"
    assert mapper.get_model("XXYY", default="Unknown") == "Unknown"
