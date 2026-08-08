"""
Constraint Module

This module provides constraint rules for entities and systems within the QuantsMind SDK.
Constraint represents rules that restrict the valid state space of entities or systems.

Purpose
-------
Provide constraint rules for entities and systems in the Foundation package.

Scientific Meaning
------------------
Constraint represents rules restricting valid state space: physical laws (conservation laws),
quantum constraints (normalization, commutation), chemical constraints (stoichiometry),
biological constraints (population limits), financial constraints (risk limits).

Responsibilities
----------------
- Manage constraint rules
- Support constraint evaluation
- Enable constraint serialization
- Handle constraint severity
- Support constraint composition

Dependencies
------------
typing (standard library)
logging (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.constants (constant values)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.enums (enumeration types)
quantsmind.foundation.interfaces (abstract interfaces)

Future Extensions
-----------------
- Constraint learning
- Constraint optimization
- Distributed constraint satisfaction
- Temporal constraints
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Callable, Dict, List, Optional

from quantsmind.foundation.constants import DEFAULT_CONSTRAINT_TYPE
from quantsmind.foundation.enums import ConstraintSeverity, ConstraintType
from quantsmind.foundation.exceptions import (
    CircularDependencyError,
    ConstraintError,
    ConstraintNotFoundError,
    ConstraintViolationError,
    EvaluationError,
    InvalidConstraintError,
)
from quantsmind.foundation.interfaces import (
    Serializable,
    Validatable,
)
from quantsmind.foundation.types import (
    ConstraintResult,
    ConstraintRule,
    MetadataDict,
    SerializedData,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class Constraint(Serializable, Validatable):
    """Concrete implementation of constraint rules for entities and systems.

    This class provides a flexible constraint representation with support for
    various constraint types, severity levels, and evaluation rules.

    Scientific Meaning
    ------------------
    In scientific computing, constraints represent rules restricting valid state space:
    physical laws (conservation laws), quantum constraints (normalization, commutation),
    chemical constraints (stoichiometry), biological constraints (population limits).

    Attributes:
        _id: Unique constraint identifier
        _name: Constraint name
        _rule: Constraint rule (callable or string)
        _constraint_type: Type of constraint
        _severity: Constraint severity level
        _metadata: Additional metadata

    Example:
        >>> def mass_constraint(context):
        ...     return (context.get("mass", 0) > 0, "Mass must be positive", ConstraintSeverity.ERROR)
        >>> constraint = Constraint(name="positive_mass", rule=mass_constraint)
        >>> result = constraint.evaluate({"mass": 5})
    """

    def __init__(
        self,
        name: str,
        rule: ConstraintRule,
        constraint_type: ConstraintType = ConstraintType.CUSTOM,
        severity: ConstraintSeverity = ConstraintSeverity.ERROR,
        metadata: Optional[MetadataDict] = None,
    ) -> None:
        """Initialize a Constraint.

        Args:
            name: Constraint name
            rule: Constraint rule (callable or string)
            constraint_type: Type of constraint
            severity: Constraint severity level
            metadata: Optional metadata dictionary

        Raises:
            InvalidConstraintError: If rule is invalid

        Example:
            >>> def mass_constraint(context):
            ...     return (context.get("mass", 0) > 0, "Mass must be positive", ConstraintSeverity.ERROR)
            >>> constraint = Constraint(name="positive_mass", rule=mass_constraint)
        """
        self._id: str = str(uuid.uuid4())
        self._name: str = name
        self._rule: ConstraintRule = rule
        self._constraint_type: ConstraintType = constraint_type
        self._severity: ConstraintSeverity = severity
        self._metadata: MetadataDict = metadata or {}

        self._validate_rule()
        logger.debug(f"Created constraint: {name}")

    def _validate_rule(self) -> None:
        """Validate the constraint rule.

        Raises:
            InvalidConstraintError: If rule is invalid
        """
        if not (callable(self._rule) or isinstance(self._rule, str)):
            raise InvalidConstraintError("Constraint rule must be callable or string")

    @property
    def id(self) -> str:
        """Get the constraint ID.

        Returns:
            Constraint ID

        Example:
            >>> print(f"ID: {constraint.id}")
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the constraint name.

        Returns:
            Constraint name

        Example:
            >>> print(f"Name: {constraint.name}")
        """
        return self._name

    @property
    def rule(self) -> ConstraintRule:
        """Get the constraint rule.

        Returns:
            Constraint rule

        Example:
            >>> print(f"Rule: {constraint.rule}")
        """
        return self._rule

    @property
    def constraint_type(self) -> ConstraintType:
        """Get the constraint type.

        Returns:
            Constraint type

        Example:
            >>> print(f"Type: {constraint.constraint_type}")
        """
        return self._constraint_type

    @property
    def severity(self) -> ConstraintSeverity:
        """Get the constraint severity.

        Returns:
            Constraint severity

        Example:
            >>> print(f"Severity: {constraint.severity}")
        """
        return self._severity

    @property
    def metadata(self) -> MetadataDict:
        """Get the constraint metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {constraint.metadata}")
        """
        return self._metadata.copy()

    @property
    def is_blocking(self) -> bool:
        """Check if constraint is blocking.

        Returns:
            True if blocking, False otherwise

        Example:
            >>> if constraint.is_blocking:
            ...     print("Blocking constraint")
        """
        return self._severity.is_blocking()

    def evaluate(self, context: Dict[str, Any]) -> ConstraintResult:
        """Evaluate the constraint.

        Args:
            context: Evaluation context

        Returns:
            Tuple of (is_satisfied, message, severity)

        Raises:
            EvaluationError: If evaluation fails

        Example:
            >>> result = constraint.evaluate({"mass": 5})
        """
        try:
            if callable(self._rule):
                result = self._rule(context)
                if isinstance(result, tuple) and len(result) == 3:
                    return result
                else:
                    return (bool(result), "Constraint evaluated", self._severity)
            else:
                # String rule - assume simple validation
                return (True, self._rule, self._severity)
        except Exception as e:
            raise EvaluationError(f"Constraint evaluation failed: {e}") from e

    # Serializable interface implementation
    def serialize(self, format: str = "json") -> bytes:
        """Serialize the constraint to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = constraint.serialize(format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        rule_str = self._rule.__name__ if callable(self._rule) else str(self._rule)

        data = {
            "id": self._id,
            "name": self._name,
            "rule": rule_str,
            "type": self._constraint_type.value,
            "severity": self._severity.value,
            "metadata": self._metadata,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes, format: str = "json") -> "Constraint":
        """Deserialize the constraint from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized Constraint instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidConstraintError: If data is invalid

        Note:
            Callable rules cannot be fully serialized. This method creates
            a placeholder constraint that must be configured with actual rules.
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            # Create a placeholder rule
            def placeholder_rule(context: Dict[str, Any]) -> bool:
                return True

            return cls(
                name=obj["name"],
                rule=placeholder_rule,
                constraint_type=ConstraintType(obj["type"]),
                severity=ConstraintSeverity(obj["severity"]),
                metadata=obj.get("metadata"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise InvalidConstraintError(f"Failed to deserialize constraint: {e}") from e

    def is_serializable(self) -> bool:
        """Check if the constraint is serializable.

        Returns:
            True (constraints are serializable, but callables are not fully preserved)

        Example:
            >>> if constraint.is_serializable():
            ...     data = constraint.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Constraint.get_supported_formats()
        """
        return ["json"]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the constraint.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = constraint.validate()
        """
        errors: list[str] = []

        try:
            self._validate_rule()
        except InvalidConstraintError as e:
            errors.append(str(e))

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = constraint.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = constraint.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the constraint.

        Returns:
            String representation

        Example:
            >>> repr(constraint)
        """
        return f"Constraint(name='{self._name}', type={self._constraint_type.value}, severity={self._severity.value})"

    def __str__(self) -> str:
        """Return string representation of the constraint.

        Returns:
            String representation

        Example:
            >>> str(constraint)
        """
        return self._name

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> constraint1 == constraint2
        """
        if not isinstance(other, Constraint):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Return hash of the constraint.

        Returns:
            Hash value

        Example:
            >>> hash(constraint)
        """
        return hash(self._id)


# Export
__all__ = ["Constraint"]
