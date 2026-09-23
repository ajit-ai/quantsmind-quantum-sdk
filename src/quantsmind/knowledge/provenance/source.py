"""
Source Module

This module provides source definitions for the Knowledge package.

Purpose
-------
Provide source management for provenance tracking.

Responsibilities
----------------
- Define source structure
- Support source operations
- Support source validation
- Support source metadata

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

from quantsmind.knowledge.exceptions import ProvenanceError
from quantsmind.knowledge.types import SourceID, ValidationResult


class Source:
    """Concrete implementation of a source.

    This class provides source functionality for provenance tracking.

    Attributes:
        _id: Source ID
        _source_type: Source type
        _location: Source location
        _accessed_at: Access timestamp
        _metadata: Source metadata

    Example:
        >>> source = Source("source_001", "file", "/data.csv")
        >>> source.location
    """

    def __init__(
        self,
        source_id: SourceID,
        source_type: str,
        location: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Source.

        Args:
            source_id: Source ID
            source_type: Source type
            location: Source location
            metadata: Source metadata

        Example:
            >>> source = Source("source_001", "file", "/data.csv")
        """
        if not source_id:
            raise ProvenanceError("Source ID cannot be empty", {"source_id": source_id})

        if not location:
            raise ProvenanceError("Source location cannot be empty", {"location": location})

        self._id = source_id
        self._source_type = source_type
        self._location = location
        self._accessed_at = datetime.now(UTC).replace(tzinfo=None)
        self._metadata = metadata or {}

    @property
    def id(self) -> SourceID:
        """Get the source ID.

        Returns:
            Source ID

        Example:
            >>> sid = source.id
        """
        return self._id

    @property
    def source_type(self) -> str:
        """Get the source type.

        Returns:
            Source type

        Example:
            >>> stype = source.source_type
        """
        return self._source_type

    @property
    def location(self) -> str:
        """Get the source location.

        Returns:
            Source location

        Example:
            >>> location = source.location
        """
        return self._location

    @property
    def accessed_at(self) -> datetime:
        """Get the access timestamp.

        Returns:
            Access timestamp

        Example:
            >>> accessed = source.accessed_at
        """
        return self._accessed_at

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the source metadata.

        Returns:
            Source metadata

        Example:
            >>> metadata = source.metadata
        """
        return self._metadata.copy()

    def update_access_time(self) -> None:
        """Update the access timestamp.

        Example:
            >>> source.update_access_time()
        """
        self._accessed_at = datetime.now(UTC).replace(tzinfo=None)

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the source.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> source.add_metadata("format", "csv")
        """
        self._metadata[key] = value

    def validate(self) -> ValidationResult:
        """Validate the source.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = source.validate()
        """
        errors = []

        if not self._id:
            errors.append("Source ID cannot be empty")

        if not self._location:
            errors.append("Source location cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Source definition

        Example:
            >>> data = source.to_dict()
        """
        return {
            "id": self._id,
            "source_type": self._source_type,
            "location": self._location,
            "accessed_at": self._accessed_at.isoformat(),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(source)
        """
        return f"Source(id={self._id}, type={self._source_type}, location={self._location})"


class SourceRegistry:
    """Registry for sources.

    This class provides source registry functionality.

    Attributes:
        _sources: Registered sources

    Example:
        >>> registry = SourceRegistry()
        >>> registry.register(Source("source_001", "file", "/data.csv"))
    """

    def __init__(self) -> None:
        """Initialize a SourceRegistry.

        Example:
            >>> registry = SourceRegistry()
        """
        self._sources: dict[SourceID, Source] = {}

    def register(self, source: Source) -> None:
        """Register a source.

        Args:
            source: Source to register

        Example:
            >>> registry.register(Source("source_001", "file", "/data.csv"))
        """
        self._sources[source.id] = source

    def unregister(self, source_id: SourceID) -> bool:
        """Unregister a source.

        Args:
            source_id: Source ID

        Returns:
            True if unregistered

        Example:
            >>> unregistered = registry.unregister("source_001")
        """
        if source_id in self._sources:
            del self._sources[source_id]
            return True
        return False

    def get(self, source_id: SourceID) -> Source | None:
        """Get a source by ID.

        Args:
            source_id: Source ID

        Returns:
            Source or None

        Example:
            >>> source = registry.get("source_001")
        """
        return self._sources.get(source_id)

    def get_by_type(self, source_type: str) -> List[Source]:
        """Get sources by type.

        Args:
            source_type: Source type

        Returns:
            List of sources

        Example:
            >>> sources = registry.get_by_type("file")
        """
        return [source for source in self._sources.values() if source.source_type == source_type]

    def list_all(self) -> List[Source]:
        """List all registered sources.

        Returns:
            List of sources

        Example:
            >>> sources = registry.list_all()
        """
        return list(self._sources.values())

    def count(self) -> int:
        """Get the number of registered sources.

        Returns:
            Number of sources

        Example:
            >>> count = registry.count()
        """
        return len(self._sources)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Registry state

        Example:
            >>> data = registry.to_dict()
        """
        return {
            "sources": [source.to_dict() for source in self._sources.values()],
            "count": len(self._sources),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(registry)
        """
        return f"SourceRegistry(sources={len(self._sources)})"


# Export
__all__ = [
    "Source",
    "SourceRegistry",
]
