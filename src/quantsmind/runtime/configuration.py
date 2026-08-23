"""
Runtime Configuration Module

This module provides configuration management for the Runtime package.

Purpose
-------
Provide configuration management for the QuantsMind SDK.

Responsibilities
----------------
- Manage configuration values
- Support multiple configuration sources
- Handle configuration validation
- Support configuration overrides

Dependencies
------------
typing (standard library)
logging (standard library)
os (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.exceptions (runtime exceptions)
"""

from __future__ import annotations

import logging
import os

from quantsmind.runtime.exceptions import ValidationError
from quantsmind.runtime.types import ConfigDict, ConfigValue

logger = logging.getLogger(__name__)


class Configuration:
    """Concrete implementation of configuration management.

    This class provides configuration management capabilities.

    Attributes:
        _config: Configuration values
        _defaults: Default values
        _validators: Configuration validators
        _overrides: Runtime overrides

    Example:
        >>> config = Configuration()
        >>> config.set("timeout", 300.0)
        >>> value = config.get("timeout")
    """

    def __init__(self, defaults: ConfigDict | None = None) -> None:
        """Initialize a Configuration.

        Args:
            defaults: Default configuration values

        Example:
            >>> config = Configuration()
        """
        self._config: ConfigDict = {}
        self._defaults = defaults or {}
        self._validators: dict[str, list[callable]] = {}
        self._overrides: ConfigDict = {}
        logger.debug("Created configuration manager")

    @property
    def defaults(self) -> ConfigDict:
        """Get the default values.

        Returns:
            Default values

        Example:
            >>> print(f"Defaults: {config.defaults}")
        """
        return self._defaults.copy()

    def set(self, key: str, value: ConfigValue, validate: bool = True) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
            validate: Whether to validate the value

        Raises:
            ValidationError: If validation fails

        Example:
            >>> config.set("timeout", 300.0)
        """
        if validate and key in self._validators:
            for validator in self._validators[key]:
                if not validator(value):
                    raise ValidationError(f"Validation failed for key: {key}", field=key)

        self._config[key] = value
        logger.debug(f"Set configuration: {key}")

    def get(self, key: str, default: ConfigValue | None = None) -> ConfigValue:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value

        Returns:
            Configuration value or default

        Example:
            >>> value = config.get("timeout")
        """
        # Check overrides first
        if key in self._overrides:
            return self._overrides[key]

        # Check config
        if key in self._config:
            return self._config[key]

        # Check defaults
        if key in self._defaults:
            return self._defaults[key]

        return default

    def has(self, key: str) -> bool:
        """Check if a configuration key exists.

        Args:
            key: Configuration key

        Returns:
            True if key exists, False otherwise

        Example:
            >>> if config.has("timeout"):
            ...     print("Timeout is configured")
        """
        return key in self._config or key in self._defaults or key in self._overrides

    def delete(self, key: str) -> None:
        """Delete a configuration value.

        Args:
            key: Configuration key

        Example:
            >>> config.delete("timeout")
        """
        if key in self._config:
            del self._config[key]
            logger.debug(f"Deleted configuration: {key}")

    def add_validator(self, key: str, validator: callable) -> None:
        """Add a validator for a configuration key.

        Args:
            key: Configuration key
            validator: Validator function

        Example:
            >>> config.add_validator("timeout", lambda x: x > 0)
        """
        if key not in self._validators:
            self._validators[key] = []
        self._validators[key].append(validator)
        logger.debug(f"Added validator for key: {key}")

    def load_from_dict(self, config: ConfigDict) -> None:
        """Load configuration from a dictionary.

        Args:
            config: Configuration dictionary

        Example:
            >>> config.load_from_dict({"timeout": 300.0, "max_workers": 4})
        """
        for key, value in config.items():
            self.set(key, value)
        logger.debug(f"Loaded configuration from dict with {len(config)} keys")

    def load_from_env(self, prefix: str = "QUANTSMIND_") -> None:
        """Load configuration from environment variables.

        Args:
            prefix: Environment variable prefix

        Example:
            >>> config.load_from_env("QUANTSMIND_")
        """
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                self.set(config_key, value)
        logger.debug("Loaded configuration from environment")

    def set_override(self, key: str, value: ConfigValue) -> None:
        """Set a runtime override.

        Args:
            key: Configuration key
            value: Override value

        Example:
            >>> config.set_override("timeout", 600.0)
        """
        self._overrides[key] = value
        logger.debug(f"Set override for key: {key}")

    def clear_overrides(self) -> None:
        """Clear all runtime overrides.

        Example:
            >>> config.clear_overrides()
        """
        self._overrides.clear()
        logger.debug("Cleared all overrides")

    def to_dict(self) -> ConfigDict:
        """Convert configuration to dictionary.

        Returns:
            Configuration dictionary

        Example:
            >>> data = config.to_dict()
        """
        result = self._defaults.copy()
        result.update(self._config)
        result.update(self._overrides)
        return result

    def reset(self) -> None:
        """Reset configuration to defaults.

        Example:
            >>> config.reset()
        """
        self._config.clear()
        self._overrides.clear()
        logger.debug("Reset configuration to defaults")


# Export
__all__ = [
    "Configuration",
]
