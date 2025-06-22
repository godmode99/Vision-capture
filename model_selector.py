"""Utilities for selecting a model based on a serial or barcode prefix."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from config_loader import load_config


class ModelSelector:
    """Select a model based on a serial number prefix.

    Parameters
    ----------
    mapping : dict[str, str], optional
        Mapping from serial prefixes to model names. If not provided,
        ``config_path`` will be loaded and ``serialMapping`` will be used.
    config_path : str or Path, optional
        Path to a configuration file that contains ``serialMapping``.
        Defaults to ``"config/config.json"``.
    """

    def __init__(self, mapping: Optional[Dict[str, str]] = None, config_path: str | Path = "config/config.json") -> None:
        if mapping is not None:
            self.mapping = mapping
        else:
            config = load_config(config_path)
            self.mapping = config.get("serialMapping", {})

    def select(self, serial: str, *, unknown: Optional[str] = None) -> Optional[str]:
        """Return the model for ``serial`` or ``unknown`` if not found."""
        if not serial:
            return unknown
        prefix = serial[:4]
        return self.mapping.get(prefix, unknown)


def select_model(serial: str, *, mapping: Optional[Dict[str, str]] = None, config_path: str | Path = "config/config.json", unknown: Optional[str] = None) -> Optional[str]:
    """Convenience function to select a model given a serial.

    Parameters
    ----------
    serial : str
        Serial or barcode string. Only the first four characters are used.
    mapping : dict[str, str], optional
        Mapping from serial prefixes to model names. If not provided,
        configuration will be loaded from ``config_path``.
    config_path : str or Path, optional
        Path to configuration file used when ``mapping`` is not supplied.
    unknown : str, optional
        Value returned when the prefix is not found. Defaults to ``None``.
    """
    selector = ModelSelector(mapping=mapping, config_path=config_path)
    return selector.select(serial, unknown=unknown)
