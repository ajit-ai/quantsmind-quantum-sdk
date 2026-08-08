"""
Lineage Node Module

This module provides lineage node definitions for the Knowledge package.

Purpose
-------
Provide lineage node management for lineage tracking.

Responsibilities
----------------
- Define lineage node structure
- Support lineage node operations
- Support lineage node validation
- Support lineage node metadata

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from quantsmind.knowledge.enums import ProvenanceType
from quantsmind.knowledge.exceptions import LineageError
from quantsmind.knowledge.types import ValidationResult


class LineageNode:
    """Concrete implementation of a lineage node.

    This class provides lineage node functionality.

    Attributes:
        _id: Node ID
        _node_type: Node type
        _entity_id: Entity ID
        _transformation: Transformation applied
        _timestamp: Creation timestamp
        _metadata: Node metadata

    Example:
        >>> node = LineageNode("node_001", "transformation", "entity_001")
        >>> node.node_type
    """

    def __init__(
        self,
        node_id: str,
        node_type: str,
        entity_id: str,
        transformation: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a LineageNode.

        Args:
            node_id: Node ID
            node_type: Node type
            entity_id: Entity ID
            transformation: Transformation applied
            metadata: Node metadata

        Example:
            >>> node = LineageNode("node_001", "transformation", "entity_001")
        """
        if not node_id:
            raise LineageError("Node ID cannot be empty", {"node_id": node_id})

        if not node_type:
            raise LineageError("Node type cannot be empty", {"node_type": node_type})

        if not entity_id:
            raise LineageError("Entity ID cannot be empty", {"entity_id": entity_id})

        self._id = node_id
        self._node_type = node_type
        self._entity_id = entity_id
        self._transformation = transformation
        self._timestamp = datetime.utcnow()
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the node ID.

        Returns:
            Node ID

        Example:
            >>> nid = node.id
        """
        return self._id

    @property
    def node_type(self) -> str:
        """Get the node type.

        Returns:
            Node type

        Example:
            >>> node_type = node.node_type
        """
        return self._node_type

    @property
    def entity_id(self) -> str:
        """Get the entity ID.

        Returns:
            Entity ID

        Example:
            >>> entity_id = node.entity_id
        """
        return self._entity_id

    @property
    def transformation(self) -> Optional[str]:
        """Get the transformation.

        Returns:
            Transformation applied

        Example:
            >>> transformation = node.transformation
        """
        return self._transformation

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp.

        Returns:
            Creation timestamp

        Example:
            >>> timestamp = node.timestamp
        """
        return self._timestamp

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the node metadata.

        Returns:
            Node metadata

        Example:
            >>> metadata = node.metadata
        """
        return self._metadata.copy()

    def set_transformation(self, transformation: str) -> None:
        """Set the transformation.

        Args:
            transformation: Transformation applied

        Example:
            >>> node.set_transformation("filter")
        """
        self._transformation = transformation

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the node.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> node.add_metadata("parameters", {"threshold": 0.5})
        """
        self._metadata[key] = value

    def validate(self) -> ValidationResult:
        """Validate the node.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = node.validate()
        """
        errors = []

        if not self._id:
            errors.append("Node ID cannot be empty")

        if not self._node_type:
            errors.append("Node type cannot be empty")

        if not self._entity_id:
            errors.append("Entity ID cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Node definition

        Example:
            >>> data = node.to_dict()
        """
        return {
            "id": self._id,
            "node_type": self._node_type,
            "entity_id": self._entity_id,
            "transformation": self._transformation,
            "timestamp": self._timestamp.isoformat(),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(node)
        """
        return f"LineageNode(id={self._id}, type={self._node_type}, entity={self._entity_id})"


# Export
__all__ = [
    "LineageNode",
]
