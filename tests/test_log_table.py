import json
from pathlib import Path
import pytest

from event_logger import EventLogger, logs_to_dataframe


def test_logs_to_dataframe_and_html(tmp_path: Path):
    pandas = pytest.importorskip("pandas")

    log_file = tmp_path / "log.txt"
    logger = EventLogger(log_file)
    logger.log_event("info", "start", {"a": 1})
    logger.log_event("warn", "stop")

    df = logs_to_dataframe(logger.logs)
    assert list(df.columns) == ["timestamp", "event_type", "message", "metadata"]
    assert df.iloc[0]["message"] == "start"

    html = logs_to_dataframe(logger.logs, as_html=True)
    assert "<table" in html and "</table>" in html
