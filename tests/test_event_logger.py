from pathlib import Path
import json
from event_logger import EventLogger


def test_log_event_stores_and_appends(tmp_path: Path):
    log_file = tmp_path / "log.txt"
    logger = EventLogger(log_file)

    logger.log_event("info", "started", {"user": "abc"})

    assert len(logger.logs) == 1
    entry = logger.logs[0]
    assert entry.event_type == "info"
    assert entry.message == "started"
    assert entry.metadata == {"user": "abc"}
    assert entry.timestamp

    data = [json.loads(line) for line in log_file.read_text().splitlines()]
    assert data == [
        {
            "timestamp": entry.timestamp,
            "event_type": "info",
            "message": "started",
            "metadata": {"user": "abc"},
        }
    ]


def test_log_event_appends_multiple(tmp_path: Path):
    log_file = tmp_path / "log.txt"
    logger = EventLogger(log_file)

    logger.log_event("info", "first")
    logger.log_event("warn", "second")

    assert len(logger.logs) == 2
    lines = log_file.read_text().splitlines()
    assert len(lines) == 2
