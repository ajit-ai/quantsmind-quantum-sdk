# Quantum Computing Package

## Purpose

`quantsmind.quantum` is the **domain-intelligence layer** of the QuantsMind
SDK. It connects QuantsMind's domain and scientific abstractions to
MicroQuantum (standalone quantum computing engine, MIT): it builds declarative
problem descriptions, selects computation strategies, maps domain models onto
runtime pipelines, and enriches quantum results with QuantsMind metadata.

It does **not** reimplement a quantum engine. Circuits, gates, operators,
state vectors, simulators, algorithms, providers, transpilers and runtimes
are owned by MicroQuantum.

## Dependency Direction

```
Domain Systems
   |
   v
QuantsMind Quantum  (domain foundation + thin integration layer)
   |
   v
MicroQuantum       (engine: circuits, algorithms, simulators, providers)
```

- `Domain Systems -> QuantsMind Quantum -> MicroQuantum`: allowed.
- `MicroQuantum -> QuantsMind`: forbidden. MicroQuantum never imports
  QuantsMind.

## Installation

Requires Python **3.13+**. The core SDK has **zero required dependencies**:

```
pip install quantsmind
```

Everything classical (problem construction, formulation, mapping, classical
execution, benchmarking, interpretation, provenance, all finance/data/ML
domains) works immediately.  To enable **quantum / hybrid execution**,
additionally install the optional engine extra (MicroQuantum, a standalone
NumPy-based quantum computing SDK):

```
pip install "quantsmind[quantum]"
```

`import quantsmind.quantum` never requires MicroQuantum; quantum execution is
requested explicitly (strategy `"quantum"` / `"hybrid"`) and either runs
through MicroQuantum when available or degrades honestly (recorded fallback,
never a fabricated quantum result).

### Quick start

```python
from quantsmind.quantum import domain_finance_example

artifacts = domain_finance_example()  # assess -> plan -> solve -> benchmark -> interpret
solve = artifacts["solve"]

print(solve.feasible)  # True
print(solve.fallback_used)  # False
print(solve.interpretation.status.value)  # "executed"
print(round(solve.objective_value, 3))  # 0.038
```

New to quantum execution? Start smaller: `python examples/bell_state.py`
runs a declarative H + CNOT program on the local statevector backend
(see `docs/bell-state-example.md`).

Supported domains (all classical by default; quantum/hybrid enabled when the
quantum extra is installed): **finance** (incl. portfolio optimization),
**data** (feature selection, clustering), **ml** (classification, regression,
model/hyperparameter selection), and the registered **domain intelligence**
layer (`assess` / `plan` / `solve` / `benchmark` / `interpret`).

Honest wording: QuantsMind Quantum is **quantum-capable** (it *executes*
through MicroQuantum when available) and **hybrid-capable** — it does not
claim quantum advantage, quantum speedup, or production quantum optimization.
It is supplied-data only: no live market data, no trading, no investment
advice, no ML model training.

## Architecture (QMQ-01)

Importing `quantsmind.quantum` never requires `microquantum` to be installed;
MicroQuantum is imported lazily only when a quantum execution API is called.

| Layer | Module | Contents |
| --- | --- | --- |
| core | `quantsmind.quantum.core` | `QuantumProblem`, `Variable`, `Objective`, `Constraint`, `DomainContext`, `ProblemSolution`; serializable via `to_dict` / `from_dict` |
| formulation | `quantsmind.quantum.formulation` | `MathematicalModel` base + `OptimizationModel`, `GraphModel`, `MLModel`, `SimulationModel`, `StatisticalModel`; dispatchers `formulate` / `model_from_dict` keyed by `metadata["model_kind"]` |
| strategy | `quantsmind.quantum.strategy` | `ComputationStrategy` enum (`CLASSICAL`, `QUANTUM`, `HYBRID`, `QUANTUM_INSPIRED`, `AUTO`) + deterministic `StrategySelector` with `microquantum_available()` / `available_algorithms()` overrides |
| mapping | `quantsmind.quantum.mapping` | `DomainMapper` ABC, `MappingResult`, `MappingError`; `QuantumCircuitMapper` maps a `QuantumProgram` onto MicroQuantum (validate + build) |
| workflow | `quantsmind.quantum.workflow` | `QuantumWorkflow`: declarative problem -> strategy -> mapping -> execution -> report; `WorkflowError` |
| result | `quantsmind.quantum.result` | `SolutionReport`, `SolutionInterpreter` / `Interpretation` / `InterpretationQuality`, `Provenance`; low-level `QuantumResult` lives in `quantsmind.quantum.circuit_result` |
| integration | `quantsmind.quantum.integration` | MicroQuantum facade: lazy `require_microquantum()`, `microquantum_available()`, `resolve_backend()` |

Meaning of `QuantumProblem` in this package (QMQ-01/QMQ-02): it is the
**domain problem holder** (`variables` + `objective` + `constraints`), not a
quantum circuit problem. A single problem object is carried through
formulation -> strategy selection -> mapping -> workflow; the mathematical
encoding into QUBO/Ising and the quantum delegation happen in the QMQ-02
layers below.

## QMQ-02 — Mathematical Formulation & Domain-to-Quantum Mapping

QMQ-02 adds the **optimization encoding pipeline**. A declarative
`QuantumProblem` with symbolic string expressions is converted to a
mathematical formulation, then to a QUBO, then to an Ising model, and finally
delegated to MicroQuantum (QAOA) or solved with a classical exact baseline.

Two independent, tested pipelines share the same encoding core:

```
Classical pipeline                          Quantum pipeline
   QuantumProblem                              QuantumProblem
        |                                           |
        v                                           v
   OptimizationModel                          OptimizationModel
        |        \______________________             |
        v                                 v           v
   QUBOModel (penalties + slacks)     QUBOModel ----+-> IsingModel(-> QUBO round-trip)
        |                                                        |
        v                                                        v
   ClassicalSolver (exhaustive, feasibility-aware)          MicroQuantum QAOA (run_qaoa)
        |                                                        |
        v                                                        v
   ProblemSolution                                      QaoaExecutionResult -> SolutionReport
```

| Layer | Module | Contents |
| --- | --- | --- |
| expression | `quantsmind.quantum.optimization.expression` | Symbolic expression engine: `Expression` (`VariableExpression`, `Constant`, `Mul`, `Add`, `Power`, ...), tokenizer/recursive-descent `parse_expression`, `expand()` to canonical monomial dict, numeric `evaluate`, coefficient helpers, typed `ExpressionError` / `ExpressionParseError`. |
| qubo | `quantsmind.quantum.optimization.qubo` | `QUBOModel` (binary quadratic pseudo-Boolean model): `linear`, `quadratic`, `constant`, `offset`, `energy(assignment)`, `to_dict` / `from_dict`, quantified variables; `QUBOError`. Round-trips exactly with Ising. |
| penalties | `quantsmind.quantum.optimization.penalties` | `ConstraintPenalizer` folds `Constraint`s into `PenaltyTerm`s (`eq`/`le`/`ge`, slack bits, `P*(rhs)^2`). Exact: satisfying assignment contributes 0. |
| ising | `quantsmind.quantum.optimization.ising` | `IsingModel` (`h` fields, `couplings` adjacency, spins +-1): `energy(spins)`, `from_qubo` / `to_qubo` (exact both directions), `IsingError`. |
| classical | `quantsmind.quantum.optimization.classical` | `ClassicalSolver` baseline: exhaustive search with constraint-aware feasibility, deterministic tie-breaking, objective + constraint violation reporting, `exhaustiveness`/`energy` metadata; `solve` returns `ProblemSolution`. |
| mapping | `quantsmind.quantum.mapping` | `ProblemMapper`/`DomainMapper`, `QUBOMapper` (problem -> `QUBOModel` with penalty weight), `IsingMapper` (QUBO -> `IsingModel`), `MappingResult` (`payload`, `target`, `metadata`). |
| workflow | `quantsmind.quantum.workflow` | `QuantumWorkflow` encodes and runs either path, choosing `CLASSICAL`/`QUANTUM` via the selector, honouring penalty weight, layer count, QAOA optimizer and shots; raises `WorkflowError` when mapping/execution cannot proceed. |
| integration | `quantsmind.quantum.integration` | `run_qaoa(ising, ...)` -> `QaoaExecutionResult` (`energy`, `assignment`, `counts`, `backend_name`, `converged`, `metadata`), `qaoa_available()`, Ising <-> `PaulSum` / `OptimizationProblem` conversion for MicroQuantum. |

Key correctness invariants (enforced by tests):

- `QUBOModel.energy(assignment)` == `IsingModel.energy(spins=2x-1)` exactly.
- `IsingModel -> to_qubo() -> IsingModel` is an exact round trip.
- A feasible assignment contributes penalty 0; constraint satisfaction is
  exact, not approximate.
- A classical run is optimal among feasible assignments (exhaustive search
  over the decision variables, slack bits excluded from the reported solution).
- QAOA runs delegate entirely to MicroQuantum; results carry `energy` and
  `assignment` decoded from the measured bitstring and are re-encoded via
  `QaoaExecutionResult` for the report.

### QMQ-02 example — 0/1 knapsack

```python
from quantsmind.quantum import (
    QuantumProblem,
    Variable,
    Objective,
    ObjectiveSense,
    Constraint,
    QuantumWorkflow,
)
from quantsmind.quantum.strategy.strategy import ComputationStrategy

problem = QuantumProblem("knapsack", domain="combinatorial/knapsack")
problem.add_variable(Variable.binary("x0"))
problem.add_variable(Variable.binary("x1"))
problem.add_variable(Variable.binary("x2"))
problem.add_objective(Objective("value", ObjectiveSense.MAXIMIZE, expression="3*x0 + 4*x1 + 5*x2"))
problem.add_constraint(Constraint.le("capacity", expression="2*x0 + 3*x1 + 4*x2", value=5.0))

report = QuantumWorkflow(problem).run()
# classical exhaustive baseline: {x0: 1, x1: 1, x2: 0}, value 7.0, feasible
```

For the quantum path set `problem.preferred_strategy = ComputationStrategy.QUANTUM`
and pass `num_layers=1`, `shots=...`, `seed=...` and a small QAOA optimizer to
`QuantumWorkflow(...)`; `report.provenance.executor == "microquantum/qaoa"`.

## QMQ-03 — Algorithm & Computational Strategy Intelligence

QMQ-03 adds the **intelligence layer**: it classifies what a problem *is*,
recommends the natural mathematical encoding, chooses the computation
strategy, recommends the best algorithm, and produces a serializable
`ComputationPlan`. The workflow now runs:

```
QuantumProblem -> classify -> recommend (formulation + strategy + algorithm)
              -> plan -> map -> execute -> SolutionReport
```

| Layer | Module | Contents |
| --- | --- | --- |
| classification | `quantsmind.quantum.intelligence.classification` | `ProblemClass` (`binary_optimization`, `integer_optimization`, `continuous_optimization`, `graph_optimization`, `constraint_optimization`, `search`, `sampling`, `simulation`, `machine_learning`, `statistical`, `linear_algebra`, `unknown`); deterministic `ProblemClassifier` over variable types, formulation kind, structure and an authoritative `metadata["problem_class"]` override. Returns `ClassificationResult` with label + reasons. |
| capabilities | `quantsmind.quantum.intelligence.capabilities` | `CapabilityModel` snapshot (`microquantum_installed`, `quantum_enabled`, `backend_available`, `qml_available`, `classical_baseline_available`, per-algorithm availability) with `detect()`, `is_available()`, `required_caps_met()`, `executable_algorithms()`, JSON round-trip. |
| algorithms | `quantsmind.quantum.intelligence.algorithms` | `AlgorithmCategory`, `AlgorithmDescriptor` (problem classes, formulations, strategies, execution modes, microquantum identifier, required capabilities), `AlgorithmAvailability` (three tiers), `AlgorithmRecommendation` (algorithm, `suitability_score`, `reason`, fallbacks, capabilities, flags). |
| registry | `quantsmind.quantum.intelligence.registry` | `AlgorithmRegistry` default catalog (15 MicroQuantum algorithms + `qml` + `exhaustive`) with `register` / `get` / `find` / `available` / `executable_algorithms`, `DuplicateAlgorithmError`, `UnknownAlgorithmError`, JSON round-trip. |
| recommender | `quantsmind.quantum.intelligence.recommender` | `FormulationRecommender` (binary->qubo, integer/constraint->optimization, continuous->optimization, graph->graph+qubo, simulation->simulation, ml->ml, statistical->statistical, search/sampling/linear->mathematical); `AlgorithmSelector` picks the best executable algorithm per class/formulation/strategy with `user_requested` honouring, never-silent fallbacks (`AlgorithmSelectionError` unless `allow_fallback`), classical baseline as fallback. |
| plan | `quantsmind.quantum.intelligence.plan` | `ComputationPlan`: algorithm, mapping, executor, fallbacks, gating capabilities, classification, recommendation, formulation recommendation; `to_dict` / `from_dict`. |
| strategy | `quantsmind.quantum.strategy.selector` | `select_reasoned()` -> `StrategyDecision` (strategy + reasons + signals + metadata): explicit preference (downgraded when no quantum runtime), no-runtime -> `CLASSICAL`, `quantum_suitable` override, structure-aware AUTO refinements (simulation -> QUANTUM, ml/statistical -> HYBRID, continuous/integer -> CLASSICAL, small-size -> HYBRID for hybrid comparison), size thresholds -> QUANTUM / QUANTUM_INSPIRED / CLASSICAL. |
| workflow | `quantsmind.quantum.workflow` | `QuantumWorkflow` now accepts `classifier`, `algorithm_selector`, `capabilities`, `requested_algorithm`, `allow_algorithm_fallback`; `run()` attaches `classification`, `recommendation`, `computation_plan` to `SolutionReport`. |

