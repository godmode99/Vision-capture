"""Simple event logging utility."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json


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
