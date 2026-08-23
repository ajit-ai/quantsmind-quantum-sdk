"""
Foundation Package Enumerations

This module defines all enumeration types used throughout the Foundation package.
Enums provide type-safe constants for categorical values.

Purpose
-------
Provide type-safe enumeration types for the Foundation package.

Scientific Meaning
------------------
Enumerations represent categorical values in scientific computing, ensuring
type safety and preventing invalid values.

Responsibilities
----------------
- Define lifecycle stages
- Define constraint severities
- Define relationship types
- Define event types
- Define observation qualities
- Define serialization formats
- Ensure type safety for categorical values

Dependencies
------------
enum (standard library)
typing (standard library)

Future Extensions
-----------------
- Enum localization
- Enum validation
- Enum serialization
- Custom enum values
"""

from __future__ import annotations

from enum import Enum, auto


class LifecycleStage(Enum):
    """Enumeration of entity lifecycle stages.

    Represents the different stages an entity can go through during its lifetime.
    Lifecycle stages enforce valid state transitions and ensure proper entity management.

    Attributes:
        CREATED: Entity has been created but not initialized
        INITIALIZED: Entity has been initialized with initial state
        VALIDATED: Entity has passed validation
        ACTIVATED: Entity is active and can participate in interactions
        SUSPENDED: Entity is temporarily suspended
        DEACTIVATED: Entity is inactive but not destroyed
        ARCHIVED: Entity is archived for long-term storage
        DESTROYED: Entity has been destroyed and resources cleaned up

    Example:
        >>> stage = LifecycleStage.ACTIVATED
        >>> if stage == LifecycleStage.ACTIVATED:
        ...     print("Entity is active")
    """

    CREATED = auto()
    INITIALIZED = auto()
    VALIDATED = auto()
    ACTIVATED = auto()
    SUSPENDED = auto()
    DEACTIVATED = auto()
    ARCHIVED = auto()
    DESTROYED = auto()

    def can_transition_to(self, target: LifecycleStage) -> bool:
        """Check if transition to target stage is valid.

        Args:
            target: Target lifecycle stage

        Returns:
            True if transition is valid, False otherwise
        """
        valid_transitions = {
            LifecycleStage.CREATED: {
                LifecycleStage.INITIALIZED,
                LifecycleStage.DESTROYED,
            },
            LifecycleStage.INITIALIZED: {
                LifecycleStage.VALIDATED,
                LifecycleStage.DESTROYED,
            },
            LifecycleStage.VALIDATED: {
                LifecycleStage.ACTIVATED,
                LifecycleStage.DESTROYED,
            },
            LifecycleStage.ACTIVATED: {
                LifecycleStage.SUSPENDED,
                LifecycleStage.DEACTIVATED,
                LifecycleStage.ARCHIVED,
            },
            LifecycleStage.SUSPENDED: {
                LifecycleStage.ACTIVATED,
                LifecycleStage.DEACTIVATED,
            },
            LifecycleStage.DEACTIVATED: {
                LifecycleStage.ACTIVATED,
                LifecycleStage.ARCHIVED,
                LifecycleStage.DESTROYED,
            },
            LifecycleStage.ARCHIVED: {
                LifecycleStage.ACTIVATED,
                LifecycleStage.DESTROYED,
            },
            LifecycleStage.DESTROYED: set(),
        }
        return target in valid_transitions.get(self, set())

    def is_terminal(self) -> bool:
        """Check if this is a terminal stage.

        Returns:
            True if terminal, False otherwise
        """
        return self == LifecycleStage.DESTROYED

    def is_active(self) -> bool:
        """Check if this is an active stage.

        Returns:
            True if active, False otherwise
        """
        return self in {
            LifecycleStage.ACTIVATED,
            LifecycleStage.SUSPENDED,
        }


