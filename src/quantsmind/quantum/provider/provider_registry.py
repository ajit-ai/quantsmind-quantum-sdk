"""
Provider Registry Module

This module provides provider registry definitions for the Quantum package.

Purpose
-------
Provide provider registry management for quantum computing operations.

Responsibilities
----------------
- Define provider registry structure
- Support provider registry operations
- Support provider registry validation
- Support provider registry metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.provider.provider (provider module)
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.algorithms.exceptions import ProviderError
from quantsmind.quantum.algorithms.types import ValidationResult
from quantsmind.quantum.provider.provider import QuantumProvider


class ProviderRegistry:
    """Concrete implementation of a provider registry.

    This class provides provider registry functionality for quantum computing.

    Attributes:
        _name: Registry name
        _providers: List of registered providers
        _metadata: Registry metadata

    Example:
        >>> registry = ProviderRegistry()
        >>> registry.register_provider(provider)
    """

    def __init__(
        self,
        name: str = "default",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a ProviderRegistry.

        Args:
            name: Registry name
            metadata: Registry metadata

        Example:
            >>> registry = ProviderRegistry()
        """
        self._name = name
        self._providers: dict[str, QuantumProvider] = {}
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the registry name.

        Returns:
            Registry name

        Example:
            >>> name = registry.name
        """
        return self._name

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the registry metadata.

        Returns:
            Registry metadata

        Example:
            >>> metadata = registry.metadata
        """
        return self._metadata.copy()

    def register_provider(self, provider: QuantumProvider) -> None:
        """Register a provider.

        Args:
            provider: Provider to register

        Example:
            >>> registry.register_provider(provider)
        """
        if provider is None:
            raise ProviderError("Provider cannot be None", {"provider": None})

        if provider.name in self._providers:
            raise ProviderError(f"Provider '{provider.name}' already registered", {"name": provider.name})

        self._providers[provider.name] = provider

    def unregister_provider(self, name: str) -> bool:
        """Unregister a provider.

        Args:
            name: Provider name

        Returns:
            True if unregistered

        Example:
            >>> unregistered = registry.unregister_provider("IBM")
        """
        if name in self._providers:
            del self._providers[name]
            return True
        return False

    def get_provider(self, name: str) -> QuantumProvider | None:
        """Get a provider by name.

        Args:
            name: Provider name

        Returns:
            Provider or None

        Example:
            >>> provider = registry.get_provider("IBM")
        """
        return self._providers.get(name)

    def list_providers(self) -> list[str]:
        """List all registered provider names.

        Returns:
            List of provider names

        Example:
            >>> providers = registry.list_providers()
        """
        return list(self._providers.keys())

    def count(self) -> int:
        """Get the number of registered providers.

        Returns:
            Number of providers

        Example:
            >>> count = registry.count()
        """
        return len(self._providers)

    def clear(self) -> None:
        """Clear all registered providers.

        Example:
            >>> registry.clear()
        """
        self._providers.clear()

    def validate(self) -> ValidationResult:
        """Validate the registry.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = registry.validate()
        """
        errors = []

        if not self._name:
            errors.append("Registry name cannot be empty")

        # Validate all providers
        for name, provider in self._providers.items():
            is_valid, provider_errors = provider.validate()
            errors.extend([f"Provider {name}: {err}" for err in provider_errors])

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Registry definition

        Example:
            >>> data = registry.to_dict()
        """
        return {
            "name": self._name,
            "provider_count": len(self._providers),
            "providers": list(self._providers.keys()),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(registry)
        """
        return f"ProviderRegistry(name={self._name}, providers={len(self._providers)})"


# Export
__all__ = [
    "ProviderRegistry",
]
