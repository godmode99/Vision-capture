"""API wrapper for selecting models and editing serial mappings."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from model_selector import ModelSelector
from serial_mapping import SerialMappingManager


_config_path = Path("config/config.json")
_mapping_manager: SerialMappingManager | None = None
_selector: ModelSelector | None = None


def _load() -> None:
    """(Re)load mapping and selector from ``_config_path``."""
    global _mapping_manager, _selector
    _mapping_manager = SerialMappingManager(config_path=_config_path)
    _selector = ModelSelector(mapping=_mapping_manager.as_dict())


def reload_mapping(config_path: str | Path | None = None) -> None:
    """Reload mapping from ``config_path`` or the existing path."""
    global _config_path
    if config_path is not None:
        _config_path = Path(config_path)
    _load()


def select_model(serial: str, *, unknown: Optional[str] = None) -> Optional[str]:
    """Return the model name for ``serial`` using the loaded mapping."""
    if _selector is None:
        _load()
    return _selector.select(serial, unknown=unknown)


def add_mapping(prefix: str, model: str) -> str:
    """Add ``prefix`` mapping and persist the config."""
    if _mapping_manager is None:
        _load()
    result = _mapping_manager.add_mapping(prefix, model)
    global _selector
    _selector = ModelSelector(mapping=_mapping_manager.as_dict())
    return result


def remove_mapping(prefix: str) -> str:
    """Remove ``prefix`` mapping from the config."""
    if _mapping_manager is None:
        _load()
    result = _mapping_manager.remove_mapping(prefix)
    global _selector
    _selector = ModelSelector(mapping=_mapping_manager.as_dict())
    return result