Design invariants (enforced by tests):

- **Never silent**: a recommended-but-unavailable algorithm is recorded in
  metadata (`recommended_but_unavailable`) with an executable fallback; a
  requested algorithm is honoured or requires `allow_algorithm_fallback`.
- **No fake advantage**: `suitability_score` is a deterministic rule-based
  score (never a confidence claim); no algorithm is endorsed as "better than
  the classical baseline" without evidence.
- **No forced QUBO**: QUBO is only recommended when the lossless binary
  encoding exists (continuous problems stay in the optimization formulation).
- **Hybrid comparison**: at small sizes a HYBRID strategy is chosen so the
  QAOA result can be compared against the classical exhaustive baseline.

### QMQ-03 example

```python
from quantsmind.quantum import (
    QuantumProblem,
    Variable,
    Objective,
    ObjectiveSense,
    QuantumWorkflow,
    ProblemClassifier,
    FormulationRecommender,
    AlgorithmSelector,
)

problem = QuantumProblem("maxcut", domain="graph/maxcut")
problem.add_variable(Variable.binary("x0"))
problem.add_variable(Variable.binary("x1"))
problem.add_objective(
    Objective("cut", ObjectiveSense.MINIMIZE, expression="-2*x0 - 2*x1 + 4*x0*x1")
)

classification = ProblemClassifier().classify(problem)
formulation = FormulationRecommender().recommend(problem)
recommendation = AlgorithmSelector().select(problem)
print(classification.label)  # binary_optimization
print(recommendation.algorithm)  # qaoa (or exhaustive when unavailable)

workflow = QuantumWorkflow(problem)
report = workflow.run()
print(report.plan.algorithm)  # planned algorithm id
print(report.classification.label)  # classification carried into the report
```

## QMQ-04 — Hybrid Workflow & Execution

QMQ-04 adds the **execution layer**: plans are executed by dedicated
executors (classical / quantum / hybrid) producing normalized execution
results, and hybrid runs produce an explicit, deterministic classical-vs-
quantum comparison with a selected winner. No quantum result is ever
fabricated and no speedup/superiority claim is ever derived from the
comparison.

```
QuantumProblem -> classify -> recommend -> plan -> map
              -> execute (classical | quantum | hybrid) -> SolutionReport
```

| Layer | Module | Contents |
| --- | --- | --- |
| errors | `quantsmind.quantum.execution.errors` | Typed failure taxonomy: `WorkflowError`, `ExecutionError`, `ClassicalExecutionError`, `QuantumExecutionError`, `HybridExecutionError`, `InvalidQuantumResultError`, and `MicroQuantumUnavailableError(ImportError, WorkflowError)` — engine absence is both `ImportError`-catchable and part of the workflow taxonomy, with a `quantsmind[quantum]` install hint. |
| options | `quantsmind.quantum.execution.options` | Frozen `ExecutionOptions` (strategy, algorithm, shots, seed, num_layers, optimization_level, metadata) with JSON round-trip and `resolved_strategy`; workflow-level args act as merge defaults. |
| evaluation | `quantsmind.quantum.execution.evaluation` | Shared feasibility/objective-evaluation helpers giving every executor a single, consistent contract. |
| executor | `quantsmind.quantum.execution.executor` | `Executor` ABC + `ExecutorContext` (problem, plan, formulation, qubo, ising, options). |
| comparison | `quantsmind.quantum.execution.comparison` | `ExecutionComparisonEntry` + `ExecutionComparison.build`: only *executed* legs are ranked — feasible first, then objective per sense (QUBO energy as fallback, lower is better), deterministic tie-break preferring the classical exact baseline; winner + reasons recorded. |
| classical | `quantsmind.quantum.execution.classical` | `ClassicalExecutor` runs the exhaustive exact baseline (`ExhaustiveSolver` unchanged); `ExhaustiveLimitError` / `NoFeasibleSolutionError` become `ClassicalExecutionError`. `ClassicalExecutionResult.from_solver`. |
| quantum | `quantsmind.quantum.execution.quantum` | `QuantumExecutor` delegates to `run_qaoa`; `prepare()` maps engine absence to `MicroQuantumUnavailableError` (ImportError) lazily; `validate()` checks assignment key coverage, binary values and recomputed QUBO energy (1e-6). `QuantumExecutionResult.from_qaoa`. |
| hybrid | `quantsmind.quantum.execution.hybrid` | `HybridExecutor` runs **both** legs. An unavailable/broken quantum leg is recorded `skipped`/`failed`; the executed classical leg wins by default and the reason says so. `HybridExecutionResult` with `classical` / `quantum` / `comparison` / `selected` / `selected_assignment`. |
| workflow | `quantsmind.quantum.workflow` | `WorkflowState` lifecycle (CREATED..COMPLETED/FAILED) with strict forward transitions; `execution_options()` merge; `create_executor()` override; `run()` guards reuse and marks FAILED on pipeline errors; `execute()` dispatches on the resolved strategy with QUANTUM -> classical fallback when the engine is unavailable and `allow_fallback`. |

Behavior invariants (enforced by tests):

- **Honest hybrid**: a hybrid run performs both computations; the comparison
  never ranks a leg that did not execute and never claims a quantum
  advantage.
- **Engine absence**: `import quantsmind.quantum` never imports microquantum.
  QUANTUM with the engine absent raises `MicroQuantumUnavailableError`
  (an `ImportError` and a `WorkflowError`, hint `quantsmind[quantum]`) at
  `map()`. HYBRID degrades honestly — with the engine wholly absent the
  strategy selector refuses HYBRID and falls back to `CLASSICAL`; when the
  engine is installed but unusable the quantum leg is recorded `skipped` with
  `quantum_unavailable` and the classical leg wins.
- **Deterministic selection**: ties resolve to the classical exact baseline;
  winner and reason are recorded in `report.comparison`.

### QMQ-04 example — hybrid max-cut with QAOA vs the exhaustive baseline

```python
from quantsmind.quantum import (
    QuantumProblem,
    Variable,
    Objective,
    ObjectiveSense,
    QuantumWorkflow,
    ComputationStrategy,
)

problem = QuantumProblem("maxcut_triangle", domain="optimization")
for variable in ("a", "b", "c"):
    problem.add_variable(Variable.binary(variable))
problem.add_objective(
    Objective(
        "cut",
        ObjectiveSense.MAXIMIZE,
        expression="1*(a+b-2*a*b) + 1*(b+c-2*b*c) + 1*(a+c-2*a*c)",
    )
)
problem.preferred_strategy = ComputationStrategy.HYBRID

report = QuantumWorkflow(problem, num_layers=1, shots=64, seed=7).run()
print(report.strategy)  # ComputationStrategy.HYBRID
print(report.comparison.winner)  # deterministic winner (classical/quantum)
print(report.provenance.executor)  # "hybrid"
print(report.solution.assignments)  # selected assignment
```

MicroQuantum performs the quantum computation; QuantsMind Quantum
orchestrates the computational strategies around it (classical exact
baseline, QAOA delegation, honest hybrid selection).

## QMQ-05 — Benchmarking & Classical Comparison

QMQ-05 adds a **benchmarking layer**: a `Benchmark` definition (problem +
strategy + classical baseline + known optimum) is executed by a
`BenchmarkRunner` and reported as a serializable `BenchmarkResult`. Every
benchmark is compared against a **real classical exact baseline** (the
QMQ-02/04 exhaustive solver reused unchanged) using one centralized,
deterministic ranking policy — and no comparison ever implies a quantum
advantage.

```
Benchmark --(runner)--> strategy workflow   --metrics-->
                    \--> classical baseline workflow --metrics-->
                          -> BenchmarkComparison (winner) -> BenchmarkResult
```

| Layer | Module | Contents |
| --- | --- | --- |
| models | `quantsmind.quantum.benchmark.models` | `Benchmark` (id, name, problem, strategy, algorithm, `ExecutionOptions`, `BaselineConfig`, `known_optimum`, metadata; `to_dict`/`from_dict`, `resolved_strategy`), `BaselineConfig` (kind `"classical"`, enabled, `ExhaustiveSolver`/`max_variables`), `BenchmarkWinner` enum, `BenchmarkComparison`, `BenchmarkMetrics`, `BenchmarkResult`, `BenchmarkRunSummary`, `BenchmarkSuite`. |
| metrics | `quantsmind.quantum.benchmark.metrics` | Centralized sense/energy math: `objective_sense`, `normalized_score` (objective per sense; energy fallback always lower-better — the QMQ-04 energy-direction fix), `optimality_gap` (`\|optimum - achieved\| / \|optimum\|`, absolute distance when optimum is 0), `approximation_ratio` (max `achieved/optimum`, min `optimum/achieved`, only when interpretable), `constraint_violations` (count + magnitude). |
| runner | `quantsmind.quantum.benchmark.runner` | `BenchmarkRunner.run(benchmark, runs=1, raise_on_error=False)`; strategy forcing via a clone with `preferred_strategy` set (never `ExecutionOptions.strategy`, which only feeds context/provenance); honest failure recording with typed errors; `runs>1` aggregation (§14). |
| suite | `quantsmind.quantum.benchmark.suite` | `default_suite()` — five small deterministic members (b1 knapsack, b2 linear max, b3 QUBO min with zero optimum, b4 Max-Cut triangle reused from QMQ-04, b5 constrained `>=` max) with explicit `known_optimum`. |

Deterministic comparison policy (`BenchmarkComparison.build`, §12/§13):

1. **Feasibility class first**: `feasible > unknown > infeasible`.
2. Both feasible (or unknown): the better normalized objective wins per sense
   (energy fallback: **lower is always better**).
3. Both infeasible: fewer constraint violations wins, then the objective.
4. Exact equalities are a `TIE`.
5. Missing/disabled baseline, missing strategy outcome, or no comparable
   objective/energy -> `NO_COMPARABLE_RESULT` (never a guessed winner).
6. A strictly better outcome maps to `CLASSICAL_WIN` / `QUANTUM_WIN` /
   `HYBRID_WIN` by the benchmarked strategy; a worse one is `CLASSICAL_WIN`.

Repeated runs (`runs > 1`) aggregate success/feasibility rate, objective
mean/min/max/best/stddev, mean wall-clock time and winner counts into a
`BenchmarkRunSummary`; the top result carries the best single run's metrics.
`BenchmarkResult` keeps a compositional reference to the underlying
`SolutionReport` (serialized only as lightweight `report_ref` — the full
report is never duplicated inside the benchmark report).

### QMQ-05 example — run the canonical suite against the classical baseline

```python
import dataclasses

from quantsmind.quantum import BenchmarkRunner, default_suite

runner = BenchmarkRunner()
suite = default_suite()

# Optional: bound the QAOA variational-loop runtime for fast, reproducible
# runs in docs/CI (the classical members do not need microquantum).
try:
    import microquantum

    fast = microquantum.GradientDescent(learning_rate=0.1, max_iter=3, tol=1e-6)
    for benchmark in suite.benchmarks.values():
        if benchmark.options is not None:
            benchmark.options = dataclasses.replace(benchmark.options, qaoa_optimizer=fast)
except ImportError:
    pass

for benchmark in suite.benchmarks.values():
    result = runner.run(benchmark)
    metrics = result.metrics
    print(
        f"{benchmark.benchmark_id:<20} strategy={result.strategy:<8} "
        f"winner={result.comparison.winner.value:<20} "
        f"objective={metrics.objective_value if metrics else None}"
    )
```

For the canonical suite every member reaches its `known_optimum`; the winner
is `tie` (the strategy matches the exact baseline) or the baseline wins —
completion alone never becomes an "advantage".

## QMQ-06 — Result Interpretation & Provenance

QMQ-06 adds a **structured interpretation layer**: `ResultInterpreter`
consumes a `SolutionReport` and an optional `BenchmarkResult` and produces a
`ResultInterpretation` — a domain-neutral, machine-readable explanation of
what was run, what the numbers say, and what they do **not** justify.

```
SolutionReport + BenchmarkResult
        |-- feasibility      (constraint counts, violated names, magnitude)
        |-- objective        (value, energy, sense, known optimum, gap, ratio)
        |   +-- solution_quality  optimal | near_optimal | feasible |
        |                          infeasible | unknown   (evidence-backed)
        |   +-- qualification      mathematical_proof | empirical |
        |                          heuristic | uncertain
        |-- benchmark        (winner, outcome, measured basis, delta)
        |-- strategy         (requested vs selected vs actual, fallback)
        |-- algorithm        (algorithm, backend, qubits, depth, gates, shots)
        |-- execution        (executor, status, error, timing, leg statuses)
        |-- limitations      (only applicable caveats, incl. heuristic_solution,
        |                     classical_fallback, known_optimum_unavailable)
        |-- provenance       (problem, formulation, strategy, executor,
        |                     backend, sdk version, benchmark id)
        \-- summary          (generated narrative over supported facts)
```

Honesty rules baked into the classification:

* a solution is labelled **`optimal` only when a known optimum establishes
  it** (exact exhaustive runs get `mathematical_proof`; a quantum run that
  matches the optimum is only `empirical` — completion alone never proves
  optimality);
* a solution with no known optimum is `feasible` (or `infeasible`), never a
  stronger label, and a `known_optimum_unavailable` limitation is recorded;
* `near_optimal` is reserved for gaps within the configured
  `near_optimal_tolerance` (default 10%), with numeric equality handled by a
  configurable `gap_tolerance` (default `1e-9`);
