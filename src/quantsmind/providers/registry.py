"""A minimal provider registry.

Maps provider names to provider instances. Deliberately standalone
(it does not import :mod:`quantsmind.runtime`) so ``providers`` keeps
zero internal coupling beyond ``exceptions``; dependency direction stays
``providers -> exceptions`` only.
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from quantsmind.providers.exceptions import ProviderError
from quantsmind.providers.interfaces import IProvider

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Name -> provider registry with duplicate protection."""

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._providers: dict[str, IProvider] = {}
        self._lock = threading.Lock()

    @property
    def provider_count(self) -> int:
        """Number of registered providers."""
        with self._lock:
            return len(self._providers)

    def register(self, provider: IProvider) -> None:
        """Register a provider under its :attr:`name`.

        Raises:
            ProviderError: If a provider with that name already exists.
        """
        with self._lock:
            if provider.name in self._providers:
                raise ProviderError(f"provider already registered: {provider.name!r}")
            self._providers[provider.name] = provider
            logger.debug(f"Registered provider: {provider.name}")

    def unregister(self, name: str) -> bool:
        """Remove the provider registered under ``name``."""
        with self._lock:
            return self._providers.pop(name, None) is not None

    def get(self, name: str) -> Any:
        """Return the provider registered under ``name`` (``None`` if absent)."""
        with self._lock:
            return self._providers.get(name)

    def names(self) -> list[str]:
        """Sorted registered provider names."""
        with self._lock:
            return sorted(self._providers)


__all__ = ["ProviderRegistry"]
