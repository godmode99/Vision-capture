import io
import types

import pytest

from barcode_scanner import BarcodeScanner


def test_usb_scanner_reads_line():
    stream = io.StringIO('SN123\n')
    scanner = BarcodeScanner(mode='usb', input_stream=stream)
    assert scanner.scan() == 'SN123'


def test_invalid_mode():
    with pytest.raises(ValueError):
        BarcodeScanner(mode='bad')


def test_com_scanner_reads_bytes():
    class DummySerial:
        def __init__(self, *args, **kwargs):
            self.buf = io.BytesIO(b'ABCD\r')

        def read(self, size=1):
            return self.buf.read(size)

        def close(self):
            pass

    serial_mod = types.SimpleNamespace(Serial=DummySerial)
    scanner = BarcodeScanner(mode='com', port='COM1', serial_module=serial_mod)
    try:
        assert scanner.scan() == 'ABCD'
    finally:
        scanner.close()
