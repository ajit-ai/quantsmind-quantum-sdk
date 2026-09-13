"""Tests for the QMQ-02 MicroQuantum QAOA integration seam.

These tests execute real MicroQuantum QAOA runs; the module is skipped when
``microquantum`` is not installed.  The integration layer itself must stay
importable without it (see ``test_optional_dependency.py``).
"""

from __future__ import annotations

import pytest

mq = pytest.importorskip("microquantum")

from quantsmind.quantum.integration.microquantum import (  # noqa: E402
    QaoaExecutionResult,
    ising_to_optimization_problem,
    ising_to_pauli_sum,
    run_qaoa,
)
from quantsmind.quantum.optimization.ising import IsingModel  # noqa: E402
from quantsmind.quantum.optimization.qubo import QUBOModel  # noqa: E402


def _fast_optimizer() -> mq.GradientDescent:
    return mq.GradientDescent(learning_rate=0.1, max_iter=3, tol=1e-6)


class TestPauliSumConversion:
    def test_ising_becomes_pauli_sum(self) -> None:
        ising = IsingModel(
            variables=["a", "b"],
            h={"a": 1.5, "b": -2.0},
            couplings={("a", "b"): 3.0},
            constant=99.0,
        )
        pauli_sum = ising_to_pauli_sum(ising)
        assert pauli_sum.num_qubits == 2
        terms = {term.label: term.coefficient.real for term in pauli_sum.terms}
        assert terms == {"ZI": 1.5, "IZ": -2.0, "ZZ": 3.0}

    def test_constant_excluded_from_pauli_sum(self) -> None:
        # The additive constant is carried by IsingModel.energy, not the
        # Pauli operators (MicroQuantum's eigenvalue excludes it).
        ising = IsingModel(variables=["a"], h={"a": 2.0}, constant=7.0)
        pauli_sum = ising_to_pauli_sum(ising)
        assert pauli_sum.num_qubits == 1
        assert {t.label: t.coefficient.real for t in pauli_sum.terms} == {"Z": 2.0}

    def test_optimization_problem_name(self) -> None:
        ising = IsingModel(variables=["a"], h={"a": 1.0}, name="demo_ising")
        problem = ising_to_optimization_problem(ising, name="demo")
        assert problem.name == "demo"
        assert problem.num_variables == 1


class TestRunQAOA:
    def test_end_to_end_consistency(self) -> None:
        qubo = QUBOModel(
            variables=["a", "b"],
            linear={"a": -3.0, "b": -4.0},
            name="demo_qubo",
        )
        ising = IsingModel.from_qubo(qubo)
        result = run_qaoa(
            ising,
            qubo=qubo,
            num_layers=1,
            shots=32,
            seed=3,
            backend="statevector",
            name="demo",
            optimizer=_fast_optimizer(),
        )
        assert isinstance(result, QaoaExecutionResult)
        assert result.solver == "microquantum/qaoa"
        assert result.algorithm == "qaoa"
        assert result.backend == "statevector"
        assert set(result.assignment) == {"a", "b"}
        assert result.bitstring
        assert result.num_layers == 1
        assert result.shots == 32
        # energies must agree exactly for the sampled assignment
        spins = [1 if result.assignment[v] == 1 else -1 for v in ising.variables]
        assert result.ising_energy == pytest.approx(result.energy)
        assert result.ising_energy == pytest.approx(ising.energy(spins))
        assert result.mq_eigenvalue is not None

    def test_result_round_trip(self) -> None:
        qubo = QUBOModel(variables=["a"], linear={"a": 1.0}, name="q")
        result = run_qaoa(
            IsingModel.from_qubo(qubo),
            qubo=qubo,
            num_layers=1,
            shots=32,
            seed=0,
            backend="statevector",
            optimizer=_fast_optimizer(),
        )
        rebuilt = QaoaExecutionResult.from_dict(result.to_dict())
        assert rebuilt.solver == result.solver
        assert rebuilt.assignment == result.assignment
        assert rebuilt.energy == result.energy
        assert rebuilt.ising_energy == result.ising_energy
        assert rebuilt.backend == result.backend
