import io
import types

from input_manager import InputManager


class DummySerial:
    def __init__(self, *args, **kwargs):
        self.buf = io.BytesIO(b'ABCD\r')
        self.closed = False

    def read(self, size=1):
        return self.buf.read(size)

    def close(self):
        self.closed = True


serial_mod = types.SimpleNamespace(Serial=DummySerial)


def test_manual_source(monkeypatch):
    inputs = iter(['SN123'])

    def fake_input(prompt: str) -> str:
        return next(inputs)

    mgr = InputManager(input_func=fake_input)
    src, status = mgr.set_source('manual')
    assert (src, status) == ('manual', 'available')
    assert mgr.read_serial() == 'SN123'


def test_switch_to_usb():
    stream = io.StringIO('CODE\n')
    mgr = InputManager(input_stream=stream)
    src, status = mgr.set_source('scanner-USB')
    assert (src, status) == ('scanner-USB', 'available')
    assert mgr.read_serial() == 'CODE'


def test_switch_to_com_and_back():
    mgr = InputManager(com_port='COM1', serial_module=serial_mod)
    src, status = mgr.set_source('scanner-COM')
    assert (src, status) == ('scanner-COM', 'available')
    assert mgr.read_serial() == 'ABCD'
    mgr.set_source('manual')
    assert mgr.current_source == 'manual'
