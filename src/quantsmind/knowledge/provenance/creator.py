"""
Creator Module

This module provides creator definitions for the Knowledge package.

Purpose
-------
Provide creator management for provenance tracking.

Responsibilities
----------------
- Define creator structure
- Support creator operations
- Support creator validation
- Support creator metadata

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
from quantsmind.knowledge.exceptions import ProvenanceError
from quantsmind.knowledge.types import CreatorID, ValidationResult


class Creator:
    """Concrete implementation of a creator.

    This class provides creator functionality for provenance tracking.

    Attributes:
        _id: Creator ID
        _name: Creator name
        _creator_type: Creator type
        _contact: Contact information
        _metadata: Creator metadata

    Example:
        >>> creator = Creator("creator_001", "John Doe", "user")
        >>> creator.name
    """

    def __init__(
        self,
        creator_id: CreatorID,
        name: str,
        creator_type: str = "user",
        contact: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Creator.

        Args:
            creator_id: Creator ID
            name: Creator name
            creator_type: Creator type
            contact: Contact information
            metadata: Creator metadata

        Example:
            >>> creator = Creator("creator_001", "John Doe", "user")
        """
        if not creator_id:
            raise ProvenanceError("Creator ID cannot be empty", {"creator_id": creator_id})

        if not name:
            raise ProvenanceError("Creator name cannot be empty", {"name": name})

        self._id = creator_id
        self._name = name
        self._creator_type = creator_type
        self._contact = contact or {}
        self._metadata = metadata or {}

    @property
    def id(self) -> CreatorID:
        """Get the creator ID.

        Returns:
            Creator ID

        Example:
            >>> cid = creator.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the creator name.

        Returns:
            Creator name

        Example:
            >>> name = creator.name
        """
        return self._name

    @property
    def creator_type(self) -> str:
        """Get the creator type.

        Returns:
            Creator type

        Example:
            >>> ctype = creator.creator_type
        """
        return self._creator_type

    @property
    def contact(self) -> Dict[str, Any]:
        """Get the contact information.

        Returns:
            Contact information

        Example:
            >>> contact = creator.contact
        """
        return self._contact.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the creator metadata.

        Returns:
            Creator metadata

        Example:
            >>> metadata = creator.metadata
        """
        return self._metadata.copy()

    def set_contact(self, contact: Dict[str, Any]) -> None:
        """Set the contact information.

        Args:
            contact: Contact information

        Example:
            >>> creator.set_contact({"email": "john@example.com"})
        """
        self._contact = contact

    def add_contact_info(self, key: str, value: Any) -> None:
        """Add contact information.

        Args:
            key: Contact key
            value: Contact value

        Example:
            >>> creator.add_contact_info("email", "john@example.com")
        """
        self._contact[key] = value

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the creator.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> creator.add_metadata("affiliation", "University")
        """
        self._metadata[key] = value

    def validate(self) -> ValidationResult:
        """Validate the creator.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = creator.validate()
        """
        errors = []

        if not self._id:
            errors.append("Creator ID cannot be empty")

        if not self._name:
            errors.append("Creator name cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Creator definition

        Example:
            >>> data = creator.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "creator_type": self._creator_type,
            "contact": self._contact,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(creator)
        """
        return f"Creator(id={self._id}, name={self._name}, type={self._creator_type})"


class CreatorRegistry:
    """Registry for creators.

    This class provides creator registry functionality.

    Attributes:
        _creators: Registered creators

    Example:
        >>> registry = CreatorRegistry()
        >>> registry.register(Creator("creator_001", "John Doe"))
    """

    def __init__(self) -> None:
        """Initialize a CreatorRegistry.

        Example:
            >>> registry = CreatorRegistry()
        """
        self._creators: Dict[CreatorID, Creator] = {}

    def register(self, creator: Creator) -> None:
        """Register a creator.

        Args:
            creator: Creator to register

        Example:
            >>> registry.register(Creator("creator_001", "John Doe"))
        """
        self._creators[creator.id] = creator

    def unregister(self, creator_id: CreatorID) -> bool:
        """Unregister a creator.

        Args:
            creator_id: Creator ID

        Returns:
            True if unregistered

        Example:
            >>> unregistered = registry.unregister("creator_001")
        """
        if creator_id in self._creators:
            del self._creators[creator_id]
            return True
        return False

    def get(self, creator_id: CreatorID) -> Optional[Creator]:
        """Get a creator by ID.

        Args:
            creator_id: Creator ID

        Returns:
            Creator or None

        Example:
            >>> creator = registry.get("creator_001")
        """
        return self._creators.get(creator_id)

    def get_by_name(self, name: str) -> Optional[Creator]:
        """Get a creator by name.

        Args:
            name: Creator name

        Returns:
            Creator or None

        Example:
            >>> creator = registry.get_by_name("John Doe")
        """
        for creator in self._creators.values():
            if creator.name == name:
                return creator
        return None

    def get_by_type(self, creator_type: str) -> List[Creator]:
        """Get creators by type.

        Args:
            creator_type: Creator type

        Returns:
            List of creators

        Example:
            >>> creators = registry.get_by_type("user")
        """
        return [creator for creator in self._creators.values() if creator.creator_type == creator_type]

    def list_all(self) -> List[Creator]:
        """List all registered creators.

        Returns:
            List of creators

        Example:
            >>> creators = registry.list_all()
        """
        return list(self._creators.values())

    def count(self) -> int:
        """Get the number of registered creators.

        Returns:
            Number of creators

        Example:
            >>> count = registry.count()
        """
        return len(self._creators)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Registry state

        Example:
            >>> data = registry.to_dict()
        """
        return {
            "creators": [creator.to_dict() for creator in self._creators.values()],
            "count": len(self._creators),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(registry)
        """
        return f"CreatorRegistry(creators={len(self._creators)})"


# Export
__all__ = [
    "Creator",
    "CreatorRegistry",
]
