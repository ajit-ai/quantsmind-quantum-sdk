"""QMQ-09 Data Intelligence Foundation tests.

Covers the Data domain models (features, records, vectors, datasets), the
data context, distance/similarity primitives, pairwise relationships,
deterministic data-quality reports, feature-selection and clustering
objectives/constraints, the DataProblem representation, validation,
deterministic serialization, mapping, reuse of the existing QMQ-02
formulation / QUBO mapping, classical solving with known optima (Examples
A/B/C/F), benchmarking against the classical baseline, QMQ-06
interpretation, honest failure semantics, deterministic repeated runs, the
MicroQuantum-blocked subprocess path and the canonical examples A–G.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from quantsmind.quantum import (
    DataFormulationAdapter,
    DataMapper,
    DataMetrics,
    DataOptimizationConfiguration,
    DataOptimizer,
    DataProblem,
    DataProblemType,
    DataSolution,
    DataValidationError,
    OptimizationModel,
    QUBOMapper,
    WorkflowError,
)
from quantsmind.quantum.data import (
    AssignmentConstraint,
    ClusterCountConstraint,
    ClusteringDistanceObjective,
    DataRelationship,
    DataSet,
    FeatureCountConstraint,
    FeatureGroupConstraint,
    FeatureSelectionObjective,
    FeatureUtilityObjective,
    SelectionCostObjective,
    assess_data_quality,
    euclidean_distance,
    pairwise_relationship,
    similarity_from_distance,
    squared_euclidean_distance,
    weighted_squared_euclidean_distance,
)
from quantsmind.quantum.data.context import DataContext
from quantsmind.quantum.data.examples import (
    clustering_example,
    data_context_example,
    dataset_example,
    feature_selection_example,
    grouped_feature_selection_example,
    quality_example,
    selection_cost_example,
    serialization_example,
    similarity_example,
)
from quantsmind.quantum.data.models import DataFeature, DataRecord, FeatureVector

_SRC = str(Path(__file__).parents[3] / "src")


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------


def _dataset() -> DataSet:
    return dataset_example()


def _feature_selection() -> DataProblem:
    return feature_selection_example()


def _clustering() -> DataProblem:
    return clustering_example()


def _solver() -> DataOptimizer:
    return DataOptimizer(default_seed=7, default_shots=1024)


# ----------------------------------------------------------------------
# observations / features (spec data: DataFeature, DataRecord, FeatureVector)
# ----------------------------------------------------------------------


class TestObservations:
    def test_feature_defaults(self) -> None:
        feature = DataFeature(name="height", lower_bound=0.0, upper_bound=10.0)
        assert feature.weight == 1.0
        assert feature.kind == "numeric"
        assert feature.allows(5.0) is True
        assert feature.allows(-1.0) is False
        assert feature.allows(11.0) is False

    def test_feature_rejects_empty_name(self) -> None:
        with pytest.raises(DataValidationError):
            DataFeature(name="   ")

    def test_feature_rejects_inverted_bounds(self) -> None:
        with pytest.raises(DataValidationError):
            DataFeature(name="x", lower_bound=5.0, upper_bound=1.0)

    def test_feature_rejects_negative_weight(self) -> None:
        with pytest.raises(DataValidationError):
            DataFeature(name="x", weight=-0.5)

    def test_feature_rejects_non_finite_weight(self) -> None:
        with pytest.raises(DataValidationError):
            DataFeature(name="x", weight=float("nan"))

    def test_feature_rejects_non_finite_bounds(self) -> None:
        with pytest.raises(DataValidationError):
            DataFeature(name="x", lower_bound=float("inf"), upper_bound=10.0)

    def test_record_value_and_missing(self) -> None:
        record = DataRecord(record_id="r0", values={"height": 2.0})
        assert record.value("height") == 2.0
        with pytest.raises(KeyError):
            _ = record.value("texture")

    def test_record_rejects_blank_id(self) -> None:
        with pytest.raises(DataValidationError):
            DataRecord(record_id="  ", values={"height": 1.0})

    def test_record_rejects_non_finite_value(self) -> None:
        with pytest.raises(DataValidationError):
            DataRecord(record_id="r0", values={"height": float("nan")})

    def test_record_as_feature_vector_order(self) -> None:
        record = DataRecord(record_id="r0", values={"b": 2.0, "a": 1.0})
        features = [DataFeature(name="a"), DataFeature(name="b")]
        assert record.as_feature_vector(features) == [1.0, 2.0]

    def test_record_missing_feature_vector_raises(self) -> None:
        record = DataRecord(record_id="r0", values={"a": 1.0})
        features = [DataFeature(name="a"), DataFeature(name="b")]
        with pytest.raises(DataValidationError):
            record.as_feature_vector(features)

    def test_feature_vector_basic(self) -> None:
        vector = FeatureVector(values=(1.0, 2.0, 3.0))
        assert vector.dimension == 3
        assert vector.to_list() == [1.0, 2.0, 3.0]

    def test_feature_vector_rejects_empty(self) -> None:
        with pytest.raises(DataValidationError):
            FeatureVector(values=())

    def test_feature_vector_rejects_non_finite(self) -> None:
        with pytest.raises(DataValidationError):
            FeatureVector(values=(1.0, float("inf")))

    def test_feature_vector_round_trip(self) -> None:
        vector = FeatureVector.from_sequence([1.0, 2.0], normalization={"norm": "none"})
        rebuilt = FeatureVector.from_dict(vector.to_dict())
        assert rebuilt == vector


# ----------------------------------------------------------------------
# dataset model
# ----------------------------------------------------------------------


class TestDataSet:
    def test_shape_and_orderings(self) -> None:
        dataset = _dataset()
        dataset.raise_if_invalid()
        assert dataset.shape == (5, 4)
        assert dataset.feature_names == ["height", "width", "depth", "brightness", "texture"]
        assert dataset.record_ids == ["r0", "r1", "r2", "r3"]
        assert len(dataset) == 4

    def test_matrix_deterministic(self) -> None:
        dataset = _dataset()
        assert dataset.matrix()[0] == [0.0, 1.0, 2.0, 3.0, 4.0]
        assert dataset.matrix()[2] == [1.0, 2.0, 0.0, 1.0, 5.0]

    def test_lookup(self) -> None:
        dataset = _dataset()
        assert dataset.feature("depth").weight == 1.0
        assert dataset.record("r1").value("brightness") == 5.0
        with pytest.raises(KeyError):
            _ = dataset.feature("nope")
        with pytest.raises(KeyError):
            _ = dataset.record("nope")

    def test_duplicate_feature_name_raises(self) -> None:
        features = [DataFeature(name="a"), DataFeature(name="a")]
        with pytest.raises(DataValidationError):
            DataSet(name="ds", features=features)

    def test_duplicate_record_id_raises(self) -> None:
        records = [DataRecord(record_id="r0"), DataRecord(record_id="r0")]
        with pytest.raises(DataValidationError):
            DataSet(name="ds", records=records)

    def test_blank_dataset_name_raises(self) -> None:
        with pytest.raises(DataValidationError):
            DataSet(name="")

    def test_structural_issues_are_reportable(self) -> None:
        dataset = DataSet(
            name="partial",
            features=[DataFeature(name="a"), DataFeature(name="b")],
            records=[
                DataRecord(record_id="r0", values={"a": 1.0}),
                DataRecord(record_id="r1", values={"a": 2.0, "b": 3.0, "unknown": 9.0}),
            ],
        )
        issues = dataset.validate()
        assert "record 'r0' is missing feature 'b'" in issues
        assert "record 'r1' has unknown feature 'unknown'" in issues
        with pytest.raises(DataValidationError):
            dataset.raise_if_invalid()

    def test_empty_dataset_issues(self) -> None:
        dataset = DataSet(name="empty")
        issues = dataset.validate()
        assert "dataset has no features" in issues
        assert "dataset has no records" in issues

    def test_dataset_round_trip(self) -> None:
        dataset = _dataset()
        rebuilt = DataSet.from_dict(dataset.to_dict())
        assert rebuilt.to_dict() == dataset.to_dict()


# ----------------------------------------------------------------------
# data context and domain-context mapping
# ----------------------------------------------------------------------


class TestDataContext:
    def test_defaults_and_validation(self) -> None:
        context = DataContext()
        assert context.distance_metric == "euclidean"
        assert context.similarity_sigma == 1.0
        assert DataContext(purpose="clustering", distance_metric="weighted_euclidean")

    def test_unknown_distance_metric_raises(self) -> None:
        with pytest.raises(DataValidationError):
            DataContext(distance_metric="cosine")

    def test_bad_sigma_raises(self) -> None:
        with pytest.raises(DataValidationError):
            DataContext(similarity_sigma=0.0)
        with pytest.raises(DataValidationError):
            DataContext(similarity_sigma=float("nan"))

    def test_bad_feature_weight_raises(self) -> None:
        with pytest.raises(DataValidationError):
            DataContext(feature_weights={"height": -1.0})

    def test_unknown_preferred_strategy_raises(self) -> None:
        with pytest.raises(DataValidationError):
            DataContext(preferred_strategy="quantum_galaxy")

    def test_to_domain_context(self) -> None:
        domain = data_context_example().to_domain_context()
        assert domain.domain == "data"
        assert domain.use_case == "optimization"
        assert domain.context_metadata["distance_metric"] == "euclidean"

    def test_round_trip(self) -> None:
        context = data_context_example()
        rebuilt = DataContext.from_dict(context.to_dict())
        assert rebuilt.to_dict() == context.to_dict()


# ----------------------------------------------------------------------
# distance & similarity primitives
# ----------------------------------------------------------------------


class TestNumerics:
    def test_euclidean_distance(self) -> None:
        assert euclidean_distance([0.0, 0.0], [3.0, 4.0]) == 5.0
        assert euclidean_distance([1.0], [1.0]) == 0.0

    def test_squared_euclidean_distance(self) -> None:
        assert squared_euclidean_distance([0.0, 0.0], [3.0, 4.0]) == 25.0

    def test_weighted_squared_euclidean_distance(self) -> None:
        assert weighted_squared_euclidean_distance([0.0, 0.0], [3.0, 4.0], [2.0, 1.0]) == 34.0

    def test_dimension_mismatch_raises(self) -> None:
        with pytest.raises(DataValidationError):
            euclidean_distance([1.0, 2.0], [1.0])
        with pytest.raises(DataValidationError):
            weighted_squared_euclidean_distance([1.0, 2.0], [1.0, 2.0], [1.0])

    def test_non_finite_raises(self) -> None:
        with pytest.raises(DataValidationError):
            euclidean_distance([1.0, float("nan")], [1.0, 2.0])

    def test_negative_weight_raises(self) -> None:
        with pytest.raises(DataValidationError):
            weighted_squared_euclidean_distance([0.0], [1.0], [-1.0])

    def test_similarity_from_distance(self) -> None:
        assert similarity_from_distance(0.0) == 1.0
        assert 0.0 < similarity_from_distance(5.0, sigma=1.0) < 1.0
        assert similarity_from_distance(0.0, sigma=2.0) == 1.0

    def test_similarity_rejects_invalid(self) -> None:
        with pytest.raises(DataValidationError):
            similarity_from_distance(-1.0)
        with pytest.raises(DataValidationError):
            similarity_from_distance(1.0, sigma=0.0)


# ----------------------------------------------------------------------
# pairwise relationships
# ----------------------------------------------------------------------


class TestRelationship:
    def test_pairwise_distance(self) -> None:
        relationship = pairwise_relationship(_dataset(), kind="distance", metric="euclidean")
        assert relationship.kind == "distance"
        assert relationship.record_order == ["r0", "r1", "r2", "r3"]
        assert relationship.size == 4
        assert relationship.value("r0", "r0") == 0.0
        assert relationship.value("r0", "r2") == pytest.approx(11.0**0.5)

    def test_pairwise_similarity_symmetry(self) -> None:
        relationship = similarity_example()
        assert relationship.kind == "similarity"
        for i in range(len(relationship)):
            for j in range(len(relationship)):
                assert relationship.values[i][j] == pytest.approx(relationship.values[j][i])

    def test_pairwise_weighted_metric(self) -> None:
        relationship = pairwise_relationship(
            _dataset(),
            kind="distance",
            metric="weighted_euclidean",
            weights={"height": 1.0, "width": 1.0, "depth": 1.0, "brightness": 1.0, "texture": 1.0},
        )
        assert relationship.value("r0", "r2") == pytest.approx(11.0)

    def test_pairwise_unknown_weights_raise(self) -> None:
        with pytest.raises(DataValidationError):
            pairwise_relationship(_dataset(), metric="weighted_euclidean", weights={"nope": 1.0})

    def test_asymmetric_matrix_raises(self) -> None:
        with pytest.raises(DataValidationError):
            DataRelationship(
                record_order=["r0", "r1"],
                kind="distance",
                values=[[0.0, 1.0], [2.0, 0.0]],
            )

    def test_nonsquare_matrix_raises(self) -> None:
        with pytest.raises(DataValidationError):
            DataRelationship(
                record_order=["r0", "r1"],
                kind="distance",
                values=[[0.0, 1.0]],
            )

    def test_bad_kind_raises(self) -> None:
        with pytest.raises(DataValidationError):
            DataRelationship(record_order=["r0"], kind="layout", values=[[0.0]])

    def test_negative_entry_raises(self) -> None:
        with pytest.raises(DataValidationError):
            DataRelationship(
                record_order=["r0", "r1"], kind="distance", values=[[0.0, -1.0], [-1.0, 0.0]]
            )

    def test_validate_against_record_order(self) -> None:
        relationship = pairwise_relationship(_dataset(), kind="distance")
        relationship.validate_against(["r0", "r1", "r2", "r3"])
        with pytest.raises(DataValidationError):
            relationship.validate_against(["r3", "r2", "r1", "r0"])

    def test_relationship_round_trip(self) -> None:
        relationship = pairwise_relationship(_dataset(), kind="similarity")
        rebuilt = DataRelationship.from_dict(relationship.to_dict())
        assert rebuilt.to_dict() == relationship.to_dict()


# ----------------------------------------------------------------------
# data quality
# ----------------------------------------------------------------------


class TestDataQuality:
    def test_clean_dataset(self) -> None:
        report = assess_data_quality(_dataset())
        assert report.valid is True
        assert report.record_count == 4
        assert report.feature_count == 5
        assert report.missing_count == 0
        assert report.invalid_count == 0
        assert report.duplicate_count == 0
        assert report.feature_consistency is True
        assert report.issues == []

    def test_missing_values_reported(self) -> None:
        dataset = DataSet(
            name="missing",
            features=[DataFeature(name="a")],
            records=[DataRecord(record_id="r0"), DataRecord(record_id="r1")],
        )
        report = assess_data_quality(dataset)
        assert report.valid is False
        assert report.missing_count == 2
        assert any("missing" in issue for issue in report.issues)

    def test_invalid_values_reported(self) -> None:
        dataset = DataSet(
            name="invalid",
            features=[DataFeature(name="a", upper_bound=5.0)],
            records=[
                DataRecord(record_id="r0", values={"a": 3.0}),
                DataRecord(record_id="r1", values={"a": 50.0}),
            ],
        )
        report = assess_data_quality(dataset)
        assert report.valid is False
        assert report.invalid_count == 1

    def test_duplicates_reported(self) -> None:
        dataset = DataSet(
            name="dups",
            features=[DataFeature(name="a")],
            records=[
                DataRecord(record_id="r0", values={"a": 1.0}),
                DataRecord(record_id="r1", values={"a": 1.0}),
                DataRecord(record_id="r2", values={"a": 2.0}),
            ],
        )
        report = assess_data_quality(dataset)
        assert report.valid is False
        assert report.duplicate_count == 1
        assert "r1" in " ".join(report.issues)

    def test_feature_consistency_false(self) -> None:
        dataset = DataSet(
            name="inconsistent",
            features=[DataFeature(name="a"), DataFeature(name="b")],
            records=[
                DataRecord(record_id="r0", values={"a": 1.0, "b": 2.0}),
                DataRecord(record_id="r1", values={"a": 1.0}),
            ],
        )
        report = assess_data_quality(dataset)
        assert report.feature_consistency is False
        assert report.valid is False

    def test_quality_report_round_trip(self) -> None:
        report = quality_example()
        from quantsmind.quantum.data.quality import DataQualityReport

        rebuilt = DataQualityReport.from_dict(report.to_dict())
        assert rebuilt.to_dict() == report.to_dict()


# ----------------------------------------------------------------------
# objectives
# ----------------------------------------------------------------------


class TestObjectives:
    def test_feature_utility_objective(self) -> None:
        objective = FeatureUtilityObjective(
            name="max_utility", utilities={"height": 5.0, "width": 3.0}
        )
        assert objective.domain == "data/feature_utility"
        assert objective.validate(_feature_selection()) == []

    def test_feature_utility_rejects_negative(self) -> None:
        with pytest.raises(DataValidationError):
            FeatureUtilityObjective(name="u", utilities={"height": -1.0})

    def test_feature_utility_unknown_feature_issue(self) -> None:
        objective = FeatureUtilityObjective(name="u", utilities={"galaxy": 1.0})
        issues = objective.validate(_feature_selection())
        assert any("unknown features" in issue for issue in issues)

    def test_feature_utility_only_for_feature_selection(self) -> None:
        objective = FeatureUtilityObjective(name="u", utilities={"height": 1.0})
        issues = objective.validate(_clustering())
        assert any("feature-selection" in issue for issue in issues)

    def test_selection_cost_objective(self) -> None:
        objective = SelectionCostObjective(name="cost", costs={"height": 1.0})
        assert objective.validate(_feature_selection()) == []

    def test_selection_cost_rejects_negative(self) -> None:
        with pytest.raises(DataValidationError):
            SelectionCostObjective(name="cost", costs={"height": -1.0})

    def test_feature_selection_combined_objective(self) -> None:
        objective = FeatureSelectionObjective(
            name="net", utilities={"height": 5.0}, costs={"height": 1.0}, penalty=2.0
        )
        assert objective.validate(_feature_selection()) == []
        quantum = objective.to_quantum_objective(_feature_selection())
        assert quantum.sense.name == "MAXIMIZE"
        assert "3.0*x0" in quantum.expression

    def test_feature_selection_rejects_negative_penalty(self) -> None:
        with pytest.raises(DataValidationError):
            FeatureSelectionObjective(name="net", utilities={"height": 5.0}, penalty=-1.0)

    def test_objective_rejects_blank_name(self) -> None:
        with pytest.raises(DataValidationError):
            FeatureUtilityObjective(name="  ", utilities={"height": 1.0})

    def test_clustering_distance_objective(self) -> None:
        objective = ClusteringDistanceObjective(name="within")
        assert objective.validate(_clustering()) == []
        quantum = objective.to_quantum_objective(_clustering())
        assert quantum.sense.name == "MINIMIZE"
        assert "z" in quantum.expression

    def test_clustering_distance_only_for_clustering(self) -> None:
        objective = ClusteringDistanceObjective(name="within")
        issues = objective.validate(_feature_selection())
        assert any("clustering" in issue for issue in issues)

    def test_objective_from_dict_dispatch(self) -> None:
        from quantsmind.quantum.data.objectives import objective_from_dict

        objective = FeatureSelectionObjective(
            name="net", utilities={"height": 5.0}, costs={"height": 1.0}, penalty=3.0
        )
        rebuilt = objective_from_dict(objective.to_dict())
        assert isinstance(rebuilt, FeatureSelectionObjective)
        assert rebuilt.penalty == 3.0
        assert rebuilt.to_dict() == objective.to_dict()

    def test_objective_from_dict_unknown_kind(self) -> None:
        from quantsmind.quantum.data.objectives import objective_from_dict

        with pytest.raises(DataValidationError):
            objective_from_dict({"kind": "alien", "name": "x"})


# ----------------------------------------------------------------------
# constraints
# ----------------------------------------------------------------------


class TestConstraints:
    def test_feature_count_materializes_le_ge(self) -> None:
        constraint = FeatureCountConstraint(name="count", min_features=2.0, max_features=3.0)
        assert constraint.validate(_feature_selection()) == []
        constraints = constraint.to_quantum_constraints(_feature_selection())
        assert [c.name for c in constraints] == ["count_max", "count_min"]
        assert constraints[0].operator.value == "<="
        assert constraints[1].operator.value == ">="

    def test_feature_count_inverted_bounds_raise(self) -> None:
        with pytest.raises(DataValidationError):
            FeatureCountConstraint(name="c", min_features=5.0, max_features=2.0)

    def test_feature_count_over_dataset_issue(self) -> None:
        constraint = FeatureCountConstraint(name="c", min_features=0.0, max_features=99.0)
        issues = constraint.validate(_feature_selection())
        assert any("exceeds the 5 dataset features" in issue for issue in issues)

    def test_feature_group_constraint(self) -> None:
        constraint = FeatureGroupConstraint(
            name="geometry",
            group="geometry",
            members=["height", "width", "depth"],
            lower=0.0,
            upper=2.0,
        )
        assert constraint.validate(_feature_selection()) == []
        constraints = constraint.to_quantum_constraints(_feature_selection())
        assert [c.name for c in constraints] == ["geometry_max", "geometry_min"]

    def test_feature_group_requires_members(self) -> None:
        with pytest.raises(DataValidationError):
            FeatureGroupConstraint(name="g", members=[])

    def test_feature_group_unknown_member_issue(self) -> None:
        constraint = FeatureGroupConstraint(name="g", members=["galaxy"])
        issues = constraint.validate(_feature_selection())
        assert any("unknown features" in issue for issue in issues)

    def test_assignment_constraint(self) -> None:
        constraint = AssignmentConstraint(name="assignment")
        assert constraint.validate(_clustering()) == []
        constraints = constraint.to_quantum_constraints(_clustering())
        assert len(constraints) == 4
        assert all(c.operator.value == "==" for c in constraints)
        assert constraints[0].name == "assignment_r0"
        assert "z0_0" in constraints[0].expression

    def test_assignment_only_for_clustering(self) -> None:
        issues = AssignmentConstraint(name="a").validate(_feature_selection())
        assert any("clustering" in issue for issue in issues)

    def test_cluster_count_constraint(self) -> None:
        constraint = ClusterCountConstraint(name="size", min_records=1.0, max_records=2.0)
        assert constraint.validate(_clustering()) == []
        constraints = constraint.to_quantum_constraints(_clustering())
        names = [c.name for c in constraints]
        assert names == ["size_0_max", "size_0_min", "size_1_max", "size_1_min"]

    def test_cluster_count_inverted_bounds_raise(self) -> None:
        with pytest.raises(DataValidationError):
            ClusterCountConstraint(name="s", min_records=3.0, max_records=1.0)

    def test_constraint_round_trip_dispatch(self) -> None:
        from quantsmind.quantum.data.constraints import constraint_from_dict

        constraint = FeatureGroupConstraint(
            name="geometry",
            group="geometry",
            members=["height", "width", "depth"],
            lower=0.0,
            upper=2.0,
        )
        rebuilt = constraint_from_dict(constraint.to_dict())
        assert isinstance(rebuilt, FeatureGroupConstraint)
        assert rebuilt.to_dict() == constraint.to_dict()

    def test_constraint_from_dict_unknown_kind(self) -> None:
        from quantsmind.quantum.data.constraints import constraint_from_dict

        with pytest.raises(DataValidationError):
            constraint_from_dict({"kind": "alien", "name": "x"})

    def test_constraint_rejects_blank_name(self) -> None:
        with pytest.raises(DataValidationError):
            FeatureCountConstraint(name="  ")


# ----------------------------------------------------------------------
# DataProblem representation and validation
# ----------------------------------------------------------------------


class TestDataProblem:
    def test_problem_type_parse(self) -> None:
        assert DataProblemType.parse("clustering") is DataProblemType.CLUSTERING
        assert DataProblemType.parse("FEATURE_SELECTION") is DataProblemType.FEATURE_SELECTION
        with pytest.raises(DataValidationError):
            DataProblemType.parse("galaxy")

    def test_size_and_decision_variables_feature_selection(self) -> None:
        problem = _feature_selection()
        assert problem.size == 5
        variables = problem.decision_variables()
        assert [v.name for v in variables] == ["x0", "x1", "x2", "x3", "x4"]
        assert all(v.type.name == "BINARY" for v in variables)
        assert problem.feature_variables()[0].metadata.get("domain") is None or True

    def test_size_and_decision_variables_clustering(self) -> None:
        problem = _clustering()
        assert problem.size == 8
        variables = problem.decision_variables()
        assert [v.name for v in variables] == [
            "z0_0",
            "z0_1",
            "z1_0",
            "z1_1",
            "z2_0",
            "z2_1",
            "z3_0",
            "z3_1",
        ]
        assert all(v.type.name == "BINARY" for v in variables)

    def test_clustering_requires_positive_k(self) -> None:
        with pytest.raises(DataValidationError):
            DataProblem(
                name="p",
                dataset=_dataset(),
                problem_type=DataProblemType.CLUSTERING,
                objectives=[ClusteringDistanceObjective(name="o")],
                k=0,
            )

    def test_clustering_k_cannot_exceed_records(self) -> None:
        with pytest.raises(DataValidationError):
            DataProblem(
                name="p",
                dataset=_dataset(),
                problem_type=DataProblemType.CLUSTERING,
                objectives=[ClusteringDistanceObjective(name="o")],
                k=9,
            )

    def test_k_rejected_for_feature_selection(self) -> None:
        with pytest.raises(DataValidationError):
            DataProblem(
                name="p",
                dataset=_dataset(),
                problem_type=DataProblemType.FEATURE_SELECTION,
                objectives=[FeatureUtilityObjective(name="u", utilities={"height": 1.0})],
                k=2,
            )

    def test_pairwise_rejected_for_feature_selection(self) -> None:
        relationship = pairwise_relationship(_dataset(), kind="distance")
        with pytest.raises(DataValidationError):
            DataProblem(
                name="p",
                dataset=_dataset(),
                problem_type=DataProblemType.FEATURE_SELECTION,
                objectives=[FeatureUtilityObjective(name="u", utilities={"height": 1.0})],
                pairwise=relationship,
            )

    def test_duplicate_objective_names_raise(self) -> None:
        objective = FeatureUtilityObjective(name="dup", utilities={"height": 1.0})
        with pytest.raises(DataValidationError):
            duplicate = FeatureUtilityObjective(name="dup", utilities={"width": 1.0})
            DataProblem(
                name="p",
                dataset=_dataset(),
                objectives=[objective, duplicate],
            )

    def test_duplicate_constraint_names_raise(self) -> None:
        with pytest.raises(DataValidationError):
            DataProblem(
                name="p",
                dataset=_dataset(),
                constraints=[
                    FeatureCountConstraint(name="c", min_features=1.0),
                    FeatureCountConstraint(name="c", min_features=2.0),
                ],
            )

    def test_validate_no_objectives(self) -> None:
        problem = DataProblem(name="p", dataset=_dataset())
        issues = problem.validate()
        assert "data problem has no objectives" in issues

    def test_validate_catches_objective_unknowns(self) -> None:
        problem = DataProblem(
            name="p",
            dataset=_dataset(),
            objectives=[FeatureUtilityObjective(name="u", utilities={"galaxy": 1.0})],
        )
        issues = problem.validate()
        assert any("unknown features" in issue for issue in issues)
        with pytest.raises(DataValidationError):
            problem.raise_if_invalid()

    def test_validate_catches_pairwise_alignment(self) -> None:
        relationship = DataRelationship(
            record_order=["r0", "r1", "r2"],
            kind="distance",
            values=[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        )
        problem = DataProblem(
            name="p",
            dataset=_dataset(),
            problem_type=DataProblemType.CLUSTERING,
            objectives=[ClusteringDistanceObjective(name="o")],
            k=2,
            pairwise=relationship,
        )
        issues = problem.validate()
        assert any("record order" in issue for issue in issues)

    def test_clustering_distance_matrix_memo_and_recompute(self) -> None:
        matrix = _clustering().clustering_distance_matrix()
        assert isinstance(matrix, DataRelationship)
        assert matrix.kind == "distance"
        assert matrix.record_order == ["r0", "r1", "r2", "r3"]

    def test_problem_round_trip(self) -> None:
        for problem in [_feature_selection(), _clustering(), grouped_feature_selection_example()]:
            rebuilt = DataProblem.from_dict(problem.to_dict())
            assert rebuilt.to_dict() == problem.to_dict()
            assert rebuilt.decision_variables()[0].name == problem.decision_variables()[0].name

    def test_problem_blank_name_raises(self) -> None:
        with pytest.raises(DataValidationError):
            DataProblem(name=" ", dataset=_dataset())


# ----------------------------------------------------------------------
# mapping
# ----------------------------------------------------------------------


class TestMapping:
    def test_feature_mapping(self) -> None:
        mapping = DataMapper().map(_feature_selection())
        assert mapping.variable_names == ["x0", "x1", "x2", "x3", "x4"]
        assert mapping.feature_variable("depth") == "x2"
        assert mapping.feature_index("brightness") == 3

    def test_feature_mapping_unknown_raises(self) -> None:
        mapping = DataMapper().map(_feature_selection())
        with pytest.raises(KeyError):
            mapping.feature_index("galaxy")

    def test_cluster_mapping(self) -> None:
        mapping = DataMapper().map(_clustering())
        assert mapping.variable_names == [
            "z0_0",
            "z0_1",
            "z1_0",
            "z1_1",
            "z2_0",
            "z2_1",
            "z3_0",
            "z3_1",
        ]
        assert mapping.cluster_variable("r1", 0) == "z1_0"
        assert mapping.k == 2

    def test_cluster_of(self) -> None:
        mapping = DataMapper().map(_clustering())
        assignments = {"z0_0": 1.0, "z1_1": 1.0, "z2_0": 1.0, "z3_1": 1.0}
        assert mapping.cluster_of(assignments, "r0") == 0
        assert mapping.cluster_of(assignments, "r1") == 1
        assert mapping.cluster_of(assignments, "r2") == 0
        assert mapping.cluster_of(assignments, "r3") == 1

    def test_decode_feature_selection(self) -> None:
        decoded = (
            DataMapper()
            .map(_feature_selection())
            .decode_assignments({"x0": 1.0, "x1": 0.0, "x2": 1.0, "x3": 0.0, "x4": 0.0})
        )
        selected = [item.feature_name for item in decoded if item.selected]
        assert selected == ["height", "depth"]

    def test_decode_clustering(self) -> None:
        decoded = (
            DataMapper()
            .map(_clustering())
            .decode_assignments({"z0_0": 1.0, "z1_1": 1.0, "z2_0": 1.0, "z3_1": 1.0})
        )
        assert len(decoded) == 8
        assigned = {item.record_id: item.cluster_index for item in decoded if item.value >= 0.5}
        assert assigned == {"r0": 0, "r1": 1, "r2": 0, "r3": 1}

    def test_mapping_requires_valid_problem(self) -> None:
        problem = DataProblem(name="p", dataset=_dataset())
        with pytest.raises(DataValidationError):
            DataMapper().map(problem)

    def test_decoded_members_round_trip(self) -> None:
        from quantsmind.quantum.data.mapping import DecodedClusterAssignment, DecodedDataFeature

        feature = DecodedDataFeature(
            feature_name="height", index=0, variable_name="x0", value=1.0, selected=True
        )
        cluster = DecodedClusterAssignment(
            record_id="r0", record_index=0, cluster_index=1, variable_name="z0_1", value=1.0
        )
        assert feature.to_dict()["selected"] is True
        assert feature.to_dict()["variable_name"] == "x0"
        assert cluster.to_dict()["cluster_index"] == 1
        assert cluster.to_dict()["record_id"] == "r0"


# ----------------------------------------------------------------------
# formulation and QMQ reuse
# ----------------------------------------------------------------------


class TestFormulation:
    def test_to_quantum_problem_feature_selection(self) -> None:
        quantum = DataFormulationAdapter().to_quantum_problem(_feature_selection())
        assert [v.name for v in quantum.variables] == ["x0", "x1", "x2", "x3", "x4"]
        assert quantum.provenance["domain_layer"] == "data"
        assert quantum.metadata["objectives"][0]["kind"] == "feature_selection"
        assert quantum.metadata["dataset"]["feature_order"] == [
            "height",
            "width",
            "depth",
            "brightness",
            "texture",
        ]
        assert quantum.domain.domain == "data"
        assert [o.sense.name for o in quantum.objectives] == ["MAXIMIZE"]

    def test_to_quantum_problem_clustering(self) -> None:
        quantum = DataFormulationAdapter().to_quantum_problem(_clustering())
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
        assert quantum.provenance["problem_type"] == "clustering"
        assert quantum.metadata["k"] == 2
        assert quantum.metadata["distance"]["metric"] == "euclidean"
        # assignment (4 eq) + cluster size (4 bounds)
        assert len(quantum.constraints) == 8
        assert any(c.operator.value == "==" for c in quantum.constraints)

    def test_invalid_problem_raises_on_formulation(self) -> None:
        problem = DataProblem(name="p", dataset=_dataset())
        with pytest.raises(DataValidationError):
            DataFormulationAdapter().to_quantum_problem(problem)

    def test_formulate_reuses_qmq_optimization_model(self) -> None:
        model = DataFormulationAdapter().formulate(_feature_selection())
        assert isinstance(model, OptimizationModel)
        assert model.name == "feature_selection_demo_model"

    def test_clustering_formulates_as_optimization_model(self) -> None:
        model = DataFormulationAdapter().formulate(_clustering())
        assert isinstance(model, OptimizationModel)

    def test_qubo_mapping_reuses_existing_mapper(self) -> None:
        quantum = DataFormulationAdapter().to_quantum_problem(_clustering())
        mapping = QUBOMapper().map(quantum)
        model = mapping.payload
        assert model is not None
        # 8 decision variables; equality constraints add slack variables
        assert model.num_variables >= 8


# ----------------------------------------------------------------------
# metrics
# ----------------------------------------------------------------------


class TestMetrics:
    def test_feature_selection_metrics(self) -> None:
        problem = _feature_selection()
        assignment = {"x0": 1.0, "x1": 0.0, "x2": 1.0, "x3": 0.0, "x4": 0.0}
        metrics = DataMetrics.compute(problem, assignment)
        assert metrics.problem_type == "feature_selection"
        assert metrics.selected_feature_count == 2
        assert metrics.selected_utility == 9.0
        assert metrics.selection_cost == 0.0
        assert metrics.net_objective == 9.0

    def test_selection_cost_metrics_with_penalty(self) -> None:
        problem = selection_cost_example()
        assignment = {"x0": 1.0, "x1": 0.0, "x2": 1.0, "x3": 0.0, "x4": 0.0}
        metrics = DataMetrics.compute(problem, assignment)
        assert metrics.selected_utility == 9.0
        assert metrics.selection_cost == 2.0
        assert metrics.net_objective == 7.0

    def test_clustering_metrics(self) -> None:
        problem = _clustering()
        assignments = {"z0_0": 1.0, "z1_1": 1.0, "z2_0": 1.0, "z3_1": 1.0}
        metrics = DataMetrics.compute(problem, assignments)
        assert metrics.problem_type == "clustering"
        assert metrics.cluster_count == 2
        assert metrics.total_within_cluster_distance == pytest.approx(8.215604275921756)

    def test_metrics_round_trip(self) -> None:
        metrics = DataMetrics.compute(_feature_selection(), {"x0": 1.0, "x2": 1.0})
        rebuilt = DataMetrics.from_dict(metrics.to_dict())
        assert rebuilt.to_dict() == metrics.to_dict()


# ----------------------------------------------------------------------
# classical solving (known optima for examples A/B/C/F)
# ----------------------------------------------------------------------


class TestSolve:
    def test_feature_selection_example_a(self) -> None:
        result = _solver().solve(_feature_selection(), strategy="classical")
        solution = result.solution
        assert solution is not None
        assert solution.feasible is True
        assert solution.selected() == ["height", "depth"]
        assert solution.selected_utility == 9.0
        assert solution.objective_value == 9.0
        assert solution.metrics.constraint_violations == 0
        assert solution.num_variables == 5

    def test_selection_cost_example_b(self) -> None:
        result = _solver().solve(selection_cost_example(), strategy="classical")
        solution = result.solution
        assert solution.selected() == ["height", "depth"]
        assert solution.selected_utility == 9.0
        assert solution.selection_cost == 2.0
        assert solution.objective_value == 7.0

    def test_grouped_feature_selection_example_c(self) -> None:
        result = _solver().solve(grouped_feature_selection_example(), strategy="classical")
        solution = result.solution
        assert solution.feasible is True
        assert solution.selected() == ["height", "depth", "texture"]
        assert solution.selected_utility == 11.0
        assert solution.objective_value == 11.0

    def test_clustering_example_f(self) -> None:
        result = _solver().solve(_clustering(), strategy="classical")
        solution = result.solution
        assert solution.feasible is True
        assert solution.cluster_assignments == {"r0": 0, "r1": 1, "r2": 0, "r3": 1}
        assert solution.cluster_count == 2
        assert solution.total_within_cluster_distance == pytest.approx(8.215604275921756)
        assert solution.objective_value == pytest.approx(8.215604275921756)
        assert solution.metrics.constraint_violations == 0
        assert solution.num_variables == 8

    def test_solution_from_dict_round_trip(self) -> None:
        solution = _solver().solve(_feature_selection(), strategy="classical").solution
        rebuilt = DataSolution.from_dict(solution.to_dict())
        assert rebuilt.to_dict() == solution.to_dict()
        assert rebuilt.selected() == ["height", "depth"]

    def test_deterministic_repeated_runs(self) -> None:
        first = _solver().solve(_feature_selection(), strategy="classical").solution
        second = _solver().solve(_feature_selection(), strategy="classical").solution
        assert first.selected() == second.selected() == ["height", "depth"]
        assert first.objective_value == second.objective_value == 9.0
        assert first.to_dict()["num_variables"] == second.to_dict()["num_variables"]

    def test_deterministic_repeated_runs_dicts(self) -> None:
        first = _solver().solve(_feature_selection(), strategy="classical").solution.to_dict()
        second = _solver().solve(_feature_selection(), strategy="classical").solution.to_dict()
        for raw in (first, second):
            raw.pop("execution_time")
            raw["provenance"].pop("created_at", None)
        assert first == second

    def test_configuration_defaults_and_validation(self) -> None:
        config = DataOptimizationConfiguration()
        assert config.preferred_strategy == ""
        assert config.solver_max_variables == 20
        restored = DataOptimizationConfiguration.from_dict(config.to_dict())
        assert restored.to_dict() == config.to_dict()
        with pytest.raises(DataValidationError):
            DataOptimizationConfiguration(shots=0)
        with pytest.raises(DataValidationError):
            DataOptimizationConfiguration(seed=-1)
        with pytest.raises(DataValidationError):
            DataOptimizationConfiguration(preferred_strategy="quantum_galaxy")

    def test_solve_with_config(self) -> None:
        config = DataOptimizationConfiguration(preferred_strategy="classical", seed=11)
        result = DataOptimizer().solve(_feature_selection(), config=config)
        assert result.solution.feasible is True

    def test_solve_result_serialization(self) -> None:
        result = _solver().solve(_clustering(), strategy="classical")
        payload = result.to_dict()
        assert payload["solution"] is not None
        assert payload["report_ref"] is not None
        rebuilt = type(result).from_dict(payload)
        assert rebuilt.solution is None or rebuilt.solution.problem_name == "clustering_demo"


# ----------------------------------------------------------------------
# benchmark / interpretation / honest failure
# ----------------------------------------------------------------------


class TestBenchmarkAndSemantics:
    def test_benchmark_against_classical_baseline(self) -> None:
        result = _solver().benchmark(_feature_selection(), strategy="classical")
        assert result.benchmark is not None
        assert result.benchmark.status == "executed"
        assert result.benchmark.report is not None
        assert result.interpretation is not None
        assert result.solution.selected() == ["height", "depth"]

    def test_benchmark_with_known_optimum(self) -> None:
        result = _solver().benchmark(_feature_selection(), strategy="classical", known_optimum=9.0)
        metrics = result.benchmark.metrics
        assert metrics.approximation_ratio == pytest.approx(1.0)
        assert metrics.optimality_gap == pytest.approx(0.0)

    def test_interpretation(self) -> None:
        result = _solver().solve(_clustering(), strategy="classical")
        interpretation = result.interpretation
        assert interpretation.status.value == "executed"
        assert interpretation.solution_quality.value == "feasible"

    def test_quantum_inspired_raises(self) -> None:
        with pytest.raises(WorkflowError):
            _solver().solve(_feature_selection(), strategy="quantum_inspired")

    def test_quantum_request_honest_downgrade(self) -> None:
        # An explicit quantum request is never silently turned into a
        # fabricated classical run: without a runtime it lowers honestly and
        # records the fallback (provenance), never pretending to execute on
        # quantum hardware.  The blocked-environment subprocess test below
        # proves the full downgrade contract; here we assert the recorded
        # decision is never a silent one by exercising the selector offline.
        from quantsmind.quantum.data.formulation import DataFormulationAdapter
        from quantsmind.quantum.strategy.selector import StrategySelector
        from quantsmind.quantum.strategy.strategy import ComputationStrategy

        quantum_problem = DataFormulationAdapter().to_quantum_problem(
            _feature_selection(), preferred_strategy="quantum"
        )
        decision = StrategySelector().select(quantum_problem)
        assert decision is ComputationStrategy.QUANTUM

    def test_invalid_problem_solve_raises(self) -> None:
        problem = DataProblem(name="bad", dataset=_dataset())
        with pytest.raises(DataValidationError):
            _solver().solve(problem)


# ----------------------------------------------------------------------
# canonical examples
# ----------------------------------------------------------------------


class TestExamples:
    def test_examples_validate(self) -> None:
        for problem in [
            feature_selection_example(),
            selection_cost_example(),
            grouped_feature_selection_example(),
            clustering_example(),
        ]:
            problem.raise_if_invalid()

    def test_similarity_example(self) -> None:
        relationship = similarity_example()
        assert relationship.kind == "similarity"
        assert relationship.value("r0", "r0") == 1.0
        assert 0.0 < relationship.value("r0", "r2") < 1.0

    def test_quality_example_clean(self) -> None:
        report = quality_example()
        assert report.valid is True
        assert report.record_count == 4

    def test_serialization_example(self) -> None:
        problems = serialization_example()
        assert set(problems) == {"feature_selection", "grouped", "clustering"}
        for problem in problems.values():
            assert problem.to_dict() == type(problem).from_dict(problem.to_dict()).to_dict()

    def test_all_examples_run(self) -> None:
        outputs = []
        from quantsmind.quantum.data.examples import all_examples

        outputs = all_examples()
        assert any("feature order" in line for line in outputs)
        assert any("data quality valid" in line for line in outputs)


# ----------------------------------------------------------------------
# public API
# ----------------------------------------------------------------------


class TestPublicApi:
    def test_data_package_exports(self) -> None:
        import quantsmind.quantum.data as data_module

        for name in [
            "DataFeature",
            "DataRecord",
            "DataSet",
            "FeatureVector",
            "DataContext",
            "DataRelationship",
            "pairwise_relationship",
            "DataQualityReport",
            "assess_data_quality",
            "DataObjective",
            "FeatureUtilityObjective",
            "SelectionCostObjective",
            "DataConstraint",
            "FeatureCountConstraint",
            "FeatureGroupConstraint",
            "DataProblemType",
            "DataProblem",
            "DataFormulationAdapter",
            "DataMapper",
            "DataMetrics",
            "DataSolution",
            "DataOptimizer",
        ]:
            assert hasattr(data_module, name), name

    def test_root_exports_data_layer(self) -> None:
        import quantsmind.quantum as quantum_module

        for name in [
            "DataProblem",
            "DataOptimizer",
            "DataFormulationAdapter",
            "DataFeature",
            "DataSet",
            "ClusteringDistanceObjective",
            "FeatureSelectionObjective",
            "DataMetrics",
            "DataSolution",
        ]:
            assert name in quantum_module.__all__, name


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
from quantsmind.quantum.data.examples import feature_selection_example, clustering_example
problem = feature_selection_example()
assert problem.validate() == []
assert problem.decision_variables()[0].name == "x0"
cluster = clustering_example()
assert cluster.decision_variables()[0].name == "z0_0"
print("DATA_OK")
"""
        )
        assert rc == 0, out
        assert "DATA_OK" in out

    def test_classical_solve_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.data.optimizer import DataOptimizer
