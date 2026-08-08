"""
Provenance Module

This module provides provenance definitions for the Knowledge package.

Purpose
-------
Provide provenance management and tracking.

Responsibilities
----------------
- Define provenance structure
- Support provenance operations
- Support provenance validation
- Support provenance tracing

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.interfaces (knowledge interfaces)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from quantsmind.knowledge.enums import ProvenanceType
from quantsmind.knowledge.exceptions import ProvenanceError
from quantsmind.knowledge.interfaces import IProvenance
from quantsmind.knowledge.types import (
    ProvenanceData,
    ProvenanceID,
    ValidationResult,
)


class Provenance(IProvenance):
    """Concrete implementation of provenance.

    This class provides provenance functionality.

    Attributes:
        _id: Provenance ID
        _provenance_type: Provenance type
        _source: Source information
        _creator: Creator information
        _timestamp: Creation timestamp
        _metadata: Provenance metadata

    Example:
        >>> provenance = Provenance("prov_001", ProvenanceType.DATASET)
        >>> provenance.add_source("source_001", {"type": "file"})
    """

    def __init__(
        self,
        provenance_id: ProvenanceID,
        provenance_type: ProvenanceType = ProvenanceType.DATASET,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Provenance.

        Args:
            provenance_id: Provenance ID
            provenance_type: Provenance type
            metadata: Provenance metadata

        Example:
            >>> provenance = Provenance("prov_001", ProvenanceType.DATASET)
        """
        self._id = provenance_id
        self._provenance_type = provenance_type
        self._source: Optional[Dict[str, Any]] = None
        self._creator: Optional[Dict[str, Any]] = None
        self._timestamp = datetime.utcnow()
        self._metadata = metadata or {}

    @property
    def id(self) -> ProvenanceID:
        """Get the provenance ID.

        Returns:
            Provenance ID

        Example:
            >>> pid = provenance.id
        """
        return self._id

    @property
    def provenance_type(self) -> ProvenanceType:
        """Get the provenance type.

        Returns:
            Provenance type

        Example:
            >>> ptype = provenance.provenance_type
        """
        return self._provenance_type

    @property
    def source(self) -> Optional[Dict[str, Any]]:
        """Get the source information.

        Returns:
            Source information

        Example:
            >>> source = provenance.source
        """
        return self._source.copy() if self._source else None

    @property
    def creator(self) -> Optional[Dict[str, Any]]:
        """Get the creator information.

        Returns:
            Creator information

        Example:
            >>> creator = provenance.creator
        """
        return self._creator.copy() if self._creator else None

    @property
    def timestamp(self) -> datetime:
        """Get the creation timestamp.

        Returns:
            Timestamp

        Example:
            >>> timestamp = provenance.timestamp
        """
        return self._timestamp

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the provenance metadata.

        Returns:
            Provenance metadata

        Example:
            >>> metadata = provenance.metadata
        """
        return self._metadata.copy()

    def set_source(self, source: Dict[str, Any]) -> None:
        """Set the source information.

        Args:
            source: Source information

        Example:
            >>> provenance.set_source({"type": "file", "path": "/data.csv"})
        """
        self._source = source

    def set_creator(self, creator: Dict[str, Any]) -> None:
        """Set the creator information.

        Args:
            creator: Creator information

        Example:
            >>> provenance.set_creator({"name": "John", "id": "user_001"})
        """
        self._creator = creator

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the provenance.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> provenance.add_metadata("version", "1.0")
        """
        self._metadata[key] = value

    def get_trace(self) -> List[Dict[str, Any]]:
        """Get the provenance trace.

        Returns:
            Trace information

        Example:
            >>> trace = provenance.get_trace()
        """
        trace = []

        if self._source:
            trace.append({"type": "source", "data": self._source})

        if self._creator:
            trace.append({"type": "creator", "data": self._creator})

        trace.append({"type": "timestamp", "data": self._timestamp.isoformat()})

        return trace

    def validate(self) -> ValidationResult:
        """Validate the provenance.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = provenance.validate()
        """
        errors = []

        if not self._id:
            errors.append("Provenance ID cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> ProvenanceData:
        """Convert to dictionary.

        Returns:
            Provenance data

        Example:
            >>> data = provenance.to_dict()
        """
        return {
            "id": self._id,
            "provenance_type": self._provenance_type.value,
            "source": self._source,
            "creator": self._creator,
            "timestamp": self._timestamp.isoformat(),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(provenance)
        """
        return f"Provenance(id={self._id}, type={self._provenance_type.value}, timestamp={self._timestamp.isoformat()})"


# Export
__all__ = [
    "Provenance",
]
