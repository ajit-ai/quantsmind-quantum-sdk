"""Plugins Package — Defines the extension mechanism that lets third parties add new domains,
providers, or backends to QuantsMind without modifying core.

This package is part of the QuantsMind SDK (R0.1.0).
Foundational implementation (Phase 11): explicit registration with
lifecycle states and compatibility checks; entry-point discovery is an
explicit opt-in helper, never automatic.
"""

from __future__ import annotations

from quantsmind.plugins.plugins import (
    IncompatiblePluginError,
    Plugin,
    PluginError,
    PluginMetadata,
    PluginRegistry,
)

__all__: list[str] = [
    "IncompatiblePluginError",
    "Plugin",
    "PluginError",
    "PluginMetadata",
    "PluginRegistry",
]
