"""
Identity Module

This module provides unique identification for entities within the QuantsMind SDK.
Identity is fundamental for tracking, referencing, and managing entities across
space and time.

Purpose
-------
Provide robust unique identification for entities in the Foundation package.

Scientific Meaning
------------------
Identity represents the unique identifier for particles, atoms, molecules, cells,
or any other scientific entity, enabling unambiguous reference across time and space.

Responsibilities
----------------
- Generate unique identifiers
- Support identity comparison
- Enable identity serialization
- Handle identity validation
- Support identity namespaces

Dependencies
------------
uuid (standard library)
typing (standard library)
logging (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.constants (constant values)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.interfaces (abstract interfaces)

Future Extensions
-----------------
- Identity namespaces and scopes
- Identity migration and remapping
- Distributed identity resolution
- Identity cryptography
- Identity versioning
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from quantsmind.foundation.constants import (
    ERROR_INVALID_IDENTITY,
    MAX_NAME_LENGTH,
    METADATA_CREATED_AT_KEY,
    METADATA_SOURCE_KEY,
)
from quantsmind.foundation.enums import SerializationFormat
from quantsmind.foundation.exceptions import (
    InvalidIdentityError,
)
from quantsmind.foundation.interfaces import (
    Comparable,
    Identifiable,
    Serializable,
    Validatable,
)
from quantsmind.foundation.types import (
    ComparisonResult,
    EntityID,
    MetadataDict,
    SerializedData,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class Identity(Identifiable, Comparable, Serializable, Validatable):
    """Concrete implementation of unique identity for entities.

    This class provides a robust identity mechanism using UUIDs, with support
    for namespaces, metadata, and validation.

    Scientific Meaning
    ------------------
    In scientific computing, identity allows us to uniquely reference particles,
    atoms, molecules, cells, or any other scientific entity across time and space.

    Attributes:
        _id: Unique identifier (UUID)
        _namespace: Optional namespace for scoping
        _metadata: Additional metadata associated with identity
        _created_at: Timestamp when identity was created

    Example:
        >>> identity = Identity.create(namespace="quantum")
        >>> print(f"ID: {identity.id}")
        >>> print(f"Namespace: {identity.namespace}")
    """

    def __init__(
        self,
        identity_id: EntityID | None = None,
        namespace: str | None = None,
        metadata: MetadataDict | None = None,
    ) -> None:
        """Initialize an Identity.

        Args:
            identity_id: Optional custom identity ID (UUID string). If not provided,
                        a new UUID will be generated.
            namespace: Optional namespace for scoping the identity
            metadata: Optional metadata dictionary

        Raises:
            InvalidIdentityError: If identity_id is invalid
            ValueError: If namespace exceeds maximum length

        Example:
            >>> identity = Identity(identity_id="custom-id", namespace="quantum")
            >>> identity = Identity()  # Auto-generates UUID
        """
        self._id: EntityID = identity_id or str(uuid.uuid4())
        self._namespace: str | None = namespace
        self._metadata: MetadataDict = metadata or {}
        self._created_at: datetime = datetime.now(UTC).replace(tzinfo=None)

        self._validate_id()
        self._validate_namespace()

        # Add creation metadata
        if METADATA_CREATED_AT_KEY not in self._metadata:
            self._metadata[METADATA_CREATED_AT_KEY] = self._created_at.isoformat()
        if namespace and METADATA_SOURCE_KEY not in self._metadata:
            self._metadata[METADATA_SOURCE_KEY] = namespace

        logger.debug(f"Created identity: {self._id} in namespace: {namespace}")

    @classmethod
    def create(
        cls,
        namespace: str | None = None,
        metadata: MetadataDict | None = None,
    ) -> Identity:
        """Create a new Identity with auto-generated UUID.

        Args:
            namespace: Optional namespace for scoping
            metadata: Optional metadata dictionary

        Returns:
            New Identity instance

        Example:
            >>> identity = Identity.create(namespace="quantum")
        """
        return cls(namespace=namespace, metadata=metadata)

    @classmethod
    def from_string(cls, identity_string: str) -> Identity:
        """Create an Identity from a string.

        Args:
            identity_string: String representation of identity

        Returns:
            New Identity instance

        Raises:
            InvalidIdentityError: If string is invalid

        Example:
            >>> identity = Identity.from_string("550e8400-e29b-41d4-a716-446655440000")
        """
        try:
            # Validate UUID format
            uuid.UUID(identity_string)
            return cls(identity_id=identity_string)
        except ValueError as e:
            raise InvalidIdentityError(
                f"Invalid identity string: {identity_string}",
                error_code=ERROR_INVALID_IDENTITY,
            ) from e

    def _validate_id(self) -> None:
        """Validate the identity ID.

        Raises:
            InvalidIdentityError: If ID is invalid
        """
        if not self._id or not isinstance(self._id, str):
            raise InvalidIdentityError(
                "Identity ID must be a non-empty string",
                error_code=ERROR_INVALID_IDENTITY,
            )

        try:
            uuid.UUID(self._id)
        except ValueError as e:
            raise InvalidIdentityError(
                f"Identity ID must be a valid UUID: {self._id}",
                error_code=ERROR_INVALID_IDENTITY,
            ) from e

    def _validate_namespace(self) -> None:
        """Validate the namespace.

        Raises:
            ValueError: If namespace exceeds maximum length
        """
        if self._namespace and len(self._namespace) > MAX_NAME_LENGTH:
            raise ValueError(
                f"Namespace exceeds maximum length of {MAX_NAME_LENGTH}"
            )

    # Identifiable interface implementation
    def get_id(self) -> EntityID:
        """Get the unique identifier.

        Returns:
            Unique identifier as string

        Example:
            >>> identity_id = identity.get_id()
        """
        return self._id

    @property
    def id(self) -> EntityID:
        """Get the unique identifier property.

        Returns:
            Unique identifier as string

        Example:
            >>> print(f"ID: {identity.id}")
        """
        return self._id

    @property
    def namespace(self) -> str | None:
        """Get the namespace.

        Returns:
            Namespace string or None

        Example:
            >>> print(f"Namespace: {identity.namespace}")
        """
        return self._namespace

    @property
    def metadata(self) -> MetadataDict:
        """Get the metadata dictionary.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {identity.metadata}")
        """
        return self._metadata.copy()

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp.

        Returns:
            Creation timestamp

        Example:
            >>> print(f"Created at: {identity.created_at}")
        """
        return self._created_at

    def set_namespace(self, namespace: str) -> None:
        """Set the namespace.

        Args:
            namespace: New namespace

        Raises:
            ValueError: If namespace exceeds maximum length

        Example:
            >>> identity.set_namespace("quantum")
        """
        self._namespace = namespace
        self._validate_namespace()
        logger.debug(f"Set namespace for identity {self._id}: {namespace}")

    def update_metadata(self, metadata: MetadataDict) -> None:
        """Update the metadata dictionary.

        Args:
            metadata: New metadata dictionary (will be merged with existing)

        Example:
            >>> identity.update_metadata({"source": "experiment"})
        """
        self._metadata.update(metadata)
        logger.debug(f"Updated metadata for identity {self._id}")

    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """Get a specific metadata value.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default

        Example:
            >>> source = identity.get_metadata_value("source", "unknown")
        """
        return self._metadata.get(key, default)

    # Comparable interface implementation
    def compare(self, other: Any) -> ComparisonResult:
        """Compare with another identity.

        Args:
            other: Object to compare with

        Returns:
            Tuple of (are_equal, similarity_score, differences_dict)

        Raises:
            TypeError: If other is not an Identity

        Example:
            >>> are_equal, similarity, differences = identity.compare(other_identity)
        """
        if not isinstance(other, Identity):
            raise TypeError(f"Cannot compare Identity with {type(other)}")

        are_equal = self._id == other._id
        similarity = 1.0 if are_equal else 0.0

        differences: dict[str, Any] = {}
        if not are_equal:
            differences["id"] = (self._id, other._id)
        if self._namespace != other._namespace:
            differences["namespace"] = (self._namespace, other._namespace)

        return (are_equal, similarity, differences)

    def equals(self, other: Any) -> bool:
        """Check equality with another identity.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> if identity.equals(other_identity):
            ...     print("Identities are equal")
        """
        if not isinstance(other, Identity):
            return False
        return self._id == other._id

    def is_less_than(self, other: Any) -> bool:
        """Check if this identity is less than another (lexicographic comparison).

        Args:
            other: Object to compare with

        Returns:
            True if less than, False otherwise

        Example:
            >>> if identity1.is_less_than(identity2):
            ...     print("identity1 < identity2")
        """
        if not isinstance(other, Identity):
            raise TypeError(f"Cannot compare Identity with {type(other)}")
        return self._id < other._id

    def is_greater_than(self, other: Any) -> bool:
        """Check if this identity is greater than another (lexicographic comparison).

        Args:
            other: Object to compare with

        Returns:
            True if greater than, False otherwise

        Example:
            >>> if identity1.is_greater_than(identity2):
            ...     print("identity1 > identity2")
        """
        if not isinstance(other, Identity):
            raise TypeError(f"Cannot compare Identity with {type(other)}")
        return self._id > other._id

    @property
    def comparison_key(self) -> EntityID:
        """Get the comparison key.

        Returns:
            Identity ID as comparison key

        Example:
            >>> key = identity.comparison_key
        """
        return self._id

    # Serializable interface implementation
    def serialize(
        self, format: SerializationFormat | str = SerializationFormat.JSON
    ) -> SerializedData:
        """Serialize the identity to bytes.

        Args:
            format: Serialization format (currently only JSON supported;
                plain ``"json"`` string accepted for backward compatibility)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = identity.serialize(format=SerializationFormat.JSON)
        """
        is_json = format is SerializationFormat.JSON or (
            isinstance(format, str) and format.lower() == "json"
        )
        if not is_json:
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        data = {
            "id": self._id,
            "namespace": self._namespace,
            "metadata": self._metadata,
            "created_at": self._created_at.isoformat(),
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(
        cls, data: SerializedData, format: SerializationFormat | str = SerializationFormat.JSON
    ) -> Identity:
        """Deserialize the identity from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only JSON supported;
                plain ``"json"`` string accepted for backward compatibility)

        Returns:
            Deserialized Identity instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidIdentityError: If data is invalid

        Example:
            >>> identity = Identity.deserialize(data, format=SerializationFormat.JSON)
        """
        is_json = format is SerializationFormat.JSON or (
            isinstance(format, str) and format.lower() == "json"
        )
        if not is_json:
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            return cls(
                identity_id=obj["id"],
                namespace=obj.get("namespace"),
                metadata=obj.get("metadata"),
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise InvalidIdentityError(
                f"Failed to deserialize identity: {e}",
                error_code=ERROR_INVALID_IDENTITY,
            ) from e

    def is_serializable(self) -> bool:
        """Check if the identity is serializable.

        Returns:
            True (identities are always serializable)

        Example:
            >>> if identity.is_serializable():
            ...     data = identity.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[SerializationFormat]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Identity.get_supported_formats()
        """
        return [SerializationFormat.JSON]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the identity.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = identity.validate()
        """
        errors: list[str] = []

        try:
            self._validate_id()
        except InvalidIdentityError as e:
            errors.append(str(e))

        try:
            self._validate_namespace()
        except ValueError as e:
            errors.append(str(e))

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = identity.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = identity.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the identity.

        Returns:
            String representation

        Example:
            >>> repr(identity)
        """
        return f"Identity(id='{self._id}', namespace='{self._namespace}')"

    def __str__(self) -> str:
        """Return string representation of the identity.

        Returns:
            String representation

        Example:
            >>> str(identity)
        """
        if self._namespace:
            return f"{self._namespace}:{self._id}"
        return self._id

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> identity1 == identity2
        """
        if not isinstance(other, Identity):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Return hash of the identity.

        Returns:
            Hash value

        Example:
            >>> hash(identity)
        """
        return hash(self._id)

    def __copy__(self) -> Identity:
        """Create a shallow copy of the identity.

        Returns:
            Shallow copy

        Example:
            >>> import copy
            >>> copied = copy.copy(identity)
        """
        return Identity(
            identity_id=self._id,
            namespace=self._namespace,
            metadata=self._metadata.copy(),
        )

    def __deepcopy__(self, memo: dict[int, Any]) -> Identity:
        """Create a deep copy of the identity.

        Args:
            memo: Memo dictionary for deepcopy

        Returns:
            Deep copy

        Example:
            >>> import copy
            >>> copied = copy.deepcopy(identity)
        """
        import copy

        return Identity(
            identity_id=self._id,
            namespace=self._namespace,
            metadata=copy.deepcopy(self._metadata, memo),
        )


# Export
__all__ = ["Identity"]
