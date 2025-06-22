"""Load serial prefix to model mapping from a JSON configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Mapping, Optional

from config_loader import ConfigLoader


def load_serial_mapping(config_path: str | Path = "config/config.json") -> Dict[str, str]:
    """Return mapping of serial prefixes to model names.

    Parameters
    ----------
    config_path : str or Path, optional
        Path to the JSON configuration file. Defaults to ``"config/config.json"``.

    Returns
    -------
    dict
        Mapping of serial prefix to model name.

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist.
    json.JSONDecodeError
        If the file contents are not valid JSON.
    TypeError
        If ``serialMapping`` is not a mapping.
    ValueError
        If ``serialMapping`` is missing or empty.
    """
    loader = ConfigLoader(config_path)
    config = loader.load_config()
    mapping = config.get("serialMapping")
    if mapping is None:
        raise ValueError("'serialMapping' section missing")
    if not isinstance(mapping, Mapping):
        raise TypeError("'serialMapping' section must be a mapping")
    if not mapping:
        raise ValueError("'serialMapping' section is empty")
    return dict(mapping)


class SerialModelMap:
    """Wrapper providing convenient access to a serial prefix mapping.

    Parameters
    ----------
    mapping : dict[str, str], optional
        Mapping of serial prefix to model name. When omitted, ``config_path``
        will be loaded using :func:`load_serial_mapping`.
    config_path : str or Path, optional
        Path to configuration file used when ``mapping`` is not supplied.

    Example
    -------
    >>> mapper = SerialModelMap(config_path="config/config.json")
    >>> mapper.get_model("AB12XXXX")
    'ModelA'
    """

    def __init__(self, mapping: Optional[Dict[str, str]] = None, *, config_path: str | Path = "config/config.json") -> None:
        self.mapping = mapping if mapping is not None else load_serial_mapping(config_path)

    def __getitem__(self, prefix: str) -> str:
        return self.mapping[prefix]

    def get_model(self, serial: str, *, default: Optional[str] = None) -> Optional[str]:
        """Return model for *serial* or ``default`` when unknown."""
        if not serial:
            return default
        return self.mapping.get(serial[:4], default)

    def as_dict(self) -> Dict[str, str]:
        return dict(self.mapping)

