"""
Runtime Registry Module

This module provides registry management for the Runtime package.

Purpose
-------
Provide registry management for the QuantsMind SDK.

Responsibilities
----------------
- Manage runtime registry
- Register components
- Track component metadata
- Support component discovery

Dependencies
------------
typing (standard library)
logging (standard library)
threading (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
quantsmind.runtime.exceptions (runtime exceptions)
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime
from typing import Any

from quantsmind.runtime.exceptions import ValidationError

logger = logging.getLogger(__name__)


class RuntimeRegistry:
    """Concrete implementation of a runtime registry.

    This class provides registry management capabilities.

    Attributes:
        _components: Registered components
        _metadata: Component metadata
        _lock: Thread lock

    Example:
        >>> registry = RuntimeRegistry()
        >>> registry.register("my_component", MyComponent)
    """

    def __init__(self) -> None:
        """Initialize a RuntimeRegistry.

        Example:
            >>> registry = RuntimeRegistry()
        """
        self._components: dict[str, Any] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()
        logger.debug("Created runtime registry")

    @property
    def component_count(self) -> int:
        """Get the number of registered components.

        Returns:
            Number of components

        Example:
            >>> print(f"Component count: {registry.component_count}")
        """
        with self._lock:
            return len(self._components)

    def register(
        self,
        name: str,
        component: Any,
        version: str = "1.0.0",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a component.

        Args:
            name: Component name
            component: Component instance or class
            version: Component version
            metadata: Optional metadata

        Raises:
            ValidationError: If component already exists

        Example:
            >>> registry.register("my_component", MyComponent)
        """
        with self._lock:
            if name in self._components:
                raise ValidationError(f"Component already registered: {name}")
            
            self._components[name] = component
            self._metadata[name] = {
                "version": version,
                "registered_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }
            logger.debug(f"Registered component: {name}")

    def unregister(self, name: str) -> bool:
        """Unregister a component.

        Args:
            name: Component name

        Returns:
            True if unregistered, False otherwise

        Example:
            >>> unregistered = registry.unregister("my_component")
        """
        with self._lock:
            if name in self._components:
                del self._components[name]
                del self._metadata[name]
                logger.debug(f"Unregistered component: {name}")
                return True
        return False

    def get(self, name: str) -> Any | None:
        """Get a component by name.

        Args:
            name: Component name

        Returns:
            Component or None

        Example:
            >>> component = registry.get("my_component")
        """
        with self._lock:
            return self._components.get(name)

    def has(self, name: str) -> bool:
        """Check if a component is registered.

        Args:
            name: Component name

        Returns:
            True if registered, False otherwise

        Example:
            >>> if registry.has("my_component"):
            ...     print("Component is registered")
        """
        with self._lock:
            return name in self._components

    def get_metadata(self, name: str) -> dict[str, Any] | None:
        """Get component metadata.

        Args:
            name: Component name

        Returns:
            Metadata or None

        Example:
            >>> metadata = registry.get_metadata("my_component")
        """
        with self._lock:
            return self._metadata.get(name)

    def list_components(self) -> list[str]:
        """List all registered components.

        Returns:
            List of component names

        Example:
            >>> components = registry.list_components()
        """
        with self._lock:
            return list(self._components.keys())

    def get_by_version(self, version: str) -> list[str]:
        """Get components by version.

        Args:
            version: Version

        Returns:
            List of component names

        Example:
            >>> components = registry.get_by_version("1.0.0")
        """
        with self._lock:
            return [
                name
                for name, meta in self._metadata.items()
                if meta.get("version") == version
            ]

    def search(self, query: str) -> list[str]:
        """Search for components.

        Args:
            query: Search query

        Returns:
            List of matching component names

        Example:
            >>> components = registry.search("my")
        """
        with self._lock:
            return [name for name in self._components if query.lower() in name.lower()]

    def clear(self) -> None:
        """Clear the registry.

        Example:
            >>> registry.clear()
        """
        with self._lock:
            self._components.clear()
            self._metadata.clear()
        logger.info("Registry cleared")

    def get_status(self) -> dict[str, Any]:
        """Get registry status.

        Returns:
            Registry status

        Example:
            >>> status = registry.get_status()
        """
        with self._lock:
            return {
                "component_count": self.component_count,
                "components": self.list_components(),
                "versions": {
                    version: len(self.get_by_version(version))
                    for version in set(meta.get("version", "1.0.0") for meta in self._metadata.values())
                },
            }


# Export
__all__ = [
    "RuntimeRegistry",
]
