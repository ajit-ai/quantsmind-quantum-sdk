"""Binary quadratic programming (QUBO) models.

A :class:`QUBOModel` represents the minimization problem::

    minimize  x^T Q x + linear . x + constant + offset
    x in {0, 1}^n

using named variables, linear coefficients, pairwise (quadratic)
coefficients and an additive constant.  Pairwise terms are canonicalised to
``i < j`` so every model has a single deterministic representation.  For
binary variables the identity ``x_i^2 = x_i`` is applied eagerly when a
diagonal term is supplied, and supplying a diagonal term via the quadratic
interface is rejected rather than silently miscounted.
"""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, ClassVar

from quantsmind.quantum.optimization.expression import Expression

_VARIABLE_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class QUBOError(ValueError):
    """Raised when a QUBO is malformed or an operation is invalid."""


def _validate_coefficient(name: str, value: float) -> float:
    if not math.isfinite(value):
        raise QUBOError(f"coefficient for {name!r} must be finite, got {value!r}")
    return float(value)


def _validate_variables(variables: list[str]) -> list[str]:
    seen: set[str] = set()
    cleaned: list[str] = []
    for name in variables:
        if not isinstance(name, str) or not _VARIABLE_PATTERN.fullmatch(name):
            raise QUBOError(f"invalid variable name {name!r}")
        if name in seen:
            raise QUBOError(f"duplicate variable name {name!r}")
        seen.add(name)
        cleaned.append(name)
    return cleaned


