"""ML -> QMQ formulation adapter.

:class:`MLFormulationAdapter` converts a validated
:class:`~quantsmind.quantum.ml.problem.MLProblem` into the existing QMQ
pipeline: a :class:`QuantumProblem` (consumed unchanged by the existing
:func:`~quantsmind.quantum.formulation.formulate` and QUBO mapper).  It
preserves objective senses, the deterministic variable naming conventions,
constraint bounds, feature/record orderings and JSON-safe ML provenance
metadata.

Feature-selection and clustering problems are **delegated** to the QMQ-09
Data layer: the adapter constructs a ``DataProblem`` from the same ML dataset
and runs it through ``DataFormulationAdapter``, so the quantum formulation,
QUBO mapping and solution decoding of the Data layer are reused end-to-end
(provenance records ``source_domain="data"``).
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.core.constraint import Constraint
from quantsmind.quantum.core.domain_context import DomainContext
from quantsmind.quantum.core.objective import Objective
from quantsmind.quantum.core.problem import QuantumProblem
from quantsmind.quantum.core.variable import Variable
from quantsmind.quantum.ml.context import MLContext
from quantsmind.quantum.ml.errors import MLValidationError
from quantsmind.quantum.ml.problem import MLProblem, MLProblemType

__all__ = ["MLFormulationAdapter"]

_FORMULATION_TYPES: dict[str, str] = {
    "CLASSIFICATION": "linear_least_squares",
    "REGRESSION": "linear_least_squares",
    "MODEL_SELECTION": "one_hot_selection",
    "HYPERPARAMETER_OPTIMIZATION": "one_hot_selection",
    "FEATURE_SELECTION": "delegated_data",
    "CLUSTERING": "delegated_data",
}


def _default_domain(context: MLContext | None) -> DomainContext:
    if context is not None:
        return context.to_domain_context()
    return DomainContext(domain="ml")


class MLFormulationAdapter:
    """Converts ML problems into the existing QMQ formulation.

    The conversion is deterministic: decision variables follow the ``w<i>``
    (fitting), ``s<c>`` (model selection) and ``h{p}_{c}`` (hyperparameter)
    conventions, objectives keep their senses, and every ML constraint
    materializes into QMQ constraints.  Feature selection and clustering
    delegate to the QMQ-09 Data layer.
    """

    def validate(self, problem: MLProblem) -> list[str]:
        """Return the validation issues of an ML problem (empty = valid)."""
        return problem.validate()

    def raise_if_invalid(self, problem: MLProblem) -> None:
        """Raise :class:`MLValidationError` when the problem is invalid.

        Raises:
            MLValidationError: If the problem fails validation.
        """
        problem.raise_if_invalid()

    def is_delegated(self, problem: MLProblem) -> bool:
        """Return whether the problem is delegated to the QMQ-09 Data layer."""
        return problem.problem_type.name in ("FEATURE_SELECTION", "CLUSTERING")

    def ml_metadata(self, problem: MLProblem) -> dict[str, Any]:
        """JSON-safe ML provenance metadata for the quantum problem."""
        problem_name = problem.problem_type.name
        meta: dict[str, Any] = {
            "domain_layer": "ml",
            "problem_type": problem.problem_type.value,
            "formulation_type": _FORMULATION_TYPES[problem_name],
            "source_domain": "data" if self.is_delegated(problem) else "ml",
        }
        if problem.dataset is not None:
            meta["dataset"] = {
                "name": problem.dataset.name,
                "feature_order": problem.dataset.feature_names,
                "record_order": problem.dataset.record_ids,
            }
            meta["objectives"] = [objective.to_dict() for objective in problem.objectives]
            meta["constraints"] = [constraint.to_dict() for constraint in problem.constraints]
        if problem.context is not None:
            meta["context"] = problem.context.to_dict()
            meta["assumptions"] = dict(problem.context.assumptions)
        if problem_name == "MODEL_SELECTION":
            meta["candidates"] = [candidate.to_dict() for candidate in problem.candidates]
        if problem_name == "HYPERPARAMETER_OPTIMIZATION":
            meta["hyperparameters"] = [
                hyperparameter.to_dict() for hyperparameter in problem.hyperparameters
            ]
        if problem_name == "CLUSTERING":
            meta["k"] = problem.k or 0
        return meta

    def to_data_problem(self, problem: MLProblem) -> Any:
        """Build the delegated QMQ-09 ``DataProblem`` of an ML problem.

        Feature selection converts ``MLFeatureSelectionObjective`` and
        ``MLFeatureCountConstraint`` into their Data equivalents; clustering
        converts the ML clustering objective/constraints (with default
        assignment semantics when absent).

        Args:
            problem: The validated ML problem (feature selection or
                clustering).

        Raises:
            MLValidationError: If the problem is not a delegated family or
                cannot be expressed by the Data layer.
        """
        from quantsmind.quantum.data.constraints import AssignmentConstraint
        from quantsmind.quantum.data.models import DataFeature, DataRecord, DataSet
        from quantsmind.quantum.data.objectives import ClusteringDistanceObjective
        from quantsmind.quantum.data.problem import DataProblem, DataProblemType

        if not self.is_delegated(problem):
            raise MLValidationError(
                "to_data_problem is only supported for feature selection and clustering"
            )
        dataset = problem.dataset
        if dataset is None:
            raise MLValidationError("a dataset is required to build the delegated problem")
        data_set = DataSet(
            name=dataset.name,
            description=dataset.description,
            features=[
                DataFeature(name=feature.name, kind=feature.kind) for feature in dataset.features
            ],
            records=[
                DataRecord(record_id=record.record_id, values=dict(record.values))
                for record in dataset.records
            ],
        )
        if problem.problem_type is MLProblemType.FEATURE_SELECTION:
            objectives = [
                objective.to_data_objective()
                for objective in problem.objectives
                if objective.kind == "ml_feature_selection"
            ]
            if not objectives:
                raise MLValidationError(
                    "feature-selection problems require an MLFeatureSelectionObjective"
                )
            constraints = [
                constraint.to_data_constraint()
                for constraint in problem.constraints
                if constraint.kind == "ml_feature_count"
            ]
            return DataProblem(
                name=problem.name,
                description=problem.description,
                dataset=data_set,
                problem_type=DataProblemType.FEATURE_SELECTION,
                objectives=objectives,
                constraints=constraints,
            )
        objectives = [
            objective.to_data_objective()
            for objective in problem.objectives
            if objective.kind == "ml_clustering_distance"
        ]
        if not objectives:
            objectives = [
                ClusteringDistanceObjective(name="min_within_cluster_distance"),
            ]
        constraints = [
            constraint.to_data_constraint()
            for constraint in problem.constraints
            if constraint.kind in ("ml_assignment", "ml_cluster_count")
        ]
        if not any(isinstance(c, AssignmentConstraint) for c in constraints):
            constraints.append(AssignmentConstraint(name="assignment"))
        return DataProblem(
            name=problem.name,
            description=problem.description,
            dataset=data_set,
            problem_type=DataProblemType.CLUSTERING,
            objectives=objectives,
            constraints=constraints,
            k=int(problem.k) if problem.k is not None else None,
        )

    def to_quantum_problem(
        self,
        problem: MLProblem,
        *,
        preferred_strategy: Any = None,
    ) -> QuantumProblem:
        """Convert an ML problem into a QMQ :class:`QuantumProblem`.

        Args:
            problem: The validated ML problem.
            preferred_strategy: Optional preferred computation strategy.

        Raises:
            MLValidationError: If the ML problem is invalid.
        """
        self.raise_if_invalid(problem)
        if self.is_delegated(problem):
            from quantsmind.quantum.data.formulation import DataFormulationAdapter

            quantum = DataFormulationAdapter().to_quantum_problem(
                self.to_data_problem(problem), preferred_strategy=preferred_strategy
            )
            problem_name = problem.problem_type.name
            quantum.metadata["domain_layer"] = "ml"
            quantum.metadata["source_domain"] = "data"
            quantum.metadata["formulation_type"] = _FORMULATION_TYPES[problem_name]
            quantum.metadata["ml_problem"] = problem.name
            quantum.provenance["ml"] = {
                "problem_type": problem.problem_type.value,
                "formulation_type": _FORMULATION_TYPES[problem_name],
                "source_domain": "data",
            }
            return quantum
        variables: list[Variable] = problem.decision_variables()
        objectives: list[Objective] = [
            objective.to_quantum_objective(problem) for objective in problem.objectives
        ]
        constraints: list[Constraint] = []
        for constraint in problem.constraints:
            constraints.extend(constraint.to_quantum_constraints(problem))
        problem_name = problem.problem_type.name
        return QuantumProblem(
            name=problem.name,
            description=problem.description,
            domain=_default_domain(problem.context),
            variables=variables,
            objectives=objectives,
            constraints=constraints,
            metadata=self.ml_metadata(problem),
            preferred_strategy=preferred_strategy,
            provenance={
                "domain_layer": "ml",
                "problem_type": problem.problem_type.value,
                "formulation_type": _FORMULATION_TYPES[problem_name],
            },
        )

    def formulate(self, problem: MLProblem) -> Any:
        """Return the existing QMQ formulation of an ML problem.

        Delegates to the existing :func:`quantsmind.quantum.formulation
        .formulate`, producing an :class:`OptimizationModel` (or another
        :class:`MathematicalModel` selected by the existing rules).
        """
        from quantsmind.quantum.formulation import formulate as qmq_formulate

        return qmq_formulate(self.to_quantum_problem(problem))
