"""Simple event logging utility.

Events are stored in memory and appended to ``file_path`` as JSON lines.  The
log list can also be saved or loaded in CSV/JSON format.

Example
-------
>>> logger = EventLogger("logs/events.txt")
>>> logger.log_event("info", "started")
>>> logger.save_log_json("logs/events.json")
>>> logger.save_log_csv("logs/events.csv")
>>> logger.load_log_json("logs/events.json")
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import csv


@dataclass
class LogEntry:
    """Data structure representing a single log event."""

    timestamp: str
    event_type: str
    message: str
    metadata: Optional[Dict[str, Any]] = None


class EventLogger:
    """Store log events in memory and append them to a file.

    Parameters
    ----------
    file_path : str or Path
        Path to the file where events are appended.
    """

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        self.logs: List[LogEntry] = []
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch(exist_ok=True)

    def log_event(
        self,
        event_type: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an event with optional metadata.

        Parameters
        ----------
        event_type : str
            Type/category of the event.
        message : str
            Human readable description for the event.
        metadata : dict, optional
            Extra metadata associated with the event.
        """
        entry = LogEntry(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            event_type=event_type,
            message=message,
            metadata=metadata,
        )
        self.logs.append(entry)
        with self.file_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(entry)) + "\n")

    def save_log_json(self, path: str | Path) -> None:
        """Write all stored logs to ``path`` in JSON format."""
        file = Path(path)
        with file.open("w", encoding="utf-8") as fh:
            json.dump([asdict(e) for e in self.logs], fh, indent=2)

    def load_log_json(self, path: str | Path) -> None:
        """Load log entries from a JSON file into memory.

        Missing or invalid files result in an empty log list.
        """
        file = Path(path)
        if not file.is_file():
            self.logs = []
            return
        try:
            with file.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.logs = [LogEntry(**d) for d in data]
        except (json.JSONDecodeError, TypeError, KeyError):
            self.logs = []

    def save_log_csv(self, path: str | Path) -> None:
        """Write all stored logs to ``path`` in CSV format."""
        file = Path(path)
        with file.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=["timestamp", "event_type", "message", "metadata"],
            )
            writer.writeheader()
            for entry in self.logs:
                row = asdict(entry)
                row["metadata"] = (
                    json.dumps(row["metadata"]) if row["metadata"] is not None else ""
                )
                writer.writerow(row)

    def load_log_csv(self, path: str | Path) -> None:
        """Load log entries from a CSV file.

        Missing or invalid files result in an empty log list.
        """
        file = Path(path)
        if not file.is_file():
            self.logs = []
            return
        try:
            with file.open("r", newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                logs = []
                for row in reader:
                    meta = row.get("metadata") or "null"
                    logs.append(
                        LogEntry(
                            timestamp=row.get("timestamp", ""),
                            event_type=row.get("event_type", ""),
                            message=row.get("message", ""),
                            metadata=json.loads(meta),
                        )
                    )
            self.logs = logs
        except (csv.Error, json.JSONDecodeError, TypeError, KeyError):
            self.logs = []


def logs_to_dataframe(logs: List[LogEntry], *, as_html: bool = False):
    """Return a pandas DataFrame or HTML table for ``logs``.

    Parameters
    ----------
    logs : list[LogEntry]
        List of log entries to convert.
    as_html : bool, optional
        When ``True`` return an HTML table string instead of a
        :class:`pandas.DataFrame`.

    Returns
    -------
    pandas.DataFrame or str
        DataFrame representing ``logs`` or HTML table string when
        ``as_html`` is ``True``.
    """

    try:
        import pandas as pd  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError("pandas is required for logs_to_dataframe") from exc

    df = pd.DataFrame([asdict(e) for e in logs])
    if as_html:
        return df.to_html(index=False)
    return df
