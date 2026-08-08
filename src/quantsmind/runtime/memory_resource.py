"""
Runtime Memory Resource Module

This module provides memory resource management for the Runtime package.

Purpose
-------
Provide memory resource management for the QuantsMind SDK.

Responsibilities
----------------
- Manage memory resources
- Track memory usage
- Handle memory allocation
- Monitor memory performance

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
from typing import Any, Dict, Optional

from quantsmind.runtime.constants import DEFAULT_MEMORY_LIMIT
from quantsmind.runtime.enums import ResourceType
from quantsmind.runtime.resource import Resource
from quantsmind.runtime.types import MemoryResource, ResourceCapacity, ResourceID

logger = logging.getLogger(__name__)


class MemoryResource(Resource):
    """Concrete implementation of a memory resource.

    This class provides memory resource management capabilities.

    Attributes:
        _memory_type: Memory type (RAM, VRAM, etc.)
        _bandwidth: Memory bandwidth in GB/s

    Example:
        >>> memory = MemoryResource(memory_type="RAM", bandwidth=25.6)
        >>> memory.allocate(4.0)
    """

    def __init__(
        self,
        memory_type: str = "RAM",
        bandwidth: float = 25.6,
        capacity: Optional[ResourceCapacity] = None,
        resource_id: Optional[ResourceID] = None,
    ) -> None:
        """Initialize a MemoryResource.

        Args:
            memory_type: Memory type
            bandwidth: Memory bandwidth in GB/s
            capacity: Resource capacity in GB (default: DEFAULT_MEMORY_LIMIT)
            resource_id: Optional resource identifier

        Example:
            >>> memory = MemoryResource(memory_type="RAM", bandwidth=25.6)
        """
        capacity = capacity or DEFAULT_MEMORY_LIMIT
        super().__init__(ResourceType.MEMORY, capacity, resource_id)
        self._memory_type = memory_type
        self._bandwidth = bandwidth
        logger.debug(f"Created memory resource with {memory_type}, {bandwidth} GB/s bandwidth")

    @property
    def memory_type(self) -> str:
        """Get the memory type.

        Returns:
            Memory type

        Example:
            >>> print(f"Memory type: {memory.memory_type}")
        """
        return self._memory_type

    @property
    def bandwidth(self) -> float:
        """Get the memory bandwidth.

        Returns:
            Memory bandwidth in GB/s

        Example:
            >>> print(f"Bandwidth: {memory.bandwidth} GB/s")
        """
        return self._bandwidth

    def to_dict(self) -> Dict[str, Any]:
        """Convert memory resource to dictionary.

        Returns:
            Dictionary representation

        Example:
            >>> data = memory.to_dict()
        """
        data = super().to_dict()
        data.update({
            "memory_type": self._memory_type,
            "bandwidth": self._bandwidth,
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(memory)
        """
        return f"MemoryResource(resource_id={self._resource_id}, type={self._memory_type}, bandwidth={self._bandwidth} GB/s)"


# Export
__all__ = [
    "MemoryResource",
]
