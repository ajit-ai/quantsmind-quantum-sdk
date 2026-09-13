"""Spin (Ising) models and QUBO <-> Ising conversion.

An :class:`IsingModel` represents the minimization over spins
``s_i in {-1, +1}`` of::

    minimize  sum(h_i * s_i) + sum(J_ij * s_i * s_j) + constant + offset

Conversion uses the standard mapping ``x = (s + 1) / 2`` (equivalently
``s = 2x - 1``).  The two representations are **energy equivalent**: for the
same assignment ``E_qubo(x) == E_ising(s(x))`` with no energy drift, because
all constant contributions are carried exactly through the conversion.  The
::ref:`tests <QMIO>` verify this numerically over small exhaustive spaces.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, ClassVar

from quantsmind.quantum.optimization.qubo import QUBOModel


class IsingError(ValueError):
    """Raised when an Ising model is malformed or an operation is invalid."""


def _canonical_terms(
    variables: list[str],
    h: dict[str, float],
    couplings: dict[tuple[str, str], float],
) -> tuple[list[str], dict[str, float], dict[tuple[str, str], float]]:
    names = list(variables)
    if len(set(names)) != len(names):
        raise IsingError("duplicate variable name(s) in Ising model")
    name_set = set(names)
    h_clean: dict[str, float] = {}
    for name, value in h.items():
        if name not in name_set:
            raise IsingError(f"field references unknown variable {name!r}")
        if value != 0.0:
            h_clean[name] = float(value)
    couplings_clean: dict[tuple[str, str], float] = {}
    for (left, right), value in couplings.items():
        if left not in name_set or right not in name_set:
            raise IsingError(f"coupling references unknown variables ({left!r}, {right!r})")
        if left == right:
            raise IsingError(f"self-coupling ({left!r}, {left!r}) is not allowed in an Ising model")
        key = (left, right) if left < right else (right, left)
        if value != 0.0:
            couplings_clean[key] = couplings_clean.get(key, 0.0) + float(value)
    return names, h_clean, couplings_clean


@dataclass
class IsingModel:
    """A canonical Ising/spin model to be minimised.

    Args:
        variables: Ordered spin variable names.
        h: Variable name -> linear field ``h_i``.
        couplings: ``(i, j)`` with ``i < j`` -> coupling ``J_ij``.
        constant: Additive constant term.
        offset: Additional additive shift (bookkeeping only).
        name: Model label.
        metadata: Free-form model metadata.

    Raises:
        IsingError: If variable names are duplicated, a field/coupling
            references an unknown variable, or a self-coupling is given.
    """

    variables: list[str]
    h: dict[str, float] = field(default_factory=dict)
    couplings: dict[tuple[str, str], float] = field(default_factory=dict)
    constant: float = 0.0
    offset: float = 0.0
    name: str = "ising"
    metadata: dict[str, Any] = field(default_factory=dict)

    kind: ClassVar[str] = "ising"

    def __post_init__(self) -> None:
        names, h, couplings = _canonical_terms(self.variables, self.h, self.couplings)
        self.variables = names
        self.h = h
        self.couplings = couplings
        if (
            float(self.constant) != self.constant or float(self.offset) != self.offset
        ):  # pragma: no cover
            raise IsingError("constant and offset must be real numbers")

    # -- construction helpers --------------------------------------------

    def add_field(self, name: str, value: float) -> IsingModel:
        """Add (or accumulate) a field ``h_i`` and return self."""
        if name not in self.variables:
            raise IsingError(f"unknown variable {name!r}")
        remaining = self.h.get(name, 0.0) + float(value)
        if remaining == 0.0:
            self.h.pop(name, None)
        else:
            self.h[name] = remaining
        return self

    def add_coupling(self, left: str, right: str, value: float) -> IsingModel:
        """Add (or accumulate) a coupling ``J_ij`` and return self."""
        if left not in self.variables or right not in self.variables:
            raise IsingError(f"unknown variable in coupling ({left!r}, {right!r})")
        if left == right:
            raise IsingError("self-couplings are not allowed in an Ising model")
        key = (left, right) if left < right else (right, left)
        remaining = self.couplings.get(key, 0.0) + float(value)
        if remaining == 0.0:
            self.couplings.pop(key, None)
        else:
            self.couplings[key] = remaining
        return self

    # -- properties -------------------------------------------------------

    @property
    def num_variables(self) -> int:
        """Number of spin variables."""
        return len(self.variables)

    @property
    def num_terms(self) -> int:
        """Number of field + coupling terms."""
        return len(self.h) + len(self.couplings)

    # -- evaluation -------------------------------------------------------

    def energy(self, assignment: dict[str, Any] | Sequence[Any]) -> float:
        """Compute the Ising energy of a spin assignment.

        ``assignment`` may be a dict name -> -1/+1 or a sequence of spins in
        :attr:`variables` order.

        Raises:
            IsingError: If an assignment is missing, unknown, or not
                ``-1``/``+1``.
        """
        spins = self._spins(assignment)
        value = self.constant + self.offset
        for index, name in enumerate(self.variables):
            value += spins[index] * self.h.get(name, 0.0)
            for other in range(index + 1, len(self.variables)):
                other_name = self.variables[other]
                key = (name, other_name) if name < other_name else (other_name, name)
                coupling = self.couplings.get(key, 0.0)
                if coupling != 0.0:
                    value += spins[index] * spins[other] * coupling
        return value

    def _spins(self, assignment: dict[str, Any] | Sequence[Any]) -> list[int]:
        if isinstance(assignment, dict):
            unknown = set(assignment) - set(self.variables)
            if unknown:
                raise IsingError(f"assignment references unknown variables: {sorted(unknown)}")
            missing = set(self.variables) - set(assignment)
            if missing:
                raise IsingError(f"assignment is missing variables: {sorted(missing)}")
            values = [assignment[name] for name in self.variables]
        else:
            values = list(assignment)
            if len(values) != self.num_variables:
                raise IsingError(
                    "sequence assignment must provide exactly one spin per "
                    f"variable (model has {self.num_variables}, got {len(values)})"
                )
        spins: list[int] = []
        for index, value in enumerate(values):
            if value not in (-1, 1):
                raise IsingError(
                    f"variable {self.variables[index]!r} is not a spin: "
                    f"got {value!r}; expected -1 or +1"
                )
            spins.append(int(value))
        return spins

    # -- conversion -------------------------------------------------------

    def to_qubo(self) -> QUBOModel:
        """Convert to an energy-equivalent :class:`QUBOModel` via s = 2x - 1."""
        adjacency: dict[str, list[tuple[str, float]]] = {}
        for left, right in self.couplings:
            value = self.couplings[(left, right)]
            adjacency.setdefault(left, []).append((right, value))
            adjacency.setdefault(right, []).append((left, value))
        linear: dict[str, float] = {}
        for name in self.variables:
            field = self.h.get(name, 0.0)
            neighbor_sum = sum(value for _, value in adjacency.get(name, []))
            linear[name] = 2.0 * field - 2.0 * neighbor_sum
        quadratic: dict[tuple[str, str], float] = {
            key: 4.0 * value for key, value in self.couplings.items()
        }
        constant = self.constant + self.offset + sum(self.couplings.values()) - sum(self.h.values())
        return QUBOModel(
            variables=list(self.variables),
            linear=linear,
            quadratic=quadratic,
            constant=constant,
            name=f"{self.name}_qubo",
            metadata={"source": "ising_to_qubo"},
        )

    @classmethod
    def from_qubo(cls, qubo: QUBOModel) -> IsingModel:
        """Convert a QUBO to an energy-equivalent :class:`IsingModel`.

        Applies ``x = (s + 1) / 2``:
        ``h_i = a_i/2 + sum_j(b_ij)/4`` and ``J_ij = b_ij/4``.
        """
        adjacency: dict[str, list[tuple[str, float]]] = {}
        for left, right in qubo.quadratic:
            value = qubo.quadratic[(left, right)]
            adjacency.setdefault(left, []).append((right, value))
            adjacency.setdefault(right, []).append((left, value))
        fields: dict[str, float] = {}
        for name in qubo.variables:
            linear = qubo.linear.get(name, 0.0)
            neighbor_sum = sum(value for _, value in adjacency.get(name, []))
            fields[name] = linear / 2.0 + neighbor_sum / 4.0
        couplings: dict[tuple[str, str], float] = {
            key: value / 4.0 for key, value in qubo.quadratic.items()
        }
        constant = (
            qubo.constant
            + qubo.offset
            + sum(qubo.linear.values()) / 2.0
            + sum(qubo.quadratic.values()) / 4.0
        )
        return cls(
            variables=list(qubo.variables),
            h=fields,
            couplings=couplings,
            constant=constant,
            name=f"{qubo.name}_ising",
            metadata={"source": "qubo_to_ising"},
        )

    # -- serialization ----------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "kind": self.kind,
            "name": self.name,
            "variables": list(self.variables),
            "h": {name: value for name, value in sorted(self.h.items())},
            "couplings": {
                f"{left},{right}": value for (left, right), value in sorted(self.couplings.items())
            },
            "constant": self.constant,
            "offset": self.offset,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IsingModel:
        """Rebuild an IsingModel from :meth:`to_dict` output."""
        couplings: dict[tuple[str, str], float] = {}
        for key, value in data.get("couplings", {}).items():
            left, right = str(key).split(",", 1)
            couplings[(left.strip(), right.strip())] = float(value)
        return cls(
            variables=[str(v) for v in data.get("variables", [])],
            h={str(k): float(v) for k, v in data.get("h", {}).items()},
            couplings=couplings,
            constant=float(data.get("constant", 0.0)),
            offset=float(data.get("offset", 0.0)),
            name=str(data.get("name", "ising")),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"IsingModel(name={self.name!r}, variables={self.num_variables}, "
            f"terms={self.num_terms}, constant={self.constant})"
        )


__all__ = ["IsingError", "IsingModel"]
