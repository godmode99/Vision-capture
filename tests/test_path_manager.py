import json
from pathlib import Path

from path_manager import PathManager, load_paths


def test_load_paths_creates_directories(tmp_path: Path):
    config = {"paths": {"images": "imgs", "logs": "logs"}}
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(config))

    manager = load_paths(cfg)
    assert manager["images"].is_dir()
    assert manager["logs"].is_dir()
    assert manager["images"].name == "imgs"


def test_load_paths_with_base(tmp_path: Path):
    config = {"paths": {"images": "images"}}
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(config))

    base = tmp_path / "base"
    manager = load_paths(cfg, base_path=base)
    expected = base / "images"
    assert manager["images"] == expected
    assert expected.is_dir()


def test_path_manager_get(tmp_path: Path):
    mapping = {"img": "i"}
    manager = PathManager(mapping, base_path=tmp_path)
    assert manager.get("img") == tmp_path / "i"
    assert manager.get("missing") is None

