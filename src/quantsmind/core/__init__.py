"""
Core Package — Provides the shared abstractions (registries, contexts, base container types)
that concrete domain packages build on top of the foundation ontology.

This package is part of the QuantsMind SDK (R0.1.0).
Architecture-only: no implementations, only public interface surface.

Core Mathematical Framework
---------------------------
Provides the foundational classes for all mathematical objects in the SDK.
"""

from quantsmind.core.equation import Equation
from quantsmind.core.expression import Expression
from quantsmind.core.expression_engine import ExpressionEngine
from quantsmind.core.formula import Formula
from quantsmind.core.math_object import MathObject
from quantsmind.core.parameter import Parameter
from quantsmind.core.variable import Variable

__all__: list[str] = [
    "MathObject",
    "Expression",
    "Formula",
    "Equation",
    "Variable",
    "Parameter",
    "ExpressionEngine",
]