* benchmark outcomes reuse the QMQ-05 comparison; a winning outcome is
  reported as **"a measured run-level result, not a quantum-advantage
  claim"**;
* missing quantum capability is surfaced as `status="degraded"`,
  `executed_strategy="classical"` and a `classical_fallback` limitation.

`SolutionReport` carries the rich interpretation and its benchmark
additively (`report.result_interpretation`, `report.benchmark`) — existing
QMQ-01..05 report consumers keep working unchanged. Every section serializes
through the established `to_dict` / `from_dict` convention; the flat view
(`winner`, `objective_value`, `optimality_gap`, `approximation_ratio`,
`requested_strategy`, `selected_strategy`, `actual_executor`,
`fallback_used`, `feasibility_status`) exposes the same facts without
descending into the sections.

### QMQ-06 example — interpret every canonical benchmark, honestly

```python
import dataclasses

from quantsmind.quantum import BenchmarkRunner, ResultInterpreter, default_suite

runner = BenchmarkRunner()
suite = default_suite()

# Optional: bound the QAOA variational-loop runtime for fast, reproducible
# runs in docs/CI (the classical members do not need microquantum).
try:
    import microquantum

    fast = microquantum.GradientDescent(learning_rate=0.1, max_iter=3, tol=1e-6)
    for benchmark in suite.benchmarks.values():
        if benchmark.options is not None:
            benchmark.options = dataclasses.replace(benchmark.options, qaoa_optimizer=fast)
except ImportError:
    pass

for benchmark in suite.benchmarks.values():
    result = runner.run(benchmark)
    interpretation = ResultInterpreter().interpret_benchmark(result)
    print(
        f"{benchmark.benchmark_id:<20} status={interpretation.status.value:<8} "
        f"quality={interpretation.solution_quality.value:<12} "
        f"winner={interpretation.winner!s:<20} fallback={interpretation.fallback_used}"
    )
    print(f"    {interpretation.summary.splitlines()[0]}")
```

Every canonical member hits its `known_optimum`, so the interpretation says
`quality=optimal` (with `mathematical_proof` on the exhaustive members and
`empirical` on the QAOA members) and `winner=tie` — and it never claims a
quantum advantage.

## QMQ-07 — Finance Domain Foundation

QMQ-07 adds a validated **finance domain foundation** on top of the existing
QMQ domain layer: `Asset` / `AssetUniverse`, the covariance `RiskMatrix`,
`Budget`, allocation kinds (`continuous` / `binary` / `integer`), the
financial constraints (budget, weight bounds, cardinality / aggregate
allocation, position limits, group allocation by `asset_class`), the
financial objectives (expected return, risk, return-minus-risk), the
`FinancialProblem` that connects them, a `FinancialContext`, and two bridges
into the existing QMQ pipeline:

* `FinanceFormulationAdapter` materializes a `FinancialProblem` into a
  standard `QuantumProblem` — a deterministic conversion with the `x<i>`
  variable convention in universe order, preserved objective senses and
  per-asset/aggregate constraints, plus Finance provenance in
  `problem.metadata` / `problem.provenance`;
* `FinanceAssetMapper` maps assets to decision variables deterministically
  and `decode_assignments(...)` turns solver output back into per-asset
  (`asset_id`, `value`, `selected`) results, ignoring auxiliary slack
  variables.

There is **no Finance-specific QUBO**: solved problems flow through the
existing QMQ-02 formulation, QUBO mapping and classical/quantum execution
exactly like any other domain problem.  QMQ-07 deliberately does **not**
implement portfolio optimization, live data or trading:
* `integer` allocation reporting is a QMQ-08 decision (the "how many units"
  variable representation is not defined here);
* risk data is **supplied**, never estimated (`RiskMatrix` validates
  dimensions, finite entries, symmetry within `1e-9`, and positive
  semidefiniteness — via numpy when available, otherwise an exact
  principal-minor check up to 14 assets, with inconclusive checks flagged
  rather than assumed);
* expected returns are supplied per asset; nothing here is investment
  advice and no live market data is read.

Validation is additive and human-actionable: every model validates itself on
construction and `FinancialProblem.validate()` / `raise_if_invalid()` surface
all remaining issues (missing universe, missing objectives, risk misalignment,
unknown asset references, in-feasible bounds).

### QMQ-07 example — a binary selection problem through the existing pipeline

```python
from quantsmind.quantum import (
    Asset,
    AssetUniverse,
    BudgetConstraint,
    CardinalityConstraint,
    ExhaustiveSolver,
    FinanceAssetMapper,
    FinanceFormulationAdapter,
    FinancialProblem,
    QUBOMapper,
    RiskAdjustedObjective,
    RiskMatrix,
)

problem = FinancialProblem(
    name="two_asset_selection",
    universe=AssetUniverse(
        assets=[
            Asset("A", expected_return=0.10, volatility=0.20, asset_class="equity"),
            Asset("B", expected_return=0.05, volatility=0.10, asset_class="equity"),
        ]
    ),
    objectives=[RiskAdjustedObjective("return_minus_risk", risk_aversion=1.0)],
    constraints=[
        BudgetConstraint(name="budget", total=1.0),
        CardinalityConstraint(name="card", min_assets=1, max_assets=1),
    ],
    risk=RiskMatrix(
        asset_order=["A", "B"],
        matrix=[[0.04, 0.0], [0.0, 0.01]],
        volatilities=[0.20, 0.10],
    ),
    allocation_kind="binary",
)

adapter = FinanceFormulationAdapter()
problem.raise_if_invalid()
quantum = adapter.to_quantum_problem(problem)  # existing QMQ domain problem
print("objective:", quantum.objectives[0].expression)
for qconstraint in quantum.constraints:
    print(f"constraint: {qconstraint.operator} {qconstraint.expression} {qconstraint.value}")

qubo = QUBOMapper().map(quantum).payload  # existing QMQ -> QUBO mapping
result = ExhaustiveSolver(max_variables=10).solve(qubo)  # exact classical solve
print("selected:", result.assignment, "energy:", result.energy, "feasible:", result.feasible)

mapping = FinanceAssetMapper().map(problem)
for asset in mapping.decode_assignments(result.assignment):
    print(f"{asset.asset_id}: selected={asset.selected} value={asset.value}")
```

The example solves exactly: asset `A` (return 0.10, variance 0.04) beats asset
`B` (0.05 − 0.01) under one-budget, exactly-one selection, so it is chosen;
the QUBO/energy/assignment/decoding all come from the existing QMQ-02
infrastructure.  Replace `allocation_kind` / objectives / constraints freely —
the same adapter and mapper drive the rest of the pipeline unchanged.  This
example is only an illustration of the conversion machinery: it is **not**
investment advice, it uses supplied numbers (no live data) and it performs no
trading or portfolio optimization (QMQ-08).

## QMQ-08 — Portfolio Optimization

QMQ-08 turns the QMQ-07 finance foundation into a **portfolio optimization
workflow** that is deliberately independent of any live-market or trading
dependency:

* `PortfolioOptimizationProblem` packages the optimization request — asset
  universe, `ExpectedReturnObjective` (`λ`-free), `RiskObjective`, or
  `RiskAdjustedObjective` (`return − risk_aversion·risk`; aversion `0`
  degenerates to pure expected return), QMQ-07 financial constraints,
  optional `Budget`, an optional `RiskMatrix`, and an `allocation_kind`
  (`binary` is fully supported; `continuous` validates/formulates then fails
  *honestly* at execution, `integer` is rejected up front);
* `OptimizationConfiguration` carries per-problem execution preferences
  (preferred strategy, algorithm, shots, seed, `solver_max_variables`,
  `optimization_level`);
* `PortfolioOptimizer.solve(...)` runs the portfolio through the **existing**
  QMQ-02 formulation / QUBO mapping and QMQ-03/QMQ-04 strategy and execution
  pipeline, and attaches `PortfolioSolution` + QMQ-06 interpretation;
  `benchmark(...)` additionally runs the QMQ-05 `BenchmarkRunner` with the
  classical exhaustive baseline;
* `PortfolioSolution.from_report(...)` decodes solver assignments back to
  per-asset `(asset, value, selected)` decisions, computes `PortfolioMetrics`
  (expected return, variance/volatility, selected count, allocation sum,
  constraint violations) from the **supplied** data, and records
  solver/strategy/energy numbers and provenance;
* everything is deterministic and JSON-serializable (`to_dict`/`from_dict`)
  on problems, solutions, metrics and results.

There is **no QMQ-08-specific QUBO**: portfolios reuse the existing QMQ-02
pipeline exactly like any other domain problem, so continuous allocation
raises the honest, evidence-backed `MappingError` casing from QMQ-02 rather
than silently approximating.  Portfolio decisions follow the same
activity/quantity semantics as QMQ-07 (`binary` = exactly one unit per asset;
`continuous` = long-only weights; `integer` = not yet supported, rejected with
a `FinanceValidationError`).

Portfolio risk data (`RiskMatrix`, per-asset expected returns/volatilities)
is **supplied**, never estimated; nothing here reads live market data,
executes trades, or constitutes investment advice (see §29 of the QMQ-08
brief for the explicit out-of-scope list).

### QMQ-08 example — the canonical risk-adjusted portfolio

```python
from quantsmind.quantum import (
    MappingError,
    PortfolioOptimizer,
    example_budget_portfolio,
    example_portfolio_problem,
)

# Canonical QMQ-08 example: risk-adjusted, binary, exactly-2 selection.
problem = example_portfolio_problem()
problem.raise_if_invalid()

# Solve through the existing pipeline (classical exhaustive baseline).
result = PortfolioOptimizer(default_seed=7).solve(problem, strategy="classical")
solution = result.solution

print("objective:", round(solution.objective_value, 6))
print("weights:", solution.weights())
print("selected:", solution.selected_assets())
print("feasible:", solution.feasible)
print("expected return:", round(solution.metrics.expected_return, 6))
print("portfolio variance:", round(solution.metrics.variance, 6))

# QMQ-06 interpretation and QMQ-05 benchmark against the classical baseline.
print("interpretation:", result.interpretation.status.value)
bench = PortfolioOptimizer(default_seed=7).benchmark(
    problem, strategy="classical", known_optimum=0.038, runs=1
)
print("benchmark:", bench.benchmark.status, bench.benchmark.comparison.winner.value)
print(
    "approximation ratio:",
    round(bench.benchmark.metrics.approximation_ratio, 6),
)

# Continuous allocation stays honest: no silent QUBO approximation.
try:
    PortfolioOptimizer().solve(example_budget_portfolio(), strategy="classical")
except MappingError:
    print("continuous: MappingError")
```

The example solves exactly: under the exact-2 cardinality card the
risk-adjusted objective (return − 2·variance) picks `TECH-B` plus `BOND-A`
(objective ≈ 0.038, expected return 0.11, portfolio variance 0.036); every
metric, strategy decision, solver result, interpretation and benchmark number
comes from the existing QMQ-02..QMQ-06 infrastructure with portfolio-specific
provenance (`domain_sublayer="portfolio"`).  All numbers are supplied
fixtures — this is a deterministic illustration, not investment advice.

## QMQ-09 - Data Intelligence Foundation

QMQ-09 adds a **generic data-domain layer** that lets you formulate
optimization problems over arbitrary observation datasets (feature
selection, cost-aware selection, grouped selection, and clustering) and
solve or benchmark them through the existing QMQ-02..QMQ-06 pipeline:

* `DataFeature` / `DataRecord` / `FeatureVector` / `DataSet` model a
  structured dataset with typed features (name, optional lower/upper
  bounds, non-negative weight) and observations;
* `DataContext` captures the measurement domain (purpose, metric, feature
  weights, assumptions);
* `DataProblem` packages a dataset together with the concrete optimization
  intent (`DataProblemType` = `FEATURE_SELECTION` | `CLUSTERING`), an
  objective, constraints, and an optional context; it exposes
  `decision_variables()` (feature `x<i>` bits for selection, binary
  `z{record}_{cluster}` assignment variables in record-major order for
  clustering) and `clustering_distance_matrix()`;
* `DataFormulationAdapter` validates the problem and translates it into
  the existing QMQ-02 `QuantumProblem` — no data-specific QUBO;
* `DataMapper` / `DataMapping` provide deterministic variable-name
  mapping and a `cluster_of(assignments, record_id)` helper;
* `DataSolution.from_report(...)` decodes solver assignments back to
  `selected()` features (selection) or `cluster_assignments()` +
  `total_within_cluster_distance()` (clustering), and computes
  `DataMetrics` (utility, cost, net objective, cluster count,
  constraint violations);
* `DataOptimizer.solve(...)` and `DataOptimizer.benchmark(...)` run the
  problem through the existing workflow pipeline with QMQ-06
  interpretation and QMQ-05 classical-comparison benchmarking;
* clustering is modelled as a **real quadratic binary QUBO**
  `sum_c sum_{i<j} d_ij z_ir z_jr` MINIMIZE subject to
  assignment-equality and cluster-count bounds, using the same QMQ-02
  QUBO mapping;
* everything is deterministic and JSON-serializable (`to_dict` /
  `from_dict`) on problems, solutions, metrics and results.

There is **no data-specific QUBO**: data problems reuse the existing
QMQ-02 pipeline exactly like any other domain problem; honest handling
of unavailable quantum runtimes works through the QMQ-03/QMQ-04 selector
exactly as in QMQ-07/QMQ-08.

All data fixtures are supplied constants — no live data feeds, no
machine learning, no statistical inference.

### QMQ-09 example — feature selection and clustering

