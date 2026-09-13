"""QMQ-03 tests — algorithm & computational strategy intelligence.

Covers classification, the algorithm registry, capability detection, the
formulation/scheme recommender, rule-based algorithm selection with
fallbacks, the reasoned strategy path, the computation plan and the
workflow pipeline integration (problem -> classify -> formulate -> strategy
-> recommend -> plan -> map -> execute).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import quantsmind.quantum as q
from quantsmind.quantum import (
    AlgorithmCategory,
    AlgorithmRecommendation,
    AlgorithmRegistry,
    AlgorithmSelectionError,
    AlgorithmSelector,
    CapabilityModel,
    ClassificationResult,
    ComputationPlan,
    DuplicateAlgorithmError,
    FormulationRecommendation,
    FormulationRecommender,
    ProblemClass,
    ProblemClassifier,
    UnknownAlgorithmError,
    Variable,
    VariableType,
)
from quantsmind.quantum.core.problem import QuantumProblem
from quantsmind.quantum.strategy.selector import StrategyDecision, StrategySelector
from quantsmind.quantum.strategy.strategy import ComputationStrategy

_SRC = str(Path(__file__).parents[3] / "src")

_ALL_ALGORITHMS = [
    "qaoa",
    "vqe",
    "vqd",
    "adapt_vqe",
    "grover",
    "shor",
    "bernstein_vazirani",
    "deutsch_jozsa",
    "qft",
    "phase_estimation",
    "amplitude_estimation",
    "hamiltonian_simulation",
    "hhl",
    "discrete_quantum_walk",
    "continuous_quantum_walk",
]


def _binary_problem(n: int = 2, *, name: str = "bin") -> QuantumProblem:
    variables = [Variable(f"x{i}", VariableType.BINARY) for i in range(n)]
    expression = " + ".join(f"{i + 1}*x{i}" for i in range(n))
    objective = q.Objective.minimize("obj", expression=expression)
    return QuantumProblem(name, variables=variables, objectives=[objective])


def _integer_problem() -> QuantumProblem:
    variables = [
        Variable("i0", VariableType.INTEGER, lower_bound=0, upper_bound=3),
        Variable("i1", VariableType.INTEGER, lower_bound=0, upper_bound=3),
    ]
    objective = q.Objective.minimize("obj", expression="i0 + 2*i1")
    return QuantumProblem("intp", variables=variables, objectives=[objective])


def _continuous_problem() -> QuantumProblem:
    variables = [
        Variable("c0", VariableType.CONTINUOUS, lower_bound=0.0, upper_bound=1.0),
        Variable("c1", VariableType.CONTINUOUS, lower_bound=0.0, upper_bound=1.0),
    ]
    objective = q.Objective.minimize("obj", expression="c0 + 2*c1")
    return QuantumProblem("contp", variables=variables, objectives=[objective])


def _formulate(problem: QuantumProblem):
    from quantsmind.quantum.formulation import formulate

    return formulate(problem)


def _mq_capabilities(quantum: bool = True) -> CapabilityModel:
    return CapabilityModel(
        microquantum_installed=quantum,
        quantum_enabled=quantum,
        simulator_available=quantum,
        backend_available=quantum,
        qml_available=quantum,
        quantum_execution_enabled=quantum,
        algorithm_available={aid: quantum for aid in _ALL_ALGORITHMS},
    )


# ------------------------------------------------------------------ §5 class


class TestProblemClassification:
    def test_binary_optimization(self) -> None:
        result = ProblemClassifier().classify(_binary_problem(), _formulate(_binary_problem()))
        assert result.label == "binary_optimization"
        assert result.is_optimization
        assert "binary" in result.reason

    def test_integer_optimization(self) -> None:
        result = ProblemClassifier().classify(_integer_problem(), _formulate(_integer_problem()))
        assert result.label == "integer_optimization"

    def test_continuous_optimization(self) -> None:
        result = ProblemClassifier().classify(
            _continuous_problem(), _formulate(_continuous_problem())
        )
        assert result.label == "continuous_optimization"

    def test_graph_optimization(self) -> None:
        model = q.GraphModel(nodes=["n0", "n1"], edges=[("n0", "n1")])
        result = ProblemClassifier().classify(_binary_problem(), model)
        assert result.label == "graph_optimization"

    def test_machine_learning(self) -> None:
        model = q.MLModel(features=["f0", "f1"], target="y", task="regression")
        result = ProblemClassifier().classify(_binary_problem(), model)
        assert result.label == "machine_learning"

    def test_simulation(self) -> None:
        model = q.SimulationModel(time_steps=4, dynamics="ising")
        result = ProblemClassifier().classify(_binary_problem(), model)
        assert result.label == "simulation"

    def test_statistical(self) -> None:
        model = q.StatisticalModel(distribution="normal")
        result = ProblemClassifier().classify(_binary_problem(), model)
        assert result.label == "statistical"

    def test_unknown_default(self) -> None:
        result = ProblemClassifier().classify(_binary_problem(), q.MathematicalModel())
        assert result.problem_class.name.lower() == "unknown"

    def test_metadata_override_wins(self) -> None:
        problem = _binary_problem()
        problem.metadata["problem_class"] = "search"
        result = ProblemClassifier().classify(problem)
        assert result.label == "search"

    def test_parse_and_roundtrip(self) -> None:
        assert ProblemClass.parse("binary-optimization") is ProblemClass.BINARY_OPTIMIZATION
        assert "sampling" in ProblemClass.known_labels()
        result = ProblemClassifier().classify(_binary_problem(), _formulate(_binary_problem()))
        assert ClassificationResult.from_dict(result.to_dict()).label == "binary_optimization"


# --------------------------------------------------------------- §4 registry


class TestAlgorithmRegistry:
    def test_default_catalog(self) -> None:
        registry = AlgorithmRegistry()
        assert "qaoa" in registry
        assert "vqe" in registry
        assert "grover" in registry
        assert "exhaustive" in registry
        assert len(registry) >= 17

    def test_get_unknown_raises(self) -> None:
        with pytest.raises(UnknownAlgorithmError):
            AlgorithmRegistry().get("nope")

    def test_duplicate_register_raises(self) -> None:
        registry = AlgorithmRegistry()
        descriptor = registry.get("qaoa")
        with pytest.raises(DuplicateAlgorithmError):
            registry.register(descriptor)

    def test_register_custom(self) -> None:
        registry = AlgorithmRegistry()
        registry.unregister("qaoa")
        assert "qaoa" not in registry
        with pytest.raises(UnknownAlgorithmError):
            registry.unregister("qaoa")

    def test_find_by_class_and_category(self) -> None:
        registry = AlgorithmRegistry()
        matches = registry.find(problem_class="binary_optimization")
        assert {"qaoa", "vqe", "exhaustive"}.issubset({d.name for d in matches})
        search = registry.find(problem_class="search", category=AlgorithmCategory.SEARCH)
        assert {d.name for d in search} == {"grover"}
        linear = registry.find(category=AlgorithmCategory.LINEAR_ALGEBRA)
        assert "qft" in {d.name for d in linear}

    def test_availability_three_tiers(self) -> None:
        registry = AlgorithmRegistry()
        capabilities = _mq_capabilities()
        availability = {entry.algorithm: entry for entry in registry.available(capabilities)}
        assert availability["qaoa"].available_in_microquantum
        assert availability["qaoa"].currently_executable
        assert availability["exhaustive"].currently_executable
        assert "qaoa" in registry.executable_algorithms(capabilities)

    def test_descriptor_serialization(self) -> None:
        registry = AlgorithmRegistry()
        descriptor = registry.get("qaoa")
        assert descriptor.microquantum_identifier == "QAOA"
        assert "qubo" in descriptor.formulations
        assert registry.from_dict(registry.to_dict())["qaoa"].name == "qaoa"


# --------------------------------------------------- §11 capability detection


class TestCapabilityModel:
    def test_detects_microquantum_when_installed(self) -> None:
        capabilities = CapabilityModel.detect()
        assert capabilities.microquantum_installed
        assert capabilities.quantum_execution_enabled
        assert capabilities.is_available("qaoa_available")
        assert capabilities.is_available("qaoa")
        assert capabilities.is_available("microquantum")
        assert capabilities.required_caps_met(("qaoa_available",))

    def test_disable_quantum_policy(self) -> None:
        capabilities = CapabilityModel.detect(quantum_enabled=False)
        assert not capabilities.quantum_execution_enabled

    def test_absent_capability_rejected(self) -> None:
        capabilities = CapabilityModel(
            microquantum_installed=True,
            simulator_available=True,
            backend_available=True,
            algorithm_available={"qaoa": False},
        )
        assert not capabilities.is_available("qaoa_available")
        assert capabilities.executable_algorithms() == []

    def test_capability_flags_and_roundtrip(self) -> None:
        capabilities = _mq_capabilities()
        flags = capabilities.capability_flags()
        assert flags["qaoa_available"] is True
        assert flags["classical_baseline_available"] is True
        rebuilt = CapabilityModel.from_dict(capabilities.to_dict())
        assert rebuilt.microquantum_installed == capabilities.microquantum_installed
        assert rebuilt.is_available("grover") is capabilities.is_available("grover")

    def test_graceful_without_microquantum(self) -> None:
        code = f"""
