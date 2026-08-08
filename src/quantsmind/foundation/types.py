"""
Foundation Package Type Definitions

This module defines all type aliases and type hints used throughout the Foundation package.
Type definitions provide type safety and improve code documentation.

Purpose
-------
Provide centralized type definitions for the Foundation package.

Scientific Meaning
------------------
Types represent the fundamental data structures used in scientific computing,
ensuring type safety and enabling static analysis.

Responsibilities
----------------
- Define type aliases
- Provide type hints
- Enable static type checking
- Improve code documentation
- Support IDE autocomplete

Dependencies
------------
typing (standard library)

Future Extensions
-----------------
- Generic type constraints
- Custom type validators
- Runtime type checking
- Cross-language type mapping
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)

# Basic Type Aliases
EntityID = str
SystemID = str
PropertyID = str
AttributeID = str
RelationshipID = str
ConstraintID = str
BehaviourID = str
EventID = str
ObservationID = str
KnowledgeID = str
TransformationID = str
SpaceID = str
TimeID = str
LifecycleID = str

# Value Types
ScalarValue = Union[int, float, complex]
VectorValue = List[ScalarValue]
TensorValue = List[List[ScalarValue]]
AttributeValue = Union[ScalarValue, VectorValue, TensorValue, str, bool, datetime]

# Data Structures
PropertyDict = Dict[str, "Property"]
AttributeDict = Dict[str, "Attribute"]
RelationshipDict = Dict[str, List["Relationship"]]
ConstraintList = List["Constraint"]
StateHistory = List["State"]
MetadataDict = Dict[str, Any]
EntityDict = Dict[EntityID, "Entity"]

# Function Types
ValidatorFunc = Callable[[Any], bool]
TransformerFunc = Callable[[Any], Any]
ObserverFunc = Callable[["Event"], None]
ConstraintRule = Union[str, Callable[[Dict[str, Any]], bool]]

# Result Types
ValidationResult = Tuple[bool, List[str]]
ComparisonResult = Tuple[bool, float, Dict[str, Any]]
InteractionResult = Tuple[bool, Dict[EntityID, "State"], List[str]]
BehaviourResult = Tuple[bool, Any, List[str]]
ConstraintResult = Tuple[bool, Optional[str], "ConstraintSeverity"]
KnowledgeResult = Tuple[bool, Any, List[str]]

# Serialization Types
SerializationFormat = Literal["json", "yaml", "toml", "msgpack", "binary", "protobuf"]
SerializedData = bytes
DeserializedData = Dict[str, Any]

# Time Types
Timestamp = datetime
TimeInterval = timedelta
TimeValue = Union[int, float, datetime]

# Space Types
Coordinate = List[float]
BasisVector = List[float]
SpaceDimension = int

# Lifecycle Types
LifecycleStage = Literal[
    "created",
    "initialized",
    "validated",
    "activated",
    "suspended",
    "deactivated",
    "archived",
    "destroyed",
]

# Constraint Types
ConstraintSeverity = Literal["error", "warning", "info"]
ConstraintType = Literal[
    "equality",
    "inequality",
    "range",
    "logical",
    "custom",
]

# Relationship Types
RelationshipType = Literal[
    "directed",
    "undirected",
    "weighted",
    "parent_child",
    "peer",
    "dependency",
    "association",
]

# Event Types
EventType = Literal[
    "entity_created",
    "entity_initialized",
    "entity_activated",
    "entity_deactivated",
    "entity_suspended",
    "entity_destroyed",
    "state_changed",
    "property_added",
    "property_removed",
    "relationship_added",
    "relationship_removed",
    "constraint_added",
    "constraint_removed",
    "constraint_violated",
    "validation_failed",
    "system_created",
    "entity_added",
    "entity_removed",
    "system_validated",
    "system_activated",
    "system_destroyed",
    "interaction_created",
    "interaction_started",
    "interaction_completed",
    "interaction_failed",
    "lifecycle_transition",
    "stage_changed",
    "observation_created",
    "observation_recorded",
    "observation_quality_changed",
]

# Observation Quality
ObservationQuality = Literal["high", "medium", "low", "unknown"]

# Knowledge Types
KnowledgeType = Literal["pattern", "model", "rule", "fact", "heuristic"]

# Transformation Types
TransformationType = Literal["linear", "nonlinear", "stochastic", "custom"]

# Space Types
SpaceType = Literal["euclidean", "hilbert", "configuration", "topological", "custom"]

# Time Types
TimeType = Literal["continuous", "discrete", "relativistic", "custom"]

# Generic Type Variables
T = TypeVar("T")
T_Entity = TypeVar("T_Entity", bound="Entity")
T_State = TypeVar("T_State", bound="State")
T_Event = TypeVar("T_Event", bound="Event")

# Protocol Definitions
class Identifiable(Protocol):
    """Protocol for objects that can be identified."""

    @property
    def id(self) -> str:
        """Get the unique identifier."""
        ...


class Observable(Protocol):
    """Protocol for objects that can emit events."""

    def add_observer(self, observer: ObserverFunc) -> None:
        """Add an event observer."""
        ...

    def remove_observer(self, observer: ObserverFunc) -> None:
        """Remove an event observer."""
        ...


class Serializable(Protocol):
    """Protocol for objects that can be serialized."""

    def serialize(self, format: SerializationFormat = "json") -> SerializedData:
        """Serialize the object to bytes."""
        ...

    @classmethod
    def deserialize(
        cls, data: SerializedData, format: SerializationFormat = "json"
    ) -> "Serializable":
        """Deserialize the object from bytes."""
        ...


class Validatable(Protocol):
    """Protocol for objects that can be validated."""

    def validate(self) -> ValidationResult:
        """Validate the object."""
        ...


class Cloneable(Protocol):
    """Protocol for objects that can be cloned."""

    def clone(self, deep: bool = True) -> "Cloneable":
        """Clone the object."""
        ...


class Comparable(Protocol):
    """Protocol for objects that can be compared."""

    def compare(self, other: Any) -> ComparisonResult:
        """Compare with another object."""
        ...

    def equals(self, other: Any) -> bool:
        """Check equality."""
        ...


class Timestamped(Protocol):
    """Protocol for objects with temporal metadata."""

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp."""
        ...


