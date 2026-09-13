"""QMQ-10 AI/ML Intelligence Foundation domain layer.

The ML layer turns small/structured ML selection problems
(classification, regression, feature selection, model selection,
hyperparameter optimization, clustering) into real QMQ problems solved by
the existing QMQ-02..06 pipeline through the QUBO formulation.

Design pillars (QMQ-10):

* **Reuse, not rewrite** — no second QUBO/Ising/solver/workflow/benchmark/
  interpreter is introduced; the ML layer only adds domain objects,
  objectives, constraints, a formulation adapter, a deterministic mapping,
  solutions, metrics, and a thin optimizer over the existing pipeline.
* **Delegation** — feature selection and clustering are delegated to the
  complete QMQ-09 Data layer (``source_domain="data"`` provenance).
* **Honest quantum semantics** — fitting is a well-posed quadratic binary
  problem; failure on a quantum runtime is reported honestly through the
  existing degradation rules.
* **No ML dependencies** — only the Python standard library is imported.

Examples and fixtures are deterministic and never import ``microquantum``.
"""

from quantsmind.quantum.ml.constraints import (
    HyperparameterOnePerParameterConstraint,
    MLAssignmentConstraint,
    MLClusterCountConstraint,
    MLCoefficientCountConstraint,
    MLConstraint,
    MLFeatureCountConstraint,
    ModelSelectionOneHotConstraint,
)
from quantsmind.quantum.ml.context import MLContext
from quantsmind.quantum.ml.errors import MLError, MLValidationError
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
from quantsmind.quantum.ml.formulation import MLFormulationAdapter
from quantsmind.quantum.ml.mapping import (
    DecodedHyperparameterChoice,
    DecodedMLCoefficient,
    DecodedModelSelection,
    MLMapper,
    MLMapping,
)
from quantsmind.quantum.ml.metrics import MLMetrics
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
    MLObjective,
    ModelSelectionObjective,
    RegressionLossObjective,
)
from quantsmind.quantum.ml.optimizer import MLOptimizationConfiguration, MLOptimizer
from quantsmind.quantum.ml.problem import MLProblem, MLProblemType
from quantsmind.quantum.ml.solution import (
    ClassificationSolution,
    HyperparameterSolution,
    MLBaseSolution,
    MLFeatureSelectionSolution,
    MLOptimizationResult,
    ModelSelectionSolution,
    RegressionSolution,
)

__all__ = [
    "MLError",
    "MLValidationError",
    "MLFeature",
    "MLRecord",
    "MLDataSet",
    "MLModelCandidate",
    "MLHyperparameterChoice",
    "MLHyperparameter",
    "MLContext",
    "MLObjective",
    "ClassificationLossObjective",
    "RegressionLossObjective",
    "ModelSelectionObjective",
    "HyperparameterObjective",
    "MLFeatureSelectionObjective",
    "MLClusteringDistanceObjective",
    "MLConstraint",
    "MLCoefficientCountConstraint",
    "ModelSelectionOneHotConstraint",
    "HyperparameterOnePerParameterConstraint",
    "MLFeatureCountConstraint",
    "MLAssignmentConstraint",
    "MLClusterCountConstraint",
    "MLProblemType",
    "MLProblem",
    "MLFormulationAdapter",
    "DecodedMLCoefficient",
    "DecodedModelSelection",
    "DecodedHyperparameterChoice",
    "MLMapping",
    "MLMapper",
    "MLMetrics",
    "MLBaseSolution",
    "ClassificationSolution",
    "RegressionSolution",
    "MLFeatureSelectionSolution",
    "ModelSelectionSolution",
    "HyperparameterSolution",
    "MLOptimizationResult",
    "MLOptimizationConfiguration",
    "MLOptimizer",
    "ml_dataset_example",
    "ml_classification_example",
    "ml_regression_example",
    "ml_feature_selection_example",
    "ml_model_selection_example",
    "ml_hyperparameter_example",
    "ml_clustering_example",
    "ml_all_examples",
]
