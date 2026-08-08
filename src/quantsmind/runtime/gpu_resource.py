"""
Runtime GPU Resource Module

This module provides GPU resource management for the Runtime package.

Purpose
-------
Provide GPU resource management for the QuantsMind SDK.

Responsibilities
----------------
- Manage GPU resources
- Track GPU usage
- Handle GPU allocation
- Monitor GPU performance

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

from quantsmind.runtime.enums import ResourceType
from quantsmind.runtime.resource import Resource
from quantsmind.runtime.types import ResourceCapacity, ResourceID

logger = logging.getLogger(__name__)


class GPUResource(Resource):
    """Concrete implementation of a GPU resource.

    This class provides GPU resource management capabilities.

    Attributes:
        _num_gpus: Number of GPUs
        _memory: GPU memory in GB
        _compute_capability: Compute capability

    Example:
        >>> gpu = GPUResource(num_gpus=1, memory=16.0, compute_capability="8.0")
        >>> gpu.allocate(1.0)
    """

    def __init__(
        self,
        num_gpus: int = 1,
        memory: float = 16.0,
        compute_capability: str = "8.0",
        capacity: Optional[ResourceCapacity] = None,
        resource_id: Optional[ResourceID] = None,
    ) -> None:
        """Initialize a GPUResource.

        Args:
            num_gpus: Number of GPUs
            memory: GPU memory in GB
            compute_capability: Compute capability
            capacity: Resource capacity (default: num_gpus)
            resource_id: Optional resource identifier

        Example:
            >>> gpu = GPUResource(num_gpus=1, memory=16.0, compute_capability="8.0")
        """
        capacity = capacity or num_gpus
        super().__init__(ResourceType.GPU, capacity, resource_id)
        self._num_gpus = num_gpus
        self._memory = memory
        self._compute_capability = compute_capability
        logger.debug(f"Created GPU resource with {num_gpus} GPUs, {memory} GB memory")

    @property
    def num_gpus(self) -> int:
        """Get the number of GPUs.

        Returns:
            Number of GPUs

        Example:
            >>> print(f"Num GPUs: {gpu.num_gpus}")
        """
        return self._num_gpus

    @property
    def memory(self) -> float:
        """Get the GPU memory.

        Returns:
            GPU memory in GB

        Example:
            >>> print(f"Memory: {gpu.memory} GB")
        """
        return self._memory

    @property
    def compute_capability(self) -> str:
        """Get the compute capability.

        Returns:
            Compute capability

        Example:
            >>> print(f"Compute capability: {gpu.compute_capability}")
        """
        return self._compute_capability

    def to_dict(self) -> Dict[str, Any]:
        """Convert GPU resource to dictionary.

        Returns:
            Dictionary representation

        Example:
            >>> data = gpu.to_dict()
        """
        data = super().to_dict()
        data.update({
            "num_gpus": self._num_gpus,
            "memory": self._memory,
            "compute_capability": self._compute_capability,
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(gpu)
        """
        return f"GPUResource(resource_id={self._resource_id}, gpus={self._num_gpus}, memory={self._memory} GB)"


# Export
__all__ = [
    "GPUResource",
]
