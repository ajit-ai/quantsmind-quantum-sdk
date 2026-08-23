"""
Runtime Resource Manager Module

This module provides resource management for the Runtime package.

Purpose
-------
Provide resource management for the QuantsMind SDK.

Responsibilities
----------------
- Manage resource pool
- Track resource allocation
- Handle resource requests
- Balance resource usage

Dependencies
------------
typing (standard library)
logging (standard library)
threading (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
quantsmind.runtime.exceptions (runtime exceptions)
quantsmind.runtime.resource (resource)
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from quantsmind.runtime.enums import ResourceType
from quantsmind.runtime.exceptions import ResourceError
from quantsmind.runtime.resource import Resource
from quantsmind.runtime.types import ResourceAmount, ResourceID

logger = logging.getLogger(__name__)


class ResourceManager:
    """Concrete implementation of a resource manager.

    This class provides resource management capabilities.

    Attributes:
        _resources: Resource pool
        _allocations: Resource allocations
        _lock: Thread lock

    Example:
        >>> manager = ResourceManager()
        >>> manager.add_resource(resource)
        >>> manager.allocate(resource_type=ResourceType.CPU, amount=2.0)
    """

    def __init__(self) -> None:
        """Initialize a ResourceManager.

        Example:
            >>> manager = ResourceManager()
        """
        self._resources: dict[ResourceID, Resource] = {}
        self._allocations: dict[str, dict[ResourceID, ResourceAmount]] = {}
        self._lock = threading.Lock()
        logger.debug("Created resource manager")

    @property
    def resource_count(self) -> int:
        """Get the number of resources.

        Returns:
            Number of resources

        Example:
            >>> print(f"Resource count: {manager.resource_count}")
        """
        with self._lock:
            return len(self._resources)

    def add_resource(self, resource: Resource) -> None:
        """Add a resource to the manager.

        Args:
            resource: Resource to add

        Raises:
            ResourceError: If resource already exists

        Example:
            >>> manager.add_resource(resource)
        """
        with self._lock:
            if resource.resource_id in self._resources:
                raise ResourceError(f"Resource already exists: {resource.resource_id}")
            self._resources[resource.resource_id] = resource
        logger.debug(f"Added resource: {resource.resource_id}")

    def remove_resource(self, resource_id: ResourceID) -> bool:
        """Remove a resource from the manager.

        Args:
            resource_id: Resource identifier

        Returns:
            True if removed, False otherwise

        Example:
            >>> removed = manager.remove_resource("resource_123")
        """
        with self._lock:
            if resource_id in self._resources:
                del self._resources[resource_id]
                return True
        return False

    def get_resource(self, resource_id: ResourceID) -> Resource | None:
        """Get a resource by ID.

        Args:
            resource_id: Resource identifier

        Returns:
            Resource or None

        Example:
            >>> resource = manager.get_resource("resource_123")
        """
        with self._lock:
            return self._resources.get(resource_id)

    def get_resources_by_type(self, resource_type: ResourceType) -> list[Resource]:
        """Get resources by type.

        Args:
            resource_type: Resource type

        Returns:
            List of resources

        Example:
            >>> resources = manager.get_resources_by_type(ResourceType.CPU)
        """
        with self._lock:
            return [r for r in self._resources.values() if r.resource_type == resource_type]

    def allocate(
        self,
        resource_type: ResourceType,
        amount: ResourceAmount,
        requester_id: str,
    ) -> bool:
        """Allocate resources.

        Args:
            resource_type: Resource type
            amount: Amount to allocate
            requester_id: Requester identifier

        Returns:
            True if allocated, False otherwise

        Example:
            >>> allocated = manager.allocate(ResourceType.CPU, 2.0, "task_123")
        """
        with self._lock:
            resources = self.get_resources_by_type(resource_type)
            
            for resource in resources:
                if resource.allocate(amount):
                    if requester_id not in self._allocations:
                        self._allocations[requester_id] = {}
                    self._allocations[requester_id][resource.resource_id] = amount
                    logger.debug(f"Allocated {amount} of {resource_type.value} to {requester_id}")
                    return True
            
            logger.warning(f"Failed to allocate {amount} of {resource_type.value} to {requester_id}")
            return False

    def release(
        self,
        resource_type: ResourceType,
        amount: ResourceAmount,
        requester_id: str,
    ) -> bool:
        """Release resources.

        Args:
            resource_type: Resource type
            amount: Amount to release
            requester_id: Requester identifier

        Returns:
            True if released, False otherwise

        Example:
            >>> released = manager.release(ResourceType.CPU, 1.0, "task_123")
        """
        with self._lock:
            if requester_id not in self._allocations:
                return False
            
            for resource_id, allocated_amount in self._allocations[requester_id].items():
                resource = self._resources.get(resource_id)
                if resource and resource.resource_type == resource_type:
                    release_amount = min(amount, allocated_amount)
                    if resource.release(release_amount):
                        self._allocations[requester_id][resource_id] -= release_amount
                        if self._allocations[requester_id][resource_id] <= 0:
                            del self._allocations[requester_id][resource_id]
                        logger.debug(f"Released {release_amount} of {resource_type.value} from {requester_id}")
                        return True
            
            return False

    def get_utilization(self, resource_type: ResourceType) -> float:
        """Get resource utilization by type.

        Args:
            resource_type: Resource type

        Returns:
            Utilization percentage

        Example:
            >>> utilization = manager.get_utilization(ResourceType.CPU)
        """
        with self._lock:
            resources = self.get_resources_by_type(resource_type)
            if not resources:
                return 0.0
            
            total_capacity = sum(r.capacity for r in resources)
            total_allocated = sum(r.allocated for r in resources)
            
            if total_capacity == 0:
                return 0.0
            
            return (total_allocated / total_capacity) * 100.0

    def get_status(self) -> dict[str, Any]:
        """Get resource manager status.

        Returns:
            Resource manager status

        Example:
            >>> status = manager.get_status()
        """
        with self._lock:
            return {
                "resource_count": self.resource_count,
                "resources_by_type": {
                    rt.value: len(self.get_resources_by_type(rt))
                    for rt in ResourceType
                },
                "utilization_by_type": {
                    rt.value: self.get_utilization(rt)
                    for rt in ResourceType
                },
                "active_allocations": len(self._allocations),
            }


# Export
__all__ = [
    "ResourceManager",
]
