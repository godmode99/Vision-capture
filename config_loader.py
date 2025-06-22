"""Utility to load configuration from a JSON file."""

import json
from pathlib import Path
from typing import Any, Dict

class ConfigLoader:
    """Load configuration data from a JSON file.

    Parameters
    ----------
    config_path : str or Path, optional
        Path to the JSON configuration file. Defaults to ``"config/config.json"``.
    """

    def __init__(self, config_path: str | Path = "config/config.json") -> None:
        self.config_path = Path(config_path)

    def load_config(self, path: str | Path | None = None) -> Dict[str, Any]:
        """Load and parse the configuration file.

        Parameters
        ----------
        path : str or Path, optional
            Optional path to a different configuration file. If provided, the
            internal ``config_path`` will be updated and the new file will be
            loaded.

        Returns
        -------
        dict
            The parsed configuration data.

        Raises
        ------
        FileNotFoundError
            If the configuration file does not exist.
        json.JSONDecodeError
            If the file contents are not valid JSON.
        """
        if path is not None:
            self.config_path = Path(path)

        if not self.config_path.is_file():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with self.config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data


def load_config(config_path: str | Path = "config/config.json") -> Dict[str, Any]:
    """Convenience function to load configuration data.

    Parameters
    ----------
    config_path : str or Path, optional
        Path to the JSON configuration file. Defaults to ``"config/config.json"``.

    Returns
    -------
    dict
        The parsed configuration data.

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist.
    json.JSONDecodeError
        If the file contents are not valid JSON.
    """
    loader = ConfigLoader(config_path)
    return loader.load_config()