# Export all types
__all__ = [
    # Basic Type Aliases
    "EntityID",
    "SystemID",
    "PropertyID",
    "AttributeID",
    "RelationshipID",
    "ConstraintID",
    "BehaviourID",
    "EventID",
    "ObservationID",
    "KnowledgeID",
    "TransformationID",
    "SpaceID",
    "TimeID",
    "LifecycleID",
    # Value Types
    "ScalarValue",
    "VectorValue",
    "TensorValue",
    "AttributeValue",
    # Data Structures
    "PropertyDict",
    "AttributeDict",
    "RelationshipDict",
    "ConstraintList",
    "StateHistory",
    "MetadataDict",
    "EntityDict",
    # Function Types
    "ValidatorFunc",
    "TransformerFunc",
    "ObserverFunc",
    "ConstraintRule",
    # Result Types
    "ValidationResult",
    "ComparisonResult",
    "InteractionResult",
    "BehaviourResult",
    "ConstraintResult",
    "KnowledgeResult",
    # Serialization Types
    "SerializationFormat",
    "SerializedData",
    "DeserializedData",
    # Time Types
    "Timestamp",
    "TimeInterval",
    "TimeValue",
    # Space Types
    "Coordinate",
    "BasisVector",
    "SpaceDimension",
    # Lifecycle Types
    "LifecycleStage",
    # Constraint Types
    "ConstraintSeverity",
    "ConstraintType",
    # Relationship Types
    "RelationshipType",
    # Event Types
    "EventType",
    # Observation Quality
    "ObservationQuality",
    # Knowledge Types
    "KnowledgeType",
    # Transformation Types
    "TransformationType",
    # Space Types
    "SpaceType",
    # Time Types
    "TimeType",
    # Generic Type Variables
    "T",
    "T_Entity",
    "T_State",
    "T_Event",
    # Protocol Definitions
    "Identifiable",
    "Observable",
    "Serializable",
    "Validatable",
    "Cloneable",
    "Comparable",
    "Timestamped",
]

# Forward references for type checking
# These will be resolved when the actual classes are imported
if __name__ == "__main__":
    # Allow for runtime type checking
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from quantsmind.foundation.entity import Entity
        from quantsmind.foundation.state import State
        from quantsmind.foundation.event import Event
        from quantsmind.foundation.property import Property
        from quantsmind.foundation.attribute import Attribute
        from quantsmind.foundation.relationship import Relationship
        from quantsmind.foundation.constraint import Constraint
