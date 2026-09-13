"""Data Intelligence domain layer of QuantsMind Quantum (QMQ-09).

The Data layer models data-intelligence optimization problems as validated,
deterministic objects — features, records, datasets, relationships, data
quality, and the feature-selection / clustering problem families — and
converts them into the existing QMQ mathematical/optimization infrastructure
(QMQ-02 formulation, QUBO mapping, workflow, execution, benchmark,
interpretation).  It works entirely from supplied/synthetic data: no live
data ingestion, no ML framework, no connectors, no cloud, no scraping.

QMQ-09 scope:

* observations/features (``DataFeature``, ``DataRecord``, ``DataSet``,
  ``FeatureVector``),
* distance & similarity primitives and pairwise relationships,
* deterministic data-quality reports,
* feature-selection objectives/constraints and clustering as a real
  quadratic binary QUBO (assignment equality constraints),
* the ``DataProblem`` domain representation, ``DataFormulationAdapter``,
  ``DataMapper``, ``DataMetrics``, ``DataSolution`` and ``DataOptimizer``,
* canonical examples A–G and JSON-safe serialization.

Importing this package never requires ``microquantum``.
"""

from __future__ import annotations

from quantsmind.quantum.data.constraints import (
    AssignmentConstraint,
    ClusterCountConstraint,
    DataConstraint,
    FeatureCountConstraint,
    FeatureGroupConstraint,
    constraint_from_dict,
)
from quantsmind.quantum.data.context import DataContext
from quantsmind.quantum.data.errors import DataError, DataValidationError
from quantsmind.quantum.data.examples import (
    all_examples,
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
from quantsmind.quantum.data.formulation import DataFormulationAdapter
from quantsmind.quantum.data.mapping import (
    DataMapper,
    DataMapping,
    DecodedClusterAssignment,
    DecodedDataFeature,
)
from quantsmind.quantum.data.metrics import DataMetrics
from quantsmind.quantum.data.models import (
    DataFeature,
    DataRecord,
    DataSet,
    FeatureVector,
)
from quantsmind.quantum.data.numerics import (
    euclidean_distance,
    similarity_from_distance,
    squared_euclidean_distance,
    weighted_squared_euclidean_distance,
)
from quantsmind.quantum.data.objectives import (
    ClusteringDistanceObjective,
    DataObjective,
    FeatureSelectionObjective,
    FeatureUtilityObjective,
    SelectionCostObjective,
    objective_from_dict,
)
from quantsmind.quantum.data.optimizer import (
    DataOptimizationConfiguration,
    DataOptimizer,
)
from quantsmind.quantum.data.problem import DataProblem, DataProblemType
from quantsmind.quantum.data.quality import DataQualityReport, assess_data_quality
from quantsmind.quantum.data.relationship import (
    DataRelationship,
    pairwise_relationship,
)
from quantsmind.quantum.data.solution import (
    DataOptimizationResult,
    DataSolution,
)

__all__ = [
    # observations / features
    "DataFeature",
    "DataRecord",
    "DataSet",
    "FeatureVector",
    # context / relationships / quality
    "DataContext",
    "DataRelationship",
    "pairwise_relationship",
    "DataQualityReport",
    "assess_data_quality",
    # distance & similarity primitives
    "euclidean_distance",
    "squared_euclidean_distance",
    "weighted_squared_euclidean_distance",
    "similarity_from_distance",
    # objectives / constraints
    "DataObjective",
    "FeatureUtilityObjective",
    "SelectionCostObjective",
    "FeatureSelectionObjective",
    "ClusteringDistanceObjective",
    "objective_from_dict",
    "DataConstraint",
    "FeatureCountConstraint",
    "FeatureGroupConstraint",
    "AssignmentConstraint",
    "ClusterCountConstraint",
    "constraint_from_dict",
    # problem / formulation / mapping
    "DataProblemType",
    "DataProblem",
    "DataFormulationAdapter",
    "DataMapper",
    "DataMapping",
    "DecodedDataFeature",
    "DecodedClusterAssignment",
    # metrics / solution / optimizer
    "DataMetrics",
    "DataSolution",
    "DataOptimizationResult",
    "DataOptimizationConfiguration",
    "DataOptimizer",
    # errors
    "DataError",
    "DataValidationError",
    # examples
    "dataset_example",
    "data_context_example",
    "feature_selection_example",
    "selection_cost_example",
    "grouped_feature_selection_example",
    "similarity_example",
    "quality_example",
    "clustering_example",
    "serialization_example",
    "all_examples",
]
