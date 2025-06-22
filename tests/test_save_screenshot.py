from pathlib import Path
from PIL import Image
import pytest

from screenshot import save_screenshot


def test_save_creates_directory(tmp_path: Path):
    img = Image.new("RGB", (2, 2), "white")
    dest = tmp_path / "shots"
    out = save_screenshot(img, dest, "img.png")
    assert out == dest / "img.png"
    assert out.is_file()


def test_save_logs_error(monkeypatch, tmp_path: Path):
    img = Image.new("RGB", (1, 1))
    messages = []
    
    def fail_save(path):
        raise OSError("fail")

    monkeypatch.setattr(img, "save", fail_save)
    with pytest.raises(OSError):
        save_screenshot(img, tmp_path, "bad.png", log_func=messages.append)
    assert messages and "fail" in messages[0]
