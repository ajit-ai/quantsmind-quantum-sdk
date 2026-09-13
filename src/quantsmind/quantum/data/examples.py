"""Canonical QMQ-09 Data Intelligence examples.

Every example is built exclusively from supplied, deterministic data and
never requires ``microquantum`` at import time.  Examples A–G:

A. :func:`feature_selection_example`   — ``height``/``depth`` selected
   (utility 9, exact-2 constraint),
B. :func:`selection_cost_example`      — cost-aware selection,
C. :func:`grouped_feature_selection_example` — geometry/appearance groups,
D. :func:`similarity_example`          — similarity / relationship matrix,
E. :func:`quality_example`             — deterministic data-quality report,
F. :func:`clustering_example`          — k=2 clustering (real quadratic
   binary QUBO), clusters ``{r0, r2}`` and ``{r1, r3}``,
G. :func:`serialization_example`       — JSON-safe round trip.
"""

from __future__ import annotations

from quantsmind.quantum.data.constraints import (
    AssignmentConstraint,
    ClusterCountConstraint,
    FeatureCountConstraint,
    FeatureGroupConstraint,
)
from quantsmind.quantum.data.context import DataContext
from quantsmind.quantum.data.errors import DataValidationError
from quantsmind.quantum.data.mapping import DataMapper
from quantsmind.quantum.data.models import DataFeature, DataRecord, DataSet
from quantsmind.quantum.data.objectives import (
    ClusteringDistanceObjective,
    FeatureSelectionObjective,
    FeatureUtilityObjective,
)
from quantsmind.quantum.data.problem import DataProblem, DataProblemType
from quantsmind.quantum.data.quality import DataQualityReport, assess_data_quality
from quantsmind.quantum.data.relationship import (
    DataRelationship,
    pairwise_relationship,
)

__all__ = [
    "all_examples",
    "data_context_example",
    "dataset_example",
    "feature_selection_example",
    "selection_cost_example",
    "grouped_feature_selection_example",
    "similarity_example",
    "quality_example",
    "clustering_example",
    "serialization_example",
]


def dataset_example() -> DataSet:
    """The canonical QMQ-09 dataset: 4 records over 5 features."""
    return DataSet(
        name="qm9_demo",
        features=[
            DataFeature(name="height", lower_bound=0.0, upper_bound=10.0, weight=1.0),
            DataFeature(name="width", lower_bound=0.0, upper_bound=10.0, weight=1.0),
            DataFeature(name="depth", lower_bound=0.0, upper_bound=10.0, weight=1.0),
            DataFeature(name="brightness", lower_bound=0.0, upper_bound=10.0, weight=1.0),
            DataFeature(name="texture", lower_bound=0.0, upper_bound=10.0, weight=1.0),
        ],
        records=[
            DataRecord(
                record_id="r0",
                values={
                    "height": 0.0,
                    "width": 1.0,
                    "depth": 2.0,
                    "brightness": 3.0,
                    "texture": 4.0,
                },
            ),
            DataRecord(
                record_id="r1",
                values={
                    "height": 4.0,
                    "width": 3.0,
                    "depth": 2.0,
                    "brightness": 5.0,
                    "texture": 1.0,
                },
            ),
            DataRecord(
                record_id="r2",
                values={
                    "height": 1.0,
                    "width": 2.0,
                    "depth": 0.0,
                    "brightness": 1.0,
                    "texture": 5.0,
                },
            ),
            DataRecord(
                record_id="r3",
                values={
                    "height": 3.0,
                    "width": 0.0,
                    "depth": 4.0,
                    "brightness": 2.0,
                    "texture": 2.0,
                },
            ),
        ],
        description="canonical QMQ-09 demo data (supplied)",
    )


def data_context_example() -> DataContext:
    """The canonical QMQ-09 data context (Euclidean, no preferred strategy)."""
    return DataContext(
        purpose="feature_selection",
        subdomain="tabular",
        distance_metric="euclidean",
        similarity_sigma=1.0,
        assumptions={"source": "supplied demo data"},
    )


def feature_selection_example() -> DataProblem:
    """Example A — exact-2 feature selection (selection set ``{height, depth}``)."""
    utilities = {"height": 5.0, "width": 3.0, "depth": 4.0, "brightness": 1.0, "texture": 2.0}
    return DataProblem(
        name="feature_selection_demo",
        dataset=dataset_example(),
        problem_type=DataProblemType.FEATURE_SELECTION,
        objectives=[
            FeatureSelectionObjective(name="max_utility", utilities=utilities, penalty=0.0)
        ],
        constraints=[
            FeatureCountConstraint(name="exactly_two", min_features=2.0, max_features=2.0)
        ],
        context=data_context_example(),
        description="Example A: exact-2 feature selection with max utility",
    )


