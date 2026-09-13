"""Execution workflows for quantum domain problems.

A :class:`QuantumWorkflow` pipelines a domain problem through the full
foundation::

    Problem -> Formulation -> Strategy Selection -> Mapping -> Execution -> Solution

QMQ-01 executed genuinely only when a :class:`QuantumProgram` was attached.
QMQ-02 completes the automatic path::

    QuantumProblem
        -> OptimizationModel
        -> QUBOModel
        -> IsingModel         (quantum strategies only)
        -> MicroQuantum       (QAOA)          | quantum / hybrid
        -> classical/exhaustive solver        | classical

QMQ-03 adds the intelligence pipeline (decisions are recorded, never faked)::

    QuantumProblem
        -> formulate -> classify -> select strategy -> recommend algorithm
        -> build computation plan -> map -> execute

The classical baseline and the MicroQuantum QAOA delegation are real work —
not placeholders.  Unsupported paths (e.g. a QUANTUM_INSPIRED execution,
non-binary problems) raise explicit :class:`WorkflowError` messages that
say what is missing, never silently pretending to run.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import Any

from quantsmind.quantum._mq import (
    _INSTALL_HINT,
    microquantum_available,
    require_microquantum,
)
from quantsmind.quantum.core.problem import QuantumProblem
from quantsmind.quantum.core.solution import ProblemSolution
from quantsmind.quantum.execution.classical import (
    ClassicalExecutionResult,
    ClassicalExecutor,
)
from quantsmind.quantum.execution.errors import (
    MicroQuantumUnavailableError,
    UnsupportedStrategyError,
    WorkflowError,
)
from quantsmind.quantum.execution.executor import Executor, ExecutorContext
from quantsmind.quantum.execution.hybrid import (
    HybridExecutionResult,
    HybridExecutor,
)
from quantsmind.quantum.execution.options import ExecutionOptions
from quantsmind.quantum.execution.quantum import (
    QuantumExecutionResult,
    QuantumExecutor,
)
from quantsmind.quantum.experiment import QuantumExperiment
from quantsmind.quantum.formulation import formulate as build_formulation
from quantsmind.quantum.formulation.mathematical_model import MathematicalModel
from quantsmind.quantum.intelligence import (
    AlgorithmRecommendation,
    AlgorithmSelector,
    CapabilityModel,
    ClassificationResult,
    ComputationPlan,
    FormulationRecommendation,
    ProblemClassifier,
)
from quantsmind.quantum.mapping.ising import IsingMapper
from quantsmind.quantum.mapping.mapper import (
    DomainMapper,
    MappingResult,
    QuantumCircuitMapper,
)
from quantsmind.quantum.mapping.qubo import QUBOMapper
from quantsmind.quantum.optimization.classical import ExhaustiveSolver
from quantsmind.quantum.result.interpretation import (
    Interpretation,
    SolutionInterpreter,
)
from quantsmind.quantum.result.provenance import Provenance
from quantsmind.quantum.result.result import SolutionReport
from quantsmind.quantum.strategy.selector import StrategyDecision, StrategySelector
from quantsmind.quantum.strategy.strategy import ComputationStrategy


class WorkflowState(Enum):
    """Lifecycle state of one :class:`QuantumWorkflow` run (QMQ-04 §3).

    Transitions are forward-only and lenient: intermediate stages may be
    skipped (e.g. ``map()`` jumps straight to ``MAPPED``), but a completed or
    failed workflow cannot be reused and no stage can move backwards.
    """

    CREATED = "created"
    FORMULATED = "formulated"
    CLASSIFIED = "classified"
    RECOMMENDED = "recommended"
    PLANNED = "planned"
    MAPPED = "mapped"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


def _microquantum_version() -> str:
    """Return the imported MicroQuantum version (``""`` when not installed)."""
    try:
        mq = require_microquantum()
    except ImportError:
        return ""
    return str(getattr(mq, "__version__", "unknown"))


class QuantumWorkflow:
    """Pipelines a domain problem through formulation, strategy, mapping,
    execution and solution reporting.

    Args:
        problem: The domain problem to process.
        program: Optional :class:`QuantumProgram` attached for the QMQ-01
            low-level quantum execution path.  When provided, the quantum
            strategy runs the explicit program instead of the automatic
            QUBO/Ising path.
        backend: Backend name (e.g. ``"statevector"``) or an engine
            backend instance.
        shots: Number of shots per execution.
        seed: Optional RNG seed for reproducibility.
        name: Workflow/experiment label.
        selector: Optional :class:`StrategySelector` (defaults to a fresh
            rule-based selector).
        mapper: Optional :class:`DomainMapper` (defaults to
            :class:`QuantumCircuitMapper`); only used for the explicit
            program path.
        classical_executor: Optional :class:`ExhaustiveSolver` for the
            classical baseline (defaults to a fresh solver with
            ``max_variables=20``).
        num_layers: QAOA layers for the automatic quantum path.
        penalty: Optional constraint penalty multiplier for the QUBO mapping.
        qaoa_optimizer: Optional MicroQuantum optimizer for the QAOA
            variational loop (useful to bound runtime in tests/CI).
        classifier: Optional :class:`ProblemClassifier` (QMQ-03).
        algorithm_selector: Optional :class:`AlgorithmSelector` (QMQ-03).
        capabilities: Optional :class:`CapabilityModel` snapshot (detected
            on demand when omitted).
        requested_algorithm: Optional explicit algorithm id honoured by the
            QMQ-03 recommender.
        allow_algorithm_fallback: If True, an unavailable requested
            algorithm falls back to an executable replacement (recorded,
            never silent).
        executor: Optional QMQ-04 :class:`Executor` overriding the
            strategy-derived executor (used as-is by :meth:`create_executor`).
        options: Optional QMQ-04 :class:`ExecutionOptions`; workflow-level
            arguments (backend, shots, seed, num_layers, penalty,
            qaoa_optimizer) act as defaults it can override.
    """

    def __init__(
        self,
        problem: QuantumProblem,
        *,
        program: Any | None = None,
        backend: str | None = None,
        shots: int = 1024,
        seed: int | None = None,
        name: str = "quantum_workflow",
        selector: StrategySelector | None = None,
        mapper: DomainMapper | None = None,
        classical_executor: ExhaustiveSolver | None = None,
        num_layers: int = 1,
        penalty: float | None = None,
        qaoa_optimizer: Any | None = None,
        classifier: ProblemClassifier | None = None,
        algorithm_selector: AlgorithmSelector | None = None,
        capabilities: CapabilityModel | None = None,
        requested_algorithm: str | None = None,
        allow_algorithm_fallback: bool = False,
        executor: Executor | None = None,
        options: ExecutionOptions | None = None,
    ) -> None:
        if not isinstance(problem, QuantumProblem):
            raise TypeError("QuantumWorkflow requires a QuantumProblem")
        self.problem = problem
        self.program = program
        self.backend = backend
        self.shots = shots
        self.seed = seed
        self.name = name
        self.selector = selector or StrategySelector()
        self.mapper = mapper or QuantumCircuitMapper()
        self.classical_executor = classical_executor or ExhaustiveSolver()
        self.num_layers = num_layers
        self.penalty = penalty
        self.qaoa_optimizer = qaoa_optimizer
        self.classifier = classifier or ProblemClassifier()
        self.algorithm_selector = algorithm_selector or AlgorithmSelector()
        self.capabilities = capabilities
        self.requested_algorithm = requested_algorithm
        self.allow_algorithm_fallback = allow_algorithm_fallback
        self.executor_override = executor
        self.options = options
        self.state = WorkflowState.CREATED
        self.quantum_unavailable: bool | None = None
        self.execution_fallback: bool = False

        # Stage outputs of the last run.
        self.formulation: MathematicalModel | None = None
        self.strategy: ComputationStrategy | None = None
        self.mapping: MappingResult | None = None
        self.formulation_mapping: MappingResult | None = None
        self.qubo: Any = None
        self.ising: Any = None
        self.execution: Any = None
        self.solution: ProblemSolution | None = None
        self.report: SolutionReport | None = None
        self.algorithm: str = ""
        self.executor: str = ""

        # QMQ-03 intelligence stage outputs.
        self.classification: ClassificationResult | None = None
        self.strategy_decision: StrategyDecision | None = None
        self.formulation_recommendation: FormulationRecommendation | None = None
        self.recommendation: AlgorithmRecommendation | None = None
        self.computation_plan: ComputationPlan | None = None

    # -- lifecycle --------------------------------------------------------

    def _transition(self, target: WorkflowState, stage: str) -> None:
        """Move the workflow forward one state (lenient, forward-only).

        Skips are allowed (intermediate stages may be jumped over), but a
        backward transition or a reuse of a completed/failed workflow raises
        :class:`WorkflowError`.
        """
        order = list(WorkflowState)
        current_index = order.index(self.state)
        target_index = order.index(target)
        if self.state in {WorkflowState.COMPLETED, WorkflowState.FAILED}:
            raise WorkflowError(
                f"workflow is already {self.state.name.lower()}; cannot perform {stage}"
            )
        if target_index < current_index:
            raise WorkflowError(
                f"cannot {stage}: state would move backward from "
                f"{self.state.name.lower()} to {target.name.lower()}"
            )
        self.state = target

    def execution_options(self) -> ExecutionOptions:
        """Resolve execution options for the current decisions.

        Workflow constructor arguments (backend, shots, seed, num_layers,
        penalty, qaoa_optimizer) act as defaults; an explicit
        :class:`ExecutionOptions` on the constructor overrides them.
        """
        base = self.options or ExecutionOptions()
        strategy = base.resolved_strategy or (
            self.strategy
            or (self.computation_plan.strategy if self.computation_plan is not None else None)
        )
        algorithm = base.algorithm or self.algorithm or None
        return ExecutionOptions(
            strategy=strategy,
            algorithm=algorithm,
            shots=base.shots if base.shots != 1024 else self.shots,
            seed=base.seed if base.seed is not None else self.seed,
            backend=base.backend if base.backend is not None else self.backend,
            num_layers=base.num_layers if base.num_layers != 1 else self.num_layers,
            penalty=base.penalty if base.penalty is not None else self.penalty,
            qaoa_optimizer=(
                base.qaoa_optimizer if base.qaoa_optimizer is not None else self.qaoa_optimizer
            ),
            optimization_level=base.optimization_level,
            run_classical_baseline=base.run_classical_baseline,
            allow_fallback=base.allow_fallback or self.allow_algorithm_fallback,
            metadata={
                "workflow": self.name,
                "workflow_requested_algorithm": self.requested_algorithm,
                **base.metadata,
            },
        )

    def create_executor(self) -> Executor:
        """Build (or reuse) the executor for the selected strategy (QMQ-04 §4).

        The classical executor reuses the workflow's configured
        :class:`ExhaustiveSolver`; the quantum executor delegates to
        MicroQuantum's QAOA.
        """
        if self.executor_override is not None:
            return self.executor_override
        strategy = self.strategy or (
            self.computation_plan.strategy if self.computation_plan is not None else None
        )
        if strategy in {ComputationStrategy.CLASSICAL, ComputationStrategy.AUTO}:
            return ClassicalExecutor(solver=self.classical_executor)
        if strategy is ComputationStrategy.QUANTUM:
            return QuantumExecutor()
        if strategy is ComputationStrategy.HYBRID:
            return HybridExecutor(
                classical_executor=ClassicalExecutor(solver=self.classical_executor)
            )
        raise UnsupportedStrategyError(
            f"cannot create an executor for strategy "
            f"{strategy.name.lower() if strategy else 'none'}"
        )

    # -- pipeline stages -------------------------------------------------

    def formulate(self) -> MathematicalModel:
        """Build (or reuse) a formulation for the problem."""
        if self.problem.formulation is None:
            self.formulation = build_formulation(self.problem)
            self.problem.formulation = self.formulation
        else:
            self.formulation = self.problem.formulation
        self._transition(WorkflowState.FORMULATED, "formulate")
        return self.formulation

    def classify(self) -> ClassificationResult:
        """Classify the problem (QMQ-03).

        Returns:
            ClassificationResult: Deterministic structural classification of
            the problem.
        """
        if self.classification is None:
            self.classification = self.classifier.classify(
                self.problem, formulation=self.formulation
            )
            self._transition(WorkflowState.CLASSIFIED, "classify")
        return self.classification

    def _capabilities(self) -> CapabilityModel:
        if self.capabilities is None:
            self.capabilities = CapabilityModel.detect()
        return self.capabilities

    def select_strategy(self) -> ComputationStrategy:
        """Select the computation strategy for the problem.

        Uses the reasoned (QMQ-03) path once the problem has been
        classified; otherwise the legacy QMQ-01 selector is used so callers
        that never classify keep identical behaviour.
        """
        if self.classification is None:
            self.strategy = self.selector.select(self.problem)
            self._transition(WorkflowState.CLASSIFIED, "select_strategy")
            return self.strategy
        decision = self.selector.select_reasoned(
            self.problem,
            formulation=self.formulation,
            classification=self.classification,
            capabilities=self._capabilities(),
        )
        self.strategy_decision = decision
        self.strategy = decision.strategy
        return self.strategy

    def recommend(self) -> AlgorithmRecommendation:
        """Recommend an algorithm for the classified problem (QMQ-03).

        Runs classification + strategy selection first, then asks the
        :class:`AlgorithmSelector` for a scored recommendation with an
        executable fallback chain.

        Returns:
            AlgorithmRecommendation: The scored recommendation.
        """
        self.classify()
        self.select_strategy()
        recommendation = self.algorithm_selector.select(
            self.problem,
            formulation=self.formulation,
            strategy=self.strategy,
            classification=self.classification,
            capabilities=self._capabilities(),
            requested_algorithm=self.requested_algorithm,
            allow_fallback=self.allow_algorithm_fallback,
        )
        self.recommendation = recommendation
        self.formulation_recommendation = self.algorithm_selector.formulation_recommendation
        self._transition(WorkflowState.RECOMMENDED, "recommend")
        return recommendation

    def plan(self) -> ComputationPlan:
        """Build a declarative computation plan for the current decisions.

        Returns:
            ComputationPlan: The plan (QMQ-03, ready for QMQ-04).
        """
        self.recommend()
        strategy = self.strategy or ComputationStrategy.CLASSICAL
        capabilities = self._capabilities()
        recommendation = self.recommendation
        if recommendation is None:
            raise WorkflowError("recommendation must run before plan()")
        plan = ComputationPlan(
            problem_name=self.problem.name,
            problem_class=(
                self.classification.label if self.classification is not None else "unknown"
            ),
            formulation=(
                self.formulation_recommendation.primary
                if self.formulation_recommendation is not None
                else (self.formulation.kind if self.formulation is not None else "optimization")
            ),
            strategy=strategy,
            algorithm=recommendation.algorithm,
            recommendation=recommendation,
            mapping="ising" if strategy.uses_quantum_runtime else "qubo",
            executor=(
                "microquantum/qaoa" if strategy.uses_quantum_runtime else "classical/exhaustive"
            ),
            fallbacks=[
                fallback.algorithm
                for fallback in recommendation.fallbacks
                if fallback.algorithm is not None
            ],
            capabilities=capabilities.capability_flags(),
            classification=self.classification,
            formulation_recommendation=self.formulation_recommendation,
            strategy_decision=self.strategy_decision,
            reason=(
                "; ".join(self.strategy_decision.reasons)
                if self.strategy_decision is not None
                else recommendation.reason
            ),
            provenance={
                "module": "quantsmind.quantum.intelligence",
                "workflow": self.name,
            },
        )
        self.computation_plan = plan
        self._transition(WorkflowState.PLANNED, "plan")
        return plan

    def map(self) -> MappingResult:
        """Map the problem to a computational representation.

        Routing rules:

        * An attached :class:`QuantumProgram` uses the QMQ-01 circuit
          mapping (quantum strategies only).
        * Otherwise CLASSICAL uses ``QUBOMapper`` (problem -> QUBO).
        * QUANTUM/HYBRID additionally use ``IsingMapper`` (QUBO -> Ising).
          QUANTUM requires MicroQuantum; HYBRID degrades to the QUBO mapping
          when MicroQuantum is absent (the quantum leg is then recorded as
          unavailable during execution — a documented fallback, never a
          fabricated quantum result).

        Raises:
            MicroQuantumUnavailableError: For a QUANTUM strategy when the
                optional dependency is missing (an ImportError-compatible
                subclass of :class:`WorkflowError`).
            WorkflowError: For unsupported strategies.
        """
        if self.program is not None:
            strategy = self.select_strategy()
            if not strategy.uses_quantum_runtime:
                raise WorkflowError(
                    f"an explicit QuantumProgram cannot run under strategy {strategy.name.lower()}"
                )
            self.strategy = strategy
            self.mapping = self.mapper.map(self.program, strategy=strategy)
            self._transition(WorkflowState.MAPPED, "map")
            return self.mapping

        strategy = self.select_strategy()
        if strategy is ComputationStrategy.QUANTUM_INSPIRED:
            raise WorkflowError(
                "QUANTUM_INSPIRED execution is not implemented yet in "
                "QMQ-02; use CLASSICAL, QUANTUM or HYBRID"
            )
        self.strategy = strategy
        self.algorithm = "exhaustive" if not strategy.uses_quantum_runtime else "qaoa"
        self.executor = (
            "classical/exhaustive" if not strategy.uses_quantum_runtime else "microquantum/qaoa"
        )

        qubo_mapper = QUBOMapper()
        qubo_mapping = qubo_mapper.map(
            self.problem,
            strategy=strategy,
            penalty=self.penalty,
        )
        self.qubo = qubo_mapping.payload
        self.formulation_mapping = qubo_mapping

        self.quantum_unavailable = False
        if strategy.uses_quantum_runtime:
            if strategy is ComputationStrategy.QUANTUM and not microquantum_available():
                raise MicroQuantumUnavailableError(_INSTALL_HINT)
            if microquantum_available():
                ising_mapping = IsingMapper().map(self.qubo, strategy=strategy)
                self.ising = ising_mapping.payload
                self.mapping = ising_mapping
            else:
                self.quantum_unavailable = True
                self.ising = None
                self.mapping = qubo_mapping
        else:
            self.mapping = qubo_mapping
        self._transition(WorkflowState.MAPPED, "map")
        return self.mapping

    def execute(self) -> Any:
        """Execute the mapped representation via the strategy-derived executor.

        QMQ-04: the QMQ-03 computation plan is executed through the
        :class:`Executor` built by :meth:`create_executor` using
        :meth:`execution_options`:

        * CLASSICAL: exhaustive baseline over the QUBO.
        * QUANTUM: QAOA delegated to MicroQuantum (validated).
        * HYBRID: both legs run; an unavailable quantum leg falls back to the
          classical result and is recorded as skipped — never fabricated.
        * Explicit-program path: run through :class:`QuantumExperiment`.

        Raises:
            WorkflowError: If mapping/planning/execution cannot proceed.
            UnsupportedStrategyError: If the plan resolves to a strategy this
                layer cannot execute.
        """
        if self.program is not None:
            if self.mapping is None:
                self.map()
            if self.mapping is None:
                raise WorkflowError("mapping did not produce a result")
            self._transition(WorkflowState.EXECUTING, "execute")
            circuit = self.mapper.build(self.mapping)
            strategy_label = self.strategy.name.lower() if self.strategy is not None else ""
            try:
                self.execution = QuantumExperiment(
                    circuit,
                    backend=self.backend,
                    shots=self.shots,
                    seed=self.seed,
                    name=self.name,
                    domain_metadata={
                        "problem": self.problem.name,
                        "strategy": strategy_label,
                    },
                ).run()
            except Exception:
                self.state = WorkflowState.FAILED
                raise
            self._transition(WorkflowState.COMPLETED, "complete execution")
            return self.execution

        if self.mapping is None:
            self.map()
        assert self.strategy is not None

        if self.strategy is ComputationStrategy.QUANTUM_INSPIRED:
            raise WorkflowError(
                "QUANTUM_INSPIRED execution is not implemented yet in "
                "QMQ-02; use CLASSICAL, QUANTUM or HYBRID"
            )

        if self.computation_plan is None:
            self.plan()

        options = self.execution_options()
        executor = self.create_executor()

        self._transition(WorkflowState.EXECUTING, "execute")
        context = ExecutorContext(
            problem=self.problem,
            plan=self.computation_plan,
            formulation=self.formulation,
            qubo=self.qubo,
            ising=self.ising,
            options=options,
            metadata={"workflow": self.name},
        )
        try:
            if self.strategy is ComputationStrategy.QUANTUM:
                if not executor.is_available() and options.allow_fallback:
                    fallback = ClassicalExecutor(solver=self.classical_executor)
                    self.execution = fallback.execute(context)
                    self.execution = fallback.validate(self.execution, context)
                    self.execution_fallback = True
                    self.executor = "classical/exhaustive"
                    self.algorithm = "exhaustive"
                else:
                    raw = executor.execute(context)
                    self.execution = executor.validate(raw, context)
            elif self.strategy is ComputationStrategy.CLASSICAL:
                self.execution = executor.execute(context)
                self.execution = executor.validate(self.execution, context)
            elif self.strategy is ComputationStrategy.HYBRID:
                result = executor.execute(context)
                self.execution = result
                self.execution_fallback = bool(getattr(result, "quantum", None) is None)
            else:
                raise UnsupportedStrategyError(
                    f"strategy {self.strategy.name.lower()} cannot be executed "
                    "by QMQ-04; the plan must resolve to CLASSICAL, QUANTUM "
                    "or HYBRID"
                )
        except Exception:
            self.state = WorkflowState.FAILED
            raise
        self._transition(WorkflowState.COMPLETED, "complete execution")
        return self.execution

    # -- feasibility / objective helpers ----------------------------------

    def _feasibility_predicate(self) -> Callable[[dict[str, int]], bool]:
        from quantsmind.quantum.core.constraint import ConstraintStatus

        def is_feasible(assignment: dict[str, int]) -> bool:
            return all(
                constraint.evaluate(assignment) is not ConstraintStatus.VIOLATED
                for constraint in self.problem.constraints
            )

        return is_feasible

    def _objective_evaluator(self) -> Callable[[dict[str, int]], float]:
        objective = self.problem.objectives[0] if self.problem.objectives else None

        def evaluate(assignment: dict[str, int]) -> float:
            if objective is None:
                return 0.0
            value = objective.evaluate(assignment)
            return 0.0 if value is None else value

        return evaluate

    # -- solution construction ---------------------------------------------

    def build_solution(self) -> ProblemSolution:
        """Derive a domain solution from the execution result.

        Quantum-program executions decode the most probable measurement
        bitstring using ``problem.metadata["encoding"]`` (QMQ-01).  QMQ-02
        executions (classical baseline, QAOA) carry an explicit
        ``assignment`` and are used directly.  Objectives and constraints
        support callable **and** symbolic string expressions.
        """
        if self.execution is None:
            raise WorkflowError("execute() must run before build_solution()")
        solution = ProblemSolution.from_names(
            self.problem.name,
            self.problem.variable_names,
            self.problem.objective_names,
            self.problem.constraint_names,
        )
        assignment = getattr(self.execution, "assignment", None)
        if isinstance(assignment, dict):
            for name, value in assignment.items():
                if name in solution.assignments:
                    solution.assignments[name] = int(value)
        else:
            solution.assignments.update(self._assignments_from_counts())
        solution.evaluate(self.problem)
        solution.score = solution.compute_score(self.problem)
        solution.metadata.update(
            {
                "backend": getattr(self.execution, "backend_name", "")
                or getattr(self.execution, "backend", ""),
                "shots": getattr(self.execution, "shots", 0),
                "execution_id": getattr(self.execution, "experiment_id", ""),
                "executor": getattr(self.execution, "solver", ""),
                "algorithm": getattr(self.execution, "algorithm", self.algorithm),
                "energy": getattr(self.execution, "energy", None),
                "exhaustive": bool(getattr(self.execution, "exhaustive", False)),
            }
        )
        if isinstance(self.execution, HybridExecutionResult):
            solution.metadata.update(
                {
                    "selected_leg": self.execution.selected,
                    "quantum_leg": (
                        "executed" if self.execution.quantum is not None else "skipped"
                    ),
                    "classical_leg": (
                        "executed" if self.execution.classical is not None else "failed"
                    ),
                    "execution_comparison": (
                        self.execution.comparison.to_dict()
                        if self.execution.comparison is not None
                        else None
                    ),
                }
            )
        solution.metadata["quantum_unavailable"] = bool(self.quantum_unavailable)
        solution.metadata["execution_fallback"] = bool(self.execution_fallback)
        return solution

    def _assignments_from_counts(self) -> dict[str, Any]:
        """Decode the most probable measurement bitstring into assignments."""
        encoding = self.problem.metadata.get("encoding")
        if not isinstance(encoding, dict):
            return {}
        counts: dict[str, int] = getattr(self.execution, "counts", {}) or {}
        if not counts:
            return {}
        bitstring = max(sorted(counts), key=lambda k: counts[k])
        assignments: dict[str, Any] = {}
        for qubit_label, variable_name in encoding.items():
            try:
                index = int(qubit_label)
            except (TypeError, ValueError):
                continue
            if 0 <= index < len(bitstring):
                assignments[str(variable_name)] = int(bitstring[index])
        return assignments

    def interpret(self, solution: ProblemSolution) -> Interpretation:
        """Produce a data-derived interpretation of the solution."""
        return SolutionInterpreter().interpret(solution, strategy=self.strategy)

    def build_provenance(self, execution: Any | None = None) -> Provenance:
        """Build provenance for the current run.

        Hybrid executions record the selected leg as the provenance executor
        (``"hybrid"``) and carry the explicit comparison in metadata.
        """
        resolved = execution if execution is not None else self.execution
        executor_label = self.executor or ""
        if isinstance(resolved, HybridExecutionResult):
            executor_label = "hybrid"
        return Provenance.from_execution(
            strategy=self.strategy,
            formulation=(self.formulation.kind if self.formulation is not None else ""),
            algorithm=self.algorithm,
            executor=executor_label,
            backend=self.backend or "",
            execution=resolved,
            metadata={
                "workflow": self.name,
                "microquantum_used": bool(
                    str(getattr(resolved, "solver", "")).startswith("microquantum")
                ),
                "microquantum_version": _microquantum_version(),
                "qubo_name": getattr(self.qubo, "name", None),
                "ising_name": getattr(self.ising, "name", None),
                "quantum_unavailable": self.quantum_unavailable,
                "execution_fallback": self.execution_fallback,
            },
        )

    # -- end-to-end ------------------------------------------------------

    def run(self) -> SolutionReport:
        """Run the full pipeline and return a :class:`SolutionReport`.

        Pipeline (QMQ-03): formulate -> classify -> select strategy ->
        recommend algorithm -> build plan -> map -> execute.
        """
        if self.state in {WorkflowState.COMPLETED, WorkflowState.FAILED}:
            raise WorkflowError(
                f"workflow is already {self.state.name.lower()}; create a new "
                "QuantumWorkflow for another run"
            )
        self.formulate()
        self.classify()
        self.recommend()
        self.plan()
        try:
            self.map()
            self.execute()
        except Exception:
            self.state = WorkflowState.FAILED
            raise
        self.solution = self.build_solution()
        interpretation = self.interpret(self.solution)
        provenance = self.build_provenance()
        if isinstance(self.execution, HybridExecutionResult):
            classical_execution = self.execution.classical
            quantum_execution = self.execution.quantum
            comparison = self.execution.comparison
            selected_leg = self.execution.selected
        else:
            classical_execution = (
                self.execution if isinstance(self.execution, ClassicalExecutionResult) else None
            )
            quantum_execution = (
                self.execution if isinstance(self.execution, QuantumExecutionResult) else None
            )
            comparison = None
            selected_leg = None
        self.report = SolutionReport(
            problem=self.problem,
            formulation=self.formulation,
            strategy=self.strategy,
            mapping=self.mapping,
            execution=self.execution,
            solution=self.solution,
            interpretation=interpretation,
            provenance=provenance,
            classification=self.classification,
            recommendation=self.recommendation,
            plan=self.computation_plan,
            classical_execution=classical_execution,
            quantum_execution=quantum_execution,
            comparison=comparison,
            selected_leg=selected_leg,
        )
        return self.report


__all__ = ["QuantumWorkflow", "WorkflowError", "WorkflowState"]