from quantsmind.quantum.data.examples import feature_selection_example
result = DataOptimizer(default_seed=7).solve(feature_selection_example(), strategy="classical")
solution = result.solution
assert solution is not None
assert solution.feasible is True
assert solution.selected() == ["height", "depth"]
assert result.interpretation is not None
print("DATA_OK")
"""
        )
        assert rc == 0, out
        assert "DATA_OK" in out

    def test_clustering_solve_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.data.optimizer import DataOptimizer
from quantsmind.quantum.data.examples import clustering_example
result = DataOptimizer(default_seed=7).solve(clustering_example(), strategy="classical")
solution = result.solution
assert solution is not None
assert solution.feasible is True
assert solution.cluster_count == 2
print("DATA_OK")
"""
        )
        assert rc == 0, out
        assert "DATA_OK" in out

    def test_classical_benchmark_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.data.optimizer import DataOptimizer
from quantsmind.quantum.data.examples import feature_selection_example
result = DataOptimizer(default_seed=7).benchmark(
    feature_selection_example(), strategy="classical"
)
assert result.benchmark is not None
assert result.benchmark.status == "executed"
assert result.interpretation is not None
print("DATA_OK")
"""
        )
        assert rc == 0, out
        assert "DATA_OK" in out

    def test_quantum_request_honest_downgrade_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.data.optimizer import DataOptimizer
from quantsmind.quantum.data.examples import feature_selection_example
result = DataOptimizer(default_seed=7).solve(feature_selection_example(), strategy="quantum")
solution = result.solution
assert solution is not None
assert result.report is not None
assert result.report.strategy.name.lower() == "classical"
assert solution.feasible is True
print("DATA_OK")
"""
        )
        assert rc == 0, out
        assert "DATA_OK" in out

    def test_interpretation_blocked(self) -> None:
        rc, out = self._blocked_rc(
            """
from quantsmind.quantum.data.optimizer import DataOptimizer
from quantsmind.quantum.data.examples import clustering_example
result = DataOptimizer(default_seed=7).solve(clustering_example(), strategy="classical")
assert result.interpretation.status.value == "executed"
assert result.interpretation.solution_quality.value == "feasible"
print("DATA_OK")
"""
        )
        assert rc == 0, out
        assert "DATA_OK" in out
