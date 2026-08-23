"""
Foundation Package Interface Definitions

This module defines the core abstract interfaces used throughout the Foundation package.
Interfaces provide contracts that classes must implement, ensuring consistency and
enabling polymorphism.

Purpose
-------
Define reusable abstract interfaces for the Foundation package.

Scientific Meaning
------------------
Interfaces represent fundamental capabilities that entities, systems, and other
objects must have to participate in the scientific computing framework.

Responsibilities
----------------
- Define core interfaces
- Enable interface composition
- Support interface validation
- Provide interface documentation
- Enable polymorphic behavior

Dependencies
------------
abc (standard library)
typing (standard library)
datetime (standard library)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.enums (enumeration types)

Future Extensions
-----------------
- Interface versioning
- Interface composition patterns
- Interface optimization
- Runtime interface checking
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from quantsmind.foundation.enums import SerializationFormat
from quantsmind.foundation.types import (
    ComparisonResult,
    ConstraintResult,
    EntityID,
    MetadataDict,
    SerializedData,
    ValidationResult,
)


class Identifiable(ABC):
    """Interface for objects with unique identity.

    This interface provides the contract for objects that can be uniquely
    identified within the system. Identity is essential for tracking,
    referencing, and managing objects.

    Scientific Meaning
    ------------------
    In scientific computing, identity allows us to uniquely reference particles,
    atoms, molecules, cells, or any other scientific entity across time and space.

    Responsibilities
    ----------------
    - Provide unique identifier
    - Support identity comparison
    - Enable identity serialization

    Methods
    -------
    get_id(): Get the unique identifier
    set_id(): Set the unique identifier (if mutable)
    """

    @abstractmethod
    def get_id(self) -> EntityID:
        """Get the unique identifier of this object.

        Returns:
            The unique identifier as a string

        Raises:
            NotImplementedError: If not implemented by subclass

        Example:
            >>> entity_id = entity.get_id()
            >>> print(f"Entity ID: {entity_id}")
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def id(self) -> EntityID:
        """Get the unique identifier property.

        Returns:
            The unique identifier as a string

        Example:
            >>> print(f"Entity ID: {entity.id}")
        """
        raise NotImplementedError

    def __eq__(self, other: Any) -> bool:
        """Check equality based on identity.

        Args:
            other: Object to compare with

        Returns:
            True if objects have the same ID, False otherwise
        """
        if not isinstance(other, Identifiable):
            return False
        return self.get_id() == other.get_id()

    def __hash__(self) -> int:
        """Return hash based on identity.

        Returns:
            Hash value based on ID
        """
        return hash(self.get_id())


