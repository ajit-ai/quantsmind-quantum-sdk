"""Unit tests for quantsmind.ai_reasoning agents."""

from __future__ import annotations

from quantsmind.ai_reasoning import (
    AlgorithmAdvisor,
    FormulaGenerator,
    MathReasoningAgent,
    ProofAssistant,
)


class TestMathReasoningAgent:
    def test_quadratic_plan(self) -> None:
        result = MathReasoningAgent().reason_about("solve x^2 = 4")
        assert result["problem"] == "solve x^2 = 4"
        assert result["reasoning_steps"][0]["description"] == (
            "Identified problem type: quadratic_equation"
        )
        assert result["confidence"] == 0.8

    def test_history(self) -> None:
        agent = MathReasoningAgent()
        agent.reason_about("x^2 = 4")
        assert len(agent.get_reasoning_history()) == 1
        agent.clear_history()
        assert agent.get_reasoning_history() == []


class TestFormulaGenerator:
    def test_sphere(self) -> None:
        formula = FormulaGenerator()._sphere_formula({"h": 0, "k": 0, "l": 0, "r": 5})
        assert formula == "(x - 0)^2 + (y - 0)^2 + (z - 0)^2 = 5^2"


class TestAlgorithmAdvisor:
    def test_recommendation(self) -> None:
        result = AlgorithmAdvisor().recommend_algorithm("solve_linear_system")
        assert result["recommended_algorithm"]["name"] == "Gaussian Elimination"

    def test_comparison(self) -> None:
        result = AlgorithmAdvisor().compare_algorithms(
            ["Gaussian Elimination", "LU Decomposition"], "solve_linear_system"
        )
        assert result["comparison"]["Gaussian Elimination"]["complexity"] == "O(n^3)"


class TestProofAssistant:
    def test_contradiction_steps(self) -> None:
        steps = ProofAssistant()._generate_proof_steps(
            "proof_by_contradiction", "sqrt(2) is irrational", None
        )
        assert steps
        assert steps[0]["action"] == "assume_opposite"
