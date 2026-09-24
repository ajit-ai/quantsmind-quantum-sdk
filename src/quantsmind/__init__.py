"""
QuantsMind SDK

A comprehensive mathematical intelligence SDK for scientific computing, optimization,
statistics, machine learning mathematics, financial mathematics, quantum mathematics,
AI-assisted reasoning, and simulation.

Version: 1.1.0

This package uses lazy attribute access (PEP 562): no subpackage is imported until
one of its public names is first accessed. This keeps ``import quantsmind`` fast
and dependency-free — optional integrations such as ``quantsmind.api`` only require
their third-party dependencies when actually used.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

__version__ = "1.1.0"

if TYPE_CHECKING:  # pragma: no cover - static-analysis surface only
    from quantsmind.ai_reasoning import (
        AlgorithmAdvisor,
        FormulaGenerator,
        MathReasoningAgent,
        ProofAssistant,
    )
    from quantsmind.algebra import (
        Matrix,
        Polynomial,
        PolynomialSolver,
        SparseMatrix,
        Tensor,
        Vector,
    )
    from quantsmind.api import (
        APIResponse,
        HealthResponse,
        MatrixEndpoints,
        MatrixRequest,
        OptimizationEndpoints,
        OptimizationRequest,
        PolynomialEndpoints,
        PolynomialRequest,
        SimulationEndpoints,
        SimulationRequest,
    )
    from quantsmind.calculus import Differentiator, Integrator, ODESolver
    from quantsmind.core import (
        Equation,
        Expression,
        ExpressionEngine,
        Formula,
        MathObject,
        Parameter,
        Variable,
    )
    from quantsmind.finance.math import (
        MonteCarloFinanceSimulator,
        OptionPricer,
        PortfolioMath,
        RiskEngine,
    )
    from quantsmind.ml_math import (
        ActivationFunction,
        CrossEntropyLoss,
        FeatureTransformer,
        HingeLoss,
        HuberLoss,
        LeakyReLU,
        LossFunction,
        MAELoss,
        MSELoss,
        Normalization,
        OneHotEncoder,
        PolynomialFeatures,
        ReLU,
        Sigmoid,
        Softmax,
        Standardization,
        Tanh,
    )
    from quantsmind.optimization import (
        AdamOptimizer,
        BayesianOptimizer,
        EvolutionaryOptimizer,
        GeneticAlgorithm,
        GradientDescent,
        GradientOptimizer,
        LBFGSOptimizer,
        NewtonMethod,
        ParticleSwarmOptimizer,
        SimulatedAnnealing,
    )

    # Quantum integration layer
    from quantsmind.quantum import (
        GateSpec,
        QuantumExperiment,
        QuantumProgram,
        QuantumResult,
        available_algorithms,
        build_circuit,
        run_algorithm,
    )
    from quantsmind.simulation import Experiment, SimulationEngine, SimulationResult, Simulator
    from quantsmind.statistics import (
        BetaDistribution,
        BinomialDistribution,
        DistributionEngine,
        ExponentialDistribution,
        GammaDistribution,
        NormalDistribution,
        PoissonDistribution,
        ProbabilityEngine,
        StatisticalAnalyzer,
    )
    from quantsmind.visualization import Plotter

# Public name -> (source module, attribute). Resolved lazily on first access.
_LAZY_ATTRS: dict[str, tuple[str, str]] = {
    # Core
    "MathObject": ("quantsmind.core", "MathObject"),
    "Expression": ("quantsmind.core", "Expression"),
    "Formula": ("quantsmind.core", "Formula"),
    "Equation": ("quantsmind.core", "Equation"),
    "Variable": ("quantsmind.core", "Variable"),
    "Parameter": ("quantsmind.core", "Parameter"),
    "ExpressionEngine": ("quantsmind.core", "ExpressionEngine"),
    # Algebra
    "Polynomial": ("quantsmind.algebra", "Polynomial"),
    "PolynomialSolver": ("quantsmind.algebra", "PolynomialSolver"),
    "Matrix": ("quantsmind.algebra", "Matrix"),
    "Vector": ("quantsmind.algebra", "Vector"),
    "Tensor": ("quantsmind.algebra", "Tensor"),
    "SparseMatrix": ("quantsmind.algebra", "SparseMatrix"),
    # Calculus
    "Differentiator": ("quantsmind.calculus", "Differentiator"),
    "Integrator": ("quantsmind.calculus", "Integrator"),
    "ODESolver": ("quantsmind.calculus", "ODESolver"),
    # Optimization
    "GradientOptimizer": ("quantsmind.optimization", "GradientOptimizer"),
    "GradientDescent": ("quantsmind.optimization", "GradientDescent"),
    "AdamOptimizer": ("quantsmind.optimization", "AdamOptimizer"),
    "NewtonMethod": ("quantsmind.optimization", "NewtonMethod"),
    "EvolutionaryOptimizer": ("quantsmind.optimization", "EvolutionaryOptimizer"),
    "GeneticAlgorithm": ("quantsmind.optimization", "GeneticAlgorithm"),
    "ParticleSwarmOptimizer": ("quantsmind.optimization", "ParticleSwarmOptimizer"),
    "LBFGSOptimizer": ("quantsmind.optimization", "LBFGSOptimizer"),
    "BayesianOptimizer": ("quantsmind.optimization", "BayesianOptimizer"),
    "SimulatedAnnealing": ("quantsmind.optimization", "SimulatedAnnealing"),
    # Numerical (function groups exposed by quantsmind.numerical)
    "root_finding": ("quantsmind.numerical", "root_finding"),
    "interpolation": ("quantsmind.numerical", "interpolation"),
    "extrapolation": ("quantsmind.numerical", "extrapolation"),
    "curve_fit": ("quantsmind.numerical", "curve_fit"),
    "approximation": ("quantsmind.numerical", "approximation"),
    "error_analysis": ("quantsmind.numerical", "error_analysis"),
    # Statistics
    "ProbabilityEngine": ("quantsmind.statistics", "ProbabilityEngine"),
    "StatisticalAnalyzer": ("quantsmind.statistics", "StatisticalAnalyzer"),
    "DistributionEngine": ("quantsmind.statistics", "DistributionEngine"),
    "NormalDistribution": ("quantsmind.statistics", "NormalDistribution"),
    "BinomialDistribution": ("quantsmind.statistics", "BinomialDistribution"),
    "PoissonDistribution": ("quantsmind.statistics", "PoissonDistribution"),
    "GammaDistribution": ("quantsmind.statistics", "GammaDistribution"),
    "BetaDistribution": ("quantsmind.statistics", "BetaDistribution"),
    "ExponentialDistribution": ("quantsmind.statistics", "ExponentialDistribution"),
    # ML math
    "LossFunction": ("quantsmind.ml_math", "LossFunction"),
    "MSELoss": ("quantsmind.ml_math", "MSELoss"),
    "MAELoss": ("quantsmind.ml_math", "MAELoss"),
    "CrossEntropyLoss": ("quantsmind.ml_math", "CrossEntropyLoss"),
    "HingeLoss": ("quantsmind.ml_math", "HingeLoss"),
    "HuberLoss": ("quantsmind.ml_math", "HuberLoss"),
    "ActivationFunction": ("quantsmind.ml_math", "ActivationFunction"),
    "ReLU": ("quantsmind.ml_math", "ReLU"),
    "Sigmoid": ("quantsmind.ml_math", "Sigmoid"),
    "Tanh": ("quantsmind.ml_math", "Tanh"),
    "Softmax": ("quantsmind.ml_math", "Softmax"),
    "LeakyReLU": ("quantsmind.ml_math", "LeakyReLU"),
    "FeatureTransformer": ("quantsmind.ml_math", "FeatureTransformer"),
    "Normalization": ("quantsmind.ml_math", "Normalization"),
    "Standardization": ("quantsmind.ml_math", "Standardization"),
    "OneHotEncoder": ("quantsmind.ml_math", "OneHotEncoder"),
    "PolynomialFeatures": ("quantsmind.ml_math", "PolynomialFeatures"),
    # Finance
    "PortfolioMath": ("quantsmind.finance.math", "PortfolioMath"),
    "RiskEngine": ("quantsmind.finance.math", "RiskEngine"),
    "OptionPricer": ("quantsmind.finance.math", "OptionPricer"),
    "MonteCarloFinanceSimulator": ("quantsmind.finance.math", "MonteCarloFinanceSimulator"),
    # Quantum integration layer
    "GateSpec": ("quantsmind.quantum", "GateSpec"),
    "QuantumProgram": ("quantsmind.quantum", "QuantumProgram"),
    "QuantumResult": ("quantsmind.quantum", "QuantumResult"),
    "QuantumExperiment": ("quantsmind.quantum", "QuantumExperiment"),
    # AI reasoning
    "MathReasoningAgent": ("quantsmind.ai_reasoning", "MathReasoningAgent"),
    "FormulaGenerator": ("quantsmind.ai_reasoning", "FormulaGenerator"),
    "ProofAssistant": ("quantsmind.ai_reasoning", "ProofAssistant"),
    "AlgorithmAdvisor": ("quantsmind.ai_reasoning", "AlgorithmAdvisor"),
    # Simulation
    "SimulationEngine": ("quantsmind.simulation", "SimulationEngine"),
    "Simulator": ("quantsmind.simulation", "Simulator"),
    "SimulationResult": ("quantsmind.simulation", "SimulationResult"),
    "Experiment": ("quantsmind.simulation", "Experiment"),
    # Visualization
    "Plotter": ("quantsmind.visualization", "Plotter"),
    # API (requires the optional ``api`` extra: pydantic)
    "PolynomialRequest": ("quantsmind.api", "PolynomialRequest"),
    "MatrixRequest": ("quantsmind.api", "MatrixRequest"),
    "OptimizationRequest": ("quantsmind.api", "OptimizationRequest"),
    "SimulationRequest": ("quantsmind.api", "SimulationRequest"),
    "APIResponse": ("quantsmind.api", "APIResponse"),
    "HealthResponse": ("quantsmind.api", "HealthResponse"),
    "router": ("quantsmind.api", "router"),
    "PolynomialEndpoints": ("quantsmind.api", "PolynomialEndpoints"),
    "MatrixEndpoints": ("quantsmind.api", "MatrixEndpoints"),
    "OptimizationEndpoints": ("quantsmind.api", "OptimizationEndpoints"),
    "SimulationEndpoints": ("quantsmind.api", "SimulationEndpoints"),
    # Utils
    "validate_type": ("quantsmind.utils", "validate_type"),
    "clamp": ("quantsmind.utils", "clamp"),
    "safe_division": ("quantsmind.utils", "safe_division"),
    "format_number": ("quantsmind.utils", "format_number"),
    "is_close": ("quantsmind.utils", "is_close"),
    "chunk_list": ("quantsmind.utils", "chunk_list"),
    "flatten_list": ("quantsmind.utils", "flatten_list"),
    "unique_preserve_order": ("quantsmind.utils", "unique_preserve_order"),
}

__all__ = [
    "__version__",
    *_LAZY_ATTRS,
]


def __getattr__(name: str) -> Any:
    """Resolve public names lazily (PEP 562).

    Args:
        name: Public attribute name listed in ``_LAZY_ATTRS``.

    Returns:
        The resolved object from its source subpackage.

    Raises:
        AttributeError: If ``name`` is not part of the public surface.
    """
    target = _LAZY_ATTRS.get(name)
    if target is None:
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)
    import importlib

    module_name, attr_name = target
    value = getattr(importlib.import_module(module_name), attr_name)
    globals()[name] = value  # cache so subsequent lookups skip resolution
    return value


def __dir__() -> list[str]:
    """Expose lazy names to :func:`dir` and IDE completion."""
    return sorted({*globals(), *_LAZY_ATTRS})
