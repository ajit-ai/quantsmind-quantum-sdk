"""Layered configuration: defaults, environment overlay, explicit overrides.

Resolution precedence (lowest to highest): defaults < environment <
overrides. Environment variables are mapped as ``{PREFIX}SECTION_KEY``
(e.g. ``QM_RUNTIME_MAX_WORKERS``). Values from the environment arrive
as strings and are cast with the schema type when one is declared.
Deterministic and dependency-free.
"""

from __future__ import annotations

import os
from typing import Any

__all__ = [
    "Config",
    "ConfigError",
]


class ConfigError(ValueError):
    """Raised for invalid schemas, values, or environment input."""


class Config:
    """Layered key-value configuration grouped by section.

    Args:
        defaults: Nested ``{section: {key: value}}`` defaults.
        schema: Optional nested ``{section: {key: type}}`` for casting
            and validation.
        env_prefix: Environment variable prefix (default ``"QM_"``).
    """

    def __init__(
        self,
        defaults: dict[str, dict[str, Any]] | None = None,
        schema: dict[str, dict[str, type]] | None = None,
        env_prefix: str = "QM_",
    ) -> None:
        """Initialize configuration layers."""
        self._defaults = {section: dict(values) for section, values in (defaults or {}).items()}
        self._schema = {section: dict(types) for section, types in (schema or {}).items()}
        self._env_prefix = env_prefix
        self._overrides: dict[str, dict[str, Any]] = {}

    def set(self, section: str, key: str, value: Any) -> None:
        """Set an explicit override (highest precedence)."""
        self._overrides.setdefault(section, {})[key] = value

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Resolve a value through overrides, environment, then defaults."""
        if section in self._overrides and key in self._overrides[section]:
            return self._overrides[section][key]
        env_name = f"{self._env_prefix}{section.upper()}_{key.upper()}"
        if env_name in os.environ:
            return self._cast(section, key, os.environ[env_name])
        return self._defaults.get(section, {}).get(key, default)

    def _cast(self, section: str, key: str, raw: str) -> Any:
        expected = self._schema.get(section, {}).get(key)
        if expected is None:
            return raw
        try:
            if expected is bool:
                return raw.strip().lower() in {"1", "true", "yes", "on"}
            return expected(raw)
        except (ValueError, TypeError) as exc:
            raise ConfigError(f"cannot cast {raw!r} to {expected.__name__}") from exc

    def validate(self) -> list[str]:
        """Check overrides against the schema; return error messages."""
        errors = []
        for section, values in self._overrides.items():
            for key, value in values.items():
                expected = self._schema.get(section, {}).get(key)
                if expected is not None and not isinstance(value, expected):
                    errors.append(
                        f"{section}.{key} must be {expected.__name__}, "
                        f"got {type(value).__name__}"
                    )
        return errors

    def to_dict(self) -> dict[str, Any]:
        """Export resolved ``{section: {key: value}}`` mapping."""
        sections = set(self._defaults) | set(self._overrides) | set(self._schema)
        for name in os.environ:
            if not name.startswith(self._env_prefix):
                continue
            rest = name[len(self._env_prefix) :].lower().split("_", 1)
            if len(rest) == 2:
                sections.add(rest[0])
        resolved: dict[str, Any] = {}
        for section in sorted(sections):
            keys = (
                set(self._defaults.get(section, {}))
                | set(self._overrides.get(section, {}))
                | set(self._schema.get(section, {}))
            )
            prefix = f"{self._env_prefix}{section.upper()}_"
            for name in os.environ:
                if name.startswith(prefix):
                    keys.add(name[len(prefix) :].lower())
            resolved[section] = {key: self.get(section, key) for key in sorted(keys)}
        return resolved
