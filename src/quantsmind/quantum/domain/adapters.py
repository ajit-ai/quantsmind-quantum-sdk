"""Built-in domain bindings (QMQ-11 §10).

Each binding ties one domain to its existing formulation adapter and
optimizer through a common :class:`DomainBinding` surface.  The bindings are
imported and registered by :class:`DomainRegistry` on construction; new
domains build their own bindings with the same public API and register them
through :meth:`DomainRegistry.register` — no core change required.
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.domain.registry import DomainBinding, DomainKind

__all__ = [
    "finance_binding",
    "portfolio_binding",
    "data_binding",
    "ml_binding",
    "default_bindings",
]


def _finance_adapter() -> Any:
    from quantsmind.quantum.finance.formulation import FinanceFormulationAdapter

    return FinanceFormulationAdapter()


def _portfolio_adapter() -> Any:
    from quantsmind.quantum.finance.portfolio import PortfolioFormulationAdapter

    return PortfolioFormulationAdapter()


def _data_adapter() -> Any:
    from quantsmind.quantum.data.formulation import DataFormulationAdapter

    return DataFormulationAdapter()


def _ml_adapter() -> Any:
    from quantsmind.quantum.ml.formulation import MLFormulationAdapter

    return MLFormulationAdapter()


def finance_binding() -> DomainBinding:
    """Binding for :class:`~quantsmind.quantum.finance.models.FinancialProblem`
    through the Finance adapter and optimizer (QMQ-11 Example A)."""
    from quantsmind.quantum.finance.models import FinancialProblem
    from quantsmind.quantum.finance.optimizer import FinanceOptimizer

    adapter = _finance_adapter()

    def solve(
        problem: Any,
        *,
        strategy: str | None = None,
        config: Any | None = None,
        seed: int | None = None,
    ) -> Any:
        return FinanceOptimizer(default_seed=seed).solve(problem, strategy=strategy, config=config)

    def benchmark(
        problem: Any,
        *,
        strategy: str | None = None,
        known_optimum: float | None = None,
        runs: int = 1,
        raise_on_error: bool = False,
        config: Any | None = None,
        seed: int | None = None,
    ) -> Any:
        return FinanceOptimizer(default_seed=seed).benchmark(
            problem,
            strategy=strategy,
            known_optimum=known_optimum,
            runs=runs,
            raise_on_error=raise_on_error,
            config=config,
        )

    return DomainBinding(
        kind=DomainKind.FINANCE,
        label="finance",
        problem_types=(FinancialProblem,),
        validate=adapter.validate,
        raise_if_invalid=adapter.raise_if_invalid,
        to_quantum_problem=adapter.to_quantum_problem,
        solve=solve,
        benchmark=benchmark,
        description=(
            "FinancialProblem selection/allocation through the Finance "
            "adapter (QMQ-07) and Finance optimizer (QMQ-11)."
        ),
        metadata={"module": "quantsmind.quantum.domain.adapters"},
    )


def portfolio_binding() -> DomainBinding:
    """Binding for :class:`~quantsmind.quantum.finance.portfolio
    .PortfolioOptimizationProblem` (QMQ-08)."""
    from quantsmind.quantum.finance.portfolio import (
        PortfolioOptimizationProblem,
        PortfolioOptimizer,
    )

    adapter = _portfolio_adapter()

    def solve(
        problem: Any,
        *,
        strategy: str | None = None,
        config: Any | None = None,
        seed: int | None = None,
    ) -> Any:
        return PortfolioOptimizer(default_seed=seed).solve(problem, strategy=strategy)

    def benchmark(
        problem: Any,
        *,
        strategy: str | None = None,
        known_optimum: float | None = None,
        runs: int = 1,
        raise_on_error: bool = False,
        config: Any | None = None,
        seed: int | None = None,
    ) -> Any:
        return PortfolioOptimizer(default_seed=seed).benchmark(
            problem,
            strategy=strategy,
            known_optimum=known_optimum,
            runs=runs,
            raise_on_error=raise_on_error,
        )

    return DomainBinding(
        kind=DomainKind.PORTFOLIO,
        label="portfolio",
        problem_types=(PortfolioOptimizationProblem,),
        validate=adapter.validate,
        raise_if_invalid=adapter.raise_if_invalid,
        to_quantum_problem=adapter.to_quantum_problem,
        solve=solve,
        benchmark=benchmark,
        description=(
            "PortfolioOptimizationProblem through the Finance adapter "
            "(QMQ-07) and Portfolio optimizer (QMQ-08)."
        ),
        metadata={"module": "quantsmind.quantum.domain.adapters"},
    )


def data_binding() -> DomainBinding:
    """Binding for :class:`~quantsmind.quantum.data.problem.DataProblem` (QMQ-09)."""
    from quantsmind.quantum.data.optimizer import DataOptimizer
    from quantsmind.quantum.data.problem import DataProblem

    adapter = _data_adapter()

    def solve(
        problem: Any,
        *,
        strategy: str | None = None,
        config: Any | None = None,
        seed: int | None = None,
    ) -> Any:
        return DataOptimizer(default_seed=seed).solve(problem, strategy=strategy, config=config)

    def benchmark(
        problem: Any,
        *,
        strategy: str | None = None,
        known_optimum: float | None = None,
        runs: int = 1,
        raise_on_error: bool = False,
        config: Any | None = None,
        seed: int | None = None,
    ) -> Any:
        return DataOptimizer(default_seed=seed).benchmark(
            problem,
            strategy=strategy,
            known_optimum=known_optimum,
            runs=runs,
            raise_on_error=raise_on_error,
            config=config,
        )

    return DomainBinding(
        kind=DomainKind.DATA,
        label="data",
        problem_types=(DataProblem,),
        validate=adapter.validate,
        raise_if_invalid=adapter.raise_if_invalid,
        to_quantum_problem=adapter.to_quantum_problem,
        solve=solve,
        benchmark=benchmark,
        description="DataProblem through the Data adapter and optimizer (QMQ-09).",
        metadata={"module": "quantsmind.quantum.domain.adapters"},
    )


def ml_binding() -> DomainBinding:
    """Binding for :class:`~quantsmind.quantum.ml.problem.MLProblem` (QMQ-10)."""
    from quantsmind.quantum.ml.optimizer import MLOptimizer
    from quantsmind.quantum.ml.problem import MLProblem

    adapter = _ml_adapter()

    def solve(
        problem: Any,
        *,
        strategy: str | None = None,
        config: Any | None = None,
        seed: int | None = None,
    ) -> Any:
        return MLOptimizer(default_seed=seed).solve(problem, strategy=strategy, config=config)

    def benchmark(
        problem: Any,
        *,
        strategy: str | None = None,
        known_optimum: float | None = None,
        runs: int = 1,
        raise_on_error: bool = False,
        config: Any | None = None,
        seed: int | None = None,
    ) -> Any:
        return MLOptimizer(default_seed=seed).benchmark(
            problem,
            strategy=strategy,
            known_optimum=known_optimum,
            runs=runs,
            raise_on_error=raise_on_error,
            config=config,
        )

    return DomainBinding(
        kind=DomainKind.ML,
        label="ml",
        problem_types=(MLProblem,),
        validate=adapter.validate,
        raise_if_invalid=adapter.raise_if_invalid,
        to_quantum_problem=adapter.to_quantum_problem,
        solve=solve,
        benchmark=benchmark,
        description=(
            "MLProblem through the ML adapter and optimizer, including "
            "delegated solves through QMQ-09 (QMQ-10)."
        ),
        metadata={"module": "quantsmind.quantum.domain.adapters"},
    )


def default_bindings() -> list[DomainBinding]:
    """The four built-in domain bindings in dispatch priority order."""
    return [
        finance_binding(),
        portfolio_binding(),
        data_binding(),
        ml_binding(),
    ]
