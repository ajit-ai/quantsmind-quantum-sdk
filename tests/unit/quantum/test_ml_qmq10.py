"""QMQ-10 AI/ML Intelligence Foundation tests.

Covers the ML domain models (features, records, datasets, candidates,
hyperparameters), the ML context, least-squares classification/regression
objectives and constraints, one-hot model-selection and hyperparameter
objectives/constraints, the MLProblem representation, validation,
deterministic serialization, mapping, reuse of the existing QMQ-02
formulation / QUBO mapping, classical solving with known optima (examples
A/B, D/E, plus delegated C/F through QMQ-09), benchmarking against the
classical baseline, QMQ-06 interpretation, deterministic repeated runs, the
MicroQuantum-blocked subprocess path and the canonical examples A–F.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from quantsmind.quantum import (
    ClassificationSolution,
    DataSolution,
    MLFeatureSelectionSolution,
    MLFormulationAdapter,
    MLMapper,
    MLMetrics,
    MLProblem,
    MLProblemType,
    MLValidationError,
    OptimizationModel,
    QUBOMapper,
)
from quantsmind.quantum.ml import (
    ClassificationLossObjective,
    HyperparameterObjective,
    HyperparameterOnePerParameterConstraint,
    MLAssignmentConstraint,
    MLBaseSolution,
    MLClusterCountConstraint,
    MLClusteringDistanceObjective,
    MLCoefficientCountConstraint,
    MLContext,
    MLDataSet,
    MLFeature,
    MLFeatureCountConstraint,
    MLFeatureSelectionObjective,
    MLHyperparameter,
    MLHyperparameterChoice,
    MLModelCandidate,
    MLOptimizationConfiguration,
    MLOptimizationResult,
    MLOptimizer,
    MLRecord,
    ModelSelectionObjective,
    ModelSelectionOneHotConstraint,
    RegressionLossObjective,
)
from quantsmind.quantum.ml.examples import (
    ml_all_examples,
    ml_classification_example,
    ml_clustering_example,
    ml_dataset_example,
    ml_feature_selection_example,
    ml_hyperparameter_example,
    ml_model_selection_example,
    ml_regression_example,
)

_SRC = str(Path(__file__).parents[3] / "src")

_ML_NAME = "ml_test_demo"


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------


def _dataset() -> MLDataSet:
    return ml_dataset_example()


def _classification() -> MLProblem:
    return ml_classification_example()


def _regression() -> MLProblem:
    return ml_regression_example()


def _feature_selection() -> MLProblem:
    return ml_feature_selection_example()


def _model_selection() -> MLProblem:
    return ml_model_selection_example()


def _hyperparameter() -> MLProblem:
    return ml_hyperparameter_example()


def _clustering() -> MLProblem:
    return ml_clustering_example()


def _solver() -> MLOptimizer:
    return MLOptimizer(default_seed=7, default_shots=1024)


# ----------------------------------------------------------------------
# observations / features / datasets
# ----------------------------------------------------------------------


class TestMLModels:
    def test_feature_defaults(self) -> None:
        feature = MLFeature(name="f0")
        assert feature.kind == "numeric"
        assert feature.description == ""
        assert feature.metadata == {}

    def test_feature_rejects_empty_name(self) -> None:
        with pytest.raises(MLValidationError):
            MLFeature(name="   ")

    def test_record_value_missing_and_target(self) -> None:
        record = MLRecord(record_id="r0", values={"f0": 0.0, "f1": 1.0}, target=2.0)
        assert record.value("f0") == 0.0
        with pytest.raises(KeyError):
            record.value("missing")
        assert record.target == 2.0

    def test_record_as_feature_vector(self) -> None:
        record = MLRecord(record_id="r0", values={"a": 1.0, "b": 2.0})
        features = [MLFeature(name="a"), MLFeature(name="b")]
        assert record.as_feature_vector(features) == [1.0, 2.0]

    def test_dataset_shape_and_orders(self) -> None:
        dataset = _dataset()
        assert dataset.shape == (3, 4)  # (num_features, num_records), as DataSet
        assert dataset.feature_names == ["f0", "f1", "f2"]
        assert dataset.record_ids == ["r0", "r1", "r2", "r3"]
        assert dataset.targets() == [2.0, 4.0, 1.0, 5.0]
        assert dataset.matrix() == [
            [0.0, 1.0, 2.0],
            [1.0, 2.0, 0.0],
            [0.0, 0.0, 1.0],
            [2.0, 1.0, 1.0],
        ]

    def test_dataset_validate(self) -> None:
        assert _dataset().validate() == []

    def test_dataset_round_trip(self) -> None:
        dataset = _dataset()
        assert MLDataSet.from_dict(dataset.to_dict()).to_dict() == dataset.to_dict()

    def test_dataset_rejects_duplicate_features(self) -> None:
        with pytest.raises(MLValidationError):
            MLDataSet(name="d", features=[MLFeature(name="f0"), MLFeature(name="f0")])

    def test_candidate_objective(self) -> None:
        candidate = MLModelCandidate(model_id="M1", validation_loss=3.0, complexity_penalty=0.5)
        assert candidate.objective() == 3.5

    def test_hyperparameter_choice_count(self) -> None:
        hyperparameter = MLHyperparameter(
            name="learning_rate",
            choices=[
                MLHyperparameterChoice(value=0.01, gain=1.5),
                MLHyperparameterChoice(value=0.1, gain=1.2),
            ],
        )
        assert hyperparameter.choice_count == 2
        assert (
            MLHyperparameter.from_dict(hyperparameter.to_dict()).to_dict()
            == hyperparameter.to_dict()
        )


# ----------------------------------------------------------------------
# ml context
# ----------------------------------------------------------------------


class TestMLContext:
    def test_defaults(self) -> None:
        context = MLContext()
        assert context.purpose == ""
        assert context.subdomain == "tabular"
        assert context.preferred_strategy == ""
        assert context.assumptions == {}

    def test_preferred_strategy_validated(self) -> None:
        context = MLContext(preferred_strategy="Classical")
        assert context.preferred_strategy == "classical"

    def test_preferred_strategy_rejects_unknown(self) -> None:
        with pytest.raises(MLValidationError):
            MLContext(preferred_strategy="quantum_magic")

    def test_to_domain_context(self) -> None:
        context = MLContext(purpose="regression", assumptions={"source": "synthetic"})
        domain = context.to_domain_context()
        assert domain.domain == "ml"
        assert domain.subdomain == "tabular"
        assert domain.use_case == "optimization"
        assert domain.context_metadata["purpose"] == "regression"
        assert domain.metadata["ml"]["assumptions"] == {"source": "synthetic"}

    def test_round_trip(self) -> None:
        context = MLContext(purpose="classification", preferred_strategy="classical")
        assert MLContext.from_dict(context.to_dict()).to_dict() == context.to_dict()


# ----------------------------------------------------------------------
# objectives
# ----------------------------------------------------------------------


class TestMLObjectives:
    def test_fitting_objective_sense(self) -> None:
        problem = _classification()
        objective = problem.objectives[0]
        assert isinstance(objective, ClassificationLossObjective)
        assert objective.kind == "classification_loss"
        quantum = objective.to_quantum_objective(problem)
        assert quantum.sense.name == "MINIMIZE"

    def test_fitting_expression_parses(self) -> None:
        quantum = _classification().objectives[0].to_quantum_objective(_classification())
        expression = str(quantum.expression)
        assert "w0" in expression
        assert "w1" in expression
        assert "w2" in expression
        assert "46" in expression  # constant term sum(y^2)

    def test_model_selection_objective(self) -> None:
        problem = _model_selection()
        objective = problem.objectives[0]
        assert objective.kind == "model_selection"
        quantum = objective.to_quantum_objective(problem)
        assert quantum.sense.name == "MINIMIZE"

    def test_hyperparameter_objective_maximizes_gain(self) -> None:
        problem = _hyperparameter()
        objective = problem.objectives[0]
        assert objective.kind == "hyperparameter"
        quantum = objective.to_quantum_objective(problem)
        assert quantum.sense.name == "MAXIMIZE"

    def test_feature_selection_to_data_objective(self) -> None:
        objective = _feature_selection().objectives[0]
        data = objective.to_data_objective()
        assert data.name == "max_utility"

    def test_clustering_to_data_objective(self) -> None:
        objective = _clustering().objectives[0]
        data = objective.to_data_objective()
        assert data.name == "min_within_cluster_distance"

    def test_objective_rejects_empty_name(self) -> None:
        with pytest.raises(MLValidationError):
            ClassificationLossObjective(name="   ")


# ----------------------------------------------------------------------
# constraints
# ----------------------------------------------------------------------


class TestMLConstraints:
    def test_coefficient_count_quantum_constraints(self) -> None:
        problem = _classification()
        (constraint,) = problem.constraints
        assert isinstance(constraint, MLCoefficientCountConstraint)
        constraints = constraint.to_quantum_constraints(problem)
        assert len(constraints) == 2  # max (<= 3) and min (>= 1)
        operator_names = sorted(c.operator.value for c in constraints)
        assert operator_names == ["<=", ">="]

    def test_one_hot_model_selection(self) -> None:
        (constraint,) = _model_selection().constraints
        assert isinstance(constraint, ModelSelectionOneHotConstraint)
        constraints = constraint.to_quantum_constraints(_model_selection())
        assert len(constraints) == 1

    def test_one_per_parameter_constraints(self) -> None:
        (constraint,) = _hyperparameter().constraints
        assert isinstance(constraint, HyperparameterOnePerParameterConstraint)
        constraints = constraint.to_quantum_constraints(_hyperparameter())
        assert len(constraints) == 2

    def test_feature_count_to_data_constraint(self) -> None:
        objective = _feature_selection().constraints[0]
        data = objective.to_data_constraint()
        assert data.name == "at_most_two"

    def test_assignment_and_cluster_count_to_data(self) -> None:
        (assignment, cluster_size) = _clustering().constraints
        assert isinstance(assignment, MLAssignmentConstraint)
        assert isinstance(cluster_size, MLClusterCountConstraint)
        assert assignment.to_data_constraint().name == "assignment"
        assert cluster_size.to_data_constraint().name == "cluster_size"

    def test_constraint_rejects_empty_name(self) -> None:
        with pytest.raises(MLValidationError):
            MLFeatureCountConstraint(name="   ")


# ----------------------------------------------------------------------
# problem representation + validation
# ----------------------------------------------------------------------


class TestMLProblem:
    def test_problem_type_parse(self) -> None:
        assert MLProblemType.parse("classification") is MLProblemType.CLASSIFICATION
        assert MLProblemType.parse("model_selection") is MLProblemType.MODEL_SELECTION
        with pytest.raises(MLValidationError):
            MLProblemType.parse("magic")

    def test_classification_validation(self) -> None:
        problem = _classification()
        assert problem.validate() == []
        assert problem.problem_type is MLProblemType.CLASSIFICATION
        assert problem.size == 3
        assert [v.name for v in problem.decision_variables()] == ["w0", "w1", "w2"]

    def test_model_selection_validation(self) -> None:
        problem = _model_selection()
        assert problem.validate() == []
        assert [v.name for v in problem.decision_variables()] == ["s0", "s1", "s2", "s3"]
        assert problem.size == 4

    def test_hyperparameter_variables_parameter_major(self) -> None:
        problem = _hyperparameter()
        assert problem.validate() == []
        assert [v.name for v in problem.decision_variables()] == [
            "h0_0",
            "h0_1",
            "h0_2",
            "h1_0",
            "h1_1",
            "h1_2",
        ]
        assert problem.hyperparameter_choice_counts == [3, 3]

    def test_delegated_raises_decision_variables(self) -> None:
        with pytest.raises(MLValidationError):
            _feature_selection().decision_variables()
        with pytest.raises(MLValidationError):
            _clustering().decision_variables()

    def test_classification_requires_dataset(self) -> None:
        with pytest.raises(MLValidationError):
            MLProblem(
                name=_ML_NAME,
                problem_type=MLProblemType.CLASSIFICATION,
                objectives=[ClassificationLossObjective(name="ssr")],
            )

    def test_model_selection_requires_candidates(self) -> None:
        with pytest.raises(MLValidationError):
            MLProblem(
                name=_ML_NAME,
                problem_type=MLProblemType.MODEL_SELECTION,
                objectives=[ModelSelectionObjective(name="loss")],
            )

    def test_hyperparameter_requires_hyperparameters(self) -> None:
        with pytest.raises(MLValidationError):
            MLProblem(
                name=_ML_NAME,
                problem_type=MLProblemType.HYPERPARAMETER_OPTIMIZATION,
                objectives=[HyperparameterObjective(name="gain")],
            )

    def test_clustering_requires_k(self) -> None:
        with pytest.raises(MLValidationError):
            MLProblem(
                name=_ML_NAME,
                dataset=_dataset(),
                problem_type=MLProblemType.CLUSTERING,
                objectives=[MLClusteringDistanceObjective(name="distance")],
            )

    def test_candidates_only_for_model_selection(self) -> None:
        with pytest.raises(MLValidationError):
            MLProblem(
                name=_ML_NAME,
                dataset=_dataset(),
                problem_type=MLProblemType.CLASSIFICATION,
                objectives=[ClassificationLossObjective(name="ssr")],
                candidates=[MLModelCandidate(model_id="M1")],
            )

    def test_k_only_for_clustering(self) -> None:
        with pytest.raises(MLValidationError):
            MLProblem(
                name=_ML_NAME,
                dataset=_dataset(),
                problem_type=MLProblemType.FEATURE_SELECTION,
                objectives=[MLFeatureSelectionObjective(name="u", utilities={"f0": 1.0})],
                k=2,
            )

    def test_requires_objectives(self) -> None:
        problem = MLProblem(
            name=_ML_NAME,
            dataset=_dataset(),
            problem_type=MLProblemType.CLASSIFICATION,
            objectives=[],
        )
        with pytest.raises(MLValidationError):
            problem.raise_if_invalid()

    def test_duplicate_objective_names(self) -> None:
        with pytest.raises(MLValidationError):
            MLProblem(
                name=_ML_NAME,
                dataset=_dataset(),
                problem_type=MLProblemType.CLASSIFICATION,
                objectives=[
                    ClassificationLossObjective(name="ssr"),
                    ClassificationLossObjective(name="ssr"),
                ],
            )

    def test_objective_kind_not_allowed_for_problem(self) -> None:
        problem = MLProblem(
            name=_ML_NAME,
            dataset=_dataset(),
            problem_type=MLProblemType.CLASSIFICATION,
            objectives=[RegressionLossObjective(name="ssr")],
        )
        issues = problem.validate()
        assert any("not valid for classification" in issue for issue in issues)

    def test_round_trips(self) -> None:
        for problem in (
            _classification(),
            _regression(),
            _feature_selection(),
            _model_selection(),
            _hyperparameter(),
            _clustering(),
        ):
            rebuilt = MLProblem.from_dict(problem.to_dict())
            assert rebuilt.to_dict() == problem.to_dict(), problem.name
            assert rebuilt.problem_type is problem.problem_type


# ----------------------------------------------------------------------
# formulation (delegated + native)
# ----------------------------------------------------------------------


class TestMLFormulation:
    def test_native_formulation(self) -> None:
        quantum = MLFormulationAdapter().to_quantum_problem(_classification())
        assert [v.name for v in quantum.variables] == ["w0", "w1", "w2"]
        assert quantum.metadata["domain_layer"] == "ml"
        assert quantum.metadata["source_domain"] == "ml"
        assert quantum.metadata["formulation_type"] == "linear_least_squares"
        assert quantum.metadata["problem_type"] == "classification"
        assert quantum.provenance["domain_layer"] == "ml"

    def test_delegated_formulation(self) -> None:
        quantum = MLFormulationAdapter().to_quantum_problem(_feature_selection())
        assert quantum.metadata["source_domain"] == "data"
        assert quantum.metadata["formulation_type"] == "delegated_data"
        assert quantum.metadata["ml_problem"] == "ml_feature_selection_demo"
        assert quantum.provenance["ml"]["source_domain"] == "data"

    def test_clustering_delegated_problem(self) -> None:
        data_problem = MLFormulationAdapter().to_data_problem(_clustering())
        assert data_problem.problem_type.value == "clustering"
        assert data_problem.k == 2
        assert data_problem.validate() == []
        quantum = MLFormulationAdapter().to_quantum_problem(_clustering())
        assert quantum.metadata["source_domain"] == "data"
        assert [v.name for v in quantum.variables] == [
            "z0_0",
            "z0_1",
            "z1_0",
            "z1_1",
            "z2_0",
            "z2_1",
            "z3_0",
            "z3_1",
        ]

    def test_optimization_model_formulated(self) -> None:
        model = MLFormulationAdapter().formulate(_classification())
        assert isinstance(model, OptimizationModel)

    def test_qubo_mapping_reused(self) -> None:
        quantum = MLFormulationAdapter().to_quantum_problem(_hyperparameter())
        mapped = QUBOMapper().map(quantum)
        assert mapped.payload.variables == ["h0_0", "h0_1", "h0_2", "h1_0", "h1_1", "h1_2"]

    def test_formulate_delegated(self) -> None:
        model = MLFormulationAdapter().formulate(_feature_selection())
        assert isinstance(model, OptimizationModel)


# ----------------------------------------------------------------------
# mapping / decoding
# ----------------------------------------------------------------------


class TestMLMapping:
    def test_coefficient_mapping(self) -> None:
        mapping = MLMapper().map(_classification())
        assert mapping.variable_names == ["w0", "w1", "w2"]
        decoded = mapping.decode_assignments({"w0": 1.0, "w1": 1.0, "w2": 1.0})
        names = [item.feature_name for item in decoded]
        assert names == ["f0", "f1", "f2"]
        assert all(item.selected for item in decoded)
        assert all(item.value == 1.0 for item in decoded)

    def test_model_selection_mapping(self) -> None:
        mapping = MLMapper().map(_model_selection())
        assert mapping.variable_names == ["s0", "s1", "s2", "s3"]
        decoded = mapping.decode_assignments({"s3": 1.0})
        assert [item.model_id for item in decoded] == ["M1", "M2", "M3", "M4"]
        assert decoded[3].selected and not decoded[0].selected
        assert mapping.candidate("M4").variable_name == "s3"

    def test_hyperparameter_mapping(self) -> None:
        mapping = MLMapper().map(_hyperparameter())
        assert mapping.variable_names == ["h0_0", "h0_1", "h0_2", "h1_0", "h1_1", "h1_2"]
        decoded = mapping.decode_assignments({"h0_1": 1.0, "h1_1": 1.0})
        selected = [(item.parameter_name, item.choice_value) for item in decoded if item.selected]
        assert selected == [("learning_rate", 0.01), ("depth", 2)]

    def test_delegated_mapping_raises(self) -> None:
        with pytest.raises(MLValidationError):
            MLMapper().map(_feature_selection())
        with pytest.raises(MLValidationError):
            MLMapper().map(_clustering())


# ----------------------------------------------------------------------
# metrics
# ----------------------------------------------------------------------


class TestMLMetrics:
    def test_fitting_metrics(self) -> None:
        metrics = MLMetrics.compute(_classification(), {"w0": 1.0, "w1": 1.0, "w2": 1.0})
        assert metrics.problem_type == "classification"
        assert metrics.ssr == pytest.approx(3.0)
        assert metrics.mse == pytest.approx(0.75)
        assert metrics.selected_feature_count == 3

    def test_model_selection_metrics(self) -> None:
        metrics = MLMetrics.compute(_model_selection(), {"s3": 1.0})
        assert metrics.selected_model_id == "M4"
        assert metrics.selected_loss == pytest.approx(2.7)
        assert metrics.selected_penalty == pytest.approx(0.1)
        assert metrics.objective_value == pytest.approx(2.8)

    def test_hyperparameter_metrics(self) -> None:
        metrics = MLMetrics.compute(_hyperparameter(), {"h0_1": 1.0, "h1_1": 1.0})
        assert metrics.total_gain == pytest.approx(3.3)
        assert metrics.objective_value == pytest.approx(3.3)

    def test_metrics_round_trip(self) -> None:
        metrics = MLMetrics.compute(_classification(), {"w0": 1.0, "w1": 1.0, "w2": 1.0})
        assert MLMetrics.from_dict(metrics.to_dict()).to_dict() == metrics.to_dict()


# ----------------------------------------------------------------------
# optimizer solve / benchmark (classical)
# ----------------------------------------------------------------------


class TestMLOptimizer:
    def test_classification_solve(self) -> None:
        result = _solver().solve(_classification(), strategy="classical")
        assert result.report is not None
        assert result.solution is not None
        assert isinstance(result.solution, ClassificationSolution)
        solution = result.solution
        assert solution.problem_type == "classification"
        assert solution.coefficients == {"f0": 1.0, "f1": 1.0, "f2": 1.0}
        assert solution.selected_features == ["f0", "f1", "f2"]
        assert solution.objective_value == pytest.approx(3.0)
        assert solution.feasible is True
        assert solution.metrics.ssr == pytest.approx(3.0)
        assert solution.solver == "classical/exhaustive"
        assert solution.strategy == "classical"
        assert solution.num_variables == 3
        assert solution.constraint_status
        assert result.interpretation is not None

    def test_regression_solve(self) -> None:
        result = _solver().solve(_regression(), strategy="classical")
        assert result.solution.objective_value == pytest.approx(3.0)
        assert result.solution.problem_type == "regression"

    def test_model_selection_solve(self) -> None:
        result = _solver().solve(_model_selection(), strategy="classical")
        solution = result.solution
        assert solution.selected_model_id == "M4"
        assert solution.objective_value == pytest.approx(2.8)
        assert solution.feasible is True
        assert solution.metrics.selected_model_id == "M4"

    def test_hyperparameter_solve(self) -> None:
        result = _solver().solve(_hyperparameter(), strategy="classical")
        solution = result.solution
        assert solution.selected_choices == {"learning_rate": 0.01, "depth": 2}
        assert solution.objective_value == pytest.approx(3.3)
        assert solution.metrics.total_gain == pytest.approx(3.3)

    def test_feature_selection_delegated_solve(self) -> None:
        result = _solver().solve(_feature_selection(), strategy="classical")
        solution = result.solution
        assert isinstance(solution, MLFeatureSelectionSolution)
        assert solution.selected_features == ["f0", "f1"]
        assert solution.selected_utility == pytest.approx(8.0)
        assert solution.objective_value == pytest.approx(6.0)
        assert solution.feasible is True
        assert result.interpretation is not None

    def test_clustering_delegated_solve(self) -> None:
        result = _solver().solve(_clustering(), strategy="classical")
        solution = result.solution
        assert isinstance(solution, DataSolution)
        assert solution.cluster_assignments == {"r0": 0, "r1": 1, "r2": 0, "r3": 1}
        assert solution.cluster_count == 2
        assert solution.feasible is True

    def test_benchmark_native(self) -> None:
        result = _solver().benchmark(_classification(), strategy="classical", known_optimum=3.0)
        assert result.benchmark is not None
        assert result.benchmark.status == "executed"
        assert result.benchmark.metrics is not None
        assert result.solution is not None
        assert result.solution.objective_value == pytest.approx(3.0)
        assert result.interpretation is not None

    def test_benchmark_delegated(self) -> None:
        result = _solver().benchmark(_feature_selection(), strategy="classical", known_optimum=6.0)
        assert result.benchmark is not None
        assert result.benchmark.status == "executed"
        assert result.solution is not None

    def test_deterministic_repeated_runs(self) -> None:
        first = _solver().solve(_classification(), strategy="classical").solution
        second = _solver().solve(_classification(), strategy="classical").solution
        assert first.coefficients == second.coefficients
        assert first.objective_value == second.objective_value

    def test_mapping_optimizer_facade(self) -> None:
        mapping = _solver().mapping(_classification())
        assert mapping.variable_names == ["w0", "w1", "w2"]

    def test_solve_invalid_raises(self) -> None:
        with pytest.raises(MLValidationError):
            problem = MLProblem(name=_ML_NAME, problem_type=MLProblemType.CLASSIFICATION)
            _solver().solve(problem, strategy="classical")

    def test_configuration_validation(self) -> None:
        config = MLOptimizationConfiguration(shots=2048, seed=3, solver_max_variables=21)
        assert config.shots == 2048
        with pytest.raises(MLValidationError):
            MLOptimizationConfiguration(shots=0)
        with pytest.raises(MLValidationError):
            MLOptimizationConfiguration(optimization_level=9)
        with pytest.raises(MLValidationError):
            MLOptimizationConfiguration(preferred_strategy="magic")
        assert MLOptimizationConfiguration.from_dict(config.to_dict()).to_dict() == config.to_dict()


# ----------------------------------------------------------------------
# serialization of solutions + results
# ----------------------------------------------------------------------


class TestMLSerialization:
    def test_classification_solution_round_trip(self) -> None:
        solution = _solver().solve(_classification(), strategy="classical").solution
        assert isinstance(solution, ClassificationSolution)
        rebuilt = ClassificationSolution.from_dict(solution.to_dict())
        assert rebuilt.problem_name == solution.problem_name
        assert rebuilt.coefficients == solution.coefficients
        assert rebuilt.predictions == solution.predictions
        assert rebuilt.metrics.to_dict() == solution.metrics.to_dict()

    def test_result_round_trip_with_benchmark(self) -> None:
        result = _solver().benchmark(_classification(), strategy="classical")
        rebuilt = MLOptimizationResult.from_dict(result.to_dict())
        assert rebuilt.solution is not None
        assert rebuilt.solution.coefficients == result.solution.coefficients
        assert rebuilt.benchmark is not None
        assert rebuilt.benchmark.status == "executed"

    def test_delegated_feature_selection_result_round_trip(self) -> None:
        result = _solver().solve(_feature_selection(), strategy="classical")
        rebuilt = MLOptimizationResult.from_dict(result.to_dict())
        assert isinstance(rebuilt.solution, MLFeatureSelectionSolution)
        assert rebuilt.solution.selected_features == ["f0", "f1"]
        assert rebuilt.solution.selected_utility == pytest.approx(8.0)
        assert rebuilt.solution.objective_value == pytest.approx(6.0)

    def test_delegated_clustering_result_round_trip(self) -> None:
        result = _solver().solve(_clustering(), strategy="classical")
        rebuilt = MLOptimizationResult.from_dict(result.to_dict())
        assert hasattr(rebuilt.solution, "cluster_assignments")
        assert rebuilt.solution.cluster_assignments == {"r0": 0, "r1": 1, "r2": 0, "r3": 1}

    def test_ml_base_solution_requires_name(self) -> None:
        with pytest.raises(ValueError):
            MLBaseSolution(problem_type="classification")


# ----------------------------------------------------------------------
# canonical examples
# ----------------------------------------------------------------------


class TestMLExamples:
    def test_examples_build(self) -> None:
        assert _dataset().name == "qm10_demo"
        assert _classification().name == "ml_classification_demo"
        assert _regression().name == "ml_regression_demo"
        assert _feature_selection().name == "ml_feature_selection_demo"
        assert _model_selection().name == "ml_model_selection_demo"
        assert _hyperparameter().name == "ml_hyperparameter_demo"
        assert _clustering().name == "ml_clustering_demo"

    def test_all_examples(self) -> None:
        artifacts = ml_all_examples()
        assert any("dataset feature order: ['f0', 'f1', 'f2']" in line for line in artifacts)
        assert any("classification variables: ['w0', 'w1', 'w2']" in line for line in artifacts)

    def test_serialization_example(self) -> None:
        classifier = MLProblemType.CLASSIFICATION
        classification = _classification()
        rebuilt = MLProblem.from_dict(classification.to_dict())
        assert rebuilt.problem_type is classifier
        assert rebuilt.to_dict() == classification.to_dict()


# ----------------------------------------------------------------------
# public exports
# ----------------------------------------------------------------------


class TestPublicExports:
    def test_ml_module_exports(self) -> None:
        import quantsmind.quantum.ml as ml_module

        for name in [
            "MLProblem",
            "MLProblemType",
            "MLDataSet",
            "MLFeature",
            "MLRecord",
            "MLContext",
            "ClassificationLossObjective",
            "MLMapper",
            "MLMetrics",
            "MLOptimizer",
            "MLOptimizationResult",
        ]:
            assert hasattr(ml_module, name), name

    def test_root_exports_ml_layer(self) -> None:
        import quantsmind.quantum as quantum_module

        for name in [
            "MLProblem",
            "MLOptimizer",
            "MLFormulationAdapter",
            "ClassificationSolution",
            "MLMapper",
            "MLMetrics",
            "MLFeatureSelectionSolution",
            "ml_dataset_example",
            "ml_all_examples",
        ]:
            assert name in quantum_module.__all__, name
            assert hasattr(quantum_module, name), name


# ----------------------------------------------------------------------
# no microquantum dependency (blocked subprocess)
# ----------------------------------------------------------------------


class TestNoMicroQuantum:
    @staticmethod
    def _blocked_rc(source: str) -> tuple[int, str]:
        code = (
            "import sys\n"
            "class _Blocker:\n"
            "    def find_spec(self, fullname, path=None, target=None):\n"
            "        if fullname == 'microquantum' or fullname.startswith('microquantum.'):\n"
            "            raise ModuleNotFoundError('blocked')\n"
            "        return None\n"
            "sys.meta_path.insert(0, _Blocker())\n" + source
        )
        env = {**os.environ, "PYTHONPATH": _SRC}
        run = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            env=env,
            timeout=180,
        )
        return run.returncode, run.stdout

    def test_import_and_construction_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.ml.examples import (
    ml_classification_example,
    ml_model_selection_example,
)
problem = ml_classification_example()
assert problem.validate() == []
assert problem.decision_variables()[0].name == "w0"
selection = ml_model_selection_example()
assert selection.decision_variables()[3].name == "s3"
print("ML_OK")
"""
        )
        assert rc == 0, out
        assert "ML_OK" in out

    def test_classical_solve_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.ml.optimizer import MLOptimizer