class Observable(ABC):
    """Interface for objects that can emit events.

    This interface provides the contract for the observer pattern, allowing
    objects to emit events that other objects can listen to and respond to.

    Scientific Meaning
    ------------------
    In scientific computing, observations and measurements emit events that
    can be monitored, logged, and analyzed. This interface enables event-driven
    architectures for scientific simulations and experiments.

    Responsibilities
    ----------------
    - Manage event observers
    - Emit events to observers
    - Support event filtering
    - Enable event logging

    Methods
    -------
    add_observer(): Add an event observer
    remove_observer(): Remove an event observer
    emit_event(): Emit an event to observers
    get_observer_count(): Get the number of observers
    """

    @abstractmethod
    def add_observer(self, observer: Callable[[Any], None]) -> None:
        """Add an event observer.

        Args:
            observer: Callable that will receive events

        Raises:
            NotImplementedError: If not implemented by subclass

        Example:
            >>> def my_observer(event):
            ...     print(f"Event: {event}")
            >>> entity.add_observer(my_observer)
        """
        raise NotImplementedError

    @abstractmethod
    def remove_observer(self, observer: Callable[[Any], None]) -> None:
        """Remove an event observer.

        Args:
            observer: Callable to remove from observers

        Raises:
            NotImplementedError: If not implemented by subclass
            ValueError: If observer is not registered

        Example:
            >>> entity.remove_observer(my_observer)
        """
        raise NotImplementedError

    @abstractmethod
    def emit_event(self, event: Any) -> None:
        """Emit an event to all registered observers.

        Args:
            event: Event object to emit

        Raises:
            NotImplementedError: If not implemented by subclass

        Example:
            >>> entity.emit_event(Event(type="state_changed", data={...}))
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def observer_count(self) -> int:
        """Get the number of registered observers.

        Returns:
            Number of observers

        Example:
            >>> print(f"Observers: {entity.observer_count}")
        """
        raise NotImplementedError


class Serializable(ABC):
    """Interface for objects that can be serialized.

    This interface provides the contract for converting objects to and from
    serializable formats, enabling persistence, network transmission, and
    data interchange.

    Scientific Meaning
    ------------------
    In scientific computing, serialization is essential for saving simulation
    states, sharing experimental data, and archiving results. This interface
    ensures consistent serialization across all scientific objects.

    Responsibilities
    ----------------
    - Serialize to supported formats
    - Deserialize from supported formats
    - Handle version compatibility
    - Support format validation

    Methods
    -------
    serialize(): Serialize object to bytes
    deserialize(): Deserialize object from bytes (class method)
    is_serializable(): Check if object is serializable
    get_supported_formats(): Get supported serialization formats
    """

    @abstractmethod
    def serialize(self, format: SerializationFormat = SerializationFormat.JSON) -> SerializedData:
        """Serialize the object to bytes.

        Args:
            format: Serialization format to use

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If not implemented by subclass
            SerializationError: If serialization fails
            UnsupportedFormatError: If format is not supported

        Example:
            >>> data = entity.serialize(format=SerializationFormat.JSON)
            >>> with open("entity.json", "wb") as f:
            ...     f.write(data)
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize(cls, data: SerializedData, format: SerializationFormat = SerializationFormat.JSON) -> Serializable:
        """Deserialize the object from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format of the data

        Returns:
            Deserialized object

        Raises:
            NotImplementedError: If not implemented by subclass
            DeserializationError: If deserialization fails
            InvalidDataError: If data is invalid
            IncompatibleVersionError: If version is incompatible

        Example:
            >>> with open("entity.json", "rb") as f:
            ...     data = f.read()
            >>> entity = Entity.deserialize(data, format=SerializationFormat.JSON)
        """
        raise NotImplementedError

    @abstractmethod
    def is_serializable(self) -> bool:
        """Check if the object is serializable.

        Returns:
            True if serializable, False otherwise

        Example:
            >>> if entity.is_serializable():
            ...     data = entity.serialize()
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_supported_formats(cls) -> list[SerializationFormat]:
        """Get the list of supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Entity.get_supported_formats()
            >>> print(f"Supported formats: {formats}")
        """
        raise NotImplementedError


class Validatable(ABC):
    """Interface for objects that can be validated.

    This interface provides the contract for validating objects against
    defined rules and constraints, ensuring data integrity and consistency.

    Scientific Meaning
    ------------------
    In scientific computing, validation is critical for ensuring that
    physical laws, mathematical constraints, and experimental parameters
    are satisfied before proceeding with computations or simulations.

    Responsibilities
    ----------------
    - Validate object structure
    - Validate object constraints
    - Provide validation results
    - Support validation rules

    Methods
    -------
    validate(): Validate the object
    is_valid(): Check if object is valid
    get_validation_errors(): Get validation errors
    get_validation_warnings(): Get validation warnings
    """

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate the object.

        Returns:
            Tuple of (is_valid, error_messages)

        Raises:
            NotImplementedError: If not implemented by subclass

        Example:
            >>> is_valid, errors = entity.validate()
            >>> if not is_valid:
            ...     print(f"Validation errors: {errors}")
        """
        raise NotImplementedError

    def is_valid(self) -> bool:
        """Check if the object is valid.

        Returns:
            True if valid, False otherwise

        Example:
            >>> if entity.is_valid():
            ...     print("Entity is valid")
        """
        is_valid, _ = self.validate()
        return is_valid

    @property
    @abstractmethod
    def validation_errors(self) -> list[str]:
        """Get the list of validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = entity.validation_errors
            >>> for error in errors:
            ...     print(f"Error: {error}")
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def validation_warnings(self) -> list[str]:
        """Get the list of validation warnings.

        Returns:
            List of warning messages

        Example:
            >>> warnings = entity.validation_warnings
            >>> for warning in warnings:
            ...     print(f"Warning: {warning}")
        """
        raise NotImplementedError


class Cloneable(ABC):
    """Interface for objects that can be cloned.

    This interface provides the contract for creating copies of objects,
    enabling object duplication, templating, and isolation.

    Scientific Meaning
    ------------------
    In scientific computing, cloning is essential for creating experimental
    variations, running parallel simulations, and preserving initial states
    for comparison and analysis.

    Responsibilities
    ----------------
    - Clone objects
    - Support deep and shallow cloning
    - Handle cloning validation
    - Ensure clone independence

    Methods
    -------
    clone(): Clone the object
    is_cloneable(): Check if object is cloneable
    supports_deep_clone(): Check if deep cloning is supported
    """

    @abstractmethod
    def clone(self, deep: bool = True) -> Cloneable:
        """Clone the object.

        Args:
            deep: Whether to perform deep copy

        Returns:
            Cloned object

        Raises:
            NotImplementedError: If not implemented by subclass
            CloneError: If cloning fails

        Example:
            >>> cloned_entity = entity.clone(deep=True)
            >>> print(f"Cloned entity ID: {cloned_entity.get_id()}")
        """
        raise NotImplementedError

    @abstractmethod
    def is_cloneable(self) -> bool:
        """Check if the object is cloneable.

        Returns:
            True if cloneable, False otherwise

        Example:
            >>> if entity.is_cloneable():
            ...     cloned = entity.clone()
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def is_deep_cloneable(self) -> bool:
        """Check if deep cloning is supported.

        Returns:
            True if deep cloning is supported, False otherwise

        Example:
            >>> if entity.is_deep_cloneable:
            ...     cloned = entity.clone(deep=True)
        """
        raise NotImplementedError