```python
from quantsmind.quantum import (
    DataFormulationAdapter,
    DataMetrics,
    DataOptimizer,
    feature_selection_example,
    clustering_example,
)

# ---- A: feature selection (4 binary x<i> variables, "height" + "depth") ---
problem = feature_selection_example()
problem.raise_if_invalid()
result = DataOptimizer(default_seed=7).solve(problem, strategy="classical")
solution = result.solution

print("selected:", solution.selected())
print("objective:", round(solution.objective_value, 6))
print("feasible:", solution.feasible)
print("interpretation:", result.interpretation.status.value)

# ---- F: clustering (4 records, k=2, 8 binary z{r}_{c} variables) ---------
problem_c = clustering_example()
result_c = DataOptimizer(default_seed=7).solve(problem_c, strategy="classical")
sol_c = result_c.solution

print("clusters:", sol_c.cluster_assignments)
print("within-cluster distance:", round(sol_c.total_within_cluster_distance, 6))
print("feasible:", sol_c.feasible)

# QMQ-05 benchmark against the classical baseline with a known optimum.
bench = DataOptimizer(default_seed=7).benchmark(
    feature_selection_example(),
    strategy="classical",
    known_optimum=9.0,
)
print("benchmark status:", bench.benchmark.status)
print("winner:", bench.benchmark.comparison.winner.value)
print(
    "approximation ratio:",
    round(bench.benchmark.metrics.approximation_ratio, 6),
)
```

The example solves exactly: feature selection picks `["height", "depth"]`
(objective 9.0, feasible); clustering assigns `r0/r2` to cluster 0 and
`r1/r3` to cluster 1 (total within-cluster distance ≈ 8.215604, feasible).
Every metric, strategy decision, solver result, interpretation and
benchmark number comes from the existing QMQ-02..QMQ-06 infrastructure with
data-specific provenance (`domain_layer="data"`).  All numbers are supplied
fixtures — this is a deterministic illustration.

## QMQ-10 — AI/ML Intelligence Foundation

QMQ-10 adds a **machine-learning domain layer** that formulates classic ML
optimization problems (classification, regression, feature selection, model
selection, hyperparameter optimization, and clustering) and solves or
benchmarks them through the existing QMQ-02..QMQ-06 pipeline:

* `MLFeature` / `MLRecord` / `MLDataSet` model a supervised dataset
  (features with an optional typed kind, records with per-feature values,
  and a numeric `target`) with a deterministic column-major `matrix()`
  and `targets()`;
* `MLContext` captures the domain intent (purpose, subdomain, optional
  preferred strategy validated against the existing strategy vocabulary,
  assumptions) and maps onto the QMQ-01 `DomainContext`;
* `MLModelCandidate` / `MLHyperparameter` / `MLHyperparameterChoice` model
  the one-hot selection vocabulary for model and hyperparameter problems;
* `MLProblem` packages the dataset/vocabulary with one of six
  `MLProblemType`s, objectives, constraints, and an optional context; it
  exposes `decision_variables()` over the deterministic ML names
  (`w{f}` fitting coefficients, `s{c}` model bits, `h{p}_{c}` choice bits;
  feature-selection and clustering delegate their variables to QMQ-09);
* `MLFormulationAdapter` validates the problem and translates it into the
  existing QMQ-02 `QuantumProblem` — classification/regression become a
  real quadratic binary least-squares SSR objective, model/hyperparameter
  problems become one-hot QUBOs, and feature-selection/clustering are
  **fully delegated** to the QMQ-09 `DataFormulationAdapter` with
  `source_domain="data"` / `formulation_type="delegated_data"` provenance;
  there is no ML-specific QUBO or solver — every number comes from the
  existing pipeline;
* `MLMapper` / `MLMapping` provide the deterministic variable-name mapping
  and `decode_assignments` back to ML domains (coefficients, selected
  model, chosen hyperparameters);
* `MLMetrics` reports SSR/MSE for fits, `selected_model_id`, the selected
  hyperparameter choices and total gain for model/hyperparameter problems,
  and reuses the QMQ-09 `DataMetrics` (utility, cost, net objective,
  cluster count) for delegated problems;
* `ClassificationSolution` / `RegressionSolution` / `MLFeatureSelectionSolution`
  / `ModelSelectionSolution` / `HyperparameterSolution` decode assignments
  into domain artifacts (coefficients, predictions, selected features,
  selected model, selected choices) with `objective_value`,
  `constraint_status`, `feasible`, `metrics` and full provenance;
* `MLOptimizer.solve(...)` / `MLOptimizer.benchmark(...)` run any ML problem
  through the existing workflow pipeline (QMQ-04), QMQ-06 interpretation and
  QMQ-05 classical-comparison benchmarking; delegated problems are forwarded
  to the QMQ-09 `DataOptimizer` end-to-end;
* everything is deterministic and JSON-serializable (`to_dict` / `from_dict`)
  on problems, contexts, objectives, constraints, solutions, metrics and
  results.

Honest handling of unavailable quantum runtimes works through the
QMQ-03/QMQ-04 selector exactly as in QMQ-07/QMQ-08/QMQ-09.  All ML fixtures
are supplied constants — no live data feeds, no training, no statistical
inference.

### QMQ-10 example — classification, delegated feature selection, benchmark

```python
from quantsmind.quantum import (
    MLFormulationAdapter,
    MLMapper,
    MLOptimizer,
    ml_classification_example,
    ml_feature_selection_example,
)

# ---- classification (real binary-coefficient least-squares SSR) -----------
problem = ml_classification_example()
problem.raise_if_invalid()
result = MLOptimizer(default_seed=7).solve(problem, strategy="classical")
solution = result.solution

print("coefficients:", solution.coefficients)
print("predictions:", solution.predictions)
print("ssr:", round(solution.metrics.ssr, 6))
print("feasible:", solution.feasible)
print("interpretation:", result.interpretation.status.value)

# ---- delegated feature selection (full QMQ-09 QUBO end-to-end) ------------
problem_fs = ml_feature_selection_example()
result_fs = MLOptimizer(default_seed=7).solve(problem_fs, strategy="classical")
sol_fs = result_fs.solution

print("selected features:", sol_fs.selected_features)
print("utility:", round(sol_fs.selected_utility, 6))
print("objective:", round(sol_fs.objective_value, 6))  # net utility - cost
formulated = MLFormulationAdapter().to_quantum_problem(problem_fs)
print("delegation:", formulated.metadata["source_domain"], formulated.metadata["formulation_type"])

# ---- QMQ-05 benchmark against the classical baseline with a known optimum --
bench = MLOptimizer(default_seed=7).benchmark(
    ml_classification_example(),
    strategy="classical",
    known_optimum=3.0,
)
print("benchmark status:", bench.benchmark.status)
print("winner:", bench.benchmark.comparison.winner.value)
print("approximation ratio:", round(bench.benchmark.metrics.approximation_ratio, 6))

# ---- deterministic variable mapping ----------------------------------------
mapping = MLMapper().map(ml_classification_example())
print("mapping variables:", mapping.variable_names)
```

The example solves exactly: classification activates all three features with
coefficients `{'f0': 1.0, 'f1': 1.0, 'f2': 1.0}`, predictions
`[3.0, 3.0, 1.0, 4.0]` and SSR `3.0` (feasible; interpretation `executed`);
feature selection picks `['f0', 'f1']` with utility `8.0` and net objective
`6.0`, delegating to QMQ-09 (`source_domain=data`, `formulation_type=delegated_data`);
the benchmark reports status `executed`, winner `tie`, approximation ratio
`1.0`; the mapping uses the three fitting variables `['w0', 'w1', 'w2']`.  Every
metric, strategy decision, solver result, interpretation and benchmark number
comes from the existing QMQ-02..QMQ-06 infrastructure (or, for delegation, the
QMQ-09 infrastructure) with ML provenance (`domain_layer="ml"`).  All numbers
are supplied fixtures — this is a deterministic illustration.

## QMQ-11 - Advanced Quantum & Domain Intelligence

The `domain` package is the explicit, inspectable front door to the whole
quantum SDK.  It **does not re-implement** any quantum math: every problem,
formulation, strategy, executor, benchmark and interpretation below it is the
existing QMQ-02..QMQ-10 infrastructure reached by *registered dispatch*.

- **Explicit registered dispatch** (`DomainRegistry` / `DomainBinding` / `DomainKind`):
  each supported domain registers a typed binding (finance, data, ml) and
  `resolve(problem)` returns the matching binding by exact type; anything else
  raises a typed `UnsupportedDomainError` (a `DomainDispatchError`).  No
  `if/elif` monolith, no silent fall-through.
- **Quantum suitability assessment** (`QuantumSuitabilityAssessor` →
  `SuitabilityAssessment` / `QuantumSuitability`): deterministic, purely
  structural rules answer *"is this formulation a genuinely binary/QUBO/Ising
  problem the quantum path can actually run?"*  A `QuantumProblem` is
  `suitable`; a continuous/integer formulation that the mapping layer would
  reject is `unsuitable`, `unknown`, or `conditional`, never a silent promise.
  `assess_problem(...)` gives the first-class entry point.
- **Strategy & algorithm reasoning** (`ProblemAssessment`): the assessment
  carries classification (scale/kind/formulation), a reasoned
  `strategy_decision` (QMQ-03 `ComputationStrategy` + `select_reasoned`
  reasons), an `algorithm_recommendation` when calculable, a
  `computation_plan` + `capabilities`, a summary `reason` and provenance.
- **Inspectable planning** (`ExecutionPlan`): every decision the orchestrator
  would make is exposed up front (domain, problem type, strategy,
  strategy_requested, executor, algorithm suitability, classification,
  formulation, reasons, provenance, metadata) and engineered to match whatever
  `solve`/`benchmark` later records.
- **Explicit domain execution** (`DomainIntelligence`): `assess`, `plan`,
  `solve`, `benchmark`, `interpret` over the resolved binding, returning
  serializable `DomainRunResult`s (round-trip safe: `to_dict` / `from_dict`).
  The default `assess`/`plan` use the AUTO strategy, so in an environment with
  MicroQuantum installed they honestly report `hybrid`/`qaoa`
  (`executor='microquantum/qaoa'`); `solve`/`benchmark` default to `classical`
  for deterministic, environment-independent results.
- **Cross-domain end-to-end** (finance / data / ml): every domain example runs
  through the same four-stage path and interpretation comes from the shared
  QMQ-06 interpretation layer.
- **Honest limitations** stay visible: they are the *domain layer's* honest
  truth about the existing pipeline (e.g. the continuous-allocation
  `MappingError`, the budget-QUBO exhaustive corner, and `"no quantum
  execution"` when a quantum run was requested but downgraded), never a
  fabricated quantum claim.

### QMQ-11 example - the canonical finance workflow through domain intelligence

```python
from quantsmind.quantum import domain_finance_example

artifacts = domain_finance_example()  # assess -> plan -> solve -> benchmark -> interpret

print("problem     :", artifacts["problem"])
print("assessment  :", artifacts["assessment"])
print("plan        :", artifacts["plan"])
print("solve       :", artifacts["solve"])
print("benchmark   :", artifacts["benchmark"])
print("interpret   :", artifacts["interpretation"])
```

Running the snippet in this environment prints:

```
problem     : FinancialProblem(name='qmq08_risk_adjusted', assets=4, objectives=1, constraints=1, allocation_kind=binary)
assessment  : ProblemAssessment('qmq08_risk_adjusted' / finance / suitable)
plan        : ExecutionPlan('qmq08_risk_adjusted' [finance] -> hybrid/'microquantum/qaoa', suitability=suitable)
solve       : DomainRunResult('qmq08_risk_adjusted' [finance] requested=classical -> executed=classical/classical, fallback=False)
benchmark   : DomainRunResult('qmq08_risk_adjusted' [finance] requested=classical -> executed=classical/classical, fallback=False)
interpret   : ResultInterpretation(status=executed, quality=feasible, winner=None)
```

The assessment/plan above use the AUTO strategy: with `microquantum` installed
they honestly report suitability `suitable`, strategy `hybrid`, algorithm
`qaoa` and executor `microquantum/qaoa` — the plan matches exactly what the
hybrid executor would do.  The final `solve`/`benchmark` request `classical`
explicitly, so this README stays deterministic in any environment: the
exhaustive baseline solves the risk-adjusted portfolio (`strategy_executed=
'classical'`, `execution_mode='classical'`, `fallback_used=False`, feasible,
objective `0.038`, selected assets `['TECH-B', 'BOND-A']`) and the shared
QMQ-06 interpretation reports `status=executed`, `quality=feasible`.  No new
QUBO, algorithm or solver was introduced: every number comes from QMQ-02..QMQ-10
through the registered dispatch.  The `domain_data_example()`,
`domain_ml_example()` and `domain_pipeline_example()` fixtures exercise the
same four-stage path for the data (feature-selection objective 9.0) and ML
(classification objective 3.0) domains.

## Optional Dependency

`microquantum` (a separate, standalone quantum-computing engine) is the only
optional extra; 1.0 is tested against the `microquantum>=0.4.0,<0.5.0` series:

```
pip install "quantsmind[quantum]"
```

`import quantsmind.quantum` works without MicroQuantum installed. Only the
functions that actually need the engine raise an `ImportError` with a hint
(`quantsmind[quantum]`). Use `microquantum_available()` to check ahead of
time.  When the engine is absent, a quantum/hybrid request either raises that
typed error or degrades to the classical baseline with `fallback_used=True`
and an honest limitation — never a fabricated quantum result.

## Public API

### Low-level layer (preserved)

