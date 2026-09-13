"""Optimization entry point of the QMQ-10 AI/ML Intelligence layer.

:class:`MLOptimizationConfiguration` carries execution/optimization
settings and :class:`MLOptimizer` solves or benchmarks
:class:`~quantsmind.quantum.ml.problem.MLProblem` instances through the
existing QMQ-03..05 pipeline — the classical exhaustive baseline (QMQ-05)
and the workflow (QMQ-04).  Feature-selection and clustering problems are
**delegated** to the QMQ-09 :class:`DataOptimizer` end-to-end; the remaining
families run as real quadratic binary problems through the existing QUBO
formulation, QUBO mapping, workflow execution and interpretation.  No second
solver or algorithm exists for the ML layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.ml.errors import MLValidationError
from quantsmind.quantum.ml.formulation import MLFormulationAdapter
from quantsmind.quantum.ml.mapping import MLMapper
from quantsmind.quantum.ml.problem import MLProblem, MLProblemType
from quantsmind.quantum.strategy.strategy import ComputationStrategy

if TYPE_CHECKING:
    from quantsmind.quantum.ml.solution import MLOptimizationResult

__all__ = ["MLOptimizationConfiguration", "MLOptimizer"]


@dataclass
class MLOptimizationConfiguration:
    """Execution/optimization configuration of an ML problem.

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
        MLValidationError: If configuration values are invalid or an unknown
            strategy is requested.
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
                    raise MLValidationError(
                        f"unknown preferred strategy {self.preferred_strategy!r}"
                    ) from None
                self.preferred_strategy = text
            else:
                self.preferred_strategy = ""
        if not isinstance(self.shots, int) or self.shots < 1:
            raise MLValidationError(
                f"ml configuration shots must be an integer >= 1, got {self.shots!r}"
            )
        if self.seed is not None and (not isinstance(self.seed, int) or self.seed < 0):
            raise MLValidationError(
                f"ml configuration seed must be an integer >= 0, got {self.seed!r}"
            )
        if not isinstance(self.solver_max_variables, int) or self.solver_max_variables < 1:
            raise MLValidationError(
                "ml configuration solver_max_variables must be an integer >= 1, "
                f"got {self.solver_max_variables!r}"
            )
        if self.optimization_level not in (0, 1, 2, 3):
            raise MLValidationError(
                f"ml configuration optimization_level must be 0..3, got {self.optimization_level!r}"
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
    def from_dict(cls, data: dict[str, Any]) -> MLOptimizationConfiguration:
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


class MLOptimizer:
    """Solves and benchmarks :class:`MLProblem` instances.

    The optimizer is a thin wrapper over the existing QMQ-03..06 pipeline:
    formulation through the ML adapter (delegating feature selection and
    clustering to the QMQ-09 Data adapter), workflow execution (QMQ-04) with
    the classical exhaustive baseline, and interpretation (QMQ-06).  No
    second quantum algorithm or solver exists for the ML layer.
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
        problem: MLProblem,
        strategy: str | None,
        seed: int | None,
        config: MLOptimizationConfiguration | None,
    ) -> Any:
        from quantsmind.quantum.execution.options import ExecutionOptions

        if config is None:
            shots = self.default_shots
            algorithm = ""
            optimization_level = 0
            domain = problem.problem_type.value
        else:
            shots = config.shots
            algorithm = config.algorithm
            optimization_level = config.optimization_level
            domain = problem.problem_type.value
        return ExecutionOptions(
            strategy=strategy,
            algorithm=algorithm or None,
            shots=shots,
            seed=seed,
            optimization_level=optimization_level,
            metadata={"ml_problem": problem.name, "domain_layer": "ml", "problem_type": domain},
        )

    def _classical_executor(self, config: MLOptimizationConfiguration | None) -> Any:
        from quantsmind.quantum.optimization.classical import ExhaustiveSolver

        cap = config.solver_max_variables if config is not None else 20
        return ExhaustiveSolver(max_variables=cap)

    def _data_config(self, config: MLOptimizationConfiguration | None) -> Any:
        """Convert the ML configuration into a QMQ-09 Data configuration."""
        from quantsmind.quantum.data.optimizer import DataOptimizationConfiguration

        if config is None:
            return None
        return DataOptimizationConfiguration(
            preferred_strategy=config.preferred_strategy,
            algorithm=config.algorithm,
            shots=config.shots,
            seed=config.seed,
            solver_max_variables=config.solver_max_variables,
            optimization_level=config.optimization_level,
            metadata=dict(config.metadata),
        )

    def _delegated_result(
        self,
        problem: MLProblem,
        data_result: Any,
    ) -> MLOptimizationResult:
        """Wrap a delegated QMQ-09 result into an ML result."""
        from quantsmind.quantum.ml.solution import MLOptimizationResult

        if problem.problem_type is MLProblemType.FEATURE_SELECTION:
            from quantsmind.quantum.ml.solution import MLFeatureSelectionSolution

            solution = MLFeatureSelectionSolution.from_data_solution(problem, data_result.solution)
        else:
            solution = data_result.solution
        return MLOptimizationResult(
            solution=solution,
            report=data_result.report,
            benchmark=data_result.benchmark,
            interpretation=data_result.interpretation,
        )

    def solve(
        self,
        problem: MLProblem,
        *,
        strategy: str | None = None,
        config: MLOptimizationConfiguration | None = None,
    ) -> MLOptimizationResult:
        """Solve an ML problem through the existing workflow pipeline.

        The chosen strategy (explicit argument, else the configuration's
        preferred strategy, else the QMQ-03 automatic rule) is executed and
        the result is decoded into an ML domain solution with ML metrics, a
        QMQ-06 interpretation, and the underlying :class:`SolutionReport`.

        Raises:
            MLValidationError: If the problem is invalid.
            UnsupportedStrategyError: For a strategy the pipeline cannot
                execute (e.g. ``QUANTUM_INSPIRED``).
        """
        problem.raise_if_invalid()
        if self._is_delegated(problem):
            from quantsmind.quantum.data.optimizer import DataOptimizer

            preferred = strategy
            if preferred is None:
                preferred = (config.preferred_strategy or None) if config is not None else None
            data_optimizer = DataOptimizer(
                default_shots=self.default_shots, default_seed=self.default_seed
            )
            data_result = data_optimizer.solve(
                MLFormulationAdapter().to_data_problem(problem),
                strategy=preferred,
                config=self._data_config(config),
            )
            return self._delegated_result(problem, data_result)
        from quantsmind.quantum.result.result_interpretation import ResultInterpreter
        from quantsmind.quantum.workflow.workflow import QuantumWorkflow

        preferred = strategy
        if preferred is None:
            preferred = (config.preferred_strategy or None) if config is not None else None
        seed = config.seed if config is not None and config.seed is not None else self.default_seed
        options = self._options(problem, preferred, seed, config)
        started = monotonic()
        workflow = QuantumWorkflow(
            problem=MLFormulationAdapter().to_quantum_problem(
                problem, preferred_strategy=preferred
            ),
            name=f"ml:{problem.name}",
            shots=options.shots,
            seed=seed,
            classical_executor=self._classical_executor(config),
            requested_algorithm=((config.algorithm or None) if config is not None else None),
            options=options,
        )
        report = workflow.run()
        execution_time = monotonic() - started
        from quantsmind.quantum.ml.solution import MLOptimizationResult, ml_solution_from_report

        solution = ml_solution_from_report(problem, report, execution_time=execution_time)
        interpretation = ResultInterpreter().interpret_report(report)
        return MLOptimizationResult(
            solution=solution,
            report=report,
            benchmark=None,
            interpretation=interpretation,
        )

    def benchmark(
        self,
        problem: MLProblem,
        *,
        strategy: str | None = None,
        known_optimum: float | None = None,
        runs: int = 1,
        raise_on_error: bool = False,
        config: MLOptimizationConfiguration | None = None,
    ) -> MLOptimizationResult:
        """Benchmark an ML problem against the classical baseline (QMQ-05).

        The baseline reuses the existing exhaustive solver.  A failing
        strategy run is recorded as ``failed`` (honest) unless
        ``raise_on_error`` is set.

        Args:
            problem: The ML problem to benchmark.
            strategy: Strategy label to benchmark; defaults to the
                configuration's preferred strategy, else ``"classical"``.
            known_optimum: Optional known objective optimum for gap/ratio.
            runs: Number of repetitions (``1`` = single run).
            raise_on_error: If True, raise instead of recording failures.
            config: Optional execution/optimization configuration.
        """
        problem.raise_if_invalid()
        if self._is_delegated(problem):
            from quantsmind.quantum.data.optimizer import DataOptimizer

            preferred = strategy
            if preferred is None:
                preferred = (
                    (config.preferred_strategy or "classical")
                    if config is not None
                    else "classical"
                )
            data_optimizer = DataOptimizer(
                default_shots=self.default_shots, default_seed=self.default_seed
            )
            data_result = data_optimizer.benchmark(
                MLFormulationAdapter().to_data_problem(problem),
                strategy=preferred,
                known_optimum=known_optimum,
                runs=runs,
                raise_on_error=raise_on_error,
                config=self._data_config(config),
            )
            return self._delegated_result(problem, data_result)
        from quantsmind.quantum.benchmark.models import BaselineConfig, Benchmark
        from quantsmind.quantum.benchmark.runner import BenchmarkRunner
        from quantsmind.quantum.result.result_interpretation import ResultInterpreter

        preferred = strategy
        if preferred is None:
            preferred = (
                (config.preferred_strategy or "classical") if config is not None else "classical"
            )
        if not preferred:
            preferred = "classical"
        seed = config.seed if config is not None and config.seed is not None else self.default_seed
        options = self._options(problem, preferred, seed, config)
        benchmark = Benchmark(
            benchmark_id=f"ml:{problem.name}",
            name=problem.name,
            problem=MLFormulationAdapter().to_quantum_problem(
                problem, preferred_strategy=preferred
            ),
            strategy=preferred,
            algorithm=(config.algorithm if config is not None else ""),
            options=options,
            formulation="optimization",
            baseline=BaselineConfig(
                kind="classical",
                enabled=True,
                solver=self._classical_executor(config),
                max_variables=(config.solver_max_variables if config is not None else 20),
            ),
            known_optimum=known_optimum,
            metadata={"ml_problem": problem.name, "domain_layer": "ml"},
        )
        runner = BenchmarkRunner(default_seed=seed, default_shots=options.shots)
        result = runner.run(benchmark, runs=runs, raise_on_error=raise_on_error)
        solution = None
        if result.report is not None:
            from quantsmind.quantum.ml.solution import ml_solution_from_report

            solution = ml_solution_from_report(
                problem, result.report, execution_time=result.total_time
            )
        interpreter = ResultInterpreter()
        interpretation = interpreter.interpret(
            report=result.report,
            benchmark=result,
        )
        from quantsmind.quantum.ml.solution import MLOptimizationResult

        return MLOptimizationResult(
            solution=solution,
            report=result.report,
            benchmark=result,
            interpretation=interpretation,
        )

    def mapping(self, problem: MLProblem) -> Any:
        """Return the deterministic ML variable mapping of a problem."""
        return MLMapper().map(problem)

    def _is_delegated(self, problem: MLProblem) -> bool:
        return problem.problem_type.name in ("FEATURE_SELECTION", "CLUSTERING")