class Comparable(ABC):
    """Interface for objects that can be compared.

    This interface provides the contract for comparing objects, enabling
    ordering, similarity measurement, and difference analysis.

    Scientific Meaning
    ------------------
    In scientific computing, comparison is essential for measuring similarity
    between states, comparing experimental results, and analyzing convergence
    in iterative computations.

    Responsibilities
    ----------------
    - Compare objects
    - Check equality
    - Measure similarity
    - Identify differences

    Methods
    -------
    compare(): Compare with another object
    equals(): Check equality
    is_less_than(): Check if less than
    is_greater_than(): Check if greater than
    get_comparison_key(): Get key for comparison
    """

    @abstractmethod
    def compare(self, other: Any) -> ComparisonResult:
        """Compare with another object.

        Args:
            other: Object to compare with

        Returns:
            Tuple of (are_equal, similarity_score, differences_dict)

        Raises:
            NotImplementedError: If not implemented by subclass
            TypeError: If types are incompatible

        Example:
            >>> are_equal, similarity, differences = entity.compare(other_entity)
            >>> print(f"Similarity: {similarity}")
        """
        raise NotImplementedError

    @abstractmethod
    def equals(self, other: Any) -> bool:
        """Check equality with another object.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> if entity.equals(other_entity):
            ...     print("Entities are equal")
        """
        raise NotImplementedError

    @abstractmethod
    def is_less_than(self, other: Any) -> bool:
        """Check if this object is less than another.

        Args:
            other: Object to compare with

        Returns:
            True if less than, False otherwise

        Example:
            >>> if state1.is_less_than(state2):
            ...     print("State1 is less than State2")
        """
        raise NotImplementedError

    @abstractmethod
    def is_greater_than(self, other: Any) -> bool:
        """Check if this object is greater than another.

        Args:
            other: Object to compare with

        Returns:
            True if greater than, False otherwise

        Example:
            >>> if state1.is_greater_than(state2):
            ...     print("State1 is greater than State2")
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def comparison_key(self) -> Any:
        """Get the key used for comparison.

        Returns:
            Comparison key

        Example:
            >>> key = entity.comparison_key
            >>> print(f"Comparison key: {key}")
        """
        raise NotImplementedError


class Timestamped(ABC):
    """Interface for objects with temporal metadata.

    This interface provides the contract for objects that have associated
    timestamps, enabling temporal tracking, auditing, and time-based queries.

    Scientific Meaning
    ------------------
    In scientific computing, timestamps are essential for tracking when
    measurements were taken, when simulations were run, and for maintaining
    temporal consistency in time-series data.

    Responsibilities
    ----------------
    - Provide timestamp access
    - Support timestamp updates (if mutable)
    - Calculate time differences
    - Enable temporal queries

    Methods
    -------
    get_timestamp(): Get the timestamp
    set_timestamp(): Set the timestamp (if mutable)
    get_age(): Get the age since timestamp
    """

    @abstractmethod
    def get_timestamp(self) -> datetime:
        """Get the timestamp of this object.

        Returns:
            Timestamp as datetime

        Raises:
            NotImplementedError: If not implemented by subclass

        Example:
            >>> timestamp = entity.get_timestamp()
            >>> print(f"Created at: {timestamp}")
        """
        raise NotImplementedError

    @abstractmethod
    def set_timestamp(self, timestamp: datetime) -> None:
        """Set the timestamp of this object.

        Args:
            timestamp: New timestamp

        Raises:
            NotImplementedError: If not implemented by subclass
            ValueError: If timestamp is invalid

        Example:
            >>> entity.set_timestamp(datetime.now())
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def timestamp(self) -> datetime:
        """Get the timestamp property.

        Returns:
            Timestamp as datetime

        Example:
            >>> print(f"Timestamp: {entity.timestamp}")
        """
        raise NotImplementedError

    @property
    def age(self) -> timedelta:
        """Get the age since the timestamp.

        Returns:
            Time difference since timestamp

        Example:
            >>> age = entity.age
            >>> print(f"Age: {age}")
        """
        return datetime.now() - self.timestamp


