"""End-to-end domain intelligence examples (QMQ-11 §16).

These examples reuse the existing per-domain example problems and run them
through :class:`DomainIntelligence`: assessment (QMQ-03) and planning
inspect the *recommended* quantum path (automatic strategy — the honest
quantum-suitability of each problem is recorded), while solve/benchmark
execute on an explicit classical strategy so they are deterministic and
fast.
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.domain.intelligence import DomainIntelligence

__all__ = [
    "domain_finance_example",
    "domain_data_example",
    "domain_ml_example",
    "domain_pipeline_example",
]

# Examples execute the classical path explicitly (deterministic and cheap);
# assessment/planning keep the automatic strategy to record the problem's
# honest quantum suitability.
_EXAMPLE_STRATEGY = "classical"


def _finance_problem() -> Any:
    from quantsmind.quantum.finance.portfolio_examples import (
        example_portfolio_problem,
    )

    return example_portfolio_problem().to_financial_problem()


def _data_problem() -> Any:
    from quantsmind.quantum.data.examples import feature_selection_example

    return feature_selection_example()


def _ml_problem() -> Any:
    from quantsmind.quantum.ml.examples import ml_classification_example

    return ml_classification_example()


def _artifacts(intelligence: DomainIntelligence, problem: Any) -> dict[str, Any]:
    """Assess, plan, solve, benchmark and interpret one problem.

    Assessment and planning run with the automatic strategy (recording the
    problem's honest quantum recommendation/suitability); execution runs on
    the explicit classical strategy for determinism.
    """
    assessment = intelligence.assess(problem)
    plan = intelligence.plan(problem)
    result = intelligence.solve(problem, strategy=_EXAMPLE_STRATEGY)
    benchmark = intelligence.benchmark(problem, strategy=_EXAMPLE_STRATEGY)
    interpretation = intelligence.interpret(result)
    return {
        "problem": problem,
        "assessment": assessment,
        "plan": plan,
        "solve": result,
        "benchmark": benchmark,
        "interpretation": interpretation,
    }


def domain_finance_example() -> dict[str, Any]:
    """Full domain pipeline on the finance example problem (QMQ-11 §16 A).

    The example problem is the deterministic financial formulation of the
    canonical QMQ-08 risk-adjusted portfolio (cardinality-only, binary), so
    its QUBO maps losslessly and the end-to-end solve is well-defined.
    """
    return _artifacts(DomainIntelligence(), _finance_problem())


def domain_data_example() -> dict[str, Any]:
    """Full domain pipeline on the Data feature-selection example (QMQ-11 §16 B)."""
    return _artifacts(DomainIntelligence(), _data_problem())


def domain_ml_example() -> dict[str, Any]:
    """Full domain pipeline on the ML classification example (QMQ-11 §16 C)."""
    return _artifacts(DomainIntelligence(), _ml_problem())


def domain_pipeline_example() -> dict[str, Any]:
    """Cross-domain example: Finance, Data and ML through one intelligence.

    Returns a dict keyed by domain label with each problem's assessment,
    plan, solve, benchmark and interpretation artifacts.
    """
    intelligence = DomainIntelligence()
    return {
        "finance": _artifacts(intelligence, _finance_problem()),
        "data": _artifacts(intelligence, _data_problem()),
        "ml": _artifacts(intelligence, _ml_problem()),
    }
