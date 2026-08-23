"""
Behaviour Module

This module provides behavior rules for entities within the QuantsMind SDK.
Behaviour represents the set of rules governing how entities respond to or participate in interactions.

Purpose
-------
Provide behavior rules for entities in the Foundation package.

Scientific Meaning
------------------
Behaviour represents the set of rules governing how entities respond to interactions:
physical laws (forces, fields), quantum evolution (unitary operators), chemical reactions,
biological processes, financial trading rules.

Responsibilities
----------------
- Manage behavior rules
- Support behavior execution
- Enable behavior serialization
- Handle behavior preconditions
- Support behavior composition

Dependencies
------------
typing (standard library)
logging (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.constants (constant values)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.interfaces (abstract interfaces)

Future Extensions
-----------------
- Behavior composition patterns
- Behavior optimization
- Behavior learning
- Distributed behavior execution
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from quantsmind.foundation.constants import DEFAULT_BEHAVIOUR_TYPE
from quantsmind.foundation.exceptions import (
    ExecutionError,
    InvalidBehaviourError,
    PreconditionError,
)
from quantsmind.foundation.interfaces import (
    Serializable,
    Validatable,
)
from quantsmind.foundation.types import (
    BehaviourResult,
    MetadataDict,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class Behaviour(Serializable, Validatable):
    """Concrete implementation of behavior rules for entities.

    This class provides a flexible behavior representation with support for
    callable rules, preconditions, and postconditions.

    Scientific Meaning
    ------------------
    In scientific computing, behaviour represents rules governing entity responses:
    physical laws (forces, fields), quantum evolution (unitary operators),
    chemical reactions, biological processes, financial trading rules.

    Attributes:
        _name: Behaviour name
        _rule: Callable rule function
        _behaviour_type: Behaviour type
        _preconditions: List of precondition functions
        _metadata: Additional metadata

    Example:
        >>> def my_rule(context):
        ...     return (True, context["value"] * 2, [])
        >>> behaviour = Behaviour(name="double", rule=my_rule)
        >>> result = behaviour.execute({"value": 5})
    """

    def __init__(
        self,
        name: str,
        rule: Callable[[dict[str, Any]], BehaviourResult],
        behaviour_type: str = DEFAULT_BEHAVIOUR_TYPE,
        preconditions: list[Callable[[dict[str, Any]], bool]] | None = None,
        metadata: MetadataDict | None = None,
    ) -> None:
        """Initialize a Behaviour.

        Args:
            name: Behaviour name
            rule: Callable rule function
            behaviour_type: Behaviour type
            preconditions: Optional list of precondition functions
            metadata: Optional metadata dictionary

        Raises:
            InvalidBehaviourError: If rule is not callable

        Example:
            >>> def my_rule(context):
            ...     return (True, context["value"] * 2, [])
            >>> behaviour = Behaviour(name="double", rule=my_rule)
        """
        self._name: str = name
        self._rule: Callable[[dict[str, Any]], BehaviourResult] = rule
        self._behaviour_type: str = behaviour_type
        self._preconditions: list[Callable[[dict[str, Any]], bool]] = preconditions or []
        self._metadata: MetadataDict = metadata or {}

        self._validate_rule()
        logger.debug(f"Created behaviour: {name}")

    def _validate_rule(self) -> None:
        """Validate the rule.

        Raises:
            InvalidBehaviourError: If rule is not callable
        """
        if not callable(self._rule):
            raise InvalidBehaviourError("Behaviour rule must be callable")

    @property
    def name(self) -> str:
        """Get the behaviour name.

        Returns:
            Behaviour name

        Example:
            >>> print(f"Behaviour: {behaviour.name}")
        """
        return self._name

    @property
    def behaviour_type(self) -> str:
        """Get the behaviour type.

        Returns:
            Behaviour type

        Example:
            >>> print(f"Type: {behaviour.behaviour_type}")
        """
        return self._behaviour_type

    @property
    def metadata(self) -> MetadataDict:
        """Get the behaviour metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {behaviour.metadata}")
        """
        return self._metadata.copy()

    @property
    def preconditions(self) -> list[Callable[[dict[str, Any]], bool]]:
        """Get the preconditions.

        Returns:
            List of precondition functions

        Example:
            >>> print(f"Preconditions: {behaviour.preconditions}")
        """
        return self._preconditions.copy()

    def add_precondition(self, precondition: Callable[[dict[str, Any]], bool]) -> None:
        """Add a precondition.

        Args:
            precondition: Precondition function

        Example:
            >>> behaviour.add_precondition(lambda ctx: ctx["value"] > 0)
        """
        self._preconditions.append(precondition)
        logger.debug(f"Added precondition to behaviour {self._name}")

    def execute(self, context: dict[str, Any]) -> BehaviourResult:
        """Execute the behaviour.

        Args:
            context: Execution context

        Returns:
            Tuple of (success, result, messages)

        Raises:
            PreconditionError: If preconditions are not satisfied
            ExecutionError: If execution fails

        Example:
            >>> result = behaviour.execute({"value": 5})
        """
        # Check preconditions
        for precondition in self._preconditions:
            if not precondition(context):
                raise PreconditionError(f"Precondition failed for behaviour {self._name}")

        try:
            logger.debug(f"Executing behaviour {self._name}")
            return self._rule(context)
        except Exception as e:
            raise ExecutionError(f"Behaviour execution failed: {e}") from e

    # Serializable interface implementation
    def serialize(self, format: str = "json") -> bytes:
        """Serialize the behaviour to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = behaviour.serialize(format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        data = {
            "name": self._name,
            "rule": self._rule.__name__ if callable(self._rule) else str(self._rule),
            "type": self._behaviour_type,
            "preconditions": [p.__name__ for p in self._preconditions],
            "metadata": self._metadata,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes, format: str = "json") -> Behaviour:
        """Deserialize the behaviour from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized Behaviour instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidBehaviourError: If data is invalid

        Note:
            Callable rules cannot be fully serialized. This method creates
            a placeholder behaviour that must be configured with actual rules.
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            # Create a placeholder rule
            def placeholder_rule(context: dict[str, Any]) -> BehaviourResult:
                return (True, None, ["Placeholder rule executed"])

            return cls(
                name=obj["name"],
                rule=placeholder_rule,
                behaviour_type=obj["type"],
                metadata=obj.get("metadata"),
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise InvalidBehaviourError(f"Failed to deserialize behaviour: {e}") from e

    def is_serializable(self) -> bool:
        """Check if the behaviour is serializable.

        Returns:
            True (behaviours are serializable, but callables are not fully preserved)

        Example:
            >>> if behaviour.is_serializable():
            ...     data = behaviour.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Behaviour.get_supported_formats()
        """
        return ["json"]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the behaviour.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = behaviour.validate()
        """
        errors: list[str] = []

        try:
            self._validate_rule()
        except InvalidBehaviourError as e:
            errors.append(str(e))

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = behaviour.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = behaviour.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the behaviour.

        Returns:
            String representation

        Example:
            >>> repr(behaviour)
        """
        return f"Behaviour(name='{self._name}', type='{self._behaviour_type}')"

    def __str__(self) -> str:
        """Return string representation of the behaviour.

        Returns:
            String representation

        Example:
            >>> str(behaviour)
        """
        return self._name

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> behaviour1 == behaviour2
        """
        if not isinstance(other, Behaviour):
            return False
        return self._name == other._name and self._behaviour_type == other._behaviour_type

    def __hash__(self) -> int:
        """Return hash of the behaviour.

        Returns:
            Hash value

        Example:
            >>> hash(behaviour)
        """
        return hash((self._name, self._behaviour_type))


# Export
__all__ = ["Behaviour"]
