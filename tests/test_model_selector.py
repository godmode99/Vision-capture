import json
from pathlib import Path

from model_selector import ModelSelector, select_model


def test_select_with_mapping():
    mapping = {"AB12": "ModelA", "CD34": "ModelB"}
    selector = ModelSelector(mapping=mapping)
    assert selector.select("AB12XYZ") == "ModelA"
    assert selector.select("CD34XYZ") == "ModelB"
    assert selector.select("ZZ99") is None
    assert selector.select("ZZ99", unknown="Unknown Model") == "Unknown Model"


def test_select_with_config(tmp_path: Path):
    config_data = {"serialMapping": {"EF56": "ModelC"}}
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(config_data))
    selector = ModelSelector(config_path=cfg)
    assert selector.select("EF56AAAA") == "ModelC"


def test_select_model_function():
    mapping = {"GH78": "ModelD"}
    assert select_model("GH78XXXX", mapping=mapping) == "ModelD"
    assert select_model("XXXX", mapping=mapping, unknown="Unknown") == "Unknown"
