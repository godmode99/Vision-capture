import json
from pathlib import Path

import pytest

from serial_mapping import (
    load_serial_mapping,
    SerialModelMap,
    SerialMappingManager,
)


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


def test_serial_mapping_manager_edit(tmp_path: Path):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"serialMapping": {"AA11": "Old"}}))

    mgr = SerialMappingManager(config_path=cfg)
    assert mgr.add_mapping("BB22", "New") == "added"
    data = json.loads(cfg.read_text())
    assert data["serialMapping"]["BB22"] == "New"

    assert mgr.update_mapping("BB22", "Newer") == "updated"
    data = json.loads(cfg.read_text())
    assert data["serialMapping"]["BB22"] == "Newer"

    assert mgr.remove_mapping("BB22") == "removed"
    data = json.loads(cfg.read_text())
    assert "BB22" not in data["serialMapping"]


def test_serial_mapping_manager_errors(tmp_path: Path):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"serialMapping": {"AA11": "Old"}}))

    mgr = SerialMappingManager(config_path=cfg)
    assert mgr.add_mapping("AA11", "Dup") == "error: prefix exists"
    assert mgr.update_mapping("ZZ99", "None") == "error: prefix not found"
    assert mgr.remove_mapping("ZZ99") == "error: prefix not found"
    data = json.loads(cfg.read_text())
    assert data["serialMapping"] == {"AA11": "Old"}
