"""
AI Reasoning Package

This package provides AI-assisted mathematical reasoning functionality for the QuantsMind SDK.

Purpose
-------
Provide AI-powered mathematical reasoning capabilities including formula generation,
proof assistance, and algorithm recommendations.

Modules
-------
- math_reasoning_agent: Mathematical reasoning agent
- formula_generator: Formula generation engine
- proof_assistant: Proof assistance engine
- algorithm_advisor: Algorithm recommendation engine
"""

from __future__ import annotations

from quantsmind.ai_reasoning.algorithm_advisor import AlgorithmAdvisor
from quantsmind.ai_reasoning.formula_generator import FormulaGenerator
from quantsmind.ai_reasoning.math_reasoning_agent import MathReasoningAgent
from quantsmind.ai_reasoning.proof_assistant import ProofAssistant

__all__: list[str] = [
    "MathReasoningAgent",
    "FormulaGenerator",
    "ProofAssistant",
    "AlgorithmAdvisor",
]
