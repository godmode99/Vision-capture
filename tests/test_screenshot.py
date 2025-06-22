from pathlib import Path
from PIL import Image
import numpy as np

from screenshot import ScreenCapture


def test_capture_returns_image(monkeypatch):
    sc = ScreenCapture()
    dummy = Image.new("RGB", (10, 10), "red")
    monkeypatch.setattr(sc, "_grab", lambda box: dummy)
    img = sc.capture()
    assert isinstance(img, Image.Image)
    assert img.size == (10, 10)


def test_capture_numpy(monkeypatch):
    sc = ScreenCapture()
    dummy = Image.new("RGB", (5, 5), "blue")
    monkeypatch.setattr(sc, "_grab", lambda box: dummy)
    arr = sc.capture(region=(0, 0, 5, 5), as_numpy=True)
    assert isinstance(arr, np.ndarray)
    assert arr.shape == (5, 5, 3)


def test_capture_file(monkeypatch, tmp_path):
    sc = ScreenCapture()
    dummy = Image.new("RGB", (4, 4), "green")
    monkeypatch.setattr(sc, "_grab", lambda box: dummy)
    path = sc.capture(to_file=True)
    assert isinstance(path, Path)
    assert path.is_file()
    img = Image.open(path)
    assert img.size == (4, 4)