| Name | Description |
| --- | --- |
| `QuantumProgram` | Declarative, vendor-neutral circuit description (gates + qubits + params). Serializable via `to_dict` / `from_dict`. |
| `GateSpec` | One gate in a `QuantumProgram` (name, qubits, params). |
| `build_circuit(program)` | Translates a `QuantumProgram` into a `microquantum.QuantumCircuit`. Raises `UnknownGateError` / `GateParamError`. |
| `validate_program(program)` | Returns a list of translation errors (empty = valid). |
| `QuantumExperiment` | Orchestrates a run: program (or direct MicroQuantum circuit) + backend + shots + seed + metadata; delegates execution to `microquantum.execute`. |
| `QuantumResult` | QuantsMind enrichment around the native MicroQuantum BackendResult (adds experiment id, program name, domain metadata, provenance, timestamps). |
| `to_microquantum_result(result)` | Converts a `QuantumResult` back to the native MicroQuantum result. |
| `available_algorithms()` | Canonical list of algorithm names delegated to MicroQuantum. |
| `resolve_algorithm(name)` | Maps an algorithm name to its MicroQuantum class. |
| `run_algorithm(name, **kwargs)` | Runs a MicroQuantum algorithm (e.g. `grover`, `vqe`, `qaoa`). |
| `microquantum_available()` | Whether MicroQuantum is importable. |
| `UnknownGateError`, `GateParamError` | Typed translation errors. |

### Domain layer (QMQ-01)

| Name | Description |
| --- | --- |
| `QuantumProblem` | Domain problem holder: variables, objective, constraints, `DomainContext`, metadata; single object passed through strategy/mapping/workflow. |
| `Variable` / `VariableType` | `binary`, `integer`, `continuous`, `categorical` with `lower_bound` / `upper_bound` validation. |
| `Objective` / `ObjectiveSense` | `maximize` / `minimize`; `evaluate(assignments)` returns the raw expression value; `weight` applies only in scoring. |
| `Constraint` | Factories `le` / `ge` / `eq` with `value=`; `ConstraintPriority` levels; `evaluate(assignments)` -> `ConstraintStatus` (`SATISFIED` / `VIOLATED` / `UNKNOWN`); EQ tolerance `1e-9`, LE/GE strict. |
| `DomainContext` | Subdomain + units metadata (`qualified()` returns e.g. `"finance/portfolio"`). |
| `ProblemSolution` | Variable assignments + constraint statuses + `compute_score()`; `from_dict` / `to_dict`. |
| `MathematicalModel` | Structural representation of a problem (constraints, objective senses, bounds, metadata). `from_problem(problem)` builds it. |
| `OptimizationModel` / `GraphModel` / `MLModel` / `SimulationModel` / `StatisticalModel` | Typed structural representations for the five model kinds. |
| `formulate(problem)` / `model_from_dict(data)` | Dispatch by `metadata["model_kind"]` between the model kinds (base `MathematicalModel` fallback). |
| `ComputationStrategy` | `CLASSICAL`, `QUANTUM`, `HYBRID`, `QUANTUM_INSPIRED`, `AUTO` (+ `parse`). |
| `StrategySelector` | Deterministic strategy choice with size thresholds, quantum-capability and `metadata["quantum_suitable"]` overrides, and `explain()`. |
| `QuantumCircuitMapper` / `DomainMapper` | Map a program onto MicroQuantum runtime objects; validates the strategy is quantum-capable. |
| `QuantumWorkflow` | Stateful end-to-end pipeline: problem -> strategy -> mapping -> execution -> `SolutionReport`. |
| `SolutionReport` | Domain-level solution artifact: solution, `Interpretation`, `Provenance`. |
| `SolutionInterpreter` / `Interpretation` / `InterpretationQuality` | Data-derived quality judgment (`HIGH` / `MEDIUM` / `LOW` / `UNKNOWN`); never fabricates domain meaning. |

### QMQ-02 optimization layer

| Name | Description |
| --- | --- |
| `parse_expression("3*x0 + 4*x1")` | Symbolic string -> `Expression` (variables, constants, +, -, *, power, parens, unary minus). |
| `Expression` / `VariableExpression` / `Constant` / `Mul` / `Add` / `Power` | Symbolic building blocks with `expand()` to canonical monomial dict and numeric `evaluate(assignments)`. |
| `QUBOModel` | Binary quadratic pseudo-Boolean model (`linear`, `quadratic`, `constant`, `offset`), `energy(assignment)`, JSON round-trip. |
| `IsingModel` | Spin (+-1) model with fields `h` and couplings; `energy(spins)`, `from_qubo` / `to_qubo` (exact). |
| `ConstraintPenalizer` / `PenaltyTerm` | Constraint -> quadratic penalty (`eq`/`le`/`ge`, slack variables, exact zero when satisfied). |
| `ClassicalSolver` / `ClassicalSolverResult` | Exhaustive, feasibility-aware exact baseline -> `ProblemSolution`; `max_variables` guard against combinatorial blow-up. |
| `QUBOMapper` / `IsingMapper` / `ProblemMapper` | problem -> `QUBOModel` and `QUBOModel` -> `IsingModel` with `MappingResult` metadata (decision/slack variables, penalty, sense). |
| `run_qaoa` / `QaoaExecutionResult` / `qaoa_available()` | MicroQuantum QAOA delegation: `ising_to_pauli_sum`, `ising_to_optimization_problem`, `QAOA.from_problem` + sampling; result carries energy/assignment/counts/backend. |
| `QuantumIntegrationError` | Raised when the MicroQuantum integration layer cannot interpret results. |

### QMQ-03 intelligence layer

| Name | Description |
| --- | --- |
| `ProblemClass` / `ClassificationResult` / `ProblemClassifier` | Deterministic problem classification (binary/integer/continuous/graph/constraint optimization, search, sampling, simulation, ml, statistical, linear algebra, unknown) with reasons; `metadata["problem_class"]` override is authoritative. |
| `CapabilityModel` | Runtime capability snapshot (`detect()`, `is_available`, `required_caps_met`, `executable_algorithms`, JSON round-trip) that gates algorithm recommendations. |
| `AlgorithmCategory` / `AlgorithmDescriptor` / `AlgorithmAvailability` / `AlgorithmRecommendation` | Catalog metadata: category, problem classes, formulations, strategies, execution modes, microquantum id, required capabilities; three availability tiers; recommendation with `suitability_score`, reason, fallbacks, capabilities. |
| `AlgorithmRegistry` / `UnknownAlgorithmError` / `DuplicateAlgorithmError` | Default catalog (15 MicroQuantum algorithms + `qml` + `exhaustive`) with `register` / `get` / `find` / `available` / `executable_algorithms` and JSON round-trip. |
| `FormulationAlternative` / `FormulationRecommendation` / `FormulationRecommender` | Encodes the natural mathematical formulation per class (qubo only when lossless; graph/simulation/ml/statistical keep native). |
| `AlgorithmSelectionError` | Raised when a requested algorithm is unknown or unavailable without a permitted fallback (never silent). |
| `AlgorithmSelector` | Best-executable algorithm per class/formulation/strategy; honours `user_requested` / `allow_algorithm_fallback`; classical baseline as executable fallback. |
| `ComputationPlan` | Serializable plan: algorithm, mapping, executor, fallbacks, gating capabilities, classification + recommendations; `to_dict` / `from_dict`. |
| `StrategyDecision` / `select_reasoned()` | Reasoned strategy decision (explicit preference, runtime-gated downgrade, `quantum_suitable` override, structure-aware AUTO refinements, size thresholds) with reasons + serializable metadata. |

### QMQ-04 execution layer

| Name | Description |
| --- | --- |
| `WorkflowError` / `ExecutionError` / `ClassicalExecutionError` / `QuantumExecutionError` / `HybridExecutionError` / `InvalidQuantumResultError` | Typed execution failure taxonomy (workflow state misuse, classical wrap of exhaustive limit/no-feasible, quantum run/validation failures, hybrid leg coordination, invalid QAOA results). |
| `MicroQuantumUnavailableError` | `(ImportError, WorkflowError)`: MicroQuantum absent/unusable, message carries the `quantsmind[quantum]` install hint — catchable as a standard `ImportError`. |
| `ExecutionOptions` | Frozen per-run options (strategy, algorithm, shots, seed, num_layers, optimization_level, metadata), `resolved_strategy`, `to_dict` / `from_dict`. |
| `ExecutorContext` / `Executor` | Execution inputs (problem, plan, formulation, qubo, ising, options) and the `prepare` -> `execute` ABC. |
| `ExecutionComparisonEntry` / `ExecutionComparison` | Explicit hybrid comparison artifact: only executed legs ranked (feasible first, objective per sense, energy fallback lower-is-better), deterministic tie-break to classical, `winner` + `selected_reason` + `tie_break`. |
| `ClassicalExecutor` / `ClassicalExecutionResult` | Exact exhaustive baseline execution, reusing `ExhaustiveSolver`; `num_evaluations`, energy, feasibility; wrap of limit/no-feasible into `ClassicalExecutionError`. |
| `QuantumExecutor` / `QuantumExecutionResult` | QAOA execution via `run_qaoa`; lazy engine-absence `ImportError`; assignment validation against the mapped variables and recomputed energy. |
| `HybridExecutor` / `HybridExecutionResult` | Executes both legs and selects deterministically; absent/broken quantum recorded `skipped`/`failed` (`quantum_unavailable`), classical winner by default. `execution.comparison` exposes entries. |
| `WorkflowState` | Lifecycle enum CREATED/FORMULATED/CLASSIFIED/RECOMMENDED/PLANNED/MAPPED/EXECUTING/COMPLETED/FAILED with strict forward-only transitions. |
| `SolutionReport` fields | `classical_execution`, `quantum_execution`, `comparison`, `selected_leg` on the report; hybrid metadata (`selected_leg`, `quantum_unavailable`, `execution_fallback`) and `microquantum_version` in provenance. |

### QMQ-05 benchmark layer

| Name | Description |
| --- | --- |
| `Benchmark` | Serializable benchmark definition: `benchmark_id`, `name`, `QuantumProblem`, strategy (own or problem-preferred via `resolved_strategy`), `algorithm`, `ExecutionOptions`, `BaselineConfig`, `known_optimum`, metadata; `to_dict` / `from_dict`. |
| `BaselineConfig` | Classical baseline configuration (kind `"classical"`, `enabled`, `ExhaustiveSolver` / `max_variables`). |
| `BenchmarkRunner` | Runs a benchmark through fresh workflows; forces the strategy by cloning the problem with `preferred_strategy`; runs the classical baseline separately; `runs>1` aggregates; `raise_on_error` for tests/CI. |
| `BenchmarkMetrics` | Measured quality/performance/resources: `objective_value`, `energy`, `feasible`, `constraint_violations`(+magnitude), `optimality_gap`, `approximation_ratio`, `wall_clock_time`, `num_evaluations`, `iterations`, `shots`, `num_qubits`, backend/optimizer/seed/microquantum-version, `status`; `from_execution` builds from a QMQ-04 execution result. |
| `BenchmarkComparison` / `BenchmarkWinner` | Deterministic policy (feasibility class -> normalized objective -> violations; energy fallback lower-is-better); winner classes `CLASSICAL_WIN` / `QUANTUM_WIN` / `HYBRID_WIN` / `TIE` / `NO_COMPARABLE_RESULT` with recorded reason + delta. |
| `BenchmarkResult` / `BenchmarkRunSummary` | Serializable single-run report (keeps the `SolutionReport` as an in-memory reference, serialized as `report_ref`) and repeated-run aggregates (success/feasibility rate, objective stats, mean time, winner counts). |
| `BenchmarkSuite` / `default_suite()` | Named collection of benchmarks keyed by id; the canonical five deterministic members with explicit `known_optimum`. |
| `optimality_gap` / `approximation_ratio` / `normalized_score` / `constraint_violations` | Pure metric math: relative/absolute gap (0-optimum safe), expressible-only ratios, sense + energy normalization (energy lower-better), violation count/magnitude. |

### QMQ-06 result interpretation layer

| Name | Description |
| --- | --- |
| `ResultInterpreter` | Builds a `ResultInterpretation` from a `SolutionReport` (+ optional `BenchmarkResult`): `interpret(report, benchmark=...)`, `interpret_benchmark(...)`, `interpret_report(...)`, `summarize(...)`; deterministic; configurable `gap_tolerance` / `near_optimal_tolerance`. |
| `ResultInterpretation` | Full structured interpretation (status, summary, `solution_quality`, `qualification`, feasibility/objective/benchmark/strategy/algorithm/execution/provenance sections, `limitations`) with `to_dict` / `from_dict` and flat view properties. |
| `InterpretationStatus` | `executed` / `failed` / `degraded` (classical fallback) / `unknown`. |
| `SolutionQuality` | Evidence-backed quality: `optimal` / `near_optimal` / `feasible` / `infeasible` / `unknown` — `optimal` only with a known-optimum basis. |
| `FeasibilityStatus` | `feasible` / `infeasible` / `unknown` (constraint counts + violated names + magnitude). |
| `Qualification` | Evidential basis: `mathematical_proof` (exact), `empirical`, `heuristic`, `uncertain`. |
| `Limitation` | One honest caveat (category + message): `known_optimum_unavailable`, `classical_fallback`, `heuristic_solution`, `no_comparable_baseline`, `failed_execution`, `timing_environment_dependent`, `energy_minimization_form`, `feasibility_unknown`. |
| `SolutionReport` additions | Additive `result_interpretation` and `benchmark` fields; serialized additively via `to_dict` (backward compatible). |

### QMQ-07 finance layer

