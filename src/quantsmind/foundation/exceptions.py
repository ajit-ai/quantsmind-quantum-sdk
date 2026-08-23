"""
Foundation Package Exception Hierarchy

This module defines the complete exception hierarchy for the QuantsMind SDK Foundation package.
All foundation-specific exceptions inherit from FoundationError, which inherits from the base
QuantsMindError (defined in quantsmind.exceptions).

Purpose
-------
Provide structured, type-safe error handling for all foundation package operations.

Scientific Meaning
------------------
Exceptions represent violations of physical laws, mathematical constraints, or system
invariants in scientific computing scenarios.

Responsibilities
----------------
- Define hierarchical exception structure
- Provide clear error categorization
- Enable precise error handling
- Support error serialization
- Facilitate debugging and logging

Dependencies
------------
None (base exceptions will be imported from quantsmind.exceptions when available)

Future Extensions
-----------------
- Exception localization
- Exception composition patterns
- Error code standardization
- Cross-language exception mapping
"""

from __future__ import annotations

from typing import Any

from quantsmind.exceptions import QuantsMindError


# Base Foundation Exception
class FoundationError(QuantsMindError):
    """Base exception for all Foundation package errors.

    This exception serves as the root of the foundation exception hierarchy.
    All foundation-specific exceptions should inherit from this class.

    Attributes:
        message: Human-readable error message
        details: Optional dictionary with additional error context
        error_code: Optional machine-readable error code

    Example:
        >>> try:
        ...     raise FoundationError("Operation failed", details={"context": "entity_creation"})
        ... except FoundationError as e:
        ...     print(f"Error: {e.message}")
    """

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
    ) -> None:
        """Initialize a FoundationError.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
            error_code: Optional machine-readable error code
        """
        self.message = message
        self.details = details or {}
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for serialization.

        Returns:
            Dictionary representation of the exception
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
            "error_code": self.error_code,
        }


# Type-related Exceptions
class FoundationTypeError(FoundationError):
    """Raised when a value has an unexpected type in foundation operations.

    This occurs when arguments, attributes, or state components do not
    match their declared foundation types.
    """

    pass


# Entity-related Exceptions
class EntityError(FoundationError):
    """Base exception for entity-related errors.

    Raised when operations on entities fail due to invalid state,
    missing data, or constraint violations.
    """

    pass


class InvalidStateError(EntityError):
    """Raised when an entity is in an invalid state for the requested operation.

    This can occur when trying to activate an entity that hasn't been initialized,
    or when trying to modify an entity in a read-only state.
    """

    pass


class InvalidLifecycleError(EntityError):
    """Raised when an entity lifecycle transition is invalid.

    This occurs when trying to transition from one lifecycle stage to another
    that is not permitted by the lifecycle rules.
    """

    pass


class CloneError(EntityError):
    """Raised when entity cloning fails.

    This can occur when the entity or its dependencies do not support cloning,
    or when cloning would violate constraints.
    """

    pass


class DuplicatePropertyError(EntityError):
    """Raised when attempting to add a property that already exists.

    Properties must have unique names within an entity.
    """

    pass


class PropertyNotFoundError(EntityError):
    """Raised when attempting to access a non-existent property.

    This occurs when trying to get, modify, or remove a property that
    does not exist in the entity.
    """

    pass


class InvalidPropertyError(EntityError):
    """Raised when a property is invalid.

    This can occur when a property's value, type, or constraints are violated.
    """

    pass


class RelationshipError(EntityError):
    """Base exception for relationship-related errors."""

    pass


class RelationshipNotFoundError(EntityError):
    """Raised when attempting to access a non-existent relationship.

    This occurs when trying to get, modify, or remove a relationship that
    does not exist in the entity.
    """

    pass


class InvalidRelationshipError(EntityError):
    """Raised when a relationship is invalid.

    This can occur when relationship endpoints are invalid, the relationship
    type is not supported, or relationship constraints are violated.
    """

    pass


class NotEndpointError(EntityError):
    """Raised when an entity is not an endpoint of a relationship.

    This occurs when trying to add a relationship to an entity that is not
    one of the relationship's defined endpoints.
    """

    pass


class ActiveRelationshipError(EntityError):
    """Raised when trying to remove an entity that has active relationships.

    This prevents orphaning relationships and maintains referential integrity.
    """

    pass


class ConstraintError(EntityError):
    """Base exception for constraint-related errors."""

    pass


