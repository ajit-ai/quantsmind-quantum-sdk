"""Portfolio optimization layer of QuantsMind Quantum (QMQ-08).

:class:`PortfolioOptimizationProblem` is the strongly typed portfolio
definition (universe, objectives, constraints, budget, allocation kind,
optimization configuration).  :class:`PortfolioFormulationAdapter` converts
it to the existing QMQ pipeline through the QMQ-07 Finance adapter —
**no second QUBO/Ising representation exists**.  :class:`PortfolioAssetMapper`
reuses the QMQ-07 asset mapping, and :class:`PortfolioOptimizer` runs the
existing QMQ-03..06 workflow/benchmark/interpretation pipeline.

Allocation representations:

* ``binary`` — 0/1 asset selection; fully supported through the QUBO path.
* ``continuous`` — real-valued long-only weights; validated and formulated,
  but the current QUBO pipeline is binary-only, so execution surfaces the
  honest :class:`MappingError` instead of silently approximating.
* ``integer`` — intentionally not represented (QMQ-07 deferred decision);
  validation raises the existing :class:`FinanceValidationError`.

This layer works entirely from supplied data.  It is not investment advice.
Importing this module never requires ``microquantum``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.finance.errors import FinanceValidationError
from quantsmind.quantum.finance.formulation import FinanceFormulationAdapter
from quantsmind.quantum.finance.mapping import AssetMapping, FinanceAssetMapper
from quantsmind.quantum.finance.models import AssetUniverse, FinancialProblem
from quantsmind.quantum.finance.portfolio_solution import (
    PortfolioOptimizationResult,
    PortfolioSolution,
)
from quantsmind.quantum.finance.weights import AllocationKind
from quantsmind.quantum.strategy.strategy import ComputationStrategy

if TYPE_CHECKING:
    from quantsmind.quantum.core.problem import QuantumProblem
    from quantsmind.quantum.core.variable import Variable
    from quantsmind.quantum.finance.budget import Budget
    from quantsmind.quantum.finance.constraints import FinancialConstraint
    from quantsmind.quantum.finance.context import FinancialContext
    from quantsmind.quantum.finance.objectives import FinancialObjective
    from quantsmind.quantum.finance.risk import RiskMatrix
    from quantsmind.quantum.formulation.mathematical_model import MathematicalModel

__all__ = [
    "OptimizationConfiguration",
    "PortfolioOptimizationProblem",
    "PortfolioFormulationAdapter",
    "PortfolioAssetMapper",
    "PortfolioOptimizer",
]


@dataclass
class OptimizationConfiguration:
    """Execution/optimization configuration of a portfolio problem.

    Args:
        preferred_strategy: Preferred computation strategy (``""``/``None``
            means automatic).  An explicit quantum-runtime strategy is
            honoured by the existing QMQ-03 selector with honest degradation
            when no quantum runtime is available.
        algorithm: Optional requested algorithm id (forwarded to the QMQ-03
            recommender).
        shots: Shot count for quantum/hybrid legs.
        seed: Optional RNG seed for reproducible runs.
        solver_max_variables: Variable cap of the classical exhaustive
            baseline (reused for state spaces of the workflow).
        optimization_level: 0..3 optimization hint (recorded in metadata).
        metadata: Free-form configuration metadata.

    Raises:
        FinanceValidationError: If configuration values are invalid or an
            unknown strategy is requested.
    """

    preferred_strategy: str | None = None
    algorithm: str = ""
    shots: int = 1024
    seed: int | None = None
    solver_max_variables: int = 20
    optimization_level: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.preferred_strategy is None:
            self.preferred_strategy = ""
        elif self.preferred_strategy:
            text = str(self.preferred_strategy).strip().lower()
            if text:
                try:
                    ComputationStrategy.parse(text)
                except ValueError:
                    raise FinanceValidationError(
                        f"unknown preferred strategy {self.preferred_strategy!r}"
                    ) from None
                self.preferred_strategy = text
            else:
                self.preferred_strategy = ""
        if not isinstance(self.shots, int) or self.shots < 1:
            raise FinanceValidationError(
                f"optimization configuration shots must be an integer >= 1, got {self.shots!r}"
            )
        if self.seed is not None and (not isinstance(self.seed, int) or self.seed < 0):
            raise FinanceValidationError(
                f"optimization configuration seed must be an integer >= 0, got {self.seed!r}"
            )
        if not isinstance(self.solver_max_variables, int) or self.solver_max_variables < 1:
            raise FinanceValidationError(
                "optimization configuration solver_max_variables must be an "
                f"integer >= 1, got {self.solver_max_variables!r}"
            )
        if self.optimization_level not in (0, 1, 2, 3):
            raise FinanceValidationError(
                "optimization configuration optimization_level must be 0..3, "
                f"got {self.optimization_level!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "preferred_strategy": self.preferred_strategy,
            "algorithm": self.algorithm,
            "shots": self.shots,
            "seed": self.seed,
            "solver_max_variables": self.solver_max_variables,
            "optimization_level": self.optimization_level,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OptimizationConfiguration:
        """Rebuild a configuration from :meth:`to_dict` output."""
        return cls(
            preferred_strategy=(
                str(data["preferred_strategy"]) if data.get("preferred_strategy") else None
            ),
            algorithm=str(data.get("algorithm", "")),
            shots=int(data.get("shots", 1024)),
            seed=(int(data["seed"]) if data.get("seed") is not None else None),
            solver_max_variables=int(data.get("solver_max_variables", 20)),
            optimization_level=int(data.get("optimization_level", 0)),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"OptimizationConfiguration(strategy={self.preferred_strategy!r}, "
            f"shots={self.shots}, seed={self.seed})"
        )


@dataclass
class PortfolioOptimizationProblem:
    """A complete portfolio optimization problem definition.

    Connects an :class:`AssetUniverse`, financial objectives/constraints,
    an optional :class:`Budget`, optional
    :class:`~quantsmind.quantum.finance.context.FinancialContext` and
    :class:`~quantsmind.quantum.finance.risk.RiskMatrix`, an allocation
    representation and an
    :class:`OptimizationConfiguration`.  Construction never invokes a quantum
    engine.

    Args:
        name: Unique problem name.
        universe: The available financial assets.
        objectives: Financial objectives (at least one).
        constraints: Financial constraints (budget/weight/cardinality/
            position/group).  A :class:`Budget` additionally materializes its
            constraints during formulation.
        allocation_kind: ``binary`` (supported) or ``continuous``
            (validated/formulated; execution honestly surfaces the binary
            pipeline limit).  ``integer`` raises
            :class:`FinanceValidationError`.
        budget: Optional budget whose constraints are materialized on
            formulation.
        context: Optional financial metadata/configuration.
        risk: Optional covariance/risk matrix over the universe.
        optimization_config: Execution/optimization configuration.
        description: Optional description.
        metadata: Free-form metadata.
    """

    name: str
    universe: AssetUniverse
    objectives: list[FinancialObjective] = field(default_factory=list)
    constraints: list[FinancialConstraint] = field(default_factory=list)
    allocation_kind: AllocationKind = AllocationKind.BINARY
    budget: Budget | None = None
    context: FinancialContext | None = None
    risk: RiskMatrix | None = None
    optimization_config: OptimizationConfiguration = field(
        default_factory=OptimizationConfiguration
    )
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise FinanceValidationError("portfolio problem name must be a non-empty string")
        self.allocation_kind = AllocationKind.parse(self.allocation_kind)
        if not isinstance(self.optimization_config, OptimizationConfiguration):
            raise TypeError("optimization_config must be an OptimizationConfiguration")
        self._assert_unique("objective", [o.name for o in self.objectives])
        self._assert_unique("constraint", [c.name for c in self.constraints])

    @staticmethod
    def _assert_unique(kind: str, names: list[str]) -> None:
        seen: set[str] = set()
        duplicates: list[str] = []
        for name in names:
            if name in seen:
                duplicates.append(name)
            seen.add(name)
        if duplicates:
            raise FinanceValidationError(
                f"duplicate {kind} name(s) in portfolio problem: {sorted(set(duplicates))}"
            )

    # -- structure --------------------------------------------------------

    @property
    def size(self) -> int:
        """Number of assets (one decision variable per asset)."""
        return len(self.universe)

    @property
    def decision_variables(self) -> list[Variable]:
        """Deterministic decision variables in universe order.

        ``binary`` yields 0/1 selection variables; ``continuous`` yields
        long-only ``[0, inf)`` weight variables.  ``integer`` raises
        :class:`FinanceValidationError` — QMQ-08 does not represent integer
        quantities (honest: nothing is silently approximated).

        Raises:
            FinanceValidationError: If the allocation kind is ``integer``.
        """
        if self.allocation_kind is AllocationKind.INTEGER:
            raise FinanceValidationError(
                "integer allocation is not supported by QMQ-08: the current QUBO "
                "pipeline represents binary decisions only; use binary selection "
                "or continuous allocation"
            )
        return self.to_financial_problem().decision_variables

    # -- conversion -------------------------------------------------------

    def to_financial_problem(self) -> FinancialProblem:
        """Materialize the portfolio as a QMQ-07 :class:`FinancialProblem`.

        Explicit constraints keep their declaration order; a
        :class:`Budget` appends its aggregate-allocation constraints (named
        ``budget`` / ``budget_min_allocation`` / ``budget_max_allocation`` /
        ``budget_allocation``) after them.

        Raises:
            FinanceValidationError: If a budget-derived name collides with an
                explicit constraint name.
        """
        financial = FinancialProblem(
            name=self.name,
            universe=self.universe,
            objectives=list(self.objectives),
            constraints=list(self.constraints),
            context=self.context,
            risk=self.risk,
            allocation_kind=self.allocation_kind,
            description=self.description,
            metadata=dict(self.metadata),
        )
        if self.budget is not None:
            budget_name = "budget"
            if financial.constraint_exists(budget_name):
                raise FinanceValidationError(
                    f"portfolio {self.name!r} declares a constraint named "
                    f"{budget_name!r} conflicting with the budget-derived constraint"
                )
            financial.to_budget_constraint(self.budget, name=budget_name)
        return financial

    def to_quantum_problem(
        self,
        *,
        preferred_strategy: Any = None,
    ) -> QuantumProblem:
        """Convert the portfolio into a QMQ :class:`QuantumProblem`.

        Delegates to :class:`PortfolioFormulationAdapter`.
        """
        return PortfolioFormulationAdapter().to_quantum_problem(
            self, preferred_strategy=preferred_strategy
        )

    def formulate(self) -> MathematicalModel:
        """Return the existing QMQ formulation of the portfolio."""
        return PortfolioFormulationAdapter().formulate(self)

    # -- validation -------------------------------------------------------

    def validate(self) -> list[str]:
        """Return a list of human-actionable validation issues.

        Validation is performed **before** any formulation: on the portfolio
        structure, the derived QMQ-07 :class:`FinancialProblem` (universe,
        objectives, risk alignment, per-constraint) and portfolio-level
        feasibility (e.g. a minimum aggregate allocation above the available
        capital).  Validation never raises; use :meth:`raise_if_invalid`.
        """
        issues: list[str] = []
        if self.allocation_kind is AllocationKind.INTEGER:
            issues.append(
                "integer allocation is not supported by QMQ-08 (the current QUBO "
                "pipeline is binary-only); use binary selection or continuous allocation"
            )
        try:
            financial = self.to_financial_problem()
        except FinanceValidationError as exc:
            issues.append(str(exc))
            return issues
        issues.extend(financial.validate())
        issues.extend(self._portfolio_level_issues(financial))
        return issues

    def _portfolio_level_issues(self, financial: FinancialProblem) -> list[str]:
        """Portfolio-level cross-constraint feasibility checks (unit costs)."""
        from quantsmind.quantum.finance.constraints import (
            BudgetConstraint,
            CardinalityConstraint,
        )

        issues: list[str] = []
        budgets = [
            constraint
            for constraint in financial.constraints
            if isinstance(constraint, BudgetConstraint)
        ]
        cardinalities = [
            constraint
            for constraint in financial.constraints
            if isinstance(constraint, CardinalityConstraint)
        ]
        for budget in budgets:
            if budget.costs:
                continue
            for cardinality in cardinalities:
                lower = cardinality.min_assets
                if cardinality.max_assets is not None:
                    lower = min(lower, cardinality.max_assets)
                if lower > budget.total:
                    issues.append(
                        f"minimum required aggregate allocation {lower} exceeds the "
                        f"available budget {budget.total}"
                    )
        return issues

    def raise_if_invalid(self) -> None:
        """Raise :class:`FinanceValidationError` listing all issues.

        Raises:
            FinanceValidationError: If :meth:`validate` returns any issue.
        """
        issues = self.validate()
        if issues:
            details = "; ".join(issues)
            raise FinanceValidationError(f"invalid portfolio problem {self.name!r}: {details}")

    # -- serialization ----------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "universe": self.universe.to_dict(),
            "objectives": [o.to_dict() for o in self.objectives],
            "constraints": [c.to_dict() for c in self.constraints],
            "allocation_kind": self.allocation_kind.name.lower(),
            "budget": self.budget.to_dict() if self.budget is not None else None,
            "context": self.context.to_dict() if self.context is not None else None,
            "risk": self.risk.to_dict() if self.risk is not None else None,
            "optimization_config": self.optimization_config.to_dict(),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PortfolioOptimizationProblem:
        """Rebuild a portfolio problem from :meth:`to_dict` output."""
        from quantsmind.quantum.finance.budget import Budget
        from quantsmind.quantum.finance.constraints import constraint_from_dict
        from quantsmind.quantum.finance.context import FinancialContext
        from quantsmind.quantum.finance.objectives import objective_from_dict
        from quantsmind.quantum.finance.risk import RiskMatrix

        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
            universe=AssetUniverse.from_dict(data["universe"]),
            objectives=[objective_from_dict(d) for d in data.get("objectives", [])],
            constraints=[constraint_from_dict(d) for d in data.get("constraints", [])],
            allocation_kind=AllocationKind.parse(data.get("allocation_kind", "binary")),
            budget=(Budget.from_dict(data["budget"]) if data.get("budget") is not None else None),
            context=(
                FinancialContext.from_dict(data["context"])
                if data.get("context") is not None
                else None
            ),
            risk=(RiskMatrix.from_dict(data["risk"]) if data.get("risk") is not None else None),
            optimization_config=OptimizationConfiguration.from_dict(
                dict(data.get("optimization_config", {}))
            ),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"PortfolioOptimizationProblem(name={self.name!r}, assets={self.size}, "
            f"objectives={len(self.objectives)}, constraints={len(self.constraints)}, "
            f"allocation_kind={self.allocation_kind.name.lower()})"
        )


class PortfolioFormulationAdapter:
    """Portfolio -> QMQ conversion adapter.

    Delegates structural conversion to the QMQ-07
    :class:`FinanceFormulationAdapter` and injects portfolio provenance
    metadata (``domain_sublayer="portfolio"``, the configuration dict, the
    budget).  Reuses the existing QMQ-02 formulation — there is no second
    portfolio QUBO/Ising representation.
    """

    def validate(self, portfolio: PortfolioOptimizationProblem) -> list[str]:
        """Return the validation issues of a portfolio (empty = valid)."""
        return portfolio.validate()

    def raise_if_invalid(self, portfolio: PortfolioOptimizationProblem) -> None:
        """Raise :class:`FinanceValidationError` when the portfolio is invalid.

        Raises:
            FinanceValidationError: If the portfolio fails validation.
        """
        portfolio.raise_if_invalid()

    def to_quantum_problem(
        self,
        portfolio: PortfolioOptimizationProblem,
        *,
        preferred_strategy: Any = None,
    ) -> QuantumProblem:
        """Convert a portfolio into a QMQ :class:`QuantumProblem`.

        Args:
            portfolio: The validated portfolio problem.
            preferred_strategy: Optional preferred computation strategy; when
                ``None`` the portfolio's optimization configuration decides.
        """
        portfolio.raise_if_invalid()
        preferred = preferred_strategy
        if preferred is None:
            preferred = portfolio.optimization_config.preferred_strategy or None
        quantum = FinanceFormulationAdapter().to_quantum_problem(
            portfolio.to_financial_problem(), preferred_strategy=preferred
        )
        quantum.metadata = {
            **quantum.metadata,
            "domain_sublayer": "portfolio",
            "portfolio": portfolio.name,
            "optimization_config": portfolio.optimization_config.to_dict(),
        }
        if portfolio.budget is not None:
            quantum.metadata["budget"] = portfolio.budget.to_dict()
        quantum.provenance = {**quantum.provenance, "domain_sublayer": "portfolio"}
        return quantum

    def formulate(self, portfolio: PortfolioOptimizationProblem) -> MathematicalModel:
        """Return the existing QMQ formulation of a portfolio.

        Delegates to the existing :func:`quantsmind.quantum.formulation
        .formulate`, producing an :class:`OptimizationModel` (or another
        :class:`MathematicalModel` selected by the existing rules).
        """
        from quantsmind.quantum.formulation import formulate as qmq_formulate

        return qmq_formulate(self.to_quantum_problem(portfolio))


class PortfolioAssetMapper:
    """Deterministic asset <-> variable mapping for portfolios.

    Reuses the QMQ-07 solution decoding: an assignment is decoded back into
    ordered asset decisions, QUBO slack/aux variables are ignored, and
    ``selected`` follows ``value > selected_threshold``.
    """

    def mapping(self, portfolio: PortfolioOptimizationProblem) -> AssetMapping:
        """Return the asset -> variable :class:`AssetMapping` of a portfolio."""
        return FinanceAssetMapper().map(portfolio.to_financial_problem())

    def decode(
        self,
        portfolio: PortfolioOptimizationProblem,
        assignments: dict[str, Any],
        *,
        selected_threshold: float = 0.5,
    ) -> list[Any]:
        """Decode an assignment into ordered asset decisions
        (:class:`DecodedAsset`)."""
        return self.mapping(portfolio).decode_assignments(
            assignments, selected_threshold=selected_threshold
        )

    def variable(self, portfolio: PortfolioOptimizationProblem, identifier: str) -> str:
        """Return the decision-variable name of an asset identifier."""
        return self.mapping(portfolio).variable(identifier)

    def asset(self, portfolio: PortfolioOptimizationProblem, variable_name: str) -> str:
        """Return the asset identifier for a decision-variable name."""
        return self.mapping(portfolio).asset(variable_name)


class PortfolioOptimizer:
    """Solves and benchmarks :class:`PortfolioOptimizationProblem` instances.

    The optimizer is a thin wrapper over the existing QMQ-03..06 pipeline:
    formulation through the Finance adapter, workflow execution (QMQ-04)
    with the classical exhaustive baseline, and interpretation (QMQ-06).
    No second quantum algorithm or solver exists for portfolios.
    """

    def __init__(
        self,
        *,
        default_shots: int = 1024,
        default_seed: int | None = None,
    ) -> None:
        self.default_shots = int(default_shots)
        self.default_seed = default_seed

    def _options(
        self,
        portfolio: PortfolioOptimizationProblem,
        strategy: str | None,
        seed: int | None,
    ) -> Any:
        from quantsmind.quantum.execution.options import ExecutionOptions

        return ExecutionOptions(
            strategy=strategy,
            algorithm=portfolio.optimization_config.algorithm or None,
            shots=portfolio.optimization_config.shots,
            seed=seed,
            optimization_level=portfolio.optimization_config.optimization_level,
            metadata={"portfolio": portfolio.name, "domain_sublayer": "portfolio"},
        )

    def solve(
        self,
        portfolio: PortfolioOptimizationProblem,
        *,
        strategy: str | None = None,
    ) -> PortfolioOptimizationResult:
        """Solve a portfolio problem through the existing workflow pipeline.

        The chosen strategy (explicit argument, else the optimization
        configuration's preferred strategy, else the QMQ-03 automatic rule)
        is executed and the result is decoded into a
        :class:`~quantsmind.quantum.finance.portfolio_solution
        .PortfolioSolution` with portfolio metrics, a QMQ-06 interpretation,
        and the underlying :class:`SolutionReport`.

        Reasons:
            FinanceValidationError: If the portfolio is invalid.
            MappingError: For a continuous allocation, because the current
                QUBO pipeline is binary-only (honest failure — no silent
                approximation).
            UnsupportedStrategyError: For a strategy the pipeline cannot
                execute (e.g. ``QUANTUM_INSPIRED``).
        """
        portfolio.raise_if_invalid()
        from quantsmind.quantum.optimization.classical import ExhaustiveSolver
        from quantsmind.quantum.result.result_interpretation import ResultInterpreter
        from quantsmind.quantum.workflow.workflow import QuantumWorkflow

        preferred = strategy
        if preferred is None:
            preferred = portfolio.optimization_config.preferred_strategy or None
        seed = (
            portfolio.optimization_config.seed
            if portfolio.optimization_config.seed is not None
            else self.default_seed
        )
        options = self._options(portfolio, preferred, seed)
        started = monotonic()
        workflow = QuantumWorkflow(
            problem=PortfolioFormulationAdapter().to_quantum_problem(
                portfolio, preferred_strategy=preferred
            ),
            name=f"portfolio:{portfolio.name}",
            shots=options.shots,
            seed=seed,
            classical_executor=ExhaustiveSolver(
                max_variables=portfolio.optimization_config.solver_max_variables
            ),
            requested_algorithm=(portfolio.optimization_config.algorithm or None),
            options=options,
        )
        report = workflow.run()
        execution_time = monotonic() - started
        solution = PortfolioSolution.from_report(portfolio, report, execution_time=execution_time)
        interpretation = ResultInterpreter().interpret_report(report)
        return PortfolioOptimizationResult(
            solution=solution,
            report=report,
            benchmark=None,
            interpretation=interpretation,
        )

    def benchmark(
        self,
        portfolio: PortfolioOptimizationProblem,
        *,
        strategy: str | None = None,
        known_optimum: float | None = None,
        runs: int = 1,
        raise_on_error: bool = False,
    ) -> PortfolioOptimizationResult:
        """Benchmark a portfolio against the classical baseline (QMQ-05).

        The baseline reuses the existing exhaustive solver.  A failing
        strategy run is recorded as ``failed`` (honest) unless
        ``raise_on_error`` is set.

        Args:
            portfolio: The portfolio problem to benchmark.
            strategy: Strategy label to benchmark; defaults to the
                optimization configuration's preferred strategy, else
                ``"classical"``.
            known_optimum: Optional known objective optimum for gap/ratio.
            runs: Number of repetitions (``1`` = single run).
            raise_on_error: If True, raise instead of recording failures.
        """
        portfolio.raise_if_invalid()
        from quantsmind.quantum.benchmark.models import BaselineConfig, Benchmark
        from quantsmind.quantum.benchmark.runner import BenchmarkRunner
        from quantsmind.quantum.optimization.classical import ExhaustiveSolver
        from quantsmind.quantum.result.result_interpretation import ResultInterpreter

        preferred = strategy
        if preferred is None:
            preferred = portfolio.optimization_config.preferred_strategy or "classical"
        if not preferred:
            preferred = "classical"
        seed = (
            portfolio.optimization_config.seed
            if portfolio.optimization_config.seed is not None
            else self.default_seed
        )
        options = self._options(portfolio, preferred, seed)
        benchmark = Benchmark(
            benchmark_id=f"portfolio:{portfolio.name}",
            name=portfolio.name,
            problem=PortfolioFormulationAdapter().to_quantum_problem(
                portfolio, preferred_strategy=preferred
            ),
            strategy=preferred,
            algorithm=portfolio.optimization_config.algorithm,
            options=options,
            formulation="optimization",
            baseline=BaselineConfig(
                kind="classical",
                enabled=True,
                solver=ExhaustiveSolver(
                    max_variables=portfolio.optimization_config.solver_max_variables
                ),
                max_variables=portfolio.optimization_config.solver_max_variables,
            ),
            known_optimum=known_optimum,
            metadata={"portfolio": portfolio.name, "domain_sublayer": "portfolio"},
        )
        runner = BenchmarkRunner(default_seed=seed, default_shots=options.shots)
        result = runner.run(benchmark, runs=runs, raise_on_error=raise_on_error)
        solution = None
        if result.report is not None:
            solution = PortfolioSolution.from_report(
                portfolio, result.report, execution_time=result.total_time
            )
        interpreter = ResultInterpreter()
        interpretation = interpreter.interpret(
            report=result.report,
            benchmark=result,
        )
        return PortfolioOptimizationResult(
            solution=solution,
            report=result.report,
            benchmark=result,
            interpretation=interpretation,
        )