| Name | Description |
| --- | --- |
| `FinancialInstrument` / `Asset` | Validated instrument identity and its optimization-relevant data (`expected_return` finite, `price` > 0, `volatility` >= 0, `asset_class`); serializable. |
| `AssetUniverse` | Ordered, validated asset collection (insertion order is deterministic — duplicates are rejected); `identifier_order()`, `asset`, `index_of`, iteration, `to_dict` / `from_dict`. |
| `RiskMatrix` | Supplied covariance/risk matrix over a deterministic `asset_order`: square, finite, symmetric within `1e-9` (normalized to exact symmetry); PSD validated by numpy or an exact principal-minor enumeration (up to 14 assets) — an inconclusive check is flagged, never assumed; `covariance` / `variance` / `correlation`, `require_psd()`. |
| `Budget` | `total` (finite, > 0), `currency`, optional `min_allocation` / `max_allocation`; serializable. |
| `AllocationKind` | `CONTINUOUS` / `BINARY` / `INTEGER` representations with `parse`; `integer` reporting is a QMQ-08 decision. |
| `Allocation` | Validated `asset -> weight` map over a fixed `asset_order` (unknown/repeated identifiers and non-finite weights rejected); `from_universe`. |
| `FinancialContext` | `currency`, `subdomain`, `investment_horizon`, `risk_free_rate`, `transaction_cost_rate` (>= 0), `assumptions`, `metadata`; `to_domain_context()` -> `DomainContext("finance")`; serializable. |
| `FinancialConstraint` and subclasses | `BudgetConstraint` (`sum cost_i*x_i <= total`, per-asset `costs` optional), `WeightBoundsConstraint` (per-asset `lower_i <= x_i <= upper_i`), `CardinalityConstraint` (`min <= sum x_i <= max` — counts under binary, aggregate allocation under continuous), `PositionLimitConstraint` (limits on named assets), `GroupAllocationConstraint` (limits on one `asset_class`); each validates against the universe and materializes to existing QMQ `Constraint` objects. |
| `constraint_from_dict` | Deterministic dispatch of the serialized `kind` back to the right constraint. |
| `FinancialObjective` and subclasses | `ExpectedReturnObjective` (MAXIMIZE expected return), `RiskObjective` (MINIMIZE variance, requires a PSD `RiskMatrix`), `RiskAdjustedObjective` (MAXIMIZE `return - risk_aversion*risk`; risk_aversion = 0 degrades to pure expected return); each materializes to an existing QMQ `Objective`. |
| `objective_from_dict` | Deterministic dispatch of the serialized `kind` back to the right objective. |
| `FinancialProblem` | The connect-everything model (universe, objectives, constraints, `context`, `risk`, `allocation_kind`, metadata); `decision_variables` (binary -> 0/1, continuous -> long-only `[0, inf)`), `validate()` / `raise_if_invalid()`, `to_budget_constraint(budget)`, `to_dict` / `from_dict`. |
| `FinanceFormulationAdapter` | `validate`, `raise_if_invalid`, `finance_metadata` (JSON-safe provenance), `to_quantum_problem` (existing `QuantumProblem`), `formulate` (delegates to the existing `quantsmind.quantum.formulation.formulate`). |
| `FinanceAssetMapper` / `AssetMapping` / `DecodedAsset` | Deterministic asset <-> `x<i>` mapping; `decode_assignments(assignments, selected_threshold=0.5)` ignores auxiliary (slack) variables and yields per-asset `asset_id` / `value` / `selected`; serializable. |
| `FinanceError` / `FinanceValidationError` | Error taxonomy (`ValueError` roots): domain validation failures are always `FinanceValidationError`. |
| `synthetic_asset`, `example_asset_universe`, `example_budget`, `example_risk_matrix`, `example_return_problem`, `example_risk_problem`, `example_combined_problem`, `example_financial_problem` | Canonical QMQ-07 fixtures (free of any external data) for tests, docs and experiments. |

### QMQ-08 portfolio layer

| Name | Description |
| --- | --- |
| `OptimizationConfiguration` | Per-problem execution preferences (`preferred_strategy` normalised via `ComputationStrategy.parse`, `algorithm`, `shots`, `seed`, `solver_max_variables`, `optimization_level`, `metadata`); `to_dict` / `from_dict`. |
| `PortfolioOptimizationProblem` | The connect-everything portfolio model (name, `AssetUniverse`, objectives, constraints, optional `Budget` / `RiskMatrix`, `allocation_kind` `binary`/`continuous`/`integer`, `FinancialContext`, `OptimizationConfiguration`); `size`, `decision_variables` (integer -> `FinanceValidationError`), `validate()` / `raise_if_invalid()` (incl. impossible-budget and cardinality-vs-universe checks), `to_financial_problem()`, `to_quantum_problem()`, `formulate()`, `to_dict` / `from_dict`. |
| `PortfolioFormulationAdapter` | `validate`, `to_quantum_problem` (delegates to the QMQ-07 `FinanceFormulationAdapter`, adds `domain_sublayer="portfolio"`, portfolio name, `optimization_config` and `budget` provenance metadata), `formulate` (reuses the existing `quantsmind.quantum.formulation.formulate`). |
| `PortfolioAssetMapper` | Deterministic asset <-> `x<i>` mapping for portfolios (delegates to `FinanceAssetMapper`); `variable`, `asset`, `mapping`, `decode(...)` (slack-tolerant, `selected_threshold`). |
| `PortfolioMetrics` | Supplied-data portfolio metrics: `expected_return`, `variance`, `volatility`, `selected_count`, `allocation_sum`, `constraint_violations`, `constraint_violation_magnitude`, `metadata`; `compute()` classmethod, `to_dict` / `from_dict`. |
| `PortfolioComponent` | One decoded portfolio position (`asset_id`, `value`, `selected`, `expected_contribution`, `risk_contribution`, `metadata`) with serialization. |
| `PortfolioSolution` | Decoded result of a portfolio solve: `weights()`, `selected_assets()`, `objective_value` / `objective_values`, `metrics`, `constraint_status`, `feasible`, `strategy` / `solver` / `algorithm` / `backend` / `shots` / `energy`, `provenance`, `metadata`; `from_report` / `to_dict` / `from_dict`. |
| `PortfolioOptimizationResult` | `solution` (+ optional `report_ref`, `benchmark`, `interpretation`), `to_dict` / `from_dict`; produced by `PortfolioOptimizer`. |
| `PortfolioOptimizer` | `solve(portfolio, *, strategy=None)` -> `PortfolioOptimizationResult` and `benchmark(portfolio, *, strategy=None, known_optimum=None, runs=1, raise_on_error=False)` -> result with QMQ-05 benchmark; strategy defaults to the configuration preference else `"classical"`; honest handling of unavailable quantum runtimes (selector downgrade / typed errors). |
| `compute_portfolio_metrics`, `expected_return_of`, `portfolio_variance`, `portfolio_volatility`, `risk_contributions` | Pure metric functions over supplied universe/risk/weights data. |
| `example_portfolio_universe`, `example_portfolio_risk_matrix`, `example_maximize_return_portfolio`, `example_minimize_risk_portfolio`, `example_risk_adjusted_portfolio`, `example_budget_portfolio` (continuous), `example_group_constraints_portfolio`, `example_portfolio_problem` | Canonical QMQ-08 fixtures (supplied data only) for tests, docs and experiments. |

### QMQ-09 data layer

| Name | Description |
| --- | --- |
| `DataFeature`, `DataRecord`, `FeatureVector`, `DataSet` | Typed data-domain models: features (name, optional bounds, non-negative weight), observations (id + per-feature values), immutable numeric vectors, and the ordered deterministic `DataSet` (matrix, bounds check, feature names, record ids). |
| `DataContext` | Measurement context (`purpose`, `distance_metric`, `feature_weights`, `assumptions`); validated, JSON-serializable, `to_domain_context()`. |
| `DataObjective` | Base objective with `to_quantum_objective(problem)` / `to_dict` / `from_dict` dispatch: `FeatureUtilityObjective` (MAX), `SelectionCostObjective` (MIN), `FeatureSelectionObjective` (net `utility - penalty*cost`, MAX), `ClusteringDistanceObjective` (MIN quadratic). |
| `DataConstraint` | Base constraint with `to_quantum_constraints(problem)` / dispatch: `FeatureCountConstraint` (min/max), `FeatureGroupConstraint` (lower/upper on a member subset), `AssignmentConstraint` (assignment equality), `ClusterCountConstraint` (min/max records per cluster). |
| `DataProblem` | The connect-everything data model (name, `DataSet`, `DataProblemType` `FEATURE_SELECTION`/`CLUSTERING`, objectives, constraints, optional `DataContext`); `size`, `decision_variables()`, `feature_variables()`, `cluster_variables()`, `clustering_distance_matrix()`, `validate()` / `raise_if_invalid()`, `to_dict` / `from_dict`. |
| `DataFormulationAdapter` | `validate`, `to_quantum_problem` (data -> existing QMQ `QuantumProblem`; adds `domain_layer="data"` provenance, problem name, dataset/context/k metadata; no data-specific QUBO), `formulate` (reuses `quantsmind.quantum.formulation.formulate`), `cluster_variable_index`. |
| `DataMapping`, `DataMapper` | Deterministic feature/cluster variable mapping + `decode_assignments` (`DecodedDataFeature`, `DecodedClusterAssignment`), `feature_variable`, `cluster_variable`, `cluster_of(assignments, record_id)`. |
| `DataRelationship`, `pairwise_relationship` | Symmetric distance/similarity relationships over a dataset (Euclidean, squared Euclidean, weighted Euclidean; Gaussian similarity). |
| `DataQualityReport`, `assess_data_quality` | Structural quality report (feature shape, record shape, bounds violations, missing values, duplicates, range coverage) with JSON serialization. |
| `DataMetrics` | Supplied-data metrics: `selected_feature_count`, `selected_utility`, `selection_cost`, `net_objective`, `cluster_count`, `total_within_cluster_distance`, `constraint_violations`; `compute(problem, assignments)`, `to_dict` / `from_dict`. |
| `DataSolution` | Decoded result of a data solve: `selected()`, `cluster_assignments()`, `objective_value`, `metrics`, `constraint_status`, `feasible`, `num_variables`, strategy/solver/backend/provenance, `execution_time`; `from_report` / `to_dict` / `from_dict`. |
| `DataOptimizationResult` | `solution` (+ optional `report_ref`, `benchmark`, `interpretation`), `to_dict` / `from_dict`; produced by `DataOptimizer`. |
| `DataOptimizer` | `solve(problem, *, strategy=None, config=None)` -> `DataOptimizationResult` and `benchmark(problem, *, strategy=None, known_optimum=None, runs=1, raise_on_error=False)` -> result with QMQ-05 benchmark + QMQ-06 interpretation; `mapping(problem)`; honest handling of unavailable quantum runtimes (selector downgrade / typed errors like QMQ-07/QMQ-08). |
| `DataOptimizationConfiguration` | Per-problem execution preferences (`preferred_strategy` normalised via `ComputationStrategy.parse`, `algorithm`, `shots`, `seed`, `solver_max_variables`, `optimization_level`, `metadata`); `to_dict` / `from_dict`. |
| `euclidean_distance`, `squared_euclidean_distance`, `weighted_squared_euclidean_distance`, `similarity_from_distance` | Pure numeric distance/similarity functions (validated, deterministic). |
| `DataError`, `DataValidationError` | Typed data-layer errors; `DataValidationError` subclasses `ValueError` so generic validation handling works across the SDK. |
| `dataset_example`, `data_context_example`, `feature_selection_example`, `selection_cost_example`, `grouped_feature_selection_example`, `similarity_example`, `quality_example`, `clustering_example`, `serialization_example`, `all_examples` | Canonical QMQ-09 fixtures (supplied data only) for tests, docs and experiments. |

### QMQ-10 ml layer

