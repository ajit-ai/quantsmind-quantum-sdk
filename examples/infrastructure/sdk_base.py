"""SDK base: config, logging, plugins, telemetry, and hashing.

Feature: the five infrastructure packages working together.
Purpose: show one coherent bootstrap with no dependencies.
Input: inline defaults and a demo plugin.
Processing: resolve config -> log with context -> register/enable plugin
-> record telemetry -> hash an artifact id.
Output: resolved port, captured log line, plugin state, event count.
Meaning: infrastructure composes without a framework.

Run from the repository root::

    python examples/infrastructure/sdk_base.py
"""

from __future__ import annotations

import logging

from quantsmind.config import Config
from quantsmind.logging import MemoryHandler, get_logger
from quantsmind.plugins import Plugin, PluginMetadata, PluginRegistry
from quantsmind.security import sha256_hex
from quantsmind.telemetry import Collector


class DemoPlugin(Plugin):
    """Example plugin (not SDK behavior)."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(name="demo")

    def is_compatible(self, sdk_version: str) -> bool:
        return sdk_version.split(".")[0] == "1"


def main() -> None:
    config = Config(defaults={"server": {"port": 80}}, schema={"server": {"port": int}})
    config.set("server", "port", 8080)
    print(f"port: {config.get('server', 'port')}")

    root = logging.getLogger("qm-infra-demo")
    handler = MemoryHandler()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)
    try:
        get_logger("qm-infra-demo", {"run": "demo"}).info("boot")
    finally:
        root.removeHandler(handler)
    print(f"logs: {[(r.level, r.message) for r in handler.records]}")

    registry = PluginRegistry(sdk_version="1.0.1")
    registry.register(DemoPlugin())
    registry.enable("demo")
    print(f"plugin enabled: {registry.is_enabled('demo')}")

    telemetry = Collector()
    telemetry.record("boot.completed", port=8080)
    print(f"events: {telemetry.count()}")
    print(f"artifact: {sha256_hex(b'demo')[:8]}")


if __name__ == "__main__":
    main()