class Constrainable(ABC):
    """Interface for objects that can have constraints.

    This interface provides the contract for managing constraints on objects,
    enabling rule enforcement and validation.

    Scientific Meaning
    ------------------
    In scientific computing, constraints represent physical laws, conservation
    rules, and experimental limitations that must be satisfied for valid
    computations and simulations.

    Responsibilities
    ----------------
    - Add constraints
    - Remove constraints
    - Evaluate constraints
    - Check constraint violations

    Methods
    -------
    add_constraint(): Add a constraint
    remove_constraint(): Remove a constraint
    evaluate_constraints(): Evaluate all constraints
    get_constraint_violations(): Get constraint violations
    """

    @abstractmethod
    def add_constraint(self, constraint: Any) -> None:
        """Add a constraint to this object.

        Args:
            constraint: Constraint to add

        Raises:
            NotImplementedError: If not implemented by subclass
            InvalidConstraintError: If constraint is invalid
            ConstraintViolationError: If current state violates constraint

        Example:
            >>> entity.add_constraint(Constraint(rule="mass > 0"))
        """
        raise NotImplementedError

    @abstractmethod
    def remove_constraint(self, constraint_id: str) -> None:
        """Remove a constraint from this object.

        Args:
            constraint_id: ID of constraint to remove

        Raises:
            NotImplementedError: If not implemented by subclass
            ConstraintNotFoundError: If constraint not found

        Example:
            >>> entity.remove_constraint(constraint_id)
        """
        raise NotImplementedError

    @abstractmethod
    def evaluate_constraints(self, context: dict[str, Any]) -> list[ConstraintResult]:
        """Evaluate all constraints.

        Args:
            context: Evaluation context

        Returns:
            List of constraint evaluation results

        Raises:
            NotImplementedError: If not implemented by subclass

        Example:
            >>> results = entity.evaluate_constraints({"state": current_state})
            >>> for result in results:
            ...     print(f"Constraint: {result}")
        """
        raise NotImplementedError

    @abstractmethod
    def get_constraint_violations(self) -> list[str]:
        """Get current constraint violations.

        Returns:
            List of violation messages

        Example:
            >>> violations = entity.get_constraint_violations()
            >>> for violation in violations:
            ...     print(f"Violation: {violation}")
        """
        raise NotImplementedError


