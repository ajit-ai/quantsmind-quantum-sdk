"""Deterministic classical baseline: exhaustive QUBO solving.

QuantsMind Quantum must eventually compare classical, quantum, hybrid and
quantum-inspired execution paths.  :class:`ExhaustiveSolver` is the QMQ-02
**classical baseline**: it enumerates every binary assignment of a small
:class:`~quantsmind.quantum.optimization.qubo.QUBOModel`, computes the exact
energy, honors an optional feasibility predicate, and returns the best
**feasible** solution.

This is intentionally not a scalable optimizer.  The enumeration space is
``2^n`` and is bounded by :attr:`ExhaustiveSolver.max_variables`; exceeding
the bound raises :class:`ExhaustiveLimitError` instead of accidentally
running forever.  The result identifies itself as ``classical/exhaustive``
so downstream reports never mistake it for a quantum or hybrid execution.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from quantsmind.quantum.optimization.qubo import QUBOModel


class ExhaustiveLimitError(ValueError):
    """Raised when exhaustive enumeration would exceed the configured limit."""


class NoFeasibleSolutionError(ValueError):
    """Raised when no assignment satisfies the feasibility predicate."""


@dataclass
class ClassicalSolverResult:
    """Result of an exhaustive classical run.

    Args:
        solver: Solver identity (``"classical/exhaustive"``).
        exhaustive: Always ``True`` (this is an exhaustive baseline).
        assignment: Chosen binary assignment (variable name -> 0/1).
        energy: QUBO energy of the chosen assignment (minimization form,
            penalties included).
        objective_value: Optional true objective value of the assignment.
        feasible: Whether the chosen assignment satisfies the predicate.
        num_evaluations: Number of enumerated assignments (``2^n``).
        num_feasible: Number of assignments satisfying the predicate.
        limit: The ``max_variables`` limit that was enforced.
        metadata: Free-form solver metadata.
    """

    solver: str = "classical/exhaustive"
    exhaustive: bool = True
    assignment: dict[str, int] = field(default_factory=dict)
    energy: float = 0.0
    objective_value: float | None = None
    feasible: bool = True
    num_evaluations: int = 0
    num_feasible: int = 0
    limit: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "solver": self.solver,
            "exhaustive": self.exhaustive,
            "assignment": {k: int(v) for k, v in self.assignment.items()},
            "energy": self.energy,
            "objective_value": self.objective_value,
            "feasible": self.feasible,
            "num_evaluations": self.num_evaluations,
            "num_feasible": self.num_feasible,
            "limit": self.limit,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ClassicalSolverResult:
        """Rebuild a result from :meth:`to_dict` output."""
        return cls(
            solver=str(data.get("solver", "classical/exhaustive")),
            exhaustive=bool(data.get("exhaustive", True)),
            assignment={str(k): int(v) for k, v in data.get("assignment", {}).items()},
            energy=float(data.get("energy", 0.0)),
            objective_value=(
                float(data["objective_value"]) if data.get("objective_value") is not None else None
            ),
            feasible=bool(data.get("feasible", True)),
            num_evaluations=int(data.get("num_evaluations", 0)),
            num_feasible=int(data.get("num_feasible", 0)),
            limit=int(data.get("limit", 0)),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"ClassicalSolverResult(energy={self.energy}, "
            f"feasible={self.feasible}, evaluated={self.num_evaluations})"
        )


class ExhaustiveSolver:
    """Deterministic exhaustive solver for small QUBOs.

    Args:
        max_variables: Upper bound on :attr:`QUBOModel.num_variables`.
            Enumeration of ``2^n`` assignments is only attempted for
            ``n <= max_variables``.
    """

    def __init__(self, *, max_variables: int = 20) -> None:
        if max_variables < 1:
            raise ValueError(f"max_variables must be >= 1, got {max_variables}")
        self.max_variables = max_variables

    def solve(
        self,
        qubo: QUBOModel,
        *,
        is_feasible: Callable[[dict[str, int]], bool] | None = None,
        objective_fn: Callable[[dict[str, int]], float] | None = None,
    ) -> ClassicalSolverResult:
        """Enumerate all ``2^n`` assignments and return the best feasible one.

        The "best" assignment minimises the QUBO energy among feasible
        assignments.  Assignment order is deterministic (Gray-code
        enumeration); ties keep the first-seen assignment.

        Args:
            qubo: The model to solve.
            is_feasible: Optional predicate deciding which assignments are
                feasible.  When omitted, every assignment is feasible.
            objective_fn: Optional true-objective evaluator used only to
                populate :attr:`ClassicalSolverResult.objective_value`.

        Raises:
            ExhaustiveLimitError: If ``qubo.num_variables > max_variables``.
            NoFeasibleSolutionError: If no assignment is feasible.
        """
        names = list(qubo.variables)
        n = len(names)
        if n > self.max_variables:
            raise ExhaustiveLimitError(
                f"exhaustive solution requires enumerating 2^{n} assignments "
                f"({n} variables) which exceeds the configured limit of "
                f"{self.max_variables}. Use a smaller problem or raise "
                "max_variables."
            )
        index = {name: i for i, name in enumerate(names)}
        linear = [qubo.linear.get(name, 0.0) for name in names]
        adjacency: list[list[tuple[int, float]]] = [[] for _ in range(n)]
        for (left, right), value in qubo.quadratic.items():
            left_index = index[left]
            right_index = index[right]
            adjacency[left_index].append((right_index, value))
            adjacency[right_index].append((left_index, value))
        base = qubo.constant + qubo.offset

        bits = [0] * n
        energy = base
        feasible_predicate = is_feasible if is_feasible is not None else _always_feasible

        best_energy: float | None = None
        best_bits: list[int] | None = None
        num_feasible = 0
        num_evaluations = 1

        if feasible_predicate(self._assignment(bits, names)):
            num_feasible = 1
            best_energy = energy
            best_bits = list(bits)

        for step in range(1, 1 << n):
            flip = (step & -step).bit_length() - 1
            delta = linear[flip]
            for neighbor, coupling in adjacency[flip]:
                if bits[neighbor]:
                    delta += coupling
            if bits[flip]:
                energy -= delta
                bits[flip] = 0
            else:
                energy += delta
                bits[flip] = 1
            num_evaluations += 1
            if feasible_predicate(self._assignment(bits, names)):
                num_feasible += 1
                if best_energy is None or energy < best_energy:
                    best_energy = energy
                    best_bits = list(bits)

        if best_bits is None or best_energy is None:
            raise NoFeasibleSolutionError(
                f"no feasible assignment found among {num_evaluations} "
                f"evaluated for QUBO {qubo.name!r}"
            )
        assignment = self._assignment(best_bits, names)
        objective_value = float(objective_fn(assignment)) if objective_fn is not None else None
        return ClassicalSolverResult(
            assignment=assignment,
            energy=best_energy,
            objective_value=objective_value,
            feasible=True,
            num_evaluations=num_evaluations,
            num_feasible=num_feasible,
            limit=self.max_variables,
            metadata={
                "max_variables": self.max_variables,
                "size": n,
                "enumeration_space": 1 << n,
                "enumeration": "gray_code",
            },
        )

    @staticmethod
    def _assignment(bits: list[int], names: list[str]) -> dict[str, int]:
        return {name: bits[i] for i, name in enumerate(names)}


def _always_feasible(assignment: dict[str, int]) -> bool:
    return True


__all__ = [
    "ClassicalSolverResult",
    "ExhaustiveSolver",
    "ExhaustiveLimitError",
    "NoFeasibleSolutionError",
]
