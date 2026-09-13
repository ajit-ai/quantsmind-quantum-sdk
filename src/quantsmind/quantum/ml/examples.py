"""Canonical QMQ-10 AI/ML Intelligence examples.

Every example is built exclusively from supplied, deterministic data and
never requires ``microquantum`` at import time.  Examples A–F:

A. :func:`ml_classification_example`      — binary-coefficient least-squares
   classification (known optimum SSR ``3.0``, all three features active),
B. :func:`ml_regression_example`          — regression variant of the same
   dataset (same optimum ``3.0``),
C. :func:`ml_feature_selection_example`   — delegated QMQ-09 selection
   (optimum ``{f0, f1}``, utility ``8.0``),
D. :func:`ml_model_selection_example`     — one-hot model selection
   (optimum candidate ``M4``, objective ``2.8``),
E. :func:`ml_hyperparameter_example`      — one-hot hyperparameter choice
   (optimum total gain ``3.3``),
F. :func:`ml_clustering_example`          — delegated QMQ-09 k=2 clustering
   of the classic geometry (clusters ``{r0, r2}`` and ``{r1, r3}``).
"""

from __future__ import annotations

from quantsmind.quantum.ml.constraints import (
    HyperparameterOnePerParameterConstraint,
    MLAssignmentConstraint,
    MLClusterCountConstraint,
    MLCoefficientCountConstraint,
    MLFeatureCountConstraint,
    ModelSelectionOneHotConstraint,
)
from quantsmind.quantum.ml.context import MLContext
from quantsmind.quantum.ml.mapping import MLMapper
from quantsmind.quantum.ml.models import (
    MLDataSet,
    MLFeature,
    MLHyperparameter,
    MLHyperparameterChoice,
    MLModelCandidate,
    MLRecord,
)
from quantsmind.quantum.ml.objectives import (
    ClassificationLossObjective,
    HyperparameterObjective,
    MLClusteringDistanceObjective,
    MLFeatureSelectionObjective,
    ModelSelectionObjective,
    RegressionLossObjective,
)
from quantsmind.quantum.ml.problem import MLProblem, MLProblemType

__all__ = [
    "ml_all_examples",
    "ml_dataset_example",
    "ml_classification_example",
    "ml_regression_example",
    "ml_feature_selection_example",
    "ml_model_selection_example",
    "ml_hyperparameter_example",
    "ml_clustering_example",
]


def ml_dataset_example() -> MLDataSet:
    """The canonical QMQ-10 dataset: 4 records over 3 features (f0..f2)."""
    return MLDataSet(
        name="qm10_demo",
        features=[
            MLFeature(name="f0", description="first explanatory feature"),
            MLFeature(name="f1", description="second explanatory feature"),
            MLFeature(name="f2", description="third explanatory feature"),
        ],
        records=[
            MLRecord(record_id="r0", values={"f0": 0.0, "f1": 1.0, "f2": 2.0}, target=2.0),
            MLRecord(record_id="r1", values={"f0": 1.0, "f1": 2.0, "f2": 0.0}, target=4.0),
            MLRecord(record_id="r2", values={"f0": 0.0, "f1": 0.0, "f2": 1.0}, target=1.0),
            MLRecord(record_id="r3", values={"f0": 2.0, "f1": 1.0, "f2": 1.0}, target=5.0),
        ],
        description="canonical QMQ-10 demo data (supplied)",
    )


def _ml_context() -> MLContext:
    return MLContext(
        purpose="ml_optimization",
        subdomain="tabular",
        assumptions={"source": "supplied demo data"},
    )


def ml_classification_example() -> MLProblem:
    """Example A — binary-coefficient least-squares classification.

    The optimum activates all three features (``f0, f1, f2``) with a residual
    sum of squares of exactly ``3.0``.
    """
    return MLProblem(
        name="ml_classification_demo",
        dataset=ml_dataset_example(),
        problem_type=MLProblemType.CLASSIFICATION,
        objectives=[ClassificationLossObjective(name="ssr", description="residual sum of squares")],
        constraints=[
            MLCoefficientCountConstraint(name="at_most_three", max_coefficients=3.0),
        ],
        context=_ml_context(),
        description="Example A: least-squares classification on the canonical dataset",
    )


def ml_regression_example() -> MLProblem:
    """Example B — regression variant of the same least-squares objective."""
    return MLProblem(
        name="ml_regression_demo",
        dataset=ml_dataset_example(),
        problem_type=MLProblemType.REGRESSION,
        objectives=[RegressionLossObjective(name="ssr", description="residual sum of squares")],
        context=_ml_context(),
        description="Example B: least-squares regression on the canonical dataset",
    )


def ml_feature_selection_example() -> MLProblem:
    """Example C — delegated QMQ-09 feature selection.

    Utilities ``{f0: 3, f1: 5, f2: 2}`` with unit costs and a maximum of two
    features; the optimum selection is ``{f0, f1}`` with utility ``8.0``.
    """
    return MLProblem(
        name="ml_feature_selection_demo",
        dataset=ml_dataset_example(),
        problem_type=MLProblemType.FEATURE_SELECTION,
        objectives=[
            MLFeatureSelectionObjective(
                name="max_utility",
                utilities={"f0": 3.0, "f1": 5.0, "f2": 2.0},
                costs={"f0": 1.0, "f1": 1.0, "f2": 1.0},
                penalty=1.0,
            )
        ],
        constraints=[
            MLFeatureCountConstraint(name="at_most_two", max_features=2.0),
        ],
        description="Example C: delegated feature selection (max 2 features)",
    )