class ConstraintNotFoundError(EntityError):
    """Raised when attempting to access a non-existent constraint.

    This occurs when trying to get, modify, or remove a constraint that
    does not exist in the entity.
    """

    pass


class InvalidConstraintError(EntityError):
    """Raised when a constraint is invalid.

    This can occur when a constraint's rule is malformed, its type is not
    supported, or its configuration is invalid.
    """

    pass


class ConstraintViolationError(EntityError):
    """Raised when a constraint is violated.

    This occurs when an entity's state or properties violate one or more
    of its defined constraints.
    """

    def __init__(
        self,
        message: str,
        constraint_id: str | None = None,
        violation_details: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a ConstraintViolationError.

        Args:
            message: Human-readable error message
            constraint_id: ID of the violated constraint
            violation_details: Details about the violation
            **kwargs: Additional arguments passed to parent
        """
        self.constraint_id = constraint_id
        self.violation_details = violation_details or {}
        details = kwargs.pop("details", {})
        details.update({"constraint_id": constraint_id, "violation_details": violation_details})
        super().__init__(message, details=details, **kwargs)


class ObservationError(EntityError):
    """Raised when observation operations fail.

    This can occur when trying to observe an entity that is not observable,
    or when the observation process itself fails.
    """

    pass


class InvalidObservationError(ObservationError):
    """Raised when an observation is invalid.

    This can occur when the observation's target, quality metadata, or
    recorded value violates observation invariants.
    """

    pass


# System-related Exceptions
class SystemError(FoundationError):
    """Base exception for system-related errors.

    Raised when operations on systems fail due to invalid state,
    missing data, or constraint violations.
    """

    pass


class DuplicateEntityError(SystemError):
    """Raised when attempting to add an entity that already exists in the system.

    Entity IDs must be unique within a system.
    """

    pass


class InvalidEntityError(SystemError):
    """Raised when an entity is invalid for system operations.

    This can occur when the entity's type is not compatible with the system,
    or when the entity is in an invalid state.
    """

    pass


class EntityNotFoundError(SystemError):
    """Raised when attempting to access a non-existent entity in the system.

    This occurs when trying to get, modify, or remove an entity that
    does not exist in the system.
    """

    pass


class InvalidSystemError(SystemError):
    """Raised when a system is invalid for the requested operation.

    This can occur when the system's configuration is malformed, its
    composition violates invariants, or it is used before initialization.
    """

    pass


class SystemValidationError(SystemError):
    """Raised when system validation fails.

    This occurs when the system's state, entities, or constraints violate
    system-level invariants.
    """

    pass


# State-related Exceptions
class StateError(FoundationError):
    """Base exception for state-related errors.

    Raised when operations on states fail due to invalid data,
    incompatible types, or transition violations.
    """

    pass


class IncompatibleStateError(StateError):
    """Raised when states are incompatible for an operation.

    This can occur when trying to compare, combine, or transform states
    that have incompatible structures or types.
    """

    pass


class StateTransitionError(StateError):
    """Raised when a state transition is invalid.

    This occurs when trying to transition from one state to another
    that is not permitted by transition rules.
    """

    pass


# Interaction-related Exceptions
class InteractionError(FoundationError):
    """Base exception for interaction-related errors.

    Raised when operations on interactions fail due to invalid participants,
    parameters, or execution failures.
    """

    pass


class InvalidInteractionError(InteractionError):
    """Raised when an interaction is invalid.

    This can occur when the interaction's type is not supported, its
    parameters are invalid, or its configuration is malformed.
    """

    pass


class InteractionExecutionError(InteractionError):
    """Raised when interaction execution fails.

    This occurs when the interaction cannot be executed due to runtime errors,
    participant failures, or resource constraints.
    """

    pass


class ParticipantError(InteractionError):
    """Raised when interaction participants are invalid.

    This can occur when participants are not in the correct state,
    do not exist, or are incompatible with the interaction.
    """

    pass


# Identity-related Exceptions
class IdentityError(FoundationError):
    """Base exception for identity-related errors.

    Raised when operations on identities fail due to invalid IDs,
    duplicates, or resolution failures.
    """

    pass


class InvalidIdentityError(IdentityError):
    """Raised when an identity is invalid.

    This can occur when the ID format is incorrect, the ID is malformed,
    or the ID does not meet validation requirements.
    """

    pass


class DuplicateIdentityError(IdentityError):
    """Raised when attempting to create a duplicate identity.

    This occurs when trying to create an identity with an ID that already
    exists in the system.
    """

    pass


class IdentityNotFoundError(IdentityError):
    """Raised when an identity cannot be found.

    This occurs when trying to resolve an identity that does not exist
    in the system.
    """

    pass


# Property-related Exceptions
class PropertyError(FoundationError):
    """Base exception for property-related errors.

    Raised when operations on properties fail due to invalid values,
    types, or constraint violations.
    """

    pass


class AttributeError(FoundationError):
    """Base exception for attribute-related errors.

    Raised when operations on attributes fail due to invalid values,
    type mismatches, or conversion failures.
    """

    pass


class TypeError(AttributeError):
    """Raised when an attribute type is invalid or incompatible.

    This can occur when trying to set an attribute with an incompatible type,
    or when type conversion fails.
    """

    pass


class ConversionError(AttributeError):
    """Raised when attribute conversion fails.

    This occurs when trying to convert an attribute to a different type
    and the conversion is not possible.
    """

    pass


# Behaviour-related Exceptions
class BehaviourError(FoundationError):
    """Base exception for behaviour-related errors.

    Raised when operations on behaviours fail due to invalid parameters,
    precondition violations, or execution failures.
    """

    pass


class InvalidBehaviourError(BehaviourError):
    """Raised when a behaviour is invalid.

    This can occur when the behaviour's type is not supported, its
    parameters are invalid, or its configuration is malformed.
    """

    pass


class ExecutionError(BehaviourError):
    """Raised when behaviour execution fails.

    This occurs when the behaviour cannot be executed due to runtime errors,
    resource constraints, or unexpected conditions.
    """

    pass


class PreconditionError(BehaviourError):
    """Raised when behaviour preconditions are not satisfied.

    This occurs when trying to execute a behaviour without meeting its
    required preconditions.
    """

    pass


# Relationship-specific Exceptions (reusing base from Entity)
class CycleError(RelationshipError):
    """Raised when a relationship would create a cycle.

    This occurs in acyclic relationship graphs when trying to add a
    relationship that would create a cycle.
    """

    pass


# Constraint-specific Exceptions (reusing base from Entity)
class EvaluationError(ConstraintError):
    """Raised when constraint evaluation fails.

    This occurs when a constraint cannot be evaluated due to runtime errors,
    missing data, or evaluation context issues.
    """

    pass


class CircularDependencyError(ConstraintError):
    """Raised when constraints have circular dependencies.

    This occurs when constraints depend on each other in a cycle,
    making evaluation impossible.
    """

    pass


# Lifecycle-related Exceptions
class LifecycleError(FoundationError):
    """Base exception for lifecycle-related errors.

    Raised when operations on lifecycles fail due to invalid stages,
    invalid transitions, or lifecycle rule violations.
    """

    pass


class InvalidTransitionError(LifecycleError):
    """Raised when a lifecycle transition is invalid.

    This occurs when trying to transition from one lifecycle stage to another
    that is not permitted by lifecycle rules.
    """

    pass


class TransitionError(LifecycleError):
    """Raised when a lifecycle transition fails.

    This occurs when the transition cannot be completed due to runtime errors,
    resource constraints, or unexpected conditions.
    """

    pass


class LifecycleStageError(LifecycleError):
    """Raised when a lifecycle stage is invalid.

    This can occur when the stage does not exist, is not supported,
    or is incompatible with the entity type.
    """

    pass


# Event-related Exceptions
class EventError(FoundationError):
    """Base exception for event-related errors.

    Raised when operations on events fail due to invalid data,
    ordering violations, or processing failures.
    """

    pass


class InvalidEventError(EventError):
    """Raised when an event is invalid.

    This can occur when the event's type is not supported, its data is invalid,
    or its configuration is malformed.
    """

    pass


class EventNotFoundError(EventError):
    """Raised when an event cannot be found.

    This occurs when trying to access an event that does not exist
    in the system.
    """

    pass


class EventOrderingError(EventError):
    """Raised when event ordering is violated.

    This occurs when events are processed out of order, violating
    temporal constraints or dependencies.
    """

    pass


# Knowledge-related Exceptions
class KnowledgeError(FoundationError):
    """Base exception for knowledge-related errors.

    Raised when operations on knowledge fail due to invalid data,
    application failures, or update errors.
    """

    pass


class InvalidKnowledgeError(KnowledgeError):
    """Raised when knowledge is invalid.

    This can occur when the knowledge's type is not supported, its content
    is invalid, or its configuration is malformed.
    """

    pass


class KnowledgeApplicationError(KnowledgeError):
    """Raised when knowledge application fails.

    This occurs when trying to apply knowledge to a context and the
    application fails due to incompatibility or runtime errors.
    """

    pass


class KnowledgeUpdateError(KnowledgeError):
    """Raised when knowledge update fails.

    This occurs when trying to update knowledge and the update fails
    due to invalid data, conflicts, or runtime errors.
    """

    pass


# Transformation-related Exceptions
class TransformationError(FoundationError):
    """Base exception for transformation-related errors.

    Raised when operations on transformations fail due to invalid data,
    application failures, or parameter errors.
    """

    pass


class InvalidTransformationError(TransformationError):
    """Raised when a transformation is invalid.

    This can occur when the transformation's type is not supported, its
    parameters are invalid, or its configuration is malformed.
    """

    pass


class TransformationExecutionError(TransformationError):
    """Raised when a transformation fails during execution.

    This occurs when the transformation itself is valid but its execution
    raises an unexpected runtime error.
    """

    pass


class TransformationApplicationError(TransformationError):
    """Raised when transformation application fails.

    This occurs when trying to apply a transformation to a state and the
    application fails due to incompatibility or runtime errors.
    """

    pass


# Space-related Exceptions
class SpaceError(FoundationError):
    """Base exception for space-related errors.

    Raised when operations on spaces fail due to invalid dimensions,
    coordinate errors, or transformation failures.
    """

    pass

    pass


class InvalidSpaceError(SpaceError):
    """Raised when a space is invalid.

    This can occur when the space's dimension is invalid, its basis is malformed,
    or its configuration is incorrect.
    """

    pass


class DimensionError(SpaceError):
    """Raised when space dimension operations fail.

    This occurs when trying to perform operations on spaces with incompatible
    dimensions or invalid dimension values.
    """

    pass


class CoordinateError(SpaceError):
    """Raised when coordinate operations fail.

    This occurs when coordinates are invalid, out of bounds, or incompatible
    with the space.
    """

    pass


# Time-related Exceptions
class TimeError(FoundationError):
    """Base exception for time-related errors.

    Raised when operations on time fail due to invalid values,
    conversion failures, or reference errors.
    """

    pass


class InvalidTimeError(TimeError):
    """Raised when a time value is invalid.

    This can occur when the time value is out of range, malformed,
    or incompatible with the time type.
    """

    pass


class TimeConversionError(TimeError):
    """Raised when time conversion fails.

    This occurs when trying to convert between different time units or
    references and the conversion fails.
    """

    pass


class TimeReferenceError(TimeError):
    """Raised when time reference operations fail.

    This occurs when trying to use an invalid or missing reference time.
    """

    pass


# Validation-related Exceptions
class ValidationError(FoundationError):
    """Base exception for validation-related errors.

    Raised when validation operations fail due to invalid rules,
    data errors, or validation context issues.
    """

    pass


class ValidationRuleError(ValidationError):
    """Raised when a validation rule is invalid.

    This can occur when the rule is malformed, not supported,
    or has invalid configuration.
    """

    pass


# Serialization-related Exceptions
class SerializationError(FoundationError):
    """Base exception for serialization-related errors.

    Raised when serialization operations fail due to format errors,
    data incompatibility, or version issues.
    """

    pass


class DeserializationError(SerializationError):
    """Raised when deserialization fails.

    This occurs when trying to deserialize data and the process fails
    due to invalid data, format errors, or version incompatibility.
    """

    pass


class InvalidDataError(SerializationError):
    """Raised when data is invalid for serialization/deserialization.

    This occurs when the data structure is invalid, contains unsupported types,
    or violates format constraints.
    """

    pass


class UnsupportedFormatError(SerializationError):
    """Raised when a serialization format is not supported.

    This occurs when trying to use a format that is not implemented or
    not available in the current configuration.
    """

    def __init__(self, format_name: str, **kwargs: Any) -> None:
        """Initialize an UnsupportedFormatError.

        Args:
            format_name: Name of the unsupported format
            **kwargs: Additional arguments passed to parent
        """
        self.format_name = format_name
        message = f"Serialization format '{format_name}' is not supported"
        details = kwargs.pop("details", {})
        details.update({"format_name": format_name})
        super().__init__(message, details=details, **kwargs)


class IncompatibleVersionError(SerializationError):
    """Raised when version incompatibility is detected.

    This occurs when trying to deserialize data from a different version
    that is not compatible with the current implementation.
    """

    def __init__(
        self,
        message: str,
        data_version: str | None = None,
        current_version: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize an IncompatibleVersionError.

        Args:
            message: Human-readable error message
            data_version: Version of the data being deserialized
            current_version: Current implementation version
            **kwargs: Additional arguments passed to parent
        """
        self.data_version = data_version
        self.current_version = current_version
        details = kwargs.pop("details", {})
        details.update(
            {"data_version": data_version, "current_version": current_version}
        )
        super().__init__(message, details=details, **kwargs)


# Interface-related Exceptions
class InterfaceError(FoundationError):
    """Base exception for interface-related errors.

    Raised when interface operations fail due to implementation errors,
    method signature mismatches, or contract violations.
    """

    pass


class InterfaceNotImplementedError(InterfaceError):
    """Raised when a required interface method is not implemented.

    This occurs when a class claims to implement an interface but does not
    implement all required methods.
    """

    pass


class InterfaceMethodError(InterfaceError):
    """Raised when an interface method is implemented incorrectly.

    This occurs when a method signature does not match the interface contract,
    or when the method behavior violates the interface contract.
    """

    pass


# Factory-related Exceptions
class FactoryError(FoundationError):
    """Base exception for factory-related errors.

    Raised when factory operations fail due to configuration errors,
    creation failures, or resource constraints.
    """

    pass


class CreationError(FactoryError):
    """Raised when object creation fails.

    This occurs when a factory cannot create an object due to invalid
    parameters, missing dependencies, or runtime errors.
    """

    pass


class ConfigurationError(FactoryError):
    """Raised when factory configuration is invalid.

    This occurs when the factory's configuration is malformed, incomplete,
    or contains invalid values.
    """

    pass


# Export all exceptions
__all__ = [
    # Base
    "FoundationError",
    # Entity
    "EntityError",
    "InvalidStateError",
    "InvalidLifecycleError",
    "CloneError",
    "DuplicatePropertyError",
    "PropertyNotFoundError",
    "InvalidPropertyError",
    "RelationshipError",
    "RelationshipNotFoundError",
    "InvalidRelationshipError",
    "NotEndpointError",
    "ActiveRelationshipError",
    "ConstraintError",
    "ConstraintNotFoundError",
    "InvalidConstraintError",
    "ConstraintViolationError",
    "ObservationError",
    # System
    "SystemError",
    "DuplicateEntityError",
    "InvalidEntityError",
    "EntityNotFoundError",
    "SystemValidationError",
    # State
    "StateError",
    "IncompatibleStateError",
    "StateTransitionError",
    # Interaction
    "InteractionError",
    "InvalidInteractionError",
    "InteractionExecutionError",
    "ParticipantError",
    # Identity
    "IdentityError",
    "InvalidIdentityError",
    "DuplicateIdentityError",
    "IdentityNotFoundError",
    # Property
    "PropertyError",
    # Attribute
    "AttributeError",
    "TypeError",
    "ConversionError",
    # Behaviour
    "BehaviourError",
    "InvalidBehaviourError",
    "ExecutionError",
    "PreconditionError",
    # Relationship specific
    "CycleError",
    # Constraint specific
    "EvaluationError",
    "CircularDependencyError",
    # Lifecycle
    "LifecycleError",
    "InvalidTransitionError",
    "TransitionError",
    "LifecycleStageError",
    # Event
    "EventError",
    "InvalidEventError",
    "EventNotFoundError",
    "EventOrderingError",
    # Knowledge
    "KnowledgeError",
    "InvalidKnowledgeError",
    "KnowledgeApplicationError",
    "KnowledgeUpdateError",
    # Transformation
    "TransformationError",
    "InvalidTransformationError",
    "TransformationApplicationError",
    # Space
    "SpaceError",
    "InvalidSpaceError",
    "DimensionError",
    "CoordinateError",
    # Time
    "TimeError",
    "InvalidTimeError",
    "TimeConversionError",
    "TimeReferenceError",
    # Validation
    "ValidationError",
    "ValidationRuleError",
    # Serialization
    "SerializationError",
    "DeserializationError",
    "InvalidDataError",
    "FoundationTypeError",
    "UnsupportedFormatError",
    "IncompatibleVersionError",
    # Interface
    "InterfaceError",
    "InterfaceNotImplementedError",
    "InvalidSystemError",
    "InvalidObservationError",
    "TransformationExecutionError",
    "InterfaceMethodError",
    # Factory
    "FactoryError",
    "CreationError",
    "ConfigurationError",
]
