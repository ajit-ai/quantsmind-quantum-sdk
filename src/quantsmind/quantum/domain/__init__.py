"""QMQ-11 — Advanced Quantum & Domain Intelligence.

This subpackage is the cross-domain intelligence layer on top of the
existing QMQ-03..06 pipeline.  It enables:

* explicit, registered domain dispatch (Finance, Portfolio, Data, ML)
  through :class:`~quantsmind.quantum.domain.registry.DomainRegistry`;
* inspectable assessment (:class:`~quantsmind.quantum.domain.assessment
  .ProblemAssessment`) and planning
  (:class:`~quantsmind.quantum.domain.plan.ExecutionPlan`) that reuse the
  QMQ-03 classification, formulation, strategy and algorithm engines;
* honest quantum suitability assessment
  (:class:`~quantsmind.quantum.domain.suitability
  .QuantumSuitabilityAssessor`) that never claims quantum execution without
  a real runtime;
* domain-agnostic solve/benchmark
  (:class:`~quantsmind.quantum.domain.intelligence.DomainIntelligence`)
  through the per-domain optimizers (QMQ-04..06).

No quantum engine, QUBO mapper or interpreter is duplicated here — every
execution reuses the existing pipeline.
"""

from quantsmind.quantum.domain.assessment import ProblemAssessment, assess_problem
from quantsmind.quantum.domain.errors import (
    DomainDispatchError,
    DomainError,
    DomainValidationError,
    UnsupportedDomainError,
)
from quantsmind.quantum.domain.examples import (
    domain_data_example,
    domain_finance_example,
    domain_ml_example,
    domain_pipeline_example,
)
from quantsmind.quantum.domain.intelligence import DomainIntelligence
from quantsmind.quantum.domain.plan import ExecutionPlan
from quantsmind.quantum.domain.registry import DomainBinding, DomainKind, DomainRegistry
from quantsmind.quantum.domain.result import DomainRunResult
from quantsmind.quantum.domain.suitability import (
    QuantumSuitability,
    QuantumSuitabilityAssessor,
    SuitabilityAssessment,
)

__all__ = [
    "DomainError",
    "DomainValidationError",
    "DomainDispatchError",
    "UnsupportedDomainError",
    "DomainKind",
    "DomainBinding",
    "DomainRegistry",
    "QuantumSuitability",
    "SuitabilityAssessment",
    "QuantumSuitabilityAssessor",
    "ProblemAssessment",
    "assess_problem",
    "ExecutionPlan",
    "DomainRunResult",
    "DomainIntelligence",
    "domain_finance_example",
    "domain_data_example",
    "domain_ml_example",
    "domain_pipeline_example",
]