class ConstraintSeverity(Enum):
    """Enumeration of constraint violation severity levels.

    Represents the severity of constraint violations, allowing for
    differentiated error handling and reporting.

    Attributes:
        ERROR: Critical violation that must be resolved
        WARNING: Non-critical violation that should be addressed
        INFO: Informational violation for logging purposes

    Example:
        >>> severity = ConstraintSeverity.ERROR
        >>> if severity == ConstraintSeverity.ERROR:
        ...     print("Critical violation")
    """

    ERROR = auto()
    WARNING = auto()
    INFO = auto()

    def is_blocking(self) -> bool:
        """Check if this severity blocks operations.

        Returns:
            True if blocking, False otherwise
        """
        return self == ConstraintSeverity.ERROR


class RelationshipType(Enum):
    """Enumeration of relationship types between entities.

    Represents the different types of relationships that can exist
    between entities in a system.

    Attributes:
        DIRECTED: Directed relationship (has source and target)
        UNDIRECTED: Undirected relationship (no direction)
        WEIGHTED: Weighted relationship (has weight value)
        PARENT_CHILD: Parent-child hierarchical relationship
        PEER: Peer relationship between equals
        DEPENDENCY: Dependency relationship
        ASSOCIATION: General association

    Example:
        >>> rel_type = RelationshipType.DIRECTED
        >>> if rel_type == RelationshipType.DIRECTED:
        ...     print("Directed relationship")
    """

    DIRECTED = auto()
    UNDIRECTED = auto()
    WEIGHTED = auto()
    PARENT_CHILD = auto()
    PEER = auto()
    DEPENDENCY = auto()
    ASSOCIATION = auto()

    def has_direction(self) -> bool:
        """Check if relationship type has direction.

        Returns:
            True if has direction, False otherwise
        """
        return self in {
            RelationshipType.DIRECTED,
            RelationshipType.PARENT_CHILD,
            RelationshipType.DEPENDENCY,
        }

    def has_weight(self) -> bool:
        """Check if relationship type has weight.

        Returns:
            True if has weight, False otherwise
        """
        return self == RelationshipType.WEIGHTED