| Name | Description |
| --- | --- |
| `MLFeature`, `MLRecord`, `MLDataSet` | Supervised-data models: named features (optional typed kind), records with per-feature values plus a numeric `target`, and the ordered deterministic `MLDataSet` (feature/record names, `matrix()`, `targets()`, `shape` as feature-count × record-count, duplicate-feature rejection). |
| `MLContext` | ML domain context (`purpose`, `subdomain`, validated `preferred_strategy`, `assumptions`); JSON-serializable, `to_domain_context()`; stores the preferred strategy lower-cased. |
| `MLObjective` | Base objective with `to_quantum_objective(problem)` / `to_dict` / `from_dict` dispatch: `ClassificationLossObjective`, `RegressionLossObjective` (least-squares SSR, MIN quadratic), `ModelSelectionObjective` (MIN `validation_loss + complexity_penalty`), `HyperparameterObjective` (MAX total gain), and the delegated `MLFeatureSelectionObjective` / `MLClusteringDistanceObjective` (`to_data_objective`). |
| `MLConstraint` | Base constraint with `to_quantum_constraints(problem)` / `to_data_constraint` / dispatch: `MLCoefficientCountConstraint` (min/max active fitting coefficients), `ModelSelectionOneHotConstraint`, `HyperparameterOnePerParameterConstraint`, and the delegated `MLFeatureCountConstraint`, `MLAssignmentConstraint`, `MLClusterCountConstraint`. |
| `MLModelCandidate`, `MLHyperparameter`, `MLHyperparameterChoice` | One-hot selection vocabulary: candidate objectives (`validation_loss`, `complexity_penalty`) and parameter choices with gains; validated, JSON-serializable. |
| `MLProblem` | The connect-everything ML model (name, optional `MLDataSet`, `MLProblemType` = `CLASSIFICATION` / `REGRESSION` / `FEATURE_SELECTION` / `MODEL_SELECTION` / `HYPERPARAMETER_OPTIMIZATION` / `CLUSTERING`, objectives, constraints, optional `MLContext`, candidates, hyperparameters, `k`); `size`, `decision_variables()`, `validate()` / `raise_if_invalid()`, `to_dict` / `from_dict`. |
| `MLFormulationAdapter` | `validate`, `to_quantum_problem` (ML -> existing QMQ `QuantumProblem`; adds `domain_layer="ml"` + problem-type/dataset/objective/constraint/k provenance; delegates feature-selection and clustering to QMQ-09 with `source_domain="data"` / `formulation_type="delegated_data"`), `formulate`, `to_data_problem`. |
| `MLMapping`, `MLMapper` | Deterministic ML variable mapping (`w{f}` / `s{c}` / `h{p}_{c}` plus delegated feature/cluster variables): `variable_names`, `coefficient()` / `candidate()` lookups, and `decode_assignments` -> `DecodedMLCoefficient` / `DecodedModelSelection` / `DecodedHyperparameterChoice`. |
| `MLMetrics` | ML metrics: for fits `ssr` / `mse`; for model selection `selected_model_id`, `selected_loss`, `selected_penalty`; for hyperparameters `selected_choices` + `total_gain`; delegated problems reuse QMQ-09 `DataMetrics` (utility, cost, net objective, cluster count); `compute(problem, assignments)`, `to_dict` / `from_dict`. |
| `MLBaseSolution` | Common solution fields (`problem_name`, `problem_type`, `objective_value`, `objective_values`, `constraint_status`, `feasible`, `energy`, `num_variables`, strategy/solver/backend/provenance, `execution_time`); `to_dict` / `from_dict`. |
| `ClassificationSolution`, `RegressionSolution` | Decoded fits: `coefficients` (feature -> 0/1), `predictions` (record order), `selected_features`; plus the inherited base fields and `MLMetrics`. |
| `MLFeatureSelectionSolution` | Wrapper around a delegated QMQ-09 result: `selected_features`, `selected_utility`, `selection_cost`; inherited base fields with QMQ-09 `DataMetrics`. |
| `ModelSelectionSolution`, `HyperparameterSolution` | Decoded one-hot results: `selected_model_id` / `selected_choices` with the inherited base fields and `MLMetrics`. |
| `MLOptimizationResult` | `solution` (+ optional `report_ref`, `benchmark`, `interpretation`); `to_dict` / `from_dict` (solution rebuilt from the report/type, report stays a reference); produced by `MLOptimizer`. |
| `MLOptimizer` | `solve(problem, *, strategy=None, config=None)` -> `MLOptimizationResult` and `benchmark(problem, *, strategy=None, known_optimum=None, runs=1, raise_on_error=False)` with QMQ-05 benchmark + QMQ-06 interpretation; delegated problems forwarded to the QMQ-09 `DataOptimizer`; honest handling of unavailable quantum runtimes (selector downgrade / typed errors like QMQ-07/QMQ-08). |
| `MLOptimizationConfiguration` | Per-problem execution preferences (`preferred_strategy` normalised via `ComputationStrategy.parse`, `algorithm`, `shots`, `seed`, `solver_max_variables`, `optimization_level`, `metadata`); `to_dict` / `from_dict`. |
| `MLError`, `MLValidationError` | Typed ML-layer errors; `MLValidationError` subclasses `ValueError` for uniform validation handling. |
| `ml_dataset_example`, `ml_classification_example`, `ml_regression_example`, `ml_feature_selection_example`, `ml_model_selection_example`, `ml_hyperparameter_example`, `ml_clustering_example`, `ml_all_examples` | Canonical QMQ-10 fixtures (supplied data only; known optima 3.0 / 3.0 / 6.0 / 2.8 / 3.3 / clusters `{r0,r2},{r1,r3}`) for tests, docs and experiments. |

### QMQ-11 domain intelligence layer

| Name | Description |
| --- | --- |
| `DomainError`, `DomainValidationError` | Typed domain-layer error base and validation error (`DomainValidationError` subclasses `ValueError`). |
| `DomainDispatchError`, `UnsupportedDomainError` | Typed dispatch failures; `UnsupportedDomainError` (no binding for a problem / `DomainKind` parse failure) subclasses `DomainDispatchError` so callers can catch either. |
| `DomainKind` | Canonical domain vocabulary (`finance`, `data`, `ml`, `quantum_problem`, `unsupported`); `parse` / `labels`. |
| `DomainBinding` | Registry entry: `kind`, display `label`, collections of accepted model types; `accepts(type)`. |
| `DomainRegistry` | Explicit, registered dispatch: `register(binding)` / `resolve(problem) -> DomainBinding` (exact-type lookup, raises `UnsupportedDomainError` on none) / `resolve_kind(problem)` / `__contains__` / `bindings()`. |
| `QuantumSuitability` | Honest suitability verdict envelope (`label`, `limitations`) with the four labels `suitable` / `unsuitable` / `unknown` / `conditional`; `is_quantum` and `is_implementable` flags; JSON-serializable. |
| `SuitabilityAssessment` | A `QuantumSuitability` plus the deterministic reason; `to_dict` / `from_dict`. |
| `QuantumSuitabilityAssessor` | Rule-based (structural, no headroom claims, no runtime) suitability check: `assess_quantum_problem` / `assess_unknown`, optionally given a `CapabilityModel` and `QuantumProblem` factory to keep the protocol-free. |
| `ProblemAssessment` | Full inspectable assessment of one problem: `problem_name`, `domain`, `problem_type`, `classification`, `formulation` (kind + description), `strategy_decision` (QMQ-03 strategy + reasons), optional `algorithm_recommendation`, `capabilities`, `suitability`, optional `computation_plan`, `reasons`, `provenance`, `created_at`, `metadata`; `summary()`, `to_dict` / `from_dict`, tolerant `from_dict` (missing optional fields). |
| `assess_problem(problem, *, registry=None, strategy=None, capabilities=None)` | First-class function entry point for `ProblemAssessment` (registry + assessor orchestration). |
| `ExecutionPlan` | Every decision the orchestrator would make, up front: direct fields `problem_type`, `strategy_requested`, `suitability`, `classification`, `formulation_kind`, `domain`, `reasons`, `provenance`, `created_at`, `metadata`; the embedded QMQ-03 `plan` (`ComputationPlan`) carries the selected `strategy`, `executor` (e.g. `classical/exhaustive`, `microquantum/qaoa`), `algorithm`, `backend`, `is_quantum` and formulation — engineered to match what `solve`/`benchmark` record; `to_dict` / `from_dict`. |
| `DomainRunResult` | Serialized execution artifact: problem name, `domain_label`, `strategy` / `strategy_requested` / `strategy_executed`, `execution_mode` (classical / quantum / hybrid), `fallback_used`, `execution_time`, `limitations`, `provenance`, `metadata`, `interpretation` (QMQ-06), optional `benchmark` (QMQ-05), and the `domain_result` payload; `to_dict` / `from_dict` round-trips (interpretation/benchmark rebuilt from their own serialized forms). |
| `DomainIntelligence` | `assess` / `plan` / `solve` / `benchmark` / `interpret` + `registry` and `assessor` members over the resolved binding; defaults to AUTO strategy for assess/plan and `classical` for solve/benchmark (see README example). |
| `domain_finance_example` | End-to-end finance artifacts `{problem, assessment, plan, solve, benchmark, interpretation}` (risk-adjusted portfolio, suitability `suitable`, classical-run). |
| `domain_data_example` | End-to-end data artifacts (feature selection, objective 9.0, classical-run). |
| `domain_ml_example` | End-to-end ML artifacts (classification, objective 3.0, classical-run). |
| `domain_pipeline_example` | The same four-stage pipeline across every registered domain. |

## Retained QuantsMind Functionality

QuantsMind keeps ownership of the **domain abstractions and metadata** that
provide value across the SDK:

- Declarative `QuantumProgram` / `GateSpec` (engine-agnostic input format with
  validation and JSON serialization).
- `QuantumExperiment` orchestration with experiment ids, domain metadata,
  reproducibility (backend, shots, seed) and provenance.
- `QuantumResult` enrichment so downstream scientific packages can attach
  domain/pipeline context to raw quantum outcomes.
- The QMQ-01 domain foundation (problem/model formulation, strategy
  selection, mapping, workflow, interpretation, provenance) so downstream
  pipeline work can build on a real, tested domain layer.

MicroQuantum features (simulators, QML, chemistry, QEC, error mitigation,
benchmarking, remote providers) are reached directly through MicroQuantum's
own API; QuantsMind delegates rather than duplicates.

## Removed Legacy Code

The R0.1-era engine skeletons (`backend.py`, `circuit.py`, `gate.py`,
`operator.py`, `qubit.py`, `register.py`, `statevector.py`, `measurement.py`,
`noise.py`, `hamiltonian.py`, `provider.py`, `runtime.py`, `transpiler.py`,
`algorithms/`, `math/`, `compiler/`, `execution/`, `state/`, ...) were
removed. Any domain model QuantsMind genuinely needs (state math, operators,
noise, error mitigation) will be re-introduced deliberately as thin
integration over MicroQuantum, not as a parallel engine.

## Status

**QuantsMind Quantum 1.1.0 — Stable** (minor: OSS program additions across
the SDK; quantum public API unchanged since 1.0.0).

QuantsMind Quantum 1.1.0 is a stable, domain-oriented quantum intelligence
SDK. It transforms supported real-world optimization problems into
mathematical computational workflows and executes them through **classical,
quantum, or hybrid** strategies, with benchmarking, interpretation, and
provenance.  The public API is frozen for 1.0 (see the committed
`api_manifest.json` baseline); the QMQ-01..QMQ-12 paragraphs below are the
phase history.

Integration layer implemented (R0.2.0). Domain foundation (QMQ-01) added:
core domain model, formulations, strategy selection, mapping, workflow,
result/interpretation/provenance, and the MicroQuantum integration facade.

QMQ-02 added (mathematical formulation & domain-to-quantum mapping): the
symbolic expression engine, QUBO and Ising encodings with exact constraint
penalties, the classical exact baseline, automatic problem -> QUBO -> Ising
mapping, and the QAOA delegation path into MicroQuantum with rich result
objects. Open scope: automatic ISQ/QMC circuit-program synthesis from a
QUBO/Ising model (pure circuit mapping remains on top of MicroQuantum API
usage).

QMQ-03 added (algorithm & computational strategy intelligence): problem
classification, the algorithm catalog/registry with capability gating,
formulation recommendation, reasoned strategy selection (`select_reasoned`),
and serializable computation plans, with the workflow carrying
classification/recommendation/plan into `SolutionReport`. Open scope:
algorithm benchmarking/evidence tables (the suitability scores are
deterministic rule-based scores, not measured performance claims) and
provider-specific backend-aware scheduling.

QMQ-04 added (hybrid workflow & execution): the execution layer with
dedicated classical/quantum/hybrid executors, the explicit deterministic
comparison and selection, engine-absence handled as `ImportError`-compatible
`MicroQuantumUnavailableError`, HYBRID honest degradation (selector fallback
or recorded skip), execution options, `WorkflowState` lifecycle, hybrid
metadata/provenance, and hybrid execution results on `SolutionReport`.
Tests: `test_hybrid_execution_qmq04.py` (executors, comparison/selection,
quantum validation, options, state machine, hybrid end-to-end with QAOA,
dependency handling in subprocesses without `microquantum`).

QMQ-05 added (benchmarking & classical comparison): the benchmark package
with metric/ranking math centralized in `benchmark/metrics.py` (energy
lower-is-better under every sense — the QMQ-04 energy-direction regression),
the purely deterministic `BenchmarkComparison.build` policy (feasibility
class -> normalized objective -> violations -> tie), serializable
`Benchmark`/`BenchmarkSuite`/`BenchmarkResult`/`BenchmarkRunSummary`, the
`BenchmarkRunner` (strategy forced via a preferred-strategy problem clone,
baseline = the reused exhaustive solver in a separate classical workflow,
honest failure recording), and the canonical five-benchmark `default_suite`.
Tests: `test_benchmark_qmq05.py` (metric math incl. §23 energy-direction
regression, winner policy, model serialization, exact classical members,
hybrid members vs real MicroQuantum QAOA, repeated-run aggregation, honest
degradation without `microquantum` in subprocesses).

QMQ-07 added (finance domain foundation): the validated `finance` package —
`Asset`/`AssetUniverse`, `RiskMatrix`, `Budget`, allocation kinds, the five
financial constraints, the three financial objectives, `FinancialProblem`,
`FinancialContext`, the `FinanceFormulationAdapter` (finance -> existing QMQ
`QuantumProblem`, no Finance-specific QUBO), and the deterministic
`FinanceAssetMapper` with solution decoding. Canonical fixtures
(`example_*`) are supplied-data only. Tests: `test_finance_qmq07.py`
(asset/universe/risk/budget/allocation, constraints, objectives, problem
validation & round-trips, the adapter, mapping/decoding incl. slack-variable
tolerance, provenance integration, the canonical examples, a binary
end-to-end run through the existing QUBO mapper + exhaustive solver, and
subprocess checks that finance construction and generic imports work with
`microquantum` blocked).

