"""
Foundation Package Protocol Definitions

This module defines structural typing protocols for the Foundation package.
Protocols provide duck-typing contracts for flexible implementation and
runtime type checking.

Purpose
-------
Define structural typing protocols for the Foundation package.

Scientific Meaning
------------------
Protocols represent behavioral contracts that objects must satisfy to participate
in the scientific computing framework, enabling flexible implementation patterns.

Responsibilities
----------------
- Define core protocols
- Enable protocol composition
- Support protocol validation
- Provide protocol documentation
- Enable runtime type checking

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.interfaces (abstract interfaces)

Future Extensions
-----------------
- Protocol composition patterns
- Protocol optimization
- Runtime protocol validation
- Protocol versioning
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any, Protocol, runtime_checkable

from quantsmind.foundation.types import (
    AttributeValue,
    ComparisonResult,
    ConstraintResult,
    EntityID,
    MetadataDict,
    SerializedData,
    ValidationResult,
)


@runtime_checkable
class IdentifiableProtocol(Protocol):
    """Protocol for objects with unique identity.

    This protocol provides a structural typing contract for objects that can be
    uniquely identified. Unlike the abstract interface, this protocol enables
    duck-typing and runtime checking.

    Scientific Meaning
    ------------------
    Enables flexible identification patterns where objects from different
    hierarchies can be treated uniformly if they provide identity.

    Methods
    -------
    get_id(): Get unique identifier
    """

    def get_id(self) -> EntityID:
        """Get the unique identifier.

        Returns:
            Unique identifier as string
        """
        ...

    @property
    def id(self) -> EntityID:
        """Get the unique identifier property.

        Returns:
            Unique identifier as string
        """
        ...


@runtime_checkable
class ObservableProtocol(Protocol):
    """Protocol for objects that can emit events.

    This protocol provides a structural typing contract for the observer pattern,
    enabling flexible event-driven architectures.

    Scientific Meaning
    ------------------
    Enables flexible event emission patterns where objects from different
    hierarchies can emit events uniformly.

    Methods
    -------
    add_observer(): Add event observer
    remove_observer(): Remove event observer
    emit_event(): Emit event to observers
    """

    def add_observer(self, observer: Callable[[Any], None]) -> None:
        """Add an event observer.

        Args:
            observer: Callable that will receive events
        """
        ...

    def remove_observer(self, observer: Callable[[Any], None]) -> None:
        """Remove an event observer.

        Args:
            observer: Callable to remove from observers
        """
        ...

    def emit_event(self, event: Any) -> None:
        """Emit an event to all registered observers.

        Args:
            event: Event object to emit
        """
        ...

    @property
    def observer_count(self) -> int:
        """Get the number of registered observers.

        Returns:
            Number of observers
        """
        ...


@runtime_checkable
class SerializableProtocol(Protocol):
    """Protocol for objects that can be serialized.

    This protocol provides a structural typing contract for serialization,
    enabling flexible persistence and data interchange patterns.

    Scientific Meaning
    ------------------
    Enables flexible serialization patterns where objects from different
    hierarchies can be serialized uniformly.

    Methods
    -------
    serialize(): Serialize to bytes
    deserialize(): Deserialize from bytes (class method)
    """

    def serialize(self, format: str = "json") -> SerializedData:
        """Serialize the object to bytes.

        Args:
            format: Serialization format

        Returns:
            Serialized data as bytes
        """
        ...

    @classmethod
    def deserialize(cls, data: SerializedData, format: str = "json") -> SerializableProtocol:
        """Deserialize the object from bytes.

        Args:
            data: Serialized data
            format: Serialization format

        Returns:
            Deserialized object
        """
        ...


@runtime_checkable
class ValidatableProtocol(Protocol):
    """Protocol for objects that can be validated.

    This protocol provides a structural typing contract for validation,
    enabling flexible validation patterns.

    Scientific Meaning
    ------------------
    Enables flexible validation patterns where objects from different
    hierarchies can be validated uniformly.

    Methods
    -------
    validate(): Validate the object
    """

    def validate(self) -> ValidationResult:
        """Validate the object.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        ...

    def is_valid(self) -> bool:
        """Check if the object is valid.

        Returns:
            True if valid, False otherwise
        """
        ...

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages
        """
        ...


@runtime_checkable
class CloneableProtocol(Protocol):
    """Protocol for objects that can be cloned.

    This protocol provides a structural typing contract for cloning,
    enabling flexible duplication patterns.

    Scientific Meaning
    ------------------
    Enables flexible cloning patterns where objects from different
    hierarchies can be cloned uniformly.

    Methods
    -------
    clone(): Clone the object
    """

    def clone(self, deep: bool = True) -> CloneableProtocol:
        """Clone the object.

        Args:
            deep: Whether to perform deep copy

        Returns:
            Cloned object
        """
        ...

    def is_cloneable(self) -> bool:
        """Check if the object is cloneable.

        Returns:
            True if cloneable, False otherwise
        """
        ...


@runtime_checkable
class ComparableProtocol(Protocol):
    """Protocol for objects that can be compared.

    This protocol provides a structural typing contract for comparison,
    enabling flexible comparison patterns.

    Scientific Meaning
    ------------------
    Enables flexible comparison patterns where objects from different
    hierarchies can be compared uniformly.

    Methods
    -------
    compare(): Compare with another object
    equals(): Check equality
    """

    def compare(self, other: Any) -> ComparisonResult:
        """Compare with another object.

        Args:
            other: Object to compare with

        Returns:
            Tuple of (are_equal, similarity_score, differences_dict)
        """
        ...

    def equals(self, other: Any) -> bool:
        """Check equality with another object.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise
        """
        ...


@runtime_checkable
class TimestampedProtocol(Protocol):
    """Protocol for objects with temporal metadata.

    This protocol provides a structural typing contract for temporal tracking,
    enabling flexible timestamp patterns.

    Scientific Meaning
    ------------------
    Enables flexible timestamp patterns where objects from different
    hierarchies can provide temporal information uniformly.

    Methods
    -------
    get_timestamp(): Get the timestamp
    """

    def get_timestamp(self) -> datetime:
        """Get the timestamp.

        Returns:
            Timestamp as datetime
        """
        ...

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp property.

        Returns:
            Timestamp as datetime
        """
        ...