class Describable(ABC):
    """Interface for objects that can describe themselves.

    This interface provides the contract for objects to provide structured
    descriptions of themselves, enabling introspection and documentation.

    Scientific Meaning
    ------------------
    In scientific computing, self-description is essential for documenting
    experimental setups, simulation configurations, and analysis parameters.

    Responsibilities
    ----------------
    - Provide structured description
    - Support description serialization
    - Enable description querying
    - Support description updates

    Methods
    -------
    describe(): Get structured description
    get_description(): Get human-readable description
    set_description(): Set human-readable description
    """

    @abstractmethod
    def describe(self) -> dict[str, Any]:
        """Get a structured description of this object.

        Returns:
            Dictionary containing structured description

        Raises:
            NotImplementedError: If not implemented by subclass

        Example:
            >>> description = entity.describe()
            >>> print(f"Description: {description}")
        """
        raise NotImplementedError

    @abstractmethod
    def get_description(self) -> str:
        """Get a human-readable description.

        Returns:
            Human-readable description string

        Example:
            >>> description = entity.get_description()
            >>> print(description)
        """
        raise NotImplementedError

    @abstractmethod
    def set_description(self, description: str) -> None:
        """Set a human-readable description.

        Args:
            description: New description

        Example:
            >>> entity.set_description("A quantum particle")
        """
        raise NotImplementedError


class Versioned(ABC):
    """Interface for objects with version tracking.

    This interface provides the contract for versioned objects, enabling
    change tracking, optimistic concurrency, and historical analysis.

    Scientific Meaning
    ------------------
    In scientific computing, versioning is essential for tracking changes
    to experimental configurations, simulation parameters, and analysis
    methods over time.

    Responsibilities
    ----------------
    - Provide version information
    - Support version increments
    - Enable version comparison
    - Track version history

    Methods
    -------
    get_version(): Get current version
    increment_version(): Increment version
    get_version_history(): Get version history
    compare_versions(): Compare versions
    """

    @abstractmethod
    def get_version(self) -> int:
        """Get the current version of this object.

        Returns:
            Version number

        Example:
            >>> version = entity.get_version()
            >>> print(f"Version: {version}")
        """
        raise NotImplementedError

    @abstractmethod
    def increment_version(self) -> None:
        """Increment the version of this object.

        Example:
            >>> entity.increment_version()
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def version(self) -> int:
        """Get the version property.

        Returns:
            Version number

        Example:
            >>> print(f"Version: {entity.version}")
        """
        raise NotImplementedError


class MetadataAware(ABC):
    """Interface for objects with metadata.

    This interface provides the contract for managing metadata on objects,
    enabling extensible annotation and documentation.

    Scientific Meaning
    ------------------
    In scientific computing, metadata is essential for documenting experimental
    conditions, provenance information, and analysis parameters.

    Responsibilities
    ----------------
    - Get metadata
    - Set metadata
    - Update metadata
    - Query metadata

    Methods
    -------
    get_metadata(): Get metadata dictionary
    set_metadata(): Set metadata dictionary
    get_metadata_value(): Get specific metadata value
    set_metadata_value(): Set specific metadata value
    """

    @abstractmethod
    def get_metadata(self) -> MetadataDict:
        """Get the metadata dictionary.

        Returns:
            Metadata dictionary

        Example:
            >>> metadata = entity.get_metadata()
            >>> print(f"Metadata: {metadata}")
        """
        raise NotImplementedError

    @abstractmethod
    def set_metadata(self, metadata: MetadataDict) -> None:
        """Set the metadata dictionary.

        Args:
            metadata: New metadata dictionary

        Example:
            >>> entity.set_metadata({"source": "experiment", "date": "2024-01-01"})
        """
        raise NotImplementedError

    @abstractmethod
    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """Get a specific metadata value.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default

        Example:
            >>> source = entity.get_metadata_value("source", "unknown")
        """
        raise NotImplementedError

    @abstractmethod
    def set_metadata_value(self, key: str, value: Any) -> None:
        """Set a specific metadata value.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> entity.set_metadata_value("source", "experiment")
        """
        raise NotImplementedError


# Export all interfaces
__all__ = [
    "Identifiable",
    "Observable",
    "Serializable",
    "Validatable",
    "Cloneable",
    "Comparable",
    "Timestamped",
    "Constrainable",
    "Describable",
    "Versioned",
    "MetadataAware",
]