from quantsmind.quantum.ml.examples import ml_classification_example
result = MLOptimizer(default_seed=7).solve(
    ml_classification_example(), strategy="classical"
)
solution = result.solution
assert solution is not None
assert solution.feasible is True
assert solution.objective_value == 3.0
assert result.interpretation is not None
print("ML_OK")
"""
        )
        assert rc == 0, out
        assert "ML_OK" in out

    def test_delegated_solve_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.ml.optimizer import MLOptimizer
from quantsmind.quantum.ml.examples import ml_feature_selection_example, ml_clustering_example
result = MLOptimizer(default_seed=7).solve(
    ml_feature_selection_example(), strategy="classical"
)
assert result.solution.selected_features == ["f0", "f1"]
cluster = MLOptimizer(default_seed=7).solve(
    ml_clustering_example(), strategy="classical"
)
assert cluster.solution.cluster_assignments == {"r0": 0, "r1": 1, "r2": 0, "r3": 1}
print("ML_OK")
"""
        )
        assert rc == 0, out
        assert "ML_OK" in out

    def test_classical_benchmark_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.ml.optimizer import MLOptimizer
from quantsmind.quantum.ml.examples import ml_model_selection_example
result = MLOptimizer(default_seed=7).benchmark(
    ml_model_selection_example(), strategy="classical"
)
assert result.benchmark is not None
assert result.benchmark.status == "executed"
assert result.interpretation is not None
print("ML_OK")
"""
        )
        assert rc == 0, out
        assert "ML_OK" in out

    def test_quantum_request_honest_downgrade_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.ml.optimizer import MLOptimizer
from quantsmind.quantum.ml.examples import ml_classification_example
result = MLOptimizer(default_seed=7).solve(
    ml_classification_example(), strategy="quantum"
)
solution = result.solution
assert solution is not None
assert result.report is not None
assert result.report.strategy.name.lower() == "classical"
assert solution.feasible is True
print("ML_OK")
"""
        )
        assert rc == 0, out
        assert "ML_OK" in out

    def test_interpretation_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.ml.optimizer import MLOptimizer
from quantsmind.quantum.ml.examples import ml_hyperparameter_example
result = MLOptimizer(default_seed=7).solve(
    ml_hyperparameter_example(), strategy="classical"
)
assert result.interpretation.status.value == "executed"
assert result.interpretation.solution_quality.value == "feasible"
print("ML_OK")
"""
        )
        assert rc == 0, out
        assert "ML_OK" in out