import sys
sys.path.insert(0, {_SRC!r})
class _Block:
    def find_spec(self, name, path=None, target=None):
        if name == "microquantum" or name.startswith("microquantum."):
            raise ImportError("blocked for test")
        return None
sys.meta_path.insert(0, _Block())
from quantsmind.quantum.intelligence import CapabilityModel, AlgorithmRegistry
c = CapabilityModel.detect()
assert c.microquantum_installed is False
assert c.quantum_execution_enabled is False
assert c.executable_algorithms() == []
assert c.classical_baseline_available is True
r = AlgorithmRegistry()
assert "exhaustive" in r.executable_algorithms(c)
print("OK")
"""
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, result.stderr


# ------------------------------------------------------ §6 formulation choice


class TestFormulationRecommender:
    def test_binary_recommends_qubo(self) -> None:
        recommendation = FormulationRecommender().recommend(
            _binary_problem(), _formulate(_binary_problem())
        )
        assert recommendation.primary == "qubo"
        assert recommendation.is_qubo
        assert {alt.kind for alt in recommendation.alternatives} == {"ising"}

    def test_integer_not_forced_into_qubo(self) -> None:
        recommendation = FormulationRecommender().recommend(
            _integer_problem(), _formulate(_integer_problem())
        )
        assert recommendation.primary == "optimization"
        assert not recommendation.is_qubo
        assert any(alt.kind == "qubo" for alt in recommendation.alternatives)

    def test_continuous_has_no_qubo(self) -> None:
        recommendation = FormulationRecommender().recommend(
            _continuous_problem(), _formulate(_continuous_problem())
        )
        assert recommendation.primary == "optimization"
        assert all(alt.kind != "qubo" for alt in recommendation.alternatives)

    def test_graph_keeps_native(self) -> None:
        model = q.GraphModel(nodes=["n0", "n1"], edges=[("n0", "n1")])
        recommendation = FormulationRecommender().recommend(_binary_problem(), model)
        assert recommendation.primary == "graph"

    def test_ml_and_simulation_keep_native(self) -> None:
        assert (
            FormulationRecommender().recommend(_binary_problem(), q.MLModel(features=["f"])).primary
            == "ml"
        )
        assert (
            FormulationRecommender()
            .recommend(_binary_problem(), q.SimulationModel(time_steps=2))
            .primary
            == "simulation"
        )

    def test_roundtrip(self) -> None:
        recommendation = FormulationRecommender().recommend(
            _binary_problem(), _formulate(_binary_problem())
        )
        rebuilt = FormulationRecommendation.from_dict(recommendation.to_dict())
        assert rebuilt.primary == "qubo"
        assert len(rebuilt.alternatives) == len(recommendation.alternatives)


# ------------------------------------------------------- §8-§10 §25 selection


class TestAlgorithmSelector:
    def test_qubo_quantum_routes_to_qaoa(self) -> None:
        selector = AlgorithmSelector()
        recommendation = selector.select(
            _binary_problem(),
            strategy=ComputationStrategy.QUANTUM,
            capabilities=_mq_capabilities(),
        )
        assert recommendation.algorithm == "qaoa"
        assert recommendation.suitability_score == 0.9
        assert recommendation.required_capabilities == [
            "quantum_execution_enabled",
            "qaoa_available",
        ]
        assert "QAOA" in recommendation.reason
        assert recommendation.execution_mode == "vqe_loop"
        assert recommendation.expected_input_representation
        # classical fallback always present for a quantum recommendation
        assert any(f.algorithm == "exhaustive" for f in recommendation.fallbacks)

    def test_qubo_classical_routes_to_exhaustive(self) -> None:
        recommendation = AlgorithmSelector().select(
            _binary_problem(),
            strategy=ComputationStrategy.CLASSICAL,
            capabilities=_mq_capabilities(quantum=False),
        )
        assert recommendation.algorithm == "exhaustive"
        assert recommendation.suitability_score == 0.9

    def test_quantum_unavailable_is_never_silent(self) -> None:
        recommendation = AlgorithmSelector().select(
            _binary_problem(),
            strategy=ComputationStrategy.QUANTUM,
            capabilities=CapabilityModel(microquantum_installed=False, quantum_enabled=True),
        )
        assert recommendation.algorithm is None
        assert recommendation.metadata.get("recommended_but_unavailable") == "qaoa"
        assert any(f.algorithm == "exhaustive" for f in recommendation.fallbacks)

    def test_hybrid_routes_to_qaoa(self) -> None:
        recommendation = AlgorithmSelector().select(
            _binary_problem(),
            strategy=ComputationStrategy.HYBRID,
            capabilities=_mq_capabilities(),
        )
        assert recommendation.algorithm == "qaoa"

    def test_search_routes_to_grover(self) -> None:
        problem = _binary_problem()
        problem.metadata["problem_class"] = "search"
        recommendation = AlgorithmSelector().select(
            problem, strategy=ComputationStrategy.QUANTUM, capabilities=_mq_capabilities()
        )
        assert recommendation.algorithm == "grover"
        assert recommendation.suitability_score == 0.9

    def test_simulation_routes_to_hamiltonian_simulation(self) -> None:
        problem = _binary_problem()
        problem.metadata["problem_class"] = "simulation"
        recommendation = AlgorithmSelector().select(
            problem,
            formulation=q.SimulationModel(time_steps=2),
            strategy=ComputationStrategy.QUANTUM,
            capabilities=_mq_capabilities(),
        )
        assert recommendation.algorithm == "hamiltonian_simulation"
        assert recommendation.suitability_score == 0.8

    def test_statistical_routes_to_amplitude_estimation(self) -> None:
        problem = _binary_problem()
        problem.metadata["problem_class"] = "statistical"
        recommendation = AlgorithmSelector().select(
            problem, strategy=ComputationStrategy.QUANTUM, capabilities=_mq_capabilities()
        )
        assert recommendation.algorithm == "amplitude_estimation"

    def test_ml_routes_to_qml(self) -> None:
        problem = _binary_problem()
        problem.metadata["problem_class"] = "machine_learning"
        recommendation = AlgorithmSelector().select(
            problem,
            formulation=q.MLModel(features=["f"], target="y"),
            strategy=ComputationStrategy.HYBRID,
            capabilities=_mq_capabilities(),
        )
        assert recommendation.algorithm == "qml"

    def test_requested_unknown_raises(self) -> None:
        with pytest.raises(AlgorithmSelectionError, match="not known"):
            AlgorithmSelector().select(_binary_problem(), requested_algorithm="not_an_algorithm")

    def test_requested_unavailable_requires_fallback(self) -> None:
        capabilities = CapabilityModel(microquantum_installed=False, quantum_enabled=True)
        with pytest.raises(AlgorithmSelectionError, match="not currently executable"):
            AlgorithmSelector().select(
                _binary_problem(),
                strategy=ComputationStrategy.QUANTUM,
                capabilities=capabilities,
                requested_algorithm="qaoa",
            )

    def test_requested_unavailable_with_permitted_fallback(self) -> None:
        recommendation = AlgorithmSelector().select(
            _binary_problem(),
            strategy=ComputationStrategy.CLASSICAL,
            capabilities=CapabilityModel(microquantum_installed=False, quantum_enabled=True),
            requested_algorithm="qaoa",
            allow_fallback=True,
        )
        assert recommendation.algorithm == "exhaustive"
        assert recommendation.user_requested
        assert recommendation.metadata.get("requested_algorithm") == "qaoa"
        assert recommendation.metadata.get("fallback_applied") is True

    def test_recommendation_serializes(self) -> None:
        recommendation = AlgorithmSelector().select(
            _binary_problem(),
            strategy=ComputationStrategy.QUANTUM,
            capabilities=_mq_capabilities(),
        )
        rebuilt = AlgorithmRecommendation.from_dict(recommendation.to_dict())
        assert rebuilt.algorithm == recommendation.algorithm
        assert rebuilt.fallbacks[0].algorithm == recommendation.fallbacks[0].algorithm


# ----------------------------------------------------------- §7 §16 §17 strategy


class TestStrategySelectorReasoned:
    def _selector(self) -> StrategySelector:
        return StrategySelector(quantum_attempt_threshold=5, quantum_inspired_threshold=20)

    def test_explicit_preference_honoured(self) -> None:
        problem = _binary_problem()
        problem.preferred_strategy = ComputationStrategy.CLASSICAL
        decision = self._selector().select_reasoned(problem, capabilities=_mq_capabilities())
        assert decision.strategy is ComputationStrategy.CLASSICAL
        assert decision.reasons

    def test_explicit_quantum_downgraded_without_runtime(self) -> None:
        problem = _binary_problem()
        problem.preferred_strategy = ComputationStrategy.QUANTUM
        decision = self._selector().select_reasoned(
            problem, capabilities=CapabilityModel(microquantum_installed=False)
        )
        assert decision.strategy is ComputationStrategy.CLASSICAL
        assert any("downgraded" in reason for reason in decision.reasons)

    def test_auto_size_hybrid(self) -> None:
        decision = self._selector().select_reasoned(
            _binary_problem(3), capabilities=_mq_capabilities()
        )
        assert decision.strategy is ComputationStrategy.HYBRID

    def test_auto_size_quantum_inspired(self) -> None:
        decision = self._selector().select_reasoned(
            _binary_problem(10), capabilities=_mq_capabilities()
        )
        assert decision.strategy is ComputationStrategy.QUANTUM_INSPIRED

    def test_auto_size_classical(self) -> None:
        decision = self._selector().select_reasoned(
            _binary_problem(30), capabilities=_mq_capabilities()
        )
        assert decision.strategy is ComputationStrategy.CLASSICAL

    def test_binary_small_routes_to_hybrid_with_reason(self) -> None:
        classification = ProblemClassifier().classify(
            _binary_problem(), _formulate(_binary_problem())
        )
        decision = self._selector().select_reasoned(
            _binary_problem(),
            classification=classification,
            formulation=_formulate(_binary_problem()),
            capabilities=_mq_capabilities(),
        )
        assert decision.strategy is ComputationStrategy.HYBRID
        assert any("comparison" in reason for reason in decision.reasons)

    def test_simulation_class_routes_to_quantum(self) -> None:
        problem = _binary_problem()
        problem.metadata["problem_class"] = "simulation"
        classification = ProblemClassifier().classify(problem)
        decision = self._selector().select_reasoned(
            problem, classification=classification, capabilities=_mq_capabilities()
        )
        assert decision.strategy is ComputationStrategy.QUANTUM

    def test_continuous_class_prefers_classical(self) -> None:
        problem = _continuous_problem()
        classification = ProblemClassifier().classify(problem, _formulate(_continuous_problem()))
        decision = self._selector().select_reasoned(
            problem,
            classification=classification,
            formulation=_formulate(_continuous_problem()),
            capabilities=_mq_capabilities(),
        )
        assert decision.strategy is ComputationStrategy.CLASSICAL

    def test_matches_legacy_select_without_signals(self) -> None:
        problem = _binary_problem(30)
        decision = self._selector().select_reasoned(problem)
        assert decision.strategy is self._selector().select(problem)

    def test_decision_roundtrip(self) -> None:
        decision = self._selector().select_reasoned(
            _binary_problem(), capabilities=_mq_capabilities()
        )
        rebuilt = StrategyDecision.from_dict(decision.to_dict())
        assert rebuilt.strategy is decision.strategy
        assert rebuilt.reasons == decision.reasons


# ------------------------------------------------- §13 §14 §22 plan + workflow


class TestComputationPlanWorkflow:
    def test_plan_serializes_roundtrip(self) -> None:
        classification = ProblemClassifier().classify(
            _binary_problem(), _formulate(_binary_problem())
        )
        caps = _mq_capabilities()
        selector = StrategySelector(quantum_attempt_threshold=5, quantum_inspired_threshold=20)
        decision = selector.select_reasoned(
            _binary_problem(),
            classification=classification,
            formulation=_formulate(_binary_problem()),
            capabilities=caps,
        )
        recommendation = AlgorithmSelector().select(
            _binary_problem(),
            strategy=decision.strategy,
            classification=classification,
            capabilities=caps,
        )
        plan = ComputationPlan(
            problem_name="bin",
            problem_class=classification.label,
            formulation="qubo",
            strategy=decision.strategy,
            algorithm=recommendation.algorithm,
            recommendation=recommendation,
            mapping="ising",
            executor="microquantum/qaoa",
            fallbacks=[f.algorithm for f in recommendation.fallbacks],
            capabilities=caps.capability_flags(),
            classification=classification,
            strategy_decision=decision,
            reason=" ".join(decision.reasons),
        )
        rebuilt = ComputationPlan.from_dict(plan.to_dict())
        assert rebuilt.strategy is plan.strategy
        assert rebuilt.algorithm == plan.algorithm
        assert rebuilt.classification.label == classification.label
        assert rebuilt.strategy_decision.strategy is decision.strategy

    def test_workflow_run_attaches_intelligence(self) -> None:
        problem = _binary_problem()
        problem.preferred_strategy = ComputationStrategy.CLASSICAL
        report = q.QuantumWorkflow(problem).run()
        assert report.classification is not None
        assert report.classification.label == "binary_optimization"
        assert report.recommendation is not None
        assert report.plan is not None
        assert report.strategy is ComputationStrategy.CLASSICAL
        assert report.plan.strategy.value == "classical"
        assert report.plan.executor == "classical/exhaustive"
        assert report.plan.algorithm == "exhaustive"
        assert report.provenance.executor == "classical/exhaustive"
        data = report.to_dict()
        assert data["classification"]["problem_class"] == "binary_optimization"
        assert data["plan"]["algorithm"] == "exhaustive"

    def test_workflow_requested_algorithm_with_permitted_fallback(self) -> None:
        problem = _binary_problem()
        problem.preferred_strategy = ComputationStrategy.CLASSICAL
        workflow = q.QuantumWorkflow(
            problem,
            requested_algorithm="qaoa",
            allow_algorithm_fallback=True,
            capabilities=CapabilityModel(microquantum_installed=False, quantum_enabled=True),
        )
        report = workflow.run()
        assert report.plan.algorithm == "exhaustive"
        assert report.recommendation.metadata.get("fallback_applied") is True

    def test_workflow_requested_algorithm_honoured_when_executable(self) -> None:
        problem = _binary_problem()
        problem.preferred_strategy = ComputationStrategy.QUANTUM
        workflow = q.QuantumWorkflow(problem, requested_algorithm="qaoa")
        report = workflow.run()
        assert report.recommendation.algorithm == "qaoa"
        assert report.recommendation.user_requested
        assert report.plan.algorithm == "qaoa"

    @pytest.mark.skipif(not q.qaoa_available(), reason="microquantum missing")
    def test_workflow_recommends_and_runs_qaoa(self) -> None:
        problem = _binary_problem()
        problem.preferred_strategy = ComputationStrategy.QUANTUM
        workflow = q.QuantumWorkflow(
            problem,
            num_layers=1,
            shots=64,
            seed=5,
            qaoa_optimizer=_fast_optimizer(),
        )
        report = workflow.run()
        assert report.recommendation.algorithm == "qaoa"
        assert report.plan.algorithm == "qaoa"
        assert report.plan.executor == "microquantum/qaoa"
        assert report.provenance.executor == "microquantum/qaoa"
        assert report.solution is not None

    def test_workflow_classify_recommend_plan_stages(self) -> None:
        workflow = q.QuantumWorkflow(_binary_problem())
        workflow.formulate()
        classification = workflow.classify()
        recommendation = workflow.recommend()
        plan = workflow.plan()
        assert classification.label == "binary_optimization"
        assert plan.strategy is workflow.strategy
        assert recommendation.algorithm == plan.algorithm
        assert plan.classification is classification


def _fast_optimizer():
    import microquantum as mq

    return mq.GradientDescent(learning_rate=0.1, max_iter=3, tol=1e-6)
