"""QMQ-03 — Algorithm & Computational Strategy Intelligence.

This subpackage implements the "intelligence" layer of QuantsMind Quantum:
it answers *what the problem is*, *how it should be formulated*, *which
strategy fits*, *which algorithm to recommend*, and *how the whole thing
will run*.  It owns no circuit, gate, state or simulator — those all live in
MicroQuantum (or in the QMQ-02 classical baseline).

Pipeline (QMQ-03 §14):

    problem -> classify -> suggest formulation -> choose strategy
             -> recommend algorithm -> build computation plan

Public entry points:

* :class:`~quantsmind.quantum.intelligence.classification.ProblemClassifier`
* :class:`~quantsmind.quantum.intelligence.recommender.FormulationRecommender`
* :class:`~quantsmind.quantum.intelligence.recommender.AlgorithmSelector`
* :class:`~quantsmind.quantum.intelligence.registry.AlgorithmRegistry`
* :class:`~quantsmind.quantum.intelligence.capabilities.CapabilityModel`
* :class:`~quantsmind.quantum.intelligence.plan.ComputationPlan`

None of these modules import ``microquantum`` at import time; capability
detection is lazy and graceful (QMQ-03 §11, §15).
"""

from quantsmind.quantum.intelligence.algorithms import (
    AlgorithmAvailability,
    AlgorithmCategory,
    AlgorithmDescriptor,
    AlgorithmRecommendation,
)
from quantsmind.quantum.intelligence.capabilities import CapabilityModel
from quantsmind.quantum.intelligence.classification import (
    ClassificationResult,
    ProblemClass,
    ProblemClassifier,
)
from quantsmind.quantum.intelligence.plan import ComputationPlan
from quantsmind.quantum.intelligence.recommender import (
    AlgorithmSelectionError,
    AlgorithmSelector,
    FormulationAlternative,
    FormulationRecommendation,
    FormulationRecommender,
)
from quantsmind.quantum.intelligence.registry import (
    AlgorithmRegistry,
    DuplicateAlgorithmError,
    UnknownAlgorithmError,
)

__all__ = [
    "ProblemClass",
    "ClassificationResult",
    "ProblemClassifier",
    "FormulationAlternative",
    "FormulationRecommendation",
    "FormulationRecommender",
    "AlgorithmCategory",
    "AlgorithmDescriptor",
    "AlgorithmAvailability",
    "AlgorithmRecommendation",
    "AlgorithmRegistry",
    "UnknownAlgorithmError",
    "DuplicateAlgorithmError",
    "CapabilityModel",
    "AlgorithmSelector",
    "AlgorithmSelectionError",
    "ComputationPlan",
]
