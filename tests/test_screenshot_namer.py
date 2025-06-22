from datetime import datetime
from pathlib import Path

from screenshot_namer import make_screenshot_name


def test_make_name_fixed_timestamp():
    ts = datetime(2024, 1, 2, 3, 4, 5)
    name = make_screenshot_name("SN12", "ok", timestamp=ts)
    assert name == "SN12_ok_20240102_030405.jpg"


def test_make_name_increments(tmp_path: Path):
    ts = datetime(2024, 1, 2, 3, 4, 5)
    base = tmp_path
    first = base / "SN12_ok_20240102_030405.jpg"
    first.touch()
    name1 = make_screenshot_name("SN12", "ok", timestamp=ts, dest_dir=base)
    assert Path(name1).name == "SN12_ok_20240102_030405_1.jpg"
    Path(name1).touch()
    name2 = make_screenshot_name("SN12", "ok", timestamp=ts, dest_dir=base)
    assert Path(name2).name == "SN12_ok_20240102_030405_2.jpg"
