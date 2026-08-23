"""
Runtime Resource Module

This module provides resource management for the Runtime package.

Purpose
-------
Provide resource management for the QuantsMind SDK.

Responsibilities
----------------
- Define resource interface
- Track resource usage
- Handle resource allocation
- Manage resource lifecycle

Dependencies
------------
typing (standard library)
logging (standard library)
uuid (standard library)
datetime (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
quantsmind.runtime.exceptions (runtime exceptions)
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from quantsmind.runtime.constants import RUNTIME_VERSION
from quantsmind.runtime.enums import ResourceType
from quantsmind.runtime.types import ResourceAmount, ResourceCapacity, ResourceID

logger = logging.getLogger(__name__)


class Resource:
    """Concrete implementation of a resource.

    This class provides resource management capabilities.

    Attributes:
        _resource_id: Resource identifier
        _resource_type: Resource type
        _capacity: Resource capacity
        _allocated: Allocated amount
        _available: Available amount
        _metadata: Resource metadata

    Example:
        >>> resource = Resource(resource_type=ResourceType.CPU, capacity=4.0)
        >>> resource.allocate(2.0)
    """

    def __init__(
        self,
        resource_type: ResourceType,
        capacity: ResourceCapacity,
        resource_id: ResourceID | None = None,
    ) -> None:
        """Initialize a Resource.

        Args:
            resource_type: Resource type
            capacity: Resource capacity
            resource_id: Optional resource identifier

        Example:
            >>> resource = Resource(resource_type=ResourceType.CPU, capacity=4.0)
        """
        self._resource_id = resource_id or str(uuid.uuid4())
        self._resource_type = resource_type
        self._capacity = capacity
        self._allocated: ResourceAmount = 0.0
        self._available: ResourceAmount = capacity
        self._metadata: dict[str, Any] = {
            "runtime_version": RUNTIME_VERSION,
        }
        logger.debug(f"Created resource: {self._resource_id} of type {resource_type.value}")

    @property
    def resource_id(self) -> ResourceID:
        """Get the resource ID.

        Returns:
            Resource identifier

        Example:
            >>> print(f"Resource ID: {resource.resource_id}")
        """
        return self._resource_id

    @property
    def resource_type(self) -> ResourceType:
        """Get the resource type.

        Returns:
            Resource type

        Example:
            >>> print(f"Resource type: {resource.resource_type}")
        """
        return self._resource_type

    @property
    def capacity(self) -> ResourceCapacity:
        """Get the resource capacity.

        Returns:
            Resource capacity

        Example:
            >>> print(f"Capacity: {resource.capacity}")
        """
        return self._capacity

    @property
    def allocated(self) -> ResourceAmount:
        """Get the allocated amount.

        Returns:
            Allocated amount

        Example:
            >>> print(f"Allocated: {resource.allocated}")
        """
        return self._allocated

    @property
    def available(self) -> ResourceAmount:
        """Get the available amount.

        Returns:
            Available amount

        Example:
            >>> print(f"Available: {resource.available}")
        """
        return self._available

    @property
    def utilization(self) -> float:
        """Get the utilization percentage.

        Returns:
            Utilization percentage (0-100)

        Example:
            >>> print(f"Utilization: {resource.utilization}%")
        """
        if self._capacity == 0:
            return 0.0
        return (self._allocated / self._capacity) * 100.0

    def allocate(self, amount: ResourceAmount) -> bool:
        """Allocate resource amount.

        Args:
            amount: Amount to allocate

        Returns:
            True if allocated, False otherwise

        Example:
            >>> allocated = resource.allocate(2.0)
        """
        if amount > self._available:
            logger.warning(f"Insufficient available resource: {amount} > {self._available}")
            return False

        self._allocated += amount
        self._available -= amount
        logger.debug(f"Allocated {amount} of resource {self._resource_id}")
        return True

    def release(self, amount: ResourceAmount) -> bool:
        """Release resource amount.

        Args:
            amount: Amount to release

        Returns:
            True if released, False otherwise

        Example:
            >>> released = resource.release(1.0)
        """
        if amount > self._allocated:
            logger.warning(f"Cannot release more than allocated: {amount} > {self._allocated}")
            return False

        self._allocated -= amount
        self._available += amount
        logger.debug(f"Released {amount} of resource {self._resource_id}")
        return True

    def reset(self) -> None:
        """Reset the resource.

        Example:
            >>> resource.reset()
        """
        self._allocated = 0.0
        self._available = self._capacity
        logger.debug(f"Reset resource {self._resource_id}")

    def set_metadata(self, key: str, value: Any) -> None:
        """Set resource metadata.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> resource.set_metadata("description", "CPU resource")
        """
        self._metadata[key] = value
        logger.debug(f"Set resource metadata: {key}")

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get resource metadata.

        Args:
            key: Metadata key
            default: Default value

        Returns:
            Metadata value or default

        Example:
            >>> value = resource.get_metadata("description")
        """
        return self._metadata.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Convert resource to dictionary.

        Returns:
            Dictionary representation

        Example:
            >>> data = resource.to_dict()
        """
        return {
            "resource_id": self._resource_id,
            "resource_type": self._resource_type.value,
            "capacity": self._capacity,
            "allocated": self._allocated,
            "available": self._available,
            "utilization": self.utilization,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(resource)
        """
        return f"Resource(resource_id={self._resource_id}, type={self._resource_type.value}, capacity={self._capacity})"


# Export
__all__ = [
    "Resource",
]
