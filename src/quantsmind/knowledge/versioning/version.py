"""
Version Module

This module provides version definitions for the Knowledge package.

Purpose
-------
Provide version management for knowledge versioning.

Responsibilities
----------------
- Define version structure
- Support version operations
- Support version validation
- Support version metadata

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
from typing import Any

from quantsmind.knowledge.enums import VersionType
from quantsmind.knowledge.exceptions import VersionError
from quantsmind.knowledge.types import ValidationResult


class Version:
    """Concrete implementation of a version.

    This class provides version functionality for knowledge versioning.

    Attributes:
        _id: Version ID
        _entity_id: Entity ID
        _version_number: Version number
        _version_type: Version type
        _data: Version data
        _timestamp: Timestamp
        _author: Author
        _description: Description
        _metadata: Version metadata

    Example:
        >>> version = Version("v_001", "entity_001", "1.0.0", VersionType.MAJOR)
    """

    def __init__(
        self,
        version_id: str,
        entity_id: str,
        version_number: str,
        version_type: VersionType,
        data: dict[str, Any] | None = None,
        author: str | None = None,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Version.

        Args:
            version_id: Version ID
            entity_id: Entity ID
            version_number: Version number
            version_type: Version type
            data: Version data
            author: Author
            description: Description
            metadata: Version metadata

        Example:
            >>> version = Version("v_001", "entity_001", "1.0.0", VersionType.MAJOR)
        """
        if not version_id:
            raise VersionError("Version ID cannot be empty", {"version_id": version_id})

        if not entity_id:
            raise VersionError("Entity ID cannot be empty", {"entity_id": entity_id})

        if not version_number:
            raise VersionError("Version number cannot be empty", {"version_number": version_number})

        self._id = version_id
        self._entity_id = entity_id
        self._version_number = version_number
        self._version_type = version_type
        self._data = data or {}
        self._timestamp = datetime.utcnow()
        self._author = author
        self._description = description
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the version ID.

        Returns:
            Version ID

        Example:
            >>> vid = version.id
        """
        return self._id

    @property
    def entity_id(self) -> str:
        """Get the entity ID.

        Returns:
            Entity ID

        Example:
            >>> entity_id = version.entity_id
        """
        return self._entity_id

    @property
    def version_number(self) -> str:
        """Get the version number.

        Returns:
            Version number

        Example:
            >>> version_number = version.version_number
        """
        return self._version_number

    @property
    def version_type(self) -> VersionType:
        """Get the version type.

        Returns:
            Version type

        Example:
            >>> vtype = version.version_type
        """
        return self._version_type

    @property
    def data(self) -> dict[str, Any]:
        """Get the version data.

        Returns:
            Version data

        Example:
            >>> data = version.data
        """
        return self._data.copy()

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp.

        Returns:
            Timestamp

        Example:
            >>> timestamp = version.timestamp
        """
        return self._timestamp

    @property
    def author(self) -> str | None:
        """Get the author.

        Returns:
            Author

        Example:
            >>> author = version.author
        """
        return self._author

    @property
    def description(self) -> str | None:
        """Get the description.

        Returns:
            Description

        Example:
            >>> description = version.description
        """
        return self._description

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the version metadata.

        Returns:
            Version metadata

        Example:
            >>> metadata = version.metadata
        """
        return self._metadata.copy()

    def set_data(self, data: dict[str, Any]) -> None:
        """Set the version data.

        Args:
            data: Version data

        Example:
            >>> version.set_data({"value": 42})
        """
        self._data = data

    def add_data(self, key: str, value: Any) -> None:
        """Add data to the version.

        Args:
            key: Data key
            value: Data value

        Example:
            >>> version.add_data("value", 42)
        """
        self._data[key] = value

    def set_author(self, author: str) -> None:
        """Set the author.

        Args:
            author: Author

        Example:
            >>> version.set_author("user_001")
        """
        self._author = author

    def set_description(self, description: str) -> None:
        """Set the description.

        Args:
            description: Description

        Example:
            >>> version.set_description("Initial version")
        """
        self._description = description

    def validate(self) -> ValidationResult:
        """Validate the version.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = version.validate()
        """
        errors = []

        if not self._id:
            errors.append("Version ID cannot be empty")

        if not self._entity_id:
            errors.append("Entity ID cannot be empty")

        if not self._version_number:
            errors.append("Version number cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Version definition

        Example:
            >>> data = version.to_dict()
        """
        return {
            "id": self._id,
            "entity_id": self._entity_id,
            "version_number": self._version_number,
            "version_type": self._version_type.value,
            "data": self._data,
            "timestamp": self._timestamp.isoformat(),
            "author": self._author,
            "description": self._description,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(version)
        """
        return f"Version(id={self._id}, entity={self._entity_id}, number={self._version_number}, type={self._version_type.value})"


class VersionHistory:
    """Concrete implementation of a version history.

    This class provides version history functionality for tracking versions.

    Attributes:
        _entity_id: Entity ID
        _versions: Version history
        _current_version: Current version

    Example:
        >>> history = VersionHistory("entity_001")
        >>> history.add_version(Version("v_001", "entity_001", "1.0.0", VersionType.MAJOR))
    """

    def __init__(self, entity_id: str) -> None:
        """Initialize a VersionHistory.

        Args:
            entity_id: Entity ID

        Example:
            >>> history = VersionHistory("entity_001")
        """
        if not entity_id:
            raise VersionError("Entity ID cannot be empty", {"entity_id": entity_id})

        self._entity_id = entity_id
        self._versions: dict[str, Version] = {}
        self._current_version: str | None = None

    @property
    def entity_id(self) -> str:
        """Get the entity ID.

        Returns:
            Entity ID

        Example:
            >>> entity_id = history.entity_id
        """
        return self._entity_id

    @property
    def versions(self) -> dict[str, Version]:
        """Get the versions.

        Returns:
            Versions dictionary

        Example:
            >>> versions = history.versions
        """
        return self._versions.copy()

    @property
    def current_version(self) -> str | None:
        """Get the current version.

        Returns:
            Current version number or None

        Example:
            >>> current = history.current_version
        """
        return self._current_version

    def add_version(self, version: Version) -> None:
        """Add a version to the history.

        Args:
            version: Version to add

        Example:
            >>> history.add_version(Version("v_001", "entity_001", "1.0.0", VersionType.MAJOR))
        """
        self._versions[version.version_number] = version
        self._current_version = version.version_number

    def remove_version(self, version_number: str) -> bool:
        """Remove a version from the history.

        Args:
            version_number: Version number

        Returns:
            True if removed

        Example:
            >>> removed = history.remove_version("1.0.0")
        """
        if version_number in self._versions:
            del self._versions[version_number]
            if self._current_version == version_number:
                self._current_version = None
            return True
        return False

    def get_version(self, version_number: str) -> Version | None:
        """Get a version by number.

        Args:
            version_number: Version number

        Returns:
            Version or None

        Example:
            >>> version = history.get_version("1.0.0")
        """
        return self._versions.get(version_number)

    def get_current(self) -> Version | None:
        """Get the current version.

        Returns:
            Current version or None

        Example:
            >>> version = history.get_current()
        """
        if self._current_version:
            return self._versions.get(self._current_version)
        return None

    def list_versions(self) -> list[str]:
        """List all version numbers.

        Returns:
            List of version numbers

        Example:
            >>> versions = history.list_versions()
        """
        return list(self._versions.keys())

    def count(self) -> int:
        """Get the number of versions.

        Returns:
            Number of versions

        Example:
            >>> count = history.count()
        """
        return len(self._versions)

    def validate(self) -> ValidationResult:
        """Validate the version history.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = history.validate()
        """
        errors = []

        if not self._entity_id:
            errors.append("Entity ID cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Version history definition

        Example:
            >>> data = history.to_dict()
        """
        return {
            "entity_id": self._entity_id,
            "current_version": self._current_version,
            "version_count": len(self._versions),
            "versions": [v.to_dict() for v in self._versions.values()],
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(history)
        """
        return f"VersionHistory(entity={self._entity_id}, current={self._current_version}, versions={len(self._versions)})"


# Export
__all__ = [
    "Version",
    "VersionHistory",
]
