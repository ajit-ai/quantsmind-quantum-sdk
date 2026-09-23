"""Import-health tests: every top-level package must import and re-export cleanly."""

from __future__ import annotations

import importlib
import pkgutil

import pytest

import quantsmind

TOP_LEVEL_PACKAGES = [
    "quantsmind.ai_reasoning",
    "quantsmind.algebra",
    "quantsmind.calculus",
    "quantsmind.core",
    "quantsmind.finance",
    "quantsmind.foundation",
    "quantsmind.io",
    "quantsmind.knowledge",
    "quantsmind.logging",
    "quantsmind.math",
    "quantsmind.ml_math",
    "quantsmind.numerical",
    "quantsmind.optimization",
    "quantsmind.quantum",
    "quantsmind.scientific",
    "quantsmind.security",
    "quantsmind.simulation",
    "quantsmind.statistics",
    "quantsmind.telemetry",
    "quantsmind.utils",
    "quantsmind.visualization",
]

# Packages behind optional extras (e.g. quantsmind.api needs fastapi):
# imported only when their third-party dependency is installed.
OPTIONAL_PACKAGES = [
    "quantsmind.api",
]


class TestPackageImports:
    def test_top_level_packages_import(self) -> None:
        for package in TOP_LEVEL_PACKAGES:
            importlib.import_module(package)

    def test_all_exports_resolve(self) -> None:
        for package in TOP_LEVEL_PACKAGES:
            module = importlib.import_module(package)
            for name in getattr(module, "__all__", []):
                assert hasattr(module, name), f"{package}.__all__ lists missing {name!r}"

    def test_submodules_import(self) -> None:
        for package in ("quantsmind.knowledge", "quantsmind.foundation", "quantsmind.runtime"):
            module = importlib.import_module(package)
            for info in pkgutil.walk_packages(module.__path__, package + "."):
                if ".foundational." in info.name:
                    continue
                importlib.import_module(info.name)

    def test_optional_packages_import_when_available(self) -> None:
        for package in OPTIONAL_PACKAGES:
            try:
                module = importlib.import_module(package)
            except ModuleNotFoundError:
                pytest.skip(f"optional extra not installed for {package}")
            for name in getattr(module, "__all__", []):
                assert hasattr(module, name), f"{package}.__all__ lists missing {name!r}"

    def test_version_available(self) -> None:
        assert quantsmind.__version__
