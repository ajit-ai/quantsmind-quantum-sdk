"""
Runtime CPU Resource Module

This module provides CPU resource management for the Runtime package.

Purpose
-------
Provide CPU resource management for the QuantsMind SDK.

Responsibilities
----------------
- Manage CPU resources
- Track CPU usage
- Handle CPU allocation
- Monitor CPU performance

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

from quantsmind.runtime.constants import DEFAULT_CPU_LIMIT
from quantsmind.runtime.enums import ResourceType
from quantsmind.runtime.resource import Resource
from quantsmind.runtime.types import ResourceCapacity, ResourceID

logger = logging.getLogger(__name__)


class CPUResource(Resource):
    """Concrete implementation of a CPU resource.

    This class provides CPU resource management capabilities.

    Attributes:
        _num_cores: Number of cores
        _frequency: CPU frequency in GHz

    Example:
        >>> cpu = CPUResource(num_cores=4, frequency=3.5)
        >>> cpu.allocate(2.0)
    """

    def __init__(
        self,
        num_cores: int = 4,
        frequency: float = 3.5,
        capacity: Optional[ResourceCapacity] = None,
        resource_id: Optional[ResourceID] = None,
    ) -> None:
        """Initialize a CPUResource.

        Args:
            num_cores: Number of cores
            frequency: CPU frequency in GHz
            capacity: Resource capacity (default: num_cores)
            resource_id: Optional resource identifier

        Example:
            >>> cpu = CPUResource(num_cores=4, frequency=3.5)
        """
        capacity = capacity or num_cores
        super().__init__(ResourceType.CPU, capacity, resource_id)
        self._num_cores = num_cores
        self._frequency = frequency
        logger.debug(f"Created CPU resource with {num_cores} cores at {frequency} GHz")

    @property
    def num_cores(self) -> int:
        """Get the number of cores.

        Returns:
            Number of cores

        Example:
            >>> print(f"Num cores: {cpu.num_cores}")
        """
        return self._num_cores

    @property
    def frequency(self) -> float:
        """Get the CPU frequency.

        Returns:
            CPU frequency in GHz

        Example:
            >>> print(f"Frequency: {cpu.frequency} GHz")
        """
        return self._frequency

    def to_dict(self) -> Dict[str, Any]:
        """Convert CPU resource to dictionary.

        Returns:
            Dictionary representation

        Example:
            >>> data = cpu.to_dict()
        """
        data = super().to_dict()
        data.update({
            "num_cores": self._num_cores,
            "frequency": self._frequency,
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(cpu)
        """
        return f"CPUResource(resource_id={self._resource_id}, cores={self._num_cores}, frequency={self._frequency} GHz)"


# Export
__all__ = [
    "CPUResource",
]
