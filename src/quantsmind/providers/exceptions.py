"""Provider exception hierarchy.

All provider errors inherit from :class:`QuantsMindError` so callers can
catch any SDK error with a single handler. Unavailable backends surface
typed errors and never silently substitute another backend.
"""

from __future__ import annotations

from quantsmind.exceptions import QuantsMindError


class ProviderError(QuantsMindError):
    """Base exception for all provider-related errors."""


class ProviderUnavailableError(ProviderError):
    """Raised when a provider (or its engine) is not installed or reachable."""


class BackendNotFoundError(ProviderError):
    """Raised when a provider has no backend under the requested name."""


class BackendUnavailableError(ProviderError):
    """Raised when a known backend cannot execute right now."""


__all__ = [
    "ProviderError",
    "ProviderUnavailableError",
    "BackendNotFoundError",
    "BackendUnavailableError",
]
