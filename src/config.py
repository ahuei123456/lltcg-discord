import json
import logging
import os
from typing import Any

_config_cache: dict[str, Any] | None = None  # Store the loaded config here

_log = logging.getLogger(__name__)


class ConfigError(Exception):
    """Custom exception for configuration errors."""

    pass


def load_config(path: str = "config.json") -> dict[str, Any]:
    """Loads configuration from a JSON file."""
    global _config_cache

    if not os.path.exists(path):
        raise ConfigError(f"Configuration file not found: {path}")

    try:
        with open(path) as f:
            # Use object_hook to load into a namespace for attribute access
            data = json.load(f, object_hook=lambda d: dict(**d))

        required_keys = ["DISCORD_TOKEN", "EVENTS_FILE", "RESPONSES_FILE", "GUILDS"]
        for key in required_keys:
            if key not in data:
                raise ConfigError(f"Missing required key '{key}' in {path}")

        if data is None:
            raise ConfigError(f"Empty configuration file: {path}")

        _config_cache = data
        _log.info(f"Configuration loaded successfully from {path}")  # Optional logging
        return _config_cache  # type: ignore
    except json.JSONDecodeError as e:
        raise ConfigError(f"Error decoding JSON from {path}: {e}")
    except Exception as e:
        # Catch other potential errors during loading/validation
        raise ConfigError(f"An error occurred loading configuration: {e}")


def get_config() -> dict[str, Any]:
    """Returns the loaded configuration, loading it if necessary."""
    if _config_cache is None:
        # Attempt to load with default path if not loaded yet
        # Alternatively, raise an error if explicit load hasn't happened
        # raise ConfigError("Configuration has not been loaded. Call load_config() first.")
        _log.warning("Warning: Config accessed before explicit load. Loading with default path.")
        load_config()  # Load with default path "config.json"

    if _config_cache is None:
        # This should ideally not be reachable if load_config works or raises
        raise ConfigError("Configuration is not available.")

    return _config_cache
