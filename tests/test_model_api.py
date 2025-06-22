import json
from pathlib import Path

import model_api


def test_select_and_modify(tmp_path: Path):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"serialMapping": {"AA11": "Model1"}}))
    model_api.reload_mapping(cfg)

    assert model_api.select_model("AA11xxxx") == "Model1"
    assert model_api.select_model("ZZ99", unknown="Unknown") == "Unknown"

    assert model_api.add_mapping("BB22", "Model2") == "added"
    assert model_api.select_model("BB22abcd") == "Model2"

    assert model_api.remove_mapping("AA11") == "removed"
    assert model_api.select_model("AA11abcd") is None


def test_reload_mapping(tmp_path: Path):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"serialMapping": {"CC33": "Model3"}}))
    model_api.reload_mapping(cfg)
    assert model_api.select_model("CC33aaaa") == "Model3"

    cfg.write_text(json.dumps({"serialMapping": {"DD44": "Model4"}}))
    model_api.reload_mapping()  # reload same path
    assert model_api.select_model("DD44bbbb") == "Model4"
