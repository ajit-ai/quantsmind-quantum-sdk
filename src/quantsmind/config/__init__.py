"""Config Package — Defines configuration loading/resolution contracts.

This package is part of the QuantsMind SDK (R0.1.0).
Foundational implementation (Phase 11): layered defaults/environment/
overrides configuration with schema casting and validation.
"""

from __future__ import annotations

from quantsmind.config.config import Config, ConfigError

__all__: list[str] = [
    "Config",
    "ConfigError",
]
