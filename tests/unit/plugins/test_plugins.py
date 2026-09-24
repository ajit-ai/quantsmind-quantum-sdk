"""Unit tests for quantsmind.plugins lifecycle."""

from __future__ import annotations

import pytest

from quantsmind.plugins import (
    IncompatiblePluginError,
    Plugin,
    PluginError,
    PluginMetadata,
    PluginRegistry,
)


class DemoPlugin(Plugin):
    """Test-only plugin (not SDK behavior)."""

    def __init__(self, name: str = "demo", requires: str = "1") -> None:
        """Initialize."""
        self._metadata = PluginMetadata(name=name, requires_sdk=requires)

    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata

    def is_compatible(self, sdk_version: str) -> bool:
        return sdk_version.split(".")[0] == self._metadata.requires_sdk


class TestLifecycle:
    def test_register_enable_disable(self) -> None:
        registry = PluginRegistry(sdk_version="1.0.1")
        registry.register(DemoPlugin())
        assert registry.names() == ["demo"]
        registry.enable("demo")
        assert registry.is_enabled("demo") is True
        registry.disable("demo")
        assert registry.is_enabled("demo") is False

    def test_duplicate_and_unknown(self) -> None:
        registry = PluginRegistry()
        registry.register(DemoPlugin())
        with pytest.raises(PluginError):
            registry.register(DemoPlugin())
        with pytest.raises(PluginError):
            registry.enable("missing")

    def test_incompatible(self) -> None:
        registry = PluginRegistry(sdk_version="1.0.1")
        registry.register(DemoPlugin(name="old", requires="2"))
        with pytest.raises(IncompatiblePluginError):
            registry.enable("old")

    def test_entry_point_listing_runs(self) -> None:
        assert isinstance(PluginRegistry().discover_entry_points("no.such.group"), list)