def selection_cost_example() -> DataProblem:
    """Example B — cost-aware selection (utility minus cost, penalty 1.0)."""
    utilities = {"height": 5.0, "width": 3.0, "depth": 4.0, "brightness": 1.0, "texture": 2.0}
    costs = {"height": 1.0, "width": 0.5, "depth": 1.0, "brightness": 0.1, "texture": 0.2}
    return DataProblem(
        name="selection_cost_demo",
        dataset=dataset_example(),
        problem_type=DataProblemType.FEATURE_SELECTION,
        objectives=[
            FeatureSelectionObjective(
                name="utility_minus_cost",
                utilities=utilities,
                costs=costs,
                penalty=1.0,
            )
        ],
        constraints=[
            FeatureCountConstraint(name="exactly_two", min_features=2.0, max_features=2.0)
        ],
        context=data_context_example(),
        description="Example B: feature selection with selection costs",
    )


def grouped_feature_selection_example() -> DataProblem:
    """Example C — grouped feature selection with group cardinality.

    Geometry group ``{height, width, depth}`` limited to ``<= 2``, appearance
    group ``{brightness, texture}`` limited to ``<= 1``, total cardinality
    ``<= 3``.  The optimal selection is ``{height, depth, texture}``
    (utility 11).
    """
    utilities = {"height": 5.0, "width": 3.0, "depth": 4.0, "brightness": 1.0, "texture": 2.0}
    return DataProblem(
        name="grouped_selection_demo",
        dataset=dataset_example(),
        problem_type=DataProblemType.FEATURE_SELECTION,
        objectives=[FeatureUtilityObjective(name="max_utility", utilities=utilities)],
        constraints=[
            FeatureGroupConstraint(
                name="geometry_group",
                group="geometry",
                members=["height", "width", "depth"],
                lower=0.0,
                upper=2.0,
            ),
            FeatureGroupConstraint(
                name="appearance_group",
                group="appearance",
                members=["brightness", "texture"],
                lower=0.0,
                upper=1.0,
            ),
            FeatureCountConstraint(name="total_at_most_3", min_features=1.0, max_features=3.0),
        ],
        context=data_context_example(),
        description="Example C: grouped feature selection (geometry + appearance)",
    )


def similarity_example() -> DataRelationship:
    """Example D — pairwise Euclidean / similarity relationship of the dataset."""
    return pairwise_relationship(dataset_example(), kind="similarity", metric="euclidean")


def quality_example() -> DataQualityReport:
    """Example E — deterministic data-quality report of the canonical dataset."""
    return assess_data_quality(dataset_example())


def clustering_example() -> DataProblem:
    """Example F — k=2 clustering of the canonical dataset.

    Executed as a real quadratic binary QUBO (assignment equality
    constraints + optional cluster-count bounds).  The expected optimum
    assigns ``{r0, r2}`` to cluster 0 and ``{r1, r3}`` to cluster 1 with a
    total within-cluster distance of approximately ``1.2``.
    """
    return DataProblem(
        name="clustering_demo",
        dataset=dataset_example(),
        problem_type=DataProblemType.CLUSTERING,
        objectives=[ClusteringDistanceObjective(name="min_within_cluster_distance")],
        constraints=[
            AssignmentConstraint(name="assignment"),
            ClusterCountConstraint(name="cluster_size", min_records=1.0, max_records=2.0),
        ],
        context=data_context_example(),
        k=2,
        description="Example F: k=2 clustering (quadratic binary QUBO)",
    )


def serialization_example() -> dict[str, DataProblem]:
    """Example G — JSON-safe round trips of the canonical problems."""
    problems: dict[str, DataProblem] = {}
    for name, problem in {
        "feature_selection": feature_selection_example(),
        "grouped": grouped_feature_selection_example(),
        "clustering": clustering_example(),
    }.items():
        rebuilt = DataProblem.from_dict(problem.to_dict())
        if rebuilt.to_dict() != problem.to_dict():
            raise DataValidationError(f"round-trip mismatch for {name!r}")
        problems[name] = rebuilt
    return problems


def all_examples() -> list[str]:
    """Run every canonical example and return the produced artifacts."""
    dataset = dataset_example()
    _ = feature_selection_example()
    _ = selection_cost_example()
    _ = grouped_feature_selection_example()
    _ = similarity_example()
    report = quality_example()
    _ = clustering_example()
    _ = serialization_example()
    mapping = DataMapper().map(feature_selection_example())
    return [
        f"dataset feature order: {dataset.feature_names}",
        f"dataset record order: {dataset.record_ids}",
        f"data quality valid: {report.valid} (records={report.record_count})",
        f"feature-selection variables: {mapping.variable_names}",
    ]
