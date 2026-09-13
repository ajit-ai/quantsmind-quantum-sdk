"""Data -> QMQ formulation adapter.

:class:`DataFormulationAdapter` converts a validated
:class:`~quantsmind.quantum.data.problem.DataProblem` into the existing QMQ
pipeline: a :class:`QuantumProblem` (consumed unchanged by the existing
:func:`~quantsmind.quantum.formulation.formulate` and QUBO mapper).  It
preserves objective senses, the deterministic variable naming conventions,
constraint bounds, feature/record orderings and JSON-safe Data provenance
metadata.  No Data-specific QUBO exists — the existing QMQ-02
representations are reused end-to-end.
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.core.constraint import Constraint
from quantsmind.quantum.core.domain_context import DomainContext
from quantsmind.quantum.core.objective import Objective
from quantsmind.quantum.core.problem import QuantumProblem
from quantsmind.quantum.core.variable import Variable
from quantsmind.quantum.data.context import DataContext
from quantsmind.quantum.data.problem import DataProblem

__all__ = ["DataFormulationAdapter"]


def _default_domain(context: DataContext | None) -> DomainContext:
    if context is not None:
        return context.to_domain_context()
    return DomainContext(domain="data")


class DataFormulationAdapter:
    """Converts data problems into the existing QMQ formulation.

    The conversion is deterministic: decision variables follow the ``x<i>``
    convention for feature selection and the ``z{record}_{cluster}``
    convention for clustering, objectives keep their senses, and every
    data constraint materializes into QMQ constraints.
    """

    def validate(self, problem: DataProblem) -> list[str]:
        """Return the validation issues of a data problem (empty = valid)."""
        return problem.validate()

    def raise_if_invalid(self, problem: DataProblem) -> None:
        """Raise :class:`DataValidationError` when the problem is invalid.

        Raises:
            DataValidationError: If the problem fails validation.
        """
        problem.raise_if_invalid()

    @staticmethod
    def data_metadata(problem: DataProblem) -> dict[str, Any]:
        """JSON-safe Data provenance metadata for the quantum problem."""
        meta: dict[str, Any] = {
            "domain_layer": "data",
            "problem_type": problem.problem_type.value,
            "dataset": {
                "name": problem.dataset.name,
                "feature_order": problem.dataset.feature_names,
                "record_order": problem.dataset.record_ids,
            },
            "objectives": [objective.to_dict() for objective in problem.objectives],
            "constraints": [constraint.to_dict() for constraint in problem.constraints],
        }
        if problem.context is not None:
            meta["context"] = problem.context.to_dict()
            meta["assumptions"] = dict(problem.context.assumptions)
        if problem.problem_type.value == "clustering":
            meta["k"] = problem.k or 0
            distance = problem.clustering_distance_matrix()
            meta["distance"] = {
                "metric": (
                    problem.context.distance_metric if problem.context is not None else "euclidean"
                ),
                "record_order": list(distance.record_order),
                "values": [[float(value) for value in row] for row in distance.values],
            }
        return meta

    def to_quantum_problem(
        self,
        problem: DataProblem,
        *,
        preferred_strategy: Any = None,
    ) -> QuantumProblem:
        """Convert a data problem into a QMQ :class:`QuantumProblem`.

        Args:
            problem: The validated data problem.
            preferred_strategy: Optional preferred computation strategy.

        Raises:
            DataValidationError: If the data problem is invalid.
        """
        self.raise_if_invalid(problem)
        variables: list[Variable] = problem.decision_variables()
        objectives: list[Objective] = [
            objective.to_quantum_objective(problem) for objective in problem.objectives
        ]
        constraints: list[Constraint] = []
        for constraint in problem.constraints:
            constraints.extend(constraint.to_quantum_constraints(problem))
        return QuantumProblem(
            name=problem.name,
            description=problem.description,
            domain=_default_domain(problem.context),
            variables=variables,
            objectives=objectives,
            constraints=constraints,
            metadata=DataFormulationAdapter.data_metadata(problem),
            preferred_strategy=preferred_strategy,
            provenance={
                "domain_layer": "data",
                "problem_type": problem.problem_type.value,
                "dataset": {
                    "name": problem.dataset.name,
                    "feature_order": problem.dataset.feature_names,
                    "record_order": problem.dataset.record_ids,
                },
            },
        )

    def formulate(self, problem: DataProblem) -> Any:
        """Return the existing QMQ formulation of a data problem.

        Delegates to the existing :func:`quantsmind.quantum.formulation
        .formulate`, producing an :class:`OptimizationModel` (or another
        :class:`MathematicalModel` selected by the existing rules).
        """
        from quantsmind.quantum.formulation import formulate as qmq_formulate

        return qmq_formulate(self.to_quantum_problem(problem))

    @classmethod
    def cluster_variable_index(cls, problem: DataProblem, record_index: int, cluster: int) -> int:
        """Return the flat QMQ index of the ``z{record}_{cluster}`` variable."""
        return record_index * (problem.k or 0) + cluster