def ml_model_selection_example() -> MLProblem:
    """Example D — one-hot model selection.

    Candidate objectives ``validation_loss + complexity_penalty``: M1 3.4,
    M2 2.9, M3 3.1, M4 2.8, so the optimum selects ``M4`` with objective
    ``2.8``.
    """
    return MLProblem(
        name="ml_model_selection_demo",
        problem_type=MLProblemType.MODEL_SELECTION,
        objectives=[
            ModelSelectionObjective(
                name="model_loss",
                description="validation loss plus complexity penalty",
            )
        ],
        constraints=[ModelSelectionOneHotConstraint(name="select_one_model")],
        candidates=[
            MLModelCandidate(model_id="M1", validation_loss=3.2, complexity_penalty=0.2),
            MLModelCandidate(model_id="M2", validation_loss=2.4, complexity_penalty=0.5),
            MLModelCandidate(model_id="M3", validation_loss=1.9, complexity_penalty=1.2),
            MLModelCandidate(model_id="M4", validation_loss=2.7, complexity_penalty=0.1),
        ],
        description="Example D: one-hot model selection over M1..M4",
    )


def ml_hyperparameter_example() -> MLProblem:
    """Example E — one-hot per-parameter hyperparameter choice.

    ``learning_rate`` gains (0.8, 1.5, 1.2) and ``depth`` gains (0.9, 1.8,
    1.4); the optimum total gain is ``1.5 + 1.8 = 3.3``.
    """
    return MLProblem(
        name="ml_hyperparameter_demo",
        problem_type=MLProblemType.HYPERPARAMETER_OPTIMIZATION,
        objectives=[
            HyperparameterObjective(
                name="total_gain",
                description="sum of per-parameter gains",
            )
        ],
        constraints=[HyperparameterOnePerParameterConstraint(name="one_per_parameter")],
        hyperparameters=[
            MLHyperparameter(
                name="learning_rate",
                choices=[
                    MLHyperparameterChoice(value=0.001, gain=0.8),
                    MLHyperparameterChoice(value=0.01, gain=1.5),
                    MLHyperparameterChoice(value=0.1, gain=1.2),
                ],
            ),
            MLHyperparameter(
                name="depth",
                choices=[
                    MLHyperparameterChoice(value=1, gain=0.9),
                    MLHyperparameterChoice(value=2, gain=1.8),
                    MLHyperparameterChoice(value=3, gain=1.4),
                ],
            ),
        ],
        description="Example E: one-hot hyperparameter choice (gain maximization)",
    )


def ml_clustering_example() -> MLProblem:
    """Example F — delegated QMQ-09 k=2 clustering.

    Uses the classic QMQ-09 geometry: clusters ``{r0, r2}`` and ``{r1, r3}``
    with a total within-cluster distance of approximately ``8.2156``.
    """
    dataset = MLDataSet(
        name="qm10_clusters",
        features=[
            MLFeature(name="height"),
            MLFeature(name="width"),
            MLFeature(name="depth"),
            MLFeature(name="brightness"),
            MLFeature(name="texture"),
        ],
        records=[
            MLRecord(
                record_id="r0",
                values={
                    "height": 0.0,
                    "width": 1.0,
                    "depth": 2.0,
                    "brightness": 3.0,
                    "texture": 4.0,
                },
                target=0.0,
            ),
            MLRecord(
                record_id="r1",
                values={
                    "height": 4.0,
                    "width": 3.0,
                    "depth": 2.0,
                    "brightness": 5.0,
                    "texture": 1.0,
                },
                target=0.0,
            ),
            MLRecord(
                record_id="r2",
                values={
                    "height": 1.0,
                    "width": 2.0,
                    "depth": 0.0,
                    "brightness": 1.0,
                    "texture": 5.0,
                },
                target=0.0,
            ),
            MLRecord(
                record_id="r3",
                values={
                    "height": 3.0,
                    "width": 0.0,
                    "depth": 4.0,
                    "brightness": 2.0,
                    "texture": 2.0,
                },
                target=0.0,
            ),
        ],
        description="canonical QMQ-10 clustering data (supplied)",
    )
    return MLProblem(
        name="ml_clustering_demo",
        dataset=dataset,
        problem_type=MLProblemType.CLUSTERING,
        objectives=[
            MLClusteringDistanceObjective(
                name="min_within_cluster_distance",
                description="sum of within-cluster pairwise distances",
            )
        ],
        constraints=[
            MLAssignmentConstraint(name="assignment"),
            MLClusterCountConstraint(name="cluster_size", min_records=1.0, max_records=2.0),
        ],
        k=2,
        description="Example F: delegated k=2 clustering (quadratic binary QUBO)",
    )


def ml_all_examples() -> list[str]:
    """Run every canonical example and return the produced artifacts."""
    dataset = ml_dataset_example()
    _ = ml_classification_example()
    _ = ml_regression_example()
    _ = ml_feature_selection_example()
    _ = ml_model_selection_example()
    _ = ml_hyperparameter_example()
    _ = ml_clustering_example()
    mapping = MLMapper().map(ml_classification_example())
    return [
        f"dataset feature order: {dataset.feature_names}",
        f"dataset record order: {dataset.record_ids}",
        f"dataset shape: {dataset.shape}",
        f"classification variables: {mapping.variable_names}",
    ]