@runtime_checkable
class ConstrainableProtocol(Protocol):
    """Protocol for objects that can have constraints.

    This protocol provides a structural typing contract for constraint management,
    enabling flexible constraint patterns.

    Scientific Meaning
    ------------------
    Enables flexible constraint patterns where objects from different
    hierarchies can manage constraints uniformly.

    Methods
    -------
    add_constraint(): Add a constraint
    remove_constraint(): Remove a constraint
    evaluate_constraints(): Evaluate all constraints
    """

    def add_constraint(self, constraint: Any) -> None:
        """Add a constraint.

        Args:
            constraint: Constraint to add
        """
        ...

    def remove_constraint(self, constraint_id: str) -> None:
        """Remove a constraint.

        Args:
            constraint_id: ID of constraint to remove
        """
        ...

    def evaluate_constraints(self, context: dict[str, Any]) -> list[ConstraintResult]:
        """Evaluate all constraints.

        Args:
            context: Evaluation context

        Returns:
            List of constraint evaluation results
        """
        ...


@runtime_checkable
class DescribableProtocol(Protocol):
    """Protocol for objects that can describe themselves.

    This protocol provides a structural typing contract for self-description,
    enabling flexible introspection patterns.

    Scientific Meaning
    ------------------
    Enables flexible description patterns where objects from different
    hierarchies can describe themselves uniformly.

    Methods
    -------
    describe(): Get structured description
    """

    def describe(self) -> dict[str, Any]:
        """Get structured description.

        Returns:
            Dictionary containing structured description
        """
        ...


@runtime_checkable
class VersionedProtocol(Protocol):
    """Protocol for objects with version tracking.

    This protocol provides a structural typing contract for version management,
    enabling flexible versioning patterns.

    Scientific Meaning
    ------------------
    Enables flexible versioning patterns where objects from different
    hierarchies can track versions uniformly.

    Methods
    -------
    get_version(): Get current version
    increment_version(): Increment version
    """

    def get_version(self) -> int:
        """Get current version.

        Returns:
            Version number
        """
        ...

    def increment_version(self) -> None:
        """Increment version."""
        ...

    @property
    def version(self) -> int:
        """Get version property.

        Returns:
            Version number
        """
        ...


@runtime_checkable
class MetadataAwareProtocol(Protocol):
    """Protocol for objects with metadata.

    This protocol provides a structural typing contract for metadata management,
    enabling flexible metadata patterns.

    Scientific Meaning
    ------------------
    Enables flexible metadata patterns where objects from different
    hierarchies can manage metadata uniformly.

    Methods
    -------
    get_metadata(): Get metadata dictionary
    set_metadata(): Set metadata dictionary
    """

    def get_metadata(self) -> MetadataDict:
        """Get metadata dictionary.

        Returns:
            Metadata dictionary
        """
        ...

    def set_metadata(self, metadata: MetadataDict) -> None:
        """Set metadata dictionary.

        Args:
            metadata: New metadata dictionary
        """
        ...


