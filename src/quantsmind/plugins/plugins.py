"""Explicit plugin registration and lifecycle.

Plugins are registered by direct call — never by implicit scanning —
so behavior stays deterministic. Each plugin declares compatibility
 metadata; enabling checks it. Entry-point discovery is available as
an explicit opt-in helper, never automatic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from importlib import metadata as importlib_metadata
from typing import Any

__all__ = [
    "Plugin",
    "PluginMetadata",
    "PluginRegistry",
    "PluginError",
    "IncompatiblePluginError",
]


class PluginError(ValueError):
    """Raised for registration and lifecycle violations."""


class IncompatiblePluginError(PluginError):
    """Raised when a plugin fails its compatibility check."""


@dataclass(frozen=True)
class PluginMetadata:
    """Static plugin description.

    Attributes:
        name: Unique plugin name.
        version: Plugin version string.
        capabilities: Feature tokens the plugin provides.
        requires_sdk: Major SDK version required (e.g. ``"1"``).
        metadata: Free-form extra fields.
    """

    name: str
    version: str = "0.1.0"
    capabilities: tuple[str, ...] = ()
    requires_sdk: str = "1"
    metadata: dict[str, Any] = field(default_factory=dict)


class Plugin(ABC):
    """Interface every plugin implements."""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Plugin description."""
        raise NotImplementedError

    @abstractmethod
    def is_compatible(self, sdk_version: str) -> bool:
        """Check compatibility against an SDK version string."""
        raise NotImplementedError

    def enable(self) -> None:  # noqa: B027 - intentional optional lifecycle hook
        """Enable the plugin (default: no-op)."""

    def disable(self) -> None:  # noqa: B027 - intentional optional lifecycle hook
        """Disable the plugin (default: no-op)."""


class PluginRegistry:
    """Explicit plugin registry with lifecycle states.

    Args:
        sdk_version: Current SDK version used for compatibility checks.
    """

    def __init__(self, sdk_version: str = "1.0.1") -> None:
        """Initialize an empty registry."""
        self._sdk_version = sdk_version
        self._plugins: dict[str, Plugin] = {}
        self._enabled: set[str] = set()

    @property
    def plugin_count(self) -> int:
        """Number of registered plugins."""
        return len(self._plugins)

    def register(self, plugin: Plugin) -> None:
        """Register a plugin (names must be unique).

        Raises:
            PluginError: For empty or duplicate names.
        """
        name = plugin.metadata.name
        if not name:
            raise PluginError("plugin name must not be empty")
        if name in self._plugins:
            raise PluginError(f"plugin already registered: {name!r}")
        self._plugins[name] = plugin

    def enable(self, name: str) -> None:
        """Compatibility-check then enable a plugin.

        Raises:
            PluginError: If the plugin is unknown.
            IncompatiblePluginError: If the compatibility check fails.
        """
        plugin = self._plugins.get(name)
        if plugin is None:
            raise PluginError(f"unknown plugin: {name!r}")
        if not plugin.is_compatible(self._sdk_version):
            raise IncompatiblePluginError(
                f"plugin {name!r} requires SDK {plugin.metadata.requires_sdk!r}"
            )
        plugin.enable()
        self._enabled.add(name)

    def disable(self, name: str) -> None:
        """Disable a plugin (unknown names raise).

        Raises:
            PluginError: If the plugin is unknown.
        """
        plugin = self._plugins.get(name)
        if plugin is None:
            raise PluginError(f"unknown plugin: {name!r}")
        plugin.disable()
        self._enabled.discard(name)

    def is_enabled(self, name: str) -> bool:
        """Whether the plugin is currently enabled."""
        return name in self._enabled

    def names(self) -> list[str]:
        """Sorted registered plugin names."""
        return sorted(self._plugins)

    def discover_entry_points(self, group: str) -> list[str]:
        """List installed distributions exposing an entry-point group.

        Explicit opt-in only: this scans installed metadata and returns
        matching ``(name)`` pairs without importing anything.

        Args:
            group: Entry-point group name.
        """
        found = []
        for dist in importlib_metadata.distributions():
            for point in dist.entry_points:
                if point.group == group:
                    found.append(f"{dist.metadata['Name']}:{point.name}")
        return sorted(found)