class EventType(Enum):
    """Enumeration of event types in the system.

    Represents the different types of events that can be emitted
    by entities and systems.

    Attributes:
        ENTITY_CREATED: Entity has been created
        ENTITY_INITIALIZED: Entity has been initialized
        ENTITY_ACTIVATED: Entity has been activated
        ENTITY_DEACTIVATED: Entity has been deactivated
        ENTITY_SUSPENDED: Entity has been suspended
        ENTITY_DESTROYED: Entity has been destroyed
        STATE_CHANGED: Entity state has changed
        PROPERTY_ADDED: Property has been added to entity
        PROPERTY_REMOVED: Property has been removed from entity
        RELATIONSHIP_ADDED: Relationship has been added to entity
        RELATIONSHIP_REMOVED: Relationship has been removed from entity
        CONSTRAINT_ADDED: Constraint has been added to entity
        CONSTRAINT_REMOVED: Constraint has been removed from entity
        CONSTRAINT_VIOLATED: Constraint has been violated
        VALIDATION_FAILED: Validation has failed
        SYSTEM_CREATED: System has been created
        ENTITY_ADDED: Entity has been added to system
        ENTITY_REMOVED: Entity has been removed from system
        SYSTEM_VALIDATED: System has been validated
        SYSTEM_ACTIVATED: System has been activated
        SYSTEM_DESTROYED: System has been destroyed
        INTERACTION_CREATED: Interaction has been created
        INTERACTION_STARTED: Interaction has started
        INTERACTION_COMPLETED: Interaction has completed
        INTERACTION_FAILED: Interaction has failed
        LIFECYCLE_TRANSITION: Lifecycle transition has occurred
        STAGE_CHANGED: Lifecycle stage has changed
        OBSERVATION_CREATED: Observation has been created
        OBSERVATION_RECORDED: Observation has been recorded
        OBSERVATION_QUALITY_CHANGED: Observation quality has changed

    Example:
        >>> event_type = EventType.ENTITY_CREATED
        >>> if event_type == EventType.ENTITY_CREATED:
        ...     print("Entity created event")
    """

    # Entity events
    ENTITY_CREATED = auto()
    ENTITY_INITIALIZED = auto()
    ENTITY_ACTIVATED = auto()
    ENTITY_DEACTIVATED = auto()
    ENTITY_SUSPENDED = auto()
    ENTITY_DESTROYED = auto()
    STATE_CHANGED = auto()
    PROPERTY_ADDED = auto()
    PROPERTY_REMOVED = auto()
    RELATIONSHIP_ADDED = auto()
    RELATIONSHIP_REMOVED = auto()
    CONSTRAINT_ADDED = auto()
    CONSTRAINT_REMOVED = auto()
    CONSTRAINT_VIOLATED = auto()
    VALIDATION_FAILED = auto()

    # System events
    SYSTEM_CREATED = auto()
    ENTITY_ADDED = auto()
    ENTITY_REMOVED = auto()
    SYSTEM_VALIDATED = auto()
    SYSTEM_ACTIVATED = auto()
    SYSTEM_DESTROYED = auto()

    # Interaction events
    INTERACTION_CREATED = auto()
    INTERACTION_STARTED = auto()
    INTERACTION_COMPLETED = auto()
    INTERACTION_FAILED = auto()

    # Lifecycle events
    LIFECYCLE_TRANSITION = auto()
    STAGE_CHANGED = auto()

    # Observation events
    OBSERVATION_CREATED = auto()
    OBSERVATION_RECORDED = auto()
    OBSERVATION_QUALITY_CHANGED = auto()

    def is_entity_event(self) -> bool:
        """Check if this is an entity event.

        Returns:
            True if entity event, False otherwise
        """
        return self in {
            EventType.ENTITY_CREATED,
            EventType.ENTITY_INITIALIZED,
            EventType.ENTITY_ACTIVATED,
            EventType.ENTITY_DEACTIVATED,
            EventType.ENTITY_SUSPENDED,
            EventType.ENTITY_DESTROYED,
            EventType.STATE_CHANGED,
            EventType.PROPERTY_ADDED,
            EventType.PROPERTY_REMOVED,
            EventType.RELATIONSHIP_ADDED,
            EventType.RELATIONSHIP_REMOVED,
            EventType.CONSTRAINT_ADDED,
            EventType.CONSTRAINT_REMOVED,
            EventType.CONSTRAINT_VIOLATED,
            EventType.VALIDATION_FAILED,
        }

    def is_system_event(self) -> bool:
        """Check if this is a system event.

        Returns:
            True if system event, False otherwise
        """
        return self in {
            EventType.SYSTEM_CREATED,
            EventType.ENTITY_ADDED,
            EventType.ENTITY_REMOVED,
            EventType.SYSTEM_VALIDATED,
            EventType.SYSTEM_ACTIVATED,
            EventType.SYSTEM_DESTROYED,
        }


class ObservationQuality(Enum):
    """Enumeration of observation quality levels.

    Represents the quality or confidence level of observations.

    Attributes:
        HIGH: High quality observation with high confidence
        MEDIUM: Medium quality observation with moderate confidence
        LOW: Low quality observation with low confidence
        UNKNOWN: Unknown quality observation

    Example:
        >>> quality = ObservationQuality.HIGH
        >>> if quality == ObservationQuality.HIGH:
        ...     print("High quality observation")
    """

    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()
    UNKNOWN = auto()

    def confidence_threshold(self) -> float:
        """Get confidence threshold for quality level.

        Returns:
            Confidence threshold value (0.0 to 1.0)
        """
        thresholds = {
            ObservationQuality.HIGH: 0.8,
            ObservationQuality.MEDIUM: 0.5,
            ObservationQuality.LOW: 0.2,
            ObservationQuality.UNKNOWN: 0.0,
        }
        return thresholds[self]


class KnowledgeType(Enum):
    """Enumeration of knowledge types.

    Represents the different types of knowledge that can be derived
    from observations.

    Attributes:
        PATTERN: Recognized pattern in data
        MODEL: Learned model from data
        RULE: Derived rule from data
        FACT: Established fact from data
        HEURISTIC: Heuristic knowledge

    Example:
        >>> knowledge_type = KnowledgeType.PATTERN
        >>> if knowledge_type == KnowledgeType.PATTERN:
        ...     print("Pattern knowledge")
    """

    PATTERN = auto()
    MODEL = auto()
    RULE = auto()
    FACT = auto()
    HEURISTIC = auto()


