"""
Providers Package — Defines the vendor-independent contract that hardware, cloud, and simulator
backends must implement to plug into QuantsMind.

This package is part of the QuantsMind SDK (R0.1.0).
Vendor-neutral ABCs plus one reference local-simulator provider that
delegates to MicroQuantum (lazy import: importing this package never
requires ``microquantum``).
"""

from __future__ import annotations

from quantsmind.providers.exceptions import (
    BackendNotFoundError,
    BackendUnavailableError,
    ProviderError,
    ProviderUnavailableError,
)
from quantsmind.providers.interfaces import (
    IBackend,
    IProvider,
    ProviderCapabilities,
    ProviderHealth,
)
from quantsmind.providers.local import LocalBackend, LocalSimulatorProvider
from quantsmind.providers.registry import ProviderRegistry

__all__: list[str] = [
    "BackendNotFoundError",
    "BackendUnavailableError",
    "ProviderError",
    "ProviderUnavailableError",
    "IBackend",
    "IProvider",
    "ProviderCapabilities",
    "ProviderHealth",
    "LocalBackend",
    "LocalSimulatorProvider",
    "ProviderRegistry",
]
