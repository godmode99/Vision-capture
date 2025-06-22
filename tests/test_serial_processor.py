from serial_processor import process_serials


def test_process_serials_calls_callback(monkeypatch):
    inputs = iter(['SN12', 'SN34'])
    collected = []

    def fake_input(prompt: str) -> str:
        return next(inputs)

    def callback(serial: str) -> None:
        collected.append(serial)

    process_serials(callback, input_func=fake_input, prompts=['p1', 'p2'])
    assert collected == ['SN12', 'SN34']


def test_process_serials_retries(monkeypatch):
    inputs = iter(['SN12'])
    logs = []
    calls = 0

    def fake_input(prompt: str) -> str:
        return next(inputs)

    def callback(serial: str) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError('fail')

    process_serials(
        callback,
        input_func=fake_input,
        prompts=['p1'],
        retries=1,
        log_func=logs.append,
    )

    assert calls == 2
    assert logs and 'fail' in logs[0]
