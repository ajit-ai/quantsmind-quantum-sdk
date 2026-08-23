"""
QuantsMind SDK

A comprehensive mathematical intelligence SDK for scientific computing, optimization,
statistics, machine learning mathematics, financial mathematics, quantum mathematics,
AI-assisted reasoning, and simulation.

Version: R0.2.0
"""

from __future__ import annotations

__version__ = "R0.2.0"

# Core mathematical framework
# AI mathematical reasoning engine
from quantsmind.ai_reasoning import (
    AlgorithmAdvisor,
    FormulaGenerator,
    MathReasoningAgent,
    ProofAssistant,
)

# Algebra engine
from quantsmind.algebra import Matrix, Polynomial, PolynomialSolver, SparseMatrix, Tensor, Vector

# API layer
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
    router,
)

# Calculus engine
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

# Financial mathematics engine
from quantsmind.finance.math import (
    MonteCarloFinanceSimulator,
    OptionPricer,
    PortfolioMath,
    RiskEngine,
)

# Machine learning mathematics engine
from quantsmind.ml_math import (
    ActivationFunction,
    FeatureTransformer,
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

# Numerical computing engine
from quantsmind.numerical import (
    approximation,
    curve_fit,
    error_analysis,
    extrapolation,
    interpolation,
    root_finding,
)

# Optimization framework
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

# Quantum mathematics engine
from quantsmind.quantum.math import QuantumMatrix, QuantumOperatorMath, QuantumStateMath

# Simulation framework
from quantsmind.simulation import Experiment, SimulationEngine, SimulationResult, Simulator

# Statistics and probability engine
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

# Utils
from quantsmind.utils import (
    chunk_list,
    clamp,
    flatten_list,
    format_number,
    is_close,
    safe_division,
    unique_preserve_order,
    validate_type,
)

# Visualization
from quantsmind.visualization import Plotter

__all__ = [
    "__version__",
    # Core
    "MathObject",
    "Expression",
    "Formula",
    "Equation",
    "Variable",
    "Parameter",
    "ExpressionEngine",
    # Algebra
    "Polynomial",
    "PolynomialSolver",
    "Matrix",
    "Vector",
    "Tensor",
    "SparseMatrix",
    # Calculus
    "Differentiator",
    "Integrator",
    "ODESolver",
    # Optimization
    "GradientOptimizer",
    "GradientDescent",
    "AdamOptimizer",
    "NewtonMethod",
    "EvolutionaryOptimizer",
    "GeneticAlgorithm",
    "ParticleSwarmOptimizer",
    "LBFGSOptimizer",
    "BayesianOptimizer",
    "SimulatedAnnealing",
    # Numerical
    "root_finding",
    "interpolation",
    "extrapolation",
    "curve_fit",
    "approximation",
    "error_analysis",
    # Statistics
    "ProbabilityEngine",
    "StatisticalAnalyzer",
    "DistributionEngine",
    "NormalDistribution",
    "BinomialDistribution",
    "PoissonDistribution",
    "GammaDistribution",
    "BetaDistribution",
    "ExponentialDistribution",
    # ML Math
    "LossFunction",
    "MSELoss",
    "MAELoss",
    "CrossEntropyLoss",
    "HingeLoss",
    "HuberLoss",
    "ActivationFunction",
    "ReLU",
    "Sigmoid",
    "Tanh",
    "Softmax",
    "LeakyReLU",
    "FeatureTransformer",
    "Normalization",
    "Standardization",
    "OneHotEncoder",
    "PolynomialFeatures",
    # Finance
    "PortfolioMath",
    "RiskEngine",
    "OptionPricer",
    "MonteCarloFinanceSimulator",
    # Quantum Math
    "QuantumMatrix",
    "QuantumStateMath",
    "QuantumOperatorMath",
    # AI Reasoning
    "MathReasoningAgent",
    "FormulaGenerator",
    "ProofAssistant",
    "AlgorithmAdvisor",
    # Simulation
    "SimulationEngine",
    "Simulator",
    "SimulationResult",
    "Experiment",
    # Visualization
    "Plotter",
    # API
    "PolynomialRequest",
    "MatrixRequest",
    "OptimizationRequest",
    "SimulationRequest",
    "APIResponse",
    "HealthResponse",
    "router",
    "PolynomialEndpoints",
    "MatrixEndpoints",
    "OptimizationEndpoints",
    "SimulationEndpoints",
    # Utils
    "validate_type",
    "clamp",
    "safe_division",
    "format_number",
    "is_close",
    "chunk_list",
    "flatten_list",
    "unique_preserve_order",
]
