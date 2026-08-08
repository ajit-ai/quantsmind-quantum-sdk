"""
Reasoning Package

This package provides reasoning management for the Knowledge package.

Purpose
-------
Provide comprehensive reasoning definitions and operations.

Modules
-------
- reasoner: Base reasoner class
- inference_engine: Inference engine management
- rule_engine: Rule engine management
- explanation_engine: Explanation engine management
- prediction_engine: Prediction engine management
"""

from __future__ import annotations

from quantsmind.knowledge.reasoning.explanation_engine import ExplanationEngine
from quantsmind.knowledge.reasoning.inference_engine import InferenceEngine
from quantsmind.knowledge.reasoning.prediction_engine import PredictionEngine
from quantsmind.knowledge.reasoning.reasoner import Reasoner
from quantsmind.knowledge.reasoning.rule_engine import RuleEngine

__all__ = [
    "Reasoner",
    "InferenceEngine",
    "RuleEngine",
    "ExplanationEngine",
    "PredictionEngine",
]