class TransformationType(Enum):
    """Enumeration of transformation types.

    Represents the different types of transformations that can be
    applied to states.

    Attributes:
        LINEAR: Linear transformation
        NONLINEAR: Nonlinear transformation
        STOCHASTIC: Stochastic transformation
        CUSTOM: Custom transformation

    Example:
        >>> trans_type = TransformationType.LINEAR
        >>> if trans_type == TransformationType.LINEAR:
        ...     print("Linear transformation")
    """

    LINEAR = auto()
    NONLINEAR = auto()
    STOCHASTIC = auto()
    CUSTOM = auto()


class SpaceType(Enum):
    """Enumeration of space types.

    Represents the different types of mathematical spaces.

    Attributes:
        EUCLIDEAN: Euclidean space
        HILBERT: Hilbert space
        CONFIGURATION: Configuration space
        TOPOLOGICAL: Topological space
        CUSTOM: Custom space

    Example:
        >>> space_type = SpaceType.EUCLIDEAN
        >>> if space_type == SpaceType.EUCLIDEAN:
        ...     print("Euclidean space")
    """

    EUCLIDEAN = auto()
    HILBERT = auto()
    CONFIGURATION = auto()
    TOPOLOGICAL = auto()
    CUSTOM = auto()


class TimeType(Enum):
    """Enumeration of time types.

    Represents the different types of time representations.

    Attributes:
        CONTINUOUS: Continuous time
        DISCRETE: Discrete time
        RELATIVISTIC: Relativistic time
        CUSTOM: Custom time

    Example:
        >>> time_type = TimeType.CONTINUOUS
        >>> if time_type == TimeType.CONTINUOUS:
        ...     print("Continuous time")
    """

    CONTINUOUS = auto()
    DISCRETE = auto()
    RELATIVISTIC = auto()
    CUSTOM = auto()


class SerializationFormat(Enum):
    """Enumeration of serialization formats.

    Represents the different formats supported for serialization.

    Attributes:
        JSON: JSON format
        YAML: YAML format
        TOML: TOML format
        MSGPACK: MessagePack format
        BINARY: Binary format
        PROTOBUF: Protocol Buffers format

    Example:
        >>> format = SerializationFormat.JSON
        >>> if format == SerializationFormat.JSON:
        ...     print("JSON format")
    """

    JSON = auto()
    YAML = auto()
    TOML = auto()
    MSGPACK = auto()
    BINARY = auto()
    PROTOBUF = auto()

    def is_text_based(self) -> bool:
        """Check if format is text-based.

        Returns:
            True if text-based, False otherwise
        """
        return self in {
            SerializationFormat.JSON,
            SerializationFormat.YAML,
            SerializationFormat.TOML,
        }

    def is_binary(self) -> bool:
        """Check if format is binary.

        Returns:
            True if binary, False otherwise
        """
        return self in {
            SerializationFormat.MSGPACK,
            SerializationFormat.BINARY,
            SerializationFormat.PROTOBUF,
        }


class ConstraintType(Enum):
    """Enumeration of constraint types.

    Represents the different types of constraints.

    Attributes:
        EQUALITY: Equality constraint
        INEQUALITY: Inequality constraint
        RANGE: Range constraint
        LOGICAL: Logical constraint
        CUSTOM: Custom constraint

    Example:
        >>> constraint_type = ConstraintType.EQUALITY
        >>> if constraint_type == ConstraintType.EQUALITY:
        ...     print("Equality constraint")
    """

    EQUALITY = auto()
    INEQUALITY = auto()
    RANGE = auto()
    LOGICAL = auto()
    CUSTOM = auto()


# Export all enums
__all__ = [
    "LifecycleStage",
    "ConstraintSeverity",
    "RelationshipType",
    "EventType",
    "ObservationQuality",
    "KnowledgeType",
    "TransformationType",
    "SpaceType",
    "TimeType",
    "SerializationFormat",
    "ConstraintType",
]
