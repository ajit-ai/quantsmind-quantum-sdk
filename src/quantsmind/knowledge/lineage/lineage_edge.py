"""
Lineage Edge Module

This module provides lineage edge definitions for the Knowledge package.

Purpose
-------
Provide lineage edge management for lineage tracking.

Responsibilities
----------------
- Define lineage edge structure
- Support lineage edge operations
- Support lineage edge validation
- Support lineage edge metadata

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from quantsmind.knowledge.exceptions import LineageError
from quantsmind.knowledge.types import ValidationResult


class LineageEdge:
    """Concrete implementation of a lineage edge.

    This class provides lineage edge functionality.

    Attributes:
        _id: Edge ID
        _source: Source node ID
        _target: Target node ID
        _edge_type: Edge type
        _weight: Edge weight
        _timestamp: Creation timestamp
        _metadata: Edge metadata

    Example:
        >>> edge = LineageEdge("edge_001", "node_001", "node_002", "derived_from")
        >>> edge.edge_type
    """

    def __init__(
        self,
        edge_id: str,
        source: str,
        target: str,
        edge_type: str = "derived_from",
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a LineageEdge.

        Args:
            edge_id: Edge ID
            source: Source node ID
            target: Target node ID
            edge_type: Edge type
            weight: Edge weight
            metadata: Edge metadata

        Example:
            >>> edge = LineageEdge("edge_001", "node_001", "node_002", "derived_from")
        """
        if not edge_id:
            raise LineageError("Edge ID cannot be empty", {"edge_id": edge_id})

        if not source:
            raise LineageError("Source cannot be empty", {"source": source})

        if not target:
            raise LineageError("Target cannot be empty", {"target": target})

        if weight < 0 or weight > 1:
            raise LineageError("Weight must be between 0 and 1", {"weight": weight})

        self._id = edge_id
        self._source = source
        self._target = target
        self._edge_type = edge_type
        self._weight = weight
        self._timestamp = datetime.now(UTC).replace(tzinfo=None)
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the edge ID.

        Returns:
            Edge ID

        Example:
            >>> eid = edge.id
        """
        return self._id

    @property
    def source(self) -> str:
        """Get the source node ID.

        Returns:
            Source node ID

        Example:
            >>> source = edge.source
        """
        return self._source

    @property
    def target(self) -> str:
        """Get the target node ID.

        Returns:
            Target node ID

        Example:
            >>> target = edge.target
        """
        return self._target

    @property
    def edge_type(self) -> str:
        """Get the edge type.

        Returns:
            Edge type

        Example:
            >>> edge_type = edge.edge_type
        """
        return self._edge_type

    @property
    def weight(self) -> float:
        """Get the edge weight.

        Returns:
            Edge weight

        Example:
            >>> weight = edge.weight
        """
        return self._weight

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp.

        Returns:
            Creation timestamp

        Example:
            >>> timestamp = edge.timestamp
        """
        return self._timestamp

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the edge metadata.

        Returns:
            Edge metadata

        Example:
            >>> metadata = edge.metadata
        """
        return self._metadata.copy()

    def set_weight(self, weight: float) -> None:
        """Set the edge weight.

        Args:
            weight: Edge weight

        Example:
            >>> edge.set_weight(0.8)
        """
        if weight < 0 or weight > 1:
            raise LineageError("Weight must be between 0 and 1", {"weight": weight})
        self._weight = weight

    def set_edge_type(self, edge_type: str) -> None:
        """Set the edge type.

        Args:
            edge_type: Edge type

        Example:
            >>> edge.set_edge_type("transformed_by")
        """
        self._edge_type = edge_type

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the edge.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> edge.add_metadata("transformation", "filter")
        """
        self._metadata[key] = value

    def validate(self) -> ValidationResult:
        """Validate the edge.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = edge.validate()
        """
        errors = []

        if not self._id:
            errors.append("Edge ID cannot be empty")

        if not self._source:
            errors.append("Source cannot be empty")

        if not self._target:
            errors.append("Target cannot be empty")

        if self._weight < 0 or self._weight > 1:
            errors.append("Weight must be between 0 and 1")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Edge definition

        Example:
            >>> data = edge.to_dict()
        """
        return {
            "id": self._id,
            "source": self._source,
            "target": self._target,
            "edge_type": self._edge_type,
            "weight": self._weight,
            "timestamp": self._timestamp.isoformat(),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(edge)
        """
        return f"LineageEdge(id={self._id}, source={self._source}, target={self._target}, type={self._edge_type})"


# Export
__all__ = [
    "LineageEdge",
]
