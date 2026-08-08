"""
Runtime Settings Module

This module provides settings management for the Runtime package.

Purpose
-------
Provide settings management for the QuantsMind SDK.

Responsibilities
----------------
- Manage runtime settings
- Support settings persistence
- Handle settings validation
- Support settings profiles

Dependencies
------------
typing (standard library)
logging (standard library)
json (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.exceptions (runtime exceptions)
quantsmind.runtime.configuration (configuration)
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from quantsmind.runtime.configuration import Configuration
from quantsmind.runtime.constants import (
    DEFAULT_CACHE_SIZE,
    DEFAULT_CACHE_TTL,
    DEFAULT_EVENT_QUEUE_SIZE,
    DEFAULT_EVENT_TIMEOUT,
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_LEVEL,
    DEFAULT_MAX_CONCURRENT_TASKS,
    DEFAULT_MAX_QUEUE_SIZE,
    DEFAULT_MEMORY_LIMIT,
    DEFAULT_METRICS_INTERVAL,
    DEFAULT_METRICS_RETENTION,
    DEFAULT_PLUGIN_TIMEOUT,
    DEFAULT_PLUGIN_VERSION,
    DEFAULT_RETRY_COUNT,
    DEFAULT_RETRY_DELAY,
    DEFAULT_STATE_TIMEOUT,
    DEFAULT_STORAGE_LIMIT,
    DEFAULT_TIMEOUT,
    RUNTIME_VERSION,
)
from quantsmind.runtime.exceptions import ConfigurationError
from quantsmind.runtime.types import ConfigDict

logger = logging.getLogger(__name__)


class Settings:
    """Concrete implementation of settings management.

    This class provides settings management capabilities.

    Attributes:
        _config: Configuration instance
        _profile: Current profile

    Example:
        >>> settings = Settings()
        >>> settings.load_profile("production")
    """

    def __init__(self) -> None:
        """Initialize Settings with default values.

        Example:
            >>> settings = Settings()
        """
        self._config = Configuration(self._get_defaults())
        self._profile = "default"
        logger.debug("Created settings manager")

    def _get_defaults(self) -> ConfigDict:
        """Get default settings.

        Returns:
            Default configuration

        Example:
            >>> defaults = settings._get_defaults()
        """
        return {
            "runtime_version": RUNTIME_VERSION,
            "timeout": DEFAULT_TIMEOUT,
            "retry_count": DEFAULT_RETRY_COUNT,
            "retry_delay": DEFAULT_RETRY_DELAY,
            "max_concurrent_tasks": DEFAULT_MAX_CONCURRENT_TASKS,
            "max_queue_size": DEFAULT_MAX_QUEUE_SIZE,
            "memory_limit": DEFAULT_MEMORY_LIMIT,
            "storage_limit": DEFAULT_STORAGE_LIMIT,
            "cache_size": DEFAULT_CACHE_SIZE,
            "cache_ttl": DEFAULT_CACHE_TTL,
            "event_queue_size": DEFAULT_EVENT_QUEUE_SIZE,
            "event_timeout": DEFAULT_EVENT_TIMEOUT,
            "log_level": DEFAULT_LOG_LEVEL,
            "log_format": DEFAULT_LOG_FORMAT,
            "metrics_interval": DEFAULT_METRICS_INTERVAL,
            "metrics_retention": DEFAULT_METRICS_RETENTION,
            "plugin_timeout": DEFAULT_PLUGIN_TIMEOUT,
            "plugin_version": DEFAULT_PLUGIN_VERSION,
            "state_timeout": DEFAULT_STATE_TIMEOUT,
        }

    @property
    def config(self) -> Configuration:
        """Get the configuration instance.

        Returns:
            Configuration instance

        Example:
            >>> config = settings.config
        """
        return self._config

    @property
    def profile(self) -> str:
        """Get the current profile.

        Returns:
            Current profile name

        Example:
            >>> print(f"Profile: {settings.profile}")
        """
        return self._profile

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get a setting value.

        Args:
            key: Setting key
            default: Default value

        Returns:
            Setting value or default

        Example:
            >>> timeout = settings.get("timeout")
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a setting value.

        Args:
            key: Setting key
            value: Setting value

        Example:
            >>> settings.set("timeout", 600.0)
        """
        self._config.set(key, value)

    def load_profile(self, profile: str, config: ConfigDict) -> None:
        """Load a settings profile.

        Args:
            profile: Profile name
            config: Configuration dictionary

        Example:
            >>> settings.load_profile("production", {"timeout": 600.0})
        """
        self._profile = profile
        self._config.load_from_dict(config)
        logger.info(f"Loaded profile: {profile}")

    def save_profile(self, profile: str) -> ConfigDict:
        """Save current settings as a profile.

        Args:
            profile: Profile name

        Returns:
            Profile configuration

        Example:
            >>> config = settings.save_profile("custom")
        """
        config = self._config.to_dict()
        logger.info(f"Saved profile: {profile}")
        return config

    def load_from_file(self, file_path: str) -> None:
        """Load settings from a JSON file.

        Args:
            file_path: Path to JSON file

        Raises:
            ConfigurationError: If file loading fails

        Example:
            >>> settings.load_from_file("settings.json")
        """
        try:
            with open(file_path, "r") as f:
                config = json.load(f)
            self._config.load_from_dict(config)
            logger.info(f"Loaded settings from file: {file_path}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load settings from file: {str(e)}") from e

    def save_to_file(self, file_path: str) -> None:
        """Save settings to a JSON file.

        Args:
            file_path: Path to JSON file

        Raises:
            ConfigurationError: If file saving fails

        Example:
            >>> settings.save_to_file("settings.json")
        """
        try:
            config = self._config.to_dict()
            with open(file_path, "w") as f:
                json.dump(config, f, indent=2)
            logger.info(f"Saved settings to file: {file_path}")
        except Exception as e:
            raise ConfigurationError(f"Failed to save settings to file: {str(e)}") from e

    def reset(self) -> None:
        """Reset settings to defaults.

        Example:
            >>> settings.reset()
        """
        self._config.reset()
        self._profile = "default"
        logger.info("Reset settings to defaults")

    def to_dict(self) -> ConfigDict:
        """Convert settings to dictionary.

        Returns:
            Settings dictionary

        Example:
            >>> data = settings.to_dict()
        """
        return self._config.to_dict()


# Export
__all__ = [
    "Settings",
]
