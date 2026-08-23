"""
Runtime Storage Resource Module

This module provides storage resource management for the Runtime package.

Purpose
-------
Provide storage resource management for the QuantsMind SDK.

Responsibilities
----------------
- Manage storage resources
- Track storage usage
- Handle storage allocation
- Monitor storage performance

Dependencies
------------
typing (standard library)
logging (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
quantsmind.runtime.exceptions (runtime exceptions)
quantsmind.runtime.resource (resource)
"""

from __future__ import annotations

import logging
from typing import Any

from quantsmind.runtime.constants import DEFAULT_STORAGE_LIMIT
from quantsmind.runtime.enums import ResourceType
from quantsmind.runtime.resource import Resource
from quantsmind.runtime.types import ResourceCapacity, ResourceID

logger = logging.getLogger(__name__)


class StorageResource(Resource):
    """Concrete implementation of a storage resource.

    This class provides storage resource management capabilities.

    Attributes:
        _storage_type: Storage type (SSD, HDD, NVMe, etc.)
        _iops: IOPS capacity
        _latency: Latency in ms

    Example:
        >>> storage = StorageResource(storage_type="NVMe", iops=100000, latency=0.1)
        >>> storage.allocate(100.0)
    """

    def __init__(
        self,
        storage_type: str = "NVMe",
        iops: int = 100000,
        latency: float = 0.1,
        capacity: ResourceCapacity | None = None,
        resource_id: ResourceID | None = None,
    ) -> None:
        """Initialize a StorageResource.

        Args:
            storage_type: Storage type
            iops: IOPS capacity
            latency: Latency in ms
            capacity: Resource capacity in GB (default: DEFAULT_STORAGE_LIMIT)
            resource_id: Optional resource identifier

        Example:
            >>> storage = StorageResource(storage_type="NVMe", iops=100000, latency=0.1)
        """
        capacity = capacity or DEFAULT_STORAGE_LIMIT
        super().__init__(ResourceType.STORAGE, capacity, resource_id)
        self._storage_type = storage_type
        self._iops = iops
        self._latency = latency
        logger.debug(f"Created storage resource with {storage_type}, {iops} IOPS, {latency} ms latency")

    @property
    def storage_type(self) -> str:
        """Get the storage type.

        Returns:
            Storage type

        Example:
            >>> print(f"Storage type: {storage.storage_type}")
        """
        return self._storage_type

    @property
    def iops(self) -> int:
        """Get the IOPS capacity.

        Returns:
            IOPS capacity

        Example:
            >>> print(f"IOPS: {storage.iops}")
        """
        return self._iops

    @property
    def latency(self) -> float:
        """Get the latency.

        Returns:
            Latency in ms

        Example:
            >>> print(f"Latency: {storage.latency} ms")
        """
        return self._latency

    def to_dict(self) -> dict[str, Any]:
        """Convert storage resource to dictionary.

        Returns:
            Dictionary representation

        Example:
            >>> data = storage.to_dict()
        """
        data = super().to_dict()
        data.update({
            "storage_type": self._storage_type,
            "iops": self._iops,
            "latency": self._latency,
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(storage)
        """
        return f"StorageResource(resource_id={self._resource_id}, type={self._storage_type}, iops={self._iops})"


# Export
__all__ = [
    "StorageResource",
]
