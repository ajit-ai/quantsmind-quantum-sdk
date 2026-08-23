"""
Provider Module

This module provides provider definitions for the Quantum package.

Purpose
-------
Provide provider management for quantum computing operations.

Responsibilities
----------------
- Define provider structure
- Support provider operations
- Support provider validation
- Support provider metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.interfaces (quantum interfaces)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.backend.backend (backend module)
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.algorithms.enums import ProviderType
from quantsmind.quantum.algorithms.exceptions import ProviderError
from quantsmind.quantum.algorithms.interfaces import IQuantumProvider
from quantsmind.quantum.algorithms.types import ProviderConfig, ValidationResult
from quantsmind.quantum.backend.backend import QuantumBackend


class QuantumProvider(IQuantumProvider):
    """Concrete implementation of a quantum provider.

    This class provides provider functionality for quantum computing.

    Attributes:
        _name: Provider name
        _provider_type: Provider type
        _backends: List of backends
        _credentials: Provider credentials
        _configuration: Provider configuration
        _metadata: Provider metadata

    Example:
        >>> provider = QuantumProvider("IBM", ProviderType.IBM)
        >>> backends = provider.get_backends()
    """

    def __init__(
        self,
        name: str,
        provider_type: ProviderType,
        credentials: dict[str, Any] | None = None,
        configuration: ProviderConfig | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a QuantumProvider.

        Args:
            name: Provider name
            provider_type: Provider type
            credentials: Provider credentials
            configuration: Provider configuration
            metadata: Provider metadata

        Example:
            >>> provider = QuantumProvider("IBM", ProviderType.IBM)
        """
        if not name:
            raise ProviderError("Provider name cannot be empty", {"name": name})

        self._name = name
        self._provider_type = provider_type
        self._backends: list[QuantumBackend] = []
        self._credentials = credentials or {}
        self._configuration = configuration or {}
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the provider name.

        Returns:
            Provider name

        Example:
            >>> name = provider.name
        """
        return self._name

    @property
    def provider_type(self) -> ProviderType:
        """Get the provider type.

        Returns:
            Provider type

        Example:
            >>> ptype = provider.provider_type
        """
        return self._provider_type

    @property
    def credentials(self) -> dict[str, Any]:
        """Get the provider credentials.

        Returns:
            Provider credentials

        Example:
            >>> creds = provider.credentials
        """
        return self._credentials.copy()

    @property
    def configuration(self) -> ProviderConfig:
        """Get the provider configuration.

        Returns:
            Provider configuration

        Example:
            >>> config = provider.configuration
        """
        return self._configuration.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the provider metadata.

        Returns:
            Provider metadata

        Example:
            >>> metadata = provider.metadata
        """
        return self._metadata.copy()

    def add_backend(self, backend: QuantumBackend) -> None:
        """Add a backend to the provider.

        Args:
            backend: Backend to add

        Example:
            >>> provider.add_backend(backend)
        """
        if backend is None:
            raise ProviderError("Backend cannot be None", {"backend": None})

        self._backends.append(backend)

    def remove_backend(self, name: str) -> bool:
        """Remove a backend from the provider.

        Args:
            name: Backend name

        Returns:
            True if removed

        Example:
            >>> removed = provider.remove_backend("ibmq_manila")
        """
        for i, backend in enumerate(self._backends):
            if backend.name == name:
                del self._backends[i]
                return True
        return False

    def get_backends(self) -> list[QuantumBackend]:
        """Get available backends.

        Returns:
            List of backends

        Example:
            >>> backends = provider.get_backends()
        """
        return self._backends.copy()

    def get_backend(self, name: str) -> QuantumBackend | None:
        """Get a specific backend.

        Args:
            name: Backend name

        Returns:
            Backend or None

        Example:
            >>> backend = provider.get_backend("ibmq_manila")
        """
        for backend in self._backends:
            if backend.name == name:
                return backend
        return None

    def authenticate(self, credentials: dict[str, Any]) -> bool:
        """Authenticate with the provider.

        Args:
            credentials: Authentication credentials

        Returns:
            True if authenticated

        Example:
            >>> success = provider.authenticate({"token": "my_token"})
        """
        # Placeholder implementation - actual authentication requires provider API
        self._credentials.update(credentials)
        return True

    def configure(self, config: ProviderConfig) -> None:
        """Configure the provider.

        Args:
            config: Provider configuration

        Example:
            >>> provider.configure({"region": "us-east"})
        """
        self._configuration.update(config)

    def validate(self) -> ValidationResult:
        """Validate the provider.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = provider.validate()
        """
        errors = []

        if not self._name:
            errors.append("Provider name cannot be empty")

        if self._provider_type not in ProviderType:
            errors.append(f"Invalid provider type: {self._provider_type}")

        # Validate all backends
        for i, backend in enumerate(self._backends):
            is_valid, backend_errors = backend.validate()
            errors.extend([f"Backend {i}: {err}" for err in backend_errors])

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Provider definition

        Example:
            >>> data = provider.to_dict()
        """
        return {
            "name": self._name,
            "provider_type": self._provider_type.value,
            "backend_count": len(self._backends),
            "backends": [backend.name for backend in self._backends],
            "has_credentials": bool(self._credentials),
            "configuration": self._configuration,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(provider)
        """
        return f"QuantumProvider(name={self._name}, type={self._provider_type.value}, backends={len(self._backends)})"