@runtime_checkable
class PropertyAwareProtocol(Protocol):
    """Protocol for objects with properties.

    This protocol provides a structural typing contract for property management,
    enabling flexible property patterns.

    Scientific Meaning
    ------------------
    Enables flexible property patterns where objects from different
    hierarchies can manage properties uniformly.

    Methods
    -------
    get_property(): Get a property
    set_property(): Set a property
    has_property(): Check if property exists
    list_properties(): List all properties
    """

    def get_property(self, name: str) -> Any:
        """Get a property by name.

        Args:
            name: Property name

        Returns:
            Property value
        """
        ...

    def set_property(self, name: str, value: AttributeValue) -> None:
        """Set a property.

        Args:
            name: Property name
            value: Property value
        """
        ...

    def has_property(self, name: str) -> bool:
        """Check if property exists.

        Args:
            name: Property name

        Returns:
            True if property exists, False otherwise
        """
        ...

    def list_properties(self) -> list[str]:
        """List all property names.

        Returns:
            List of property names
        """
        ...


@runtime_checkable
class StatefulProtocol(Protocol):
    """Protocol for objects with state.

    This protocol provides a structural typing contract for state management,
    enabling flexible state patterns.

    Scientific Meaning
    ------------------
    Enables flexible state patterns where objects from different
    hierarchies can manage state uniformly.

    Methods
    -------
    get_state(): Get current state
    set_state(): Set current state
    update_state(): Update state with transformation
    """

    def get_state(self) -> Any:
        """Get current state.

        Returns:
            Current state
        """
        ...

    def set_state(self, state: Any) -> None:
        """Set current state.

        Args:
            state: New state
        """
        ...

    def update_state(self, transformation: Any) -> Any:
        """Update state with transformation.

        Args:
            transformation: Transformation to apply

        Returns:
            New state
        """
        ...


@runtime_checkable
class LifecycleAwareProtocol(Protocol):
    """Protocol for objects with lifecycle management.

    This protocol provides a structural typing contract for lifecycle management,
    enabling flexible lifecycle patterns.

    Scientific Meaning
    ------------------
    Enables flexible lifecycle patterns where objects from different
    hierarchies can manage lifecycle uniformly.

    Methods
    -------
    get_lifecycle_stage(): Get current lifecycle stage
    transition_to(): Transition to new lifecycle stage
    """

    def get_lifecycle_stage(self) -> str:
        """Get current lifecycle stage.

        Returns:
            Lifecycle stage as string
        """
        ...

    def transition_to(self, stage: str) -> None:
        """Transition to new lifecycle stage.

        Args:
            stage: Target lifecycle stage
        """
        ...


@runtime_checkable
class RelationshipAwareProtocol(Protocol):
    """Protocol for objects with relationships.

    This protocol provides a structural typing contract for relationship management,
    enabling flexible relationship patterns.

    Scientific Meaning
    ------------------
    Enables flexible relationship patterns where objects from different
    hierarchies can manage relationships uniformly.

    Methods
    -------
    add_relationship(): Add a relationship
    remove_relationship(): Remove a relationship
    get_relationships(): Get relationships
    """

    def add_relationship(self, relationship: Any) -> None:
        """Add a relationship.

        Args:
            relationship: Relationship to add
        """
        ...

    def remove_relationship(self, relationship_id: str) -> None:
        """Remove a relationship.

        Args:
            relationship_id: ID of relationship to remove
        """
        ...

    def get_relationships(self, relationship_type: str | None = None) -> list[Any]:
        """Get relationships.

        Args:
            relationship_type: Optional relationship type filter

        Returns:
            List of relationships
        """
        ...


# Export all protocols
__all__ = [
    "IdentifiableProtocol",
    "ObservableProtocol",
    "SerializableProtocol",
    "ValidatableProtocol",
    "CloneableProtocol",
    "ComparableProtocol",
    "TimestampedProtocol",
    "ConstrainableProtocol",
    "DescribableProtocol",
    "VersionedProtocol",
    "MetadataAwareProtocol",
    "PropertyAwareProtocol",
    "StatefulProtocol",
    "LifecycleAwareProtocol",
    "RelationshipAwareProtocol",
]
