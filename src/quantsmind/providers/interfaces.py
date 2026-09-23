"""Vendor-neutral provider and backend contracts.

These ABCs describe what a hardware, cloud, or simulator backend must
expose to plug into QuantsMind. They reference no vendor SDK: capability
descriptions are plain QuantsMind dataclasses, and concrete providers
import their engine lazily (see :mod:`quantsmind.providers.local`).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProviderCapabilities:
    """What a provider offers, in vendor-neutral terms.

    Attributes:
        name: Provider identity (e.g. ``"local_simulator"``).
        kinds: Capability tokens (e.g. ``{"simulator"}``, ``{"hardware"}``).
        max_qubits: Maximum qubits, if the provider declares a bound.
        metadata: Free-form extra capability details (JSON-safe).
    """

    name: str
    kinds: frozenset[str] = frozenset({"simulator"})
    max_qubits: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderHealth:
    """Point-in-time health of a provider.

    Attributes:
        available: Whether the provider can execute right now.
        message: Human-readable explanation when unavailable.
    """

    available: bool
    message: str = ""


class IBackend(ABC):
    """Contract for a single executable backend."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Backend identity."""
        raise NotImplementedError

    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Describe what this backend offers."""
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Whether this backend can execute right now."""
        raise NotImplementedError


class IProvider(ABC):
    """Contract for a backend provider (registry of named backends)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identity."""
        raise NotImplementedError

    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Describe what this provider offers."""
        raise NotImplementedError

    @abstractmethod
    def health(self) -> ProviderHealth:
        """Report whether this provider can execute right now."""
        raise NotImplementedError

    @abstractmethod
    def backend_names(self) -> list[str]:
        """Names of the backends this provider exposes."""
        raise NotImplementedError

    @abstractmethod
    def get_backend(self, name: str) -> Any:
        """Return the backend registered under ``name``.

        Raises:
            BackendNotFoundError: If no backend has that name.
            ProviderUnavailableError: If the provider cannot serve backends.
        """
        raise NotImplementedError


__all__ = [
    "ProviderCapabilities",
    "ProviderHealth",
    "IBackend",
    "IProvider",
]