@dataclass
class QUBOModel:
    """A canonical binary quadratic model to be minimised.

    Args:
        variables: Ordered variable names (one QUBO bit per variable).
        linear: Variable name -> linear coefficient (``c_i``).
        quadratic: ``(i, j)`` with ``i < j`` -> pairwise coefficient
            (``c_ij``).  Diagonal terms are rewritten into ``linear``.
        constant: Additive constant term.
        offset: Additional additive shift (bookkeeping only; both
            ``constant`` and ``offset`` contribute to :meth:`energy`).
        name: Model label.
        metadata: Free-form model metadata (e.g. penalty records).

    Raises:
        QUBOError: If names are invalid/duplicated, a coefficient is not
            finite, a quadratic key is malformed (``i == j`` or reversed
            hands accepted and canonicalised), or a quadratic references an
            unknown variable.
    """

    variables: list[str]
    linear: dict[str, float] = field(default_factory=dict)
    quadratic: dict[tuple[str, str], float] = field(default_factory=dict)
    constant: float = 0.0
    offset: float = 0.0
    name: str = "qubo"
    metadata: dict[str, Any] = field(default_factory=dict)

    kind: ClassVar[str] = "qubo"

    def __post_init__(self) -> None:
        names = _validate_variables(list(self.variables))
        name_set = set(names)
        linear: dict[str, float] = {}
        quadratic: dict[tuple[str, str], float] = {}
        for name, value in self.linear.items():
            if name not in name_set:
                raise QUBOError(f"linear coefficient references unknown variable {name!r}")
            coefficient = _validate_coefficient(name, value)
            if coefficient != 0.0:
                linear[name] = coefficient
        for (left, right), value in self.quadratic.items():
            if left not in name_set or right not in name_set:
                raise QUBOError(
                    f"quadratic coefficient references unknown variable ({left!r}, {right!r})"
                )
            coefficient = _validate_coefficient(f"{left},{right}", value)
            if coefficient == 0.0:
                continue
            if left == right:
                linear[left] = linear.get(left, 0.0) + coefficient
                continue
            key = (left, right) if left < right else (right, left)
            quadratic[key] = quadratic.get(key, 0.0) + coefficient
        self.variables = names
        self.linear = linear
        self.quadratic = quadratic
        self.constant = _validate_coefficient("constant", self.constant)
        self.offset = _validate_coefficient("offset", self.offset)

    # -- construction helpers --------------------------------------------

    def add_linear(self, name: str, value: float) -> QUBOModel:
        """Add (or accumulate) a linear coefficient and return self."""
        if name not in self.variables:
            raise QUBOError(f"unknown variable {name!r}")
        coefficient = _validate_coefficient(name, value)
        remaining = self.linear.get(name, 0.0) + coefficient
        if remaining == 0.0:
            self.linear.pop(name, None)
        else:
            self.linear[name] = remaining
        return self

    def add_quadratic(self, left: str, right: str, value: float) -> QUBOModel:
        """Add (or accumulate) a pairwise coefficient and return self.

        Raises:
            QUBOError: If ``left == right`` (diagonal terms belong on
                ``linear`` for binary variables) or a variable is unknown.
        """
        if left not in self.variables or right not in self.variables:
            raise QUBOError(f"unknown variable in quadratic term ({left!r}, {right!r})")
        if left == right:
            raise QUBOError(
                f"diagonal quadratic term ({left!r}, {left!r}) is not allowed; "
                "use linear coefficients (x^2 = x for binary variables)"
            )
        coefficient = _validate_coefficient(f"{left},{right}", value)
        key = (left, right) if left < right else (right, left)
        remaining = self.quadratic.get(key, 0.0) + coefficient
        if remaining == 0.0:
            self.quadratic.pop(key, None)
        else:
            self.quadratic[key] = remaining
        return self

    def add_constant(self, value: float) -> QUBOModel:
        """Add to the constant term and return self."""
        self.constant += _validate_coefficient("constant", value)
        return self

    # -- properties -------------------------------------------------------

    @property
    def num_variables(self) -> int:
        """Number of QUBO variables (bits)."""
        return len(self.variables)

    @property
    def num_terms(self) -> int:
        """Number of linear + pairwise terms."""
        return len(self.linear) + len(self.quadratic)

    @property
    def degree(self) -> int:
        """Polynomial degree (``2`` when pairwise terms exist, else ``1``)."""
        return 2 if self.quadratic else (1 if self.linear else 0)

    # -- evaluation -------------------------------------------------------

    def energy(self, assignment: dict[str, Any] | Sequence[Any]) -> float:
        """Compute the QUBO energy of a binary assignment.

        ``assignment`` may be a dict mapping variable name -> 0/1 or a
        sequence of bits in :attr:`variables` order.

        Raises:
            QUBOError: If an assignment is missing, unknown, or not binary.
        """
        bits = self._bits(assignment)
        value = self.constant + self.offset
        for index, name in enumerate(self.variables):
            if bits[index]:
                value += self.linear.get(name, 0.0)
                for other in range(index + 1, len(self.variables)):
                    if not bits[other]:
                        continue
                    other_name = self.variables[other]
                    key = (name, other_name) if name < other_name else (other_name, name)
                    value += self.quadratic.get(key, 0.0)
        return value

    def _bits(self, assignment: dict[str, Any] | Sequence[Any]) -> list[int]:
        if isinstance(assignment, dict):
            unknown = set(assignment) - set(self.variables)
            if unknown:
                raise QUBOError(f"assignment references unknown variables: {sorted(unknown)}")
            missing = set(self.variables) - set(assignment)
            if missing:
                raise QUBOError(f"assignment is missing variables: {sorted(missing)}")
            values = [assignment[name] for name in self.variables]
        else:
            values = list(assignment)
            if len(values) != self.num_variables:
                raise QUBOError(
                    "sequence assignment must provide exactly one bit per "
                    "variable (model has "
                    f"{self.num_variables}, got {len(values)})"
                )
        bits: list[int] = []
        for index, value in enumerate(values):
            if value is True:
                value = 1
            elif value is False:
                value = 0
            if value not in (0, 1):
                raise QUBOError(
                    f"variable {self.variables[index]!r} is not binary: "
                    f"got {value!r}; expected 0 or 1"
                )
            bits.append(int(value))
        return bits

    # -- serialization ----------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "kind": self.kind,
            "name": self.name,
            "variables": list(self.variables),
            "linear": {name: value for name, value in sorted(self.linear.items())},
            "quadratic": {
                f"{left},{right}": value for (left, right), value in sorted(self.quadratic.items())
            },
            "constant": self.constant,
            "offset": self.offset,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QUBOModel:
        """Rebuild a QUBOModel from :meth:`to_dict` output."""
        quadratic: dict[tuple[str, str], float] = {}
        for key, value in data.get("quadratic", {}).items():
            left, right = str(key).split(",", 1)
            quadratic[(left.strip(), right.strip())] = float(value)
        return cls(
            variables=[str(v) for v in data.get("variables", [])],
            linear={str(k): float(v) for k, v in data.get("linear", {}).items()},
            quadratic=quadratic,
            constant=float(data.get("constant", 0.0)),
            offset=float(data.get("offset", 0.0)),
            name=str(data.get("name", "qubo")),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"QUBOModel(name={self.name!r}, variables={self.num_variables}, "
            f"terms={self.num_terms}, constant={self.constant})"
        )


def qubo_from_expression(
    expression: Expression,
    variables: Sequence[str],
    *,
    name: str = "qubo",
) -> QUBOModel:
    """Build a QUBO from a symbolic expression over binary variables.

    Linear monomials become linear terms, degree-two monomials become
    pairwise terms and the constant monomial becomes the constant term.
    Products that collapse to the same variable (``x^2``) are reduced via
    binary idempotence to linear terms.  Terms of degree greater than two
    are rejected explicitly.

    Raises:
        QUBOError: If the expression references an unknown variable or
            contains a term of degree greater than two.
    """
    names = list(_validate_variables(list(variables)))
    if set(expression.variables) - set(names):
        unknown = sorted(set(expression.variables) - set(names))
        raise QUBOError(f"expression references variables outside the model: {unknown}")
    model = QUBOModel(variables=names, name=name)
    for monomial, value in expression.expand().items():
        if len(monomial) == 0:
            model.add_constant(value)
        elif len(monomial) == 1 or len(monomial) == 2 and monomial[0] == monomial[1]:
            model.add_linear(monomial[0], value)
        elif len(monomial) == 2:
            model.add_quadratic(monomial[0], monomial[1], value)
        else:
            raise QUBOError(
                f"QUBO requires terms of degree at most 2; got monomial "
                f"({'*'.join(monomial)}) with coefficient {value}"
            )
    return model


__all__ = ["QUBOError", "QUBOModel", "qubo_from_expression"]
