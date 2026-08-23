"""
Probability Engine Module

This module provides probability computation functionality for the QuantsMind SDK.

Purpose
-------
Provide probability computation and analysis capabilities.

Classes
-------
ProbabilityEngine: Probability computation engine

Responsibilities
----------------
- Compute probabilities
- Handle conditional probabilities
- Compute joint probabilities
- Support Bayesian inference

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

import math
from typing import Any


class ProbabilityEngine:
    """Probability computation engine.

    This class provides functionality for computing and analyzing probabilities.

    Attributes:
        _name: Engine name
        _events: Event definitions
        _probabilities: Event probabilities
        _metadata: Additional metadata

    Example:
        >>> engine = ProbabilityEngine()
        >>> engine.add_event("A", 0.3)
        >>> prob = engine.compute_probability("A")
    """

    def __init__(
        self,
        name: str = "default",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a ProbabilityEngine.

        Args:
            name: Engine name
            metadata: Additional metadata

        Example:
            >>> engine = ProbabilityEngine()
        """
        self._name = name
        self._events: dict[str, float] = {}
        self._conditional_probs: dict[tuple[str, str], float] = {}
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the engine name.

        Returns:
            Engine name

        Example:
            >>> name = engine.name
        """
        return self._name

    def add_event(self, event: str, probability: float) -> None:
        """Add an event with its probability.

        Args:
            event: Event name
            probability: Event probability

        Example:
            >>> engine.add_event("A", 0.3)
        """
        if probability < 0 or probability > 1:
            raise ValueError("Probability must be between 0 and 1")
        self._events[event] = probability

    def add_conditional_probability(self, event: str, condition: str, probability: float) -> None:
        """Add a conditional probability P(event|condition).

        Args:
            event: Event name
            condition: Condition event
            probability: Conditional probability

        Example:
            >>> engine.add_conditional_probability("A", "B", 0.5)
        """
        if probability < 0 or probability > 1:
            raise ValueError("Probability must be between 0 and 1")
        self._conditional_probs[(event, condition)] = probability

    def compute_probability(self, event: str) -> float:
        """Compute the probability of an event.

        Args:
            event: Event name

        Returns:
            Event probability

        Example:
            >>> prob = engine.compute_probability("A")
        """
        return self._events.get(event, 0.0)

    def conditional_probability(self, event: str, condition: str) -> float:
        """Compute conditional probability P(event|condition).

        Args:
            event: Event name
            condition: Condition event

        Returns:
            Conditional probability

        Example:
            >>> prob = engine.conditional_probability("A", "B")
        """
        return self._conditional_probs.get((event, condition), 0.0)

    def joint_probability(self, *events: str) -> float:
        """Compute joint probability of multiple events.

        Args:
            *events: Event names

        Returns:
            Joint probability

        Example:
            >>> prob = engine.joint_probability("A", "B")
        """
        # Assuming independence for simplicity
        result = 1.0
        for event in events:
            result *= self._events.get(event, 0.0)
        return result

    def bayes_theorem(self, event: str, condition: str) -> float:
        """Apply Bayes' theorem: P(condition|event) = P(event|condition) * P(condition) / P(event).

        Args:
            event: Event name
            condition: Condition event

        Returns:
            Posterior probability

        Example:
            >>> prob = engine.bayes_theorem("A", "B")
        """
        p_event_given_condition = self.conditional_probability(event, condition)
        p_condition = self._events.get(condition, 0.0)
        p_event = self._events.get(event, 0.0)

        if p_event == 0:
            raise ValueError("P(event) cannot be zero for Bayes' theorem")

        return (p_event_given_condition * p_condition) / p_event

    def complement(self, event: str) -> float:
        """Compute the complement probability P(not event).

        Args:
            event: Event name

        Returns:
            Complement probability

        Example:
            >>> prob = engine.complement("A")
        """
        return 1.0 - self._events.get(event, 0.0)

    def union(self, *events: str) -> float:
        """Compute union probability P(A or B or ...).

        Args:
            *events: Event names

        Returns:
            Union probability

        Example:
            >>> prob = engine.union("A", "B")
        """
        if len(events) == 1:
            return self._events.get(events[0], 0.0)
        elif len(events) == 2:
            # P(A or B) = P(A) + P(B) - P(A and B)
            p_a = self._events.get(events[0], 0.0)
            p_b = self._events.get(events[1], 0.0)
            p_a_and_b = self.joint_probability(events[0], events[1])
            return p_a + p_b - p_a_and_b
        else:
            # Inclusion-exclusion principle (simplified)
            result = sum(self._events.get(e, 0.0) for e in events)
            # Subtract pairwise intersections
            for i in range(len(events)):
                for j in range(i + 1, len(events)):
                    result -= self.joint_probability(events[i], events[j])
            return max(0.0, result)

    def intersection(self, *events: str) -> float:
        """Compute intersection probability P(A and B and ...).

        Args:
            *events: Event names

        Returns:
            Intersection probability

        Example:
            >>> prob = engine.intersection("A", "B")
        """
        return self.joint_probability(*events)

    def expected_value(self, outcomes: list[float], probabilities: list[float]) -> float:
        """Compute expected value.

        Args:
            outcomes: Possible outcomes
            probabilities: Corresponding probabilities

        Returns:
            Expected value

        Example:
            >>> ev = engine.expected_value([1, 2, 3], [0.3, 0.5, 0.2])
        """
        if len(outcomes) != len(probabilities):
            raise ValueError("Outcomes and probabilities must have same length")

        if abs(sum(probabilities) - 1.0) > 1e-6:
            raise ValueError("Probabilities must sum to 1")

        return sum(o * p for o, p in zip(outcomes, probabilities, strict=False))

    def variance(self, outcomes: list[float], probabilities: list[float]) -> float:
        """Compute variance.

        Args:
            outcomes: Possible outcomes
            probabilities: Corresponding probabilities

        Returns:
            Variance

        Example:
            >>> var = engine.variance([1, 2, 3], [0.3, 0.5, 0.2])
        """
        ev = self.expected_value(outcomes, probabilities)
        return sum(p * (o - ev) ** 2 for o, p in zip(outcomes, probabilities, strict=False))

    def standard_deviation(self, outcomes: list[float], probabilities: list[float]) -> float:
        """Compute standard deviation.

        Args:
            outcomes: Possible outcomes
            probabilities: Corresponding probabilities

        Returns:
            Standard deviation

        Example:
            >>> std = engine.standard_deviation([1, 2, 3], [0.3, 0.5, 0.2])
        """
        return math.sqrt(self.variance(outcomes, probabilities))

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(engine)
        """
        return f"ProbabilityEngine(name={self._name}, events={len(self._events)})"


__all__ = [
    "ProbabilityEngine",
]