QMQ-08 added (portfolio optimization): the validated `finance` portfolio layer
— `PortfolioOptimizationProblem` (binary/continuous/integer allocation,
objectives, constraints, optional `Budget`/`RiskMatrix`,
`OptimizationConfiguration`), the deterministic `PortfolioFormulationAdapter`
(reusing the QMQ-07 adapter and the existing QMQ-02 pipeline — no QMQ-08
QUBO), `PortfolioAssetMapper`, `PortfolioMetrics` / `PortfolioSolution` /
`PortfolioOptimizationResult`, and `PortfolioOptimizer` with `solve()` and
`benchmark()` (QMQ-05 runner + QMQ-06 interpretation).  Continuous allocation
validates/formulates then fails *honestly* at execution (`MappingError`, no
silent QUBO approximation); `integer` is rejected up front
(`FinanceValidationError`); missing quantum runtimes downgrade through the
QMQ-03/QMQ-04 selector as before.  Canonical `example_*` fixtures are
supplied-data only (no live market data, no trading, no investment advice).
Tests: `test_portfolio_qmq08.py`.

QMQ-09 added (data intelligence foundation): the validated `data` layer — the
typed data-domain models (`DataFeature`/`DataRecord`/`FeatureVector`/
`DataSet`), `DataContext`, `DataProblem` (feature selection and clustering
problem types), `DataRelationship`/`pairwise_relationship`,
`DataQualityReport`/`assess_data_quality`, the data objectives and
constraints (incl. the real quadratic clustering objective), the
deterministic `DataFormulationAdapter` / `DataMapper`, `DataMetrics` /
`DataSolution` / `DataOptimizationResult`, and `DataOptimizer` with
`solve()` and `benchmark()` (QMQ-05 runner + QMQ-06 interpretation).  The
Data layer reuses the existing QMQ-02 formulation/QUBO mapping and
QMQ-03/QMQ-04 strategy/execution pipeline (no data-specific QUBO); missing
quantum runtimes downgrade through the QMQ-03/QMQ-04 selector as before.
Canonical `example_*` fixtures are supplied-data only (no data feeds, no
machine learning, no statistical inference).  Tests:
`test_data_qmq09.py` (models, context, numerics, relationships, quality,
objectives, constraints, problem validation & round-trips, mapping/decoding,
the adapter + existing-optimization-model reuse, QUBO mapping via the
existing mapper, metrics, the canonical examples A/B/C/F solved through the
classical baseline, interpretation/benchmark semantics, the public API, and
subprocess checks that data construction and generic imports work with
`microquantum` blocked).

QMQ-10 added (AI/ML intelligence foundation): the validated `ml` layer — the
supervised-data models (`MLFeature`/`MLRecord`/`MLDataSet`), `MLContext`,
`MLModelCandidate`/`MLHyperparameter`/`MLHyperparameterChoice`,
`MLProblem` (classification, regression, feature selection, model selection,
hyperparameter optimization, and clustering problem types), the ML objectives
and constraints (incl. the real quadratic least-squares SSR for fits and the
one-hot model/hyperparameter QUBOs), the deterministic
`MLFormulationAdapter` / `MLMapper`, `MLMetrics` /
`ClassificationSolution`/`RegressionSolution`/`MLFeatureSelectionSolution`/
`ModelSelectionSolution`/`HyperparameterSolution` /
`MLOptimizationResult`, and `MLOptimizer` with `solve()` and `benchmark()`
(QMQ-05 runner + QMQ-06 interpretation).  Feature selection and clustering are
**fully delegated** to the QMQ-09 `DataOptimizer` end-to-end with honest
provenance (`source_domain="data"`, `formulation_type="delegated_data"`);
there is no ML-specific QUBO, algorithm or solver — all numbers come from the
existing pipeline.  Honest handling of unavailable quantum runtimes downgrades
through the QMQ-03/QMQ-04 selector as before.  Canonical `ml_*_example`
fixtures are supplied-data only (known optima 3.0 / 3.0 / 6.0 / 2.8 / 3.3 /
clusters `{r0,r2},{r1,r3}`).  Tests: `test_ml_qmq10.py` (models, context,
objectives, constraints, problem validation & round-trips, formulation +
quantum-problem delegation provenance, mapping/decoding, metrics, the six
problem types solved through the classical baseline with known optima,
serialization round-trips, the canonical examples, the public API exports,
and subprocess checks that ML construction and generic imports work with
`microquantum` blocked).

QMQ-11 added (advanced quantum & domain intelligence): the `domain` package —
explicit registered dispatch (`DomainRegistry`/`DomainBinding`/`DomainKind`,
typed `DomainDispatchError`/`UnsupportedDomainError`, no if/elif monolith),
honest quantum suitability assessment (`QuantumSuitabilityAssessor` →
`SuitabilityAssessment`/`QuantumSuitability`: suitable/unsuitable/unknown/
conditional, structural rules, never a false promise), strategy & algorithm
reasoning (`ProblemAssessment` with strategy decision, optional algorithm
recommendation, computation plan, capabilities and provenance), inspectable
planning (`ExecutionPlan` matching what solve/benchmark later record),
explicit cross-domain execution (`DomainIntelligence` assess/plan/solve/
benchmark/interpret → serializable round-trip `DomainRunResult`s), the
first-class `assess_problem(...)` entry point, and end-to-end finance/data/ML
examples through the same four-stage path reusing QMQ-02..QMQ-10 infrastructure
(no new QUBO, algorithm or solver).  Honest limitations stay visible: a
continuous allocation still fails with the existing `MappingError`, the
budget-QUBO exhaustive corner and quantum-request downgrades are recorded in
`limitations` (`"no quantum execution"`), never a fabricated quantum claim.
Tests: `test_domain_qmq11.py` (registry dispatch & typed failures, assessment +
planning incl. AUTO vs classical, suitability determinism, solve/benchmark/
interpret with result round-trips and no-false-quantum-claim checks, the three
domain examples, and `microquantum`-blocked subprocess runs: import+assess,
classical solve, and honest downgrade of a quantum request).

QMQ-12 added (release hardening / API freeze): version **1.0.0** with a single
authoritative version source (pyproject <-> `quantsmind.__version__`), the
frozen public 1.0 surface captured in `api_manifest.json` (generated by
`scripts/generate_api_manifest.py`; verified by the release tests), validated
`__all__` across every public module, clean sdist/wheel builds with inspected
contents and legal files, an isolated-environment install + functional smoke
run (classical everywhere; honest degradation of quantum requests without
MicroQuantum), full-suite regression, ruff/format/mypy gates, installation &
quick-start documentation, and release notes.  The optional-engine metadata
matches the published MicroQuantum series (`microquantum>=0.4.0,<0.5.0`).
Tests:
`test_release_qmq12.py`.

## Testing

See `tests/unit/quantum/`:
- `test_program.py` — declarative program model + serialization
- `test_bridge.py` — program -> MicroQuantum circuit translation + typed errors
- `test_experiment.py` — orchestration, backend resolution, result enrichment
- `test_algorithm.py` — algorithm delegation into MicroQuantum
- `test_optional_dependency.py` — import without `microquantum` (subprocess)
- `test_core.py` — variables, objective, constraints, domain context,
  solution scoring and serialization
- `test_formulation.py` — `formulate` / `model_from_dict` dispatch and the
  five structural model kinds
- `test_strategy.py` — strategy parsing, size rules, capability overrides,
  master switch, `explain()`
- `test_mapping.py` — program-to-runtime mapping, validation errors,
  bridge delegation
- `test_workflow.py` — end-to-end `QuantumWorkflow` run, result decoding,
  provenance
- `test_result.py` — interpretation quality, provenance round-trip,
  `SolutionReport`
- `test_optimization_expression.py` — parser/evaluator, expand/canonical form,
  coercion rules, error cases
- `test_optimization_qubo.py` — `QUBOModel` energy, serialization round-trip,
  quantified variables
- `test_optimization_penalties.py` — eq/le/ge penalty terms, slack bits,
  exactness when satisfied
- `test_optimization_ising.py` — Ising energy, QUBO <-> Ising exact
  round-trip/energy equality
- `test_optimization_classical.py` — exhaustive baseline optimality,
  feasibility filtering, metadata
- `test_mapping_qmq02.py` — problem -> QUBO, QUBO -> Ising mappings, penalty/
  slack metadata
- `test_qaoa_integration.py` — Ising -> PaulSum/`OptimizationProblem`,
  `run_qaoa` energy/assignment consistency (skipped without `microquantum`)
- `test_workflow_qmq02.py` — classical end-to-end, QAOA end-to-end, quantum
  path requires MicroQuantum
- `test_intelligence_qmq03.py` — classification, registry/catalog, capability
  model (incl. unavailable-runtime subprocess), formulation recommender,
  algorithm selection (available / requested / fallback / never-silent),
  reasoned strategy (`select_reasoned`), `ComputationPlan` round-trip and the
  workflow pipeline with classification/recommendation/plan attached
- `test_hybrid_execution_qmq04.py` — classical/quantum/hybrid executors,
  comparison ranking + deterministic selection, quantum result validation,
  `ExecutionOptions` round-trip/merge, workflow state machine, hybrid
  end-to-end (max-cut with QAOA, constrained knapsack, deterministic seed,
  engine-skip fallback, report round-trip), and dependency handling in
  subprocesses without `microquantum` (ImportError taxonomy, honest HYBRID
  degradation, classical offline)
- `test_benchmark_qmq05.py` — metric math (gap/ratio/sense/energy-rule
  incl. §23 regression), the deterministic winner policy, model/suite
  serialization, exact classical members of the canonical suite, hybrid
  members vs real MicroQuantum QAOA, repeated-run aggregation, and honest
  degradation without `microquantum` in subprocesses
- `test_finance_qmq07.py` — asset/universe/risk/budget/allocation models,
  every financial constraint and objective (materialization, validation,
  dispatch round-trips), `FinancialProblem` validation and serialization,
  the `FinanceFormulationAdapter`, deterministic asset mapping and
  `decode_assignments` (slack-tolerant), provenance metadata, the canonical
  `example_*` fixtures, a binary end-to-end solve through the existing QUBO
  mapper + exhaustive solver, and `microquantum`-blocked imports in
  subprocesses
- `test_portfolio_qmq08.py` — `OptimizationConfiguration` and
  `PortfolioOptimizationProblem` (binary/continuous/integer, validation incl.
  impossible budgets), objectives/constraints/budget materialization,
  deterministic serialization, QMQ-02 formulation reuse (no second QUBO),
  `PortfolioMetrics`, classical solves with known optima (deterministic
  across repeated runs), benchmarking (status, known-optimum ratio, repeated
  runs, result round-trips), QMQ-06 interpretation, honest failures
  (continuous `MappingError`, integer `FinanceValidationError`,
  `QUANTUM_INSPIRED` `WorkflowError`), the canonical examples A–F, and
  `microquantum`-blocked subprocess runs (import, classical solve/benchmark,
  quantum-request downgrade, interpretation)
- `test_data_qmq09.py` �?" data-domain models (features/records/vectors/
  datasets, bounds and weight validation), `DataContext`, distance and
  similarity numerics, pairwise relationships, `assess_data_quality`, data
  objectives and constraints (materialization, validation, dispatch
  round-trips), `DataProblem` validation and serialization, the
  `DataFormulationAdapter` (existing `OptimizationModel` reuse), the
  `DataMapper`/decoding, `DataMetrics`, classical solves of the canonical
  examples A/B/C/F (deterministic across repeated runs), QMQ-05 benchmarking
  and QMQ-06 interpretation, honest failures (`QUANTUM_INSPIRED`
  `WorkflowError`, `DataValidationError` on invalid problems), the public
  API, and `microquantum`-blocked subprocess runs (import/construction,
  classical solve/benchmark, quantum-request honest downgrade,
  interpretation)
- `test_ml_qmq10.py` — ML-domain models (`MLFeature`/`MLRecord`/`MLDataSet`,
  duplicate-feature rejection, shape/order determinism), `MLContext`,
  model-selection candidates, hyperparameters, ML objectives and constraints
  (materialization, validation, dispatch round-trips, the delegated
  `to_data_*` translation), `MLProblem` validation and serialization, the
  `MLFormulationAdapter` (existing `QuantumProblem` reuse + delegation
  provenance), the `MLMapper`/decoding, `MLMetrics`, classical solves of all
  six canonical examples (known optima, deterministic), QMQ-05 benchmarking
  and QMQ-06 interpretation, serialization round-trips, the public API
  exports, and `microquantum`-blocked subprocess runs (import/construction,
  classical solve/benchmark, quantum-request honest downgrade,
  interpretation)
- `test_domain_qmq11.py` — registered dispatch (`DomainRegistry` resolve/
  contains/kind, exact-type bindings, typed `UnsupportedDomainError` on unknown
  kinds and on non-domain problems), assessment and planning (`assess_problem`,
  AUTO vs classical strategy decisions, `ExecutionPlan` round-trips,
  classification/formulation/provenance), deterministic suitability
  (`QuantumSuitability` verdicts driven by crafted computation plans and
  capability models), domain execution (solve/benchmark/interpret with
  `DomainRunResult` round-trips and no-false-quantum-claim assertions), the
  three domain examples (finance 0.038 / data 9.0 / ml 3.0), and
  `microquantum`-blocked subprocess runs (import + assess, classical solve,
  honest quantum-request downgrade)
- `test_release_qmq12.py` — release properties: single authoritative version
  1.0.0, production classifier, zero required dependencies + MicroQuantum as
  an optional extra, `__all__` integrity (resolve/no-duplicates/no-accidental
  private exports) across all public packages, the committed API manifest
  matching the live import surface, representative serialization round-trips
  (execution plans, domain run results, provenance, interpretation), the
  canonical documented finance values, honest blocked-MicroQuantum behavior,
  and stable-release README language