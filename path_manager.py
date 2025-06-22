"""Utility for managing filesystem paths used by the application."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Mapping, Optional

from config_loader import load_config


class PathManager:
    """Manage directories defined in configuration.

    Parameters
    ----------
    path_map : Mapping[str, str | Path]
        Mapping of path names to directory paths.
    base_path : str or Path, optional
        Base directory prepended to each path in ``path_map`` when provided.
    """

    def __init__(self, path_map: Mapping[str, str | Path], base_path: str | Path | None = None) -> None:
        self.base_path = Path(base_path) if base_path is not None else None
        self.paths: Dict[str, Path] = {}
        for name, value in path_map.items():
            p = Path(value)
            if self.base_path is not None:
                p = self.base_path / p
            try:
                p.mkdir(parents=True, exist_ok=True)
            except OSError as exc:  # pragma: no cover - very unlikely in tests
                raise OSError(f"Failed to create directory {p}: {exc}") from exc
            self.paths[name] = p

    def __getitem__(self, item: str) -> Path:
        return self.paths[item]

    def get(self, item: str, default: Optional[Path] = None) -> Optional[Path]:
        return self.paths.get(item, default)

    def as_dict(self) -> Dict[str, Path]:
        return dict(self.paths)


def load_paths(config_path: str | Path = "config/config.json", *, base_path: str | Path | None = None) -> PathManager:
    """Load path configuration and return a :class:`PathManager` instance."""
    config = load_config(config_path)
    path_map = config.get("paths", {})
    if not isinstance(path_map, Mapping):
        raise TypeError("'paths' section must be a mapping")
    return PathManager(path_map, base_path=base_path)

