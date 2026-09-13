"""Domain problem variables for QuantsMind Quantum.

Variables are the decision quantities of a :class:`QuantumProblem`.  They
carry a type, optional bounds and domain metadata that later formulation
phases (QMQ-02 onward) translate into QUBO variables, Ising spins, circuit
qubits or classical decision variables.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class VariableType(Enum):
    """Type of a decision variable.

    Attributes:
        BINARY: 0/1 decision variable.
        INTEGER: Discrete integer variable (bounded).
        CONTINUOUS: Real-valued variable.
        CATEGORICAL: Discrete label variable with no numeric bounds.
    """

    BINARY = auto()
    INTEGER = auto()
    CONTINUOUS = auto()
    CATEGORICAL = auto()

    @classmethod
    def parse(cls, value: Any) -> VariableType:
        """Coerce a name or member to a :class:`VariableType` (e.g. ``"binary"``)."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower()
        for member in cls:
            if member.name.lower() == text:
                return member
        names = ", ".join(m.name.lower() for m in cls)
        raise ValueError(f"unknown variable type {value!r}; expected one of: {names}")


@dataclass
class Variable:
    """A decision variable of a quantum domain problem.

    Args:
        name: Unique variable name within the problem.
        type: Variable category (binary/integer/continuous/categorical).
        lower_bound: Inclusive numeric lower bound for non-categorical types.
        upper_bound: Inclusive numeric upper bound for non-categorical types.
        domain: Optional namespace the variable belongs to (e.g. ``"asset"``).
        description: Optional human-readable explanation.
        metadata: Free-form metadata.

    Raises:
        ValueError: If bounds are inconsistent with the variable type.
    """

    name: str
    type: VariableType = VariableType.CONTINUOUS
    lower_bound: int | float | None = None
    upper_bound: int | float | None = None
    domain: str = ""
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("variable name must be a non-empty string")
        self.type = VariableType.parse(self.type)
        if self.type is VariableType.CATEGORICAL:
            if self.lower_bound is not None or self.upper_bound is not None:
                raise ValueError(f"categorical variable {self.name!r} cannot carry numeric bounds")
            return
        if self.type is VariableType.BINARY:
            self.lower_bound = 0
            self.upper_bound = 1
        if self.type is VariableType.INTEGER:
            if self.lower_bound is not None and not isinstance(self.lower_bound, int):
                raise ValueError(f"integer variable {self.name!r} needs an int lower_bound")
            if self.upper_bound is not None and not isinstance(self.upper_bound, int):
                raise ValueError(f"integer variable {self.name!r} needs an int upper_bound")
        if (
            self.lower_bound is not None
            and self.upper_bound is not None
            and self.lower_bound > self.upper_bound
        ):
            raise ValueError(
                f"variable {self.name!r} has lower_bound {self.lower_bound} > "
                f"upper_bound {self.upper_bound}"
            )

    @classmethod
    def binary(cls, name: str, *, domain: str = "", description: str = "") -> Variable:
        """Create a 0/1 decision variable."""
        return cls(name, VariableType.BINARY, domain=domain, description=description)

    @classmethod
    def integer(
        cls,
        name: str,
        lower_bound: int,
        upper_bound: int,
        *,
        domain: str = "",
        description: str = "",
    ) -> Variable:
        """Create an integer variable with inclusive bounds."""
        return cls(
            name,
            VariableType.INTEGER,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            domain=domain,
            description=description,
        )

    @classmethod
    def continuous(
        cls,
        name: str,
        lower_bound: int | float | None = None,
        upper_bound: int | float | None = None,
        *,
        domain: str = "",
        description: str = "",
    ) -> Variable:
        """Create a real-valued variable with optional inclusive bounds."""
        return cls(
            name,
            VariableType.CONTINUOUS,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            domain=domain,
            description=description,
        )

    @classmethod
    def categorical(cls, name: str, *, domain: str = "", description: str = "") -> Variable:
        """Create a categorical variable (no numeric bounds)."""
        return cls(name, VariableType.CATEGORICAL, domain=domain, description=description)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "type": self.type.name.lower(),
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "domain": self.domain,
            "description": self.description,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Variable:
        """Rebuild a Variable from :meth:`to_dict` output."""
        return cls(
            name=str(data["name"]),
            type=VariableType.parse(data.get("type", "continuous")),
            lower_bound=data.get("lower_bound"),
            upper_bound=data.get("upper_bound"),
            domain=str(data.get("domain", "")),
            description=str(data.get("description", "")),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        if self.type is VariableType.CATEGORICAL:
            bounds = ""
        else:
            bounds = f" [{self.lower_bound}, {self.upper_bound}]"
        return f"Variable(name={self.name!r}, type={self.type.name.lower()}{bounds})"


__all__ = ["Variable", "VariableType"]
