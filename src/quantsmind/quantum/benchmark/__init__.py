"""QMQ-05: benchmarking & classical comparison.

Public surface:

* :class:`Benchmark` — a serializable benchmark definition (problem +
  strategy + baseline + known optimum).
* :class:`BenchmarkSuite` / :func:`default_suite` — the canonical five
  deterministic benchmark problems.
* :class:`BenchmarkRunner` — executes a benchmark against a classical
  exhaustive baseline (reusing QMQ-02/04) and reports honest results.
* :class:`BenchmarkMetrics` — measured quality / performance / resources.
* :class:`BenchmarkComparison` / :class:`BenchmarkWinner` — deterministic
  strategy-vs-baseline classification (feasibility class first, then
  normalized objective; a completion alone never claims advantage).
* :class:`BenchmarkResult` / :class:`BenchmarkRunSummary` — serializable
  reports, repeated-run aggregates (§14) and the solution-report reference
  (composition, §17).
"""

from quantsmind.quantum.benchmark.metrics import (
    approximation_ratio,
    constraint_violations,
    is_better,
    normalized_score,
    objective_sense,
    optimality_gap,
    sense_label,
)
from quantsmind.quantum.benchmark.models import (
    BaselineConfig,
    Benchmark,
    BenchmarkComparison,
    BenchmarkMetrics,
    BenchmarkResult,
    BenchmarkRunSummary,
    BenchmarkSuite,
    BenchmarkWinner,
    metrics_rank_key,
)
from quantsmind.quantum.benchmark.runner import BenchmarkRunner
from quantsmind.quantum.benchmark.suite import (
    b1_knapsack,
    b2_linear_max,
    b3_qubo_min,
    b4_maxcut_triangle,
    b5_geq_max,
    default_suite,
    default_suite_examples,
)

__all__ = [
    "BaselineConfig",
    "Benchmark",
    "BenchmarkComparison",
    "BenchmarkMetrics",
    "BenchmarkResult",
    "BenchmarkRunner",
    "BenchmarkRunSummary",
    "BenchmarkSuite",
    "BenchmarkWinner",
    "approximation_ratio",
    "b1_knapsack",
    "b2_linear_max",
    "b3_qubo_min",
    "b4_maxcut_triangle",
    "b5_geq_max",
    "constraint_violations",
    "default_suite",
    "default_suite_examples",
    "is_better",
    "metrics_rank_key",
    "normalized_score",
    "objective_sense",
    "optimality_gap",
    "sense_label",
]
