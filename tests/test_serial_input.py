import builtins

from serial_input import validate_serial, validate_prefix, get_serial


def test_validate_serial():
    assert validate_serial('AB12')
    assert validate_serial('a1B2c3')
    assert validate_serial('1' * 20)
    assert not validate_serial('abc')
    assert not validate_serial('a' * 21)
    assert not validate_serial('123$')


def test_validate_prefix():
    assert validate_prefix('AB12')
    assert not validate_prefix('ABC')
    assert not validate_prefix('ABCDE')
    assert not validate_prefix('AB!2')


def test_get_serial(monkeypatch):
    inputs = iter(['bad', '123$', 'SN1234'])
    outputs = []

    def fake_input(prompt: str) -> str:
        return next(inputs)

    def fake_print(msg: str) -> None:
        outputs.append(msg)

    result = get_serial(input_func=fake_input, output_func=fake_print)
    assert result == 'SN1234'
    assert len(outputs) == 2
