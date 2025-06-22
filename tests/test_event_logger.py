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


def test_save_and_load_json(tmp_path: Path):
    log_file = tmp_path / "log.txt"
    logger = EventLogger(log_file)
    logger.log_event("info", "start", {"a": 1})

    out = tmp_path / "events.json"
    logger.save_log_json(out)

    new_logger = EventLogger(tmp_path / "new.txt")
    new_logger.load_log_json(out)

    assert len(new_logger.logs) == 1
    entry = new_logger.logs[0]
    assert entry.event_type == "info"
    assert entry.metadata == {"a": 1}


def test_save_and_load_csv(tmp_path: Path):
    log_file = tmp_path / "log.txt"
    logger = EventLogger(log_file)
    logger.log_event("warn", "oops", {"b": 2})

    csv_path = tmp_path / "events.csv"
    logger.save_log_csv(csv_path)

    other = EventLogger(tmp_path / "other.txt")
    other.load_log_csv(csv_path)

    assert len(other.logs) == 1
    entry = other.logs[0]
    assert entry.message == "oops"
    assert entry.metadata == {"b": 2}


def test_load_json_invalid_or_missing(tmp_path: Path):
    logger = EventLogger(tmp_path / "log.txt")

    missing = tmp_path / "missing.json"
    logger.load_log_json(missing)
    assert logger.logs == []

    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    logger.load_log_json(bad)
    assert logger.logs == []


def test_load_csv_invalid_or_missing(tmp_path: Path):
    logger = EventLogger(tmp_path / "log.txt")

    missing = tmp_path / "missing.csv"
    logger.load_log_csv(missing)
    assert logger.logs == []

    bad = tmp_path / "bad.csv"
    bad.write_text("bad,data")
    logger.load_log_csv(bad)
    assert logger.logs == []
