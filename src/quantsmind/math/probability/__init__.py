"""
Probability Module

This module provides probability theory operations for the Mathematics package.
Probability represents random events, random variables, and probability distributions.

Purpose
-------
Provide probability theory operations for the Mathematics package.

Scientific Meaning
------------------
Probability theory represents the study of uncertainty and randomness, essential for
quantum mechanics, statistical mechanics, machine learning, and many other scientific applications.

Responsibilities
----------------
- Support probability calculations
- Enable random variable operations
- Support distribution operations
- Handle probability validation

Dependencies
------------
typing (standard library)
quantsmind.math.exceptions (exception hierarchy)
quantsmind.math.types (type definitions)
quantsmind.math.validation (validation functions)

Future Extensions
-----------------
- Bayesian inference
- Markov chains
- Stochastic processes
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, Dict, List, Optional, Union

from quantsmind.math.exceptions import ProbabilityError
from quantsmind.math.types import Scalar
from quantsmind.math.validation import validate_probability

logger = logging.getLogger(__name__)


class Probability:
    """Concrete implementation of a probability value.

    This class provides a probability value with validation and common operations.

    Scientific Meaning
    ------------------
    In probability theory, probability represents the likelihood of an event occurring,
    ranging from 0 (impossible) to 1 (certain).

    Attributes:
        _value: Probability value

    Example:
        >>> p = Probability(0.5)
        >>> print(f"Value: {p.value}")
    """

    def __init__(self, value: float) -> None:
        """Initialize a Probability.

        Args:
            value: Probability value (must be in [0, 1])

        Raises:
            ProbabilityError: If value is outside [0, 1]

        Example:
            >>> p = Probability(0.5)
        """
        is_valid, errors = validate_probability(value)
        if not is_valid:
            raise ProbabilityError(f"Invalid probability: {errors}")
        self._value = value
        logger.debug(f"Created probability: {value}")

    @property
    def value(self) -> float:
        """Get the probability value.

        Returns:
            Probability value

        Example:
            >>> print(f"Value: {probability.value}")
        """
        return self._value

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(probability)
        """
        return f"Probability({self._value})"

    def __str__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> str(probability)
        """
        return f"{self._value}"

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> p1 == p2
        """
        if isinstance(other, Probability):
            return self._value == other._value
        return False

    def __hash__(self) -> int:
        """Return hash.

        Returns:
            Hash value

        Example:
            >>> hash(probability)
        """
        return hash(self._value)

    def __add__(self, other: Probability | float) -> Probability:
        """Add probabilities.

        Args:
            other: Other probability or float

        Returns:
            Sum probability

        Raises:
            ProbabilityError: If result is outside [0, 1]

        Example:
            >>> result = p1 + p2
        """
        if isinstance(other, Probability):
            value = self._value + other._value
        else:
            value = self._value + other
        return Probability(value)

    def __sub__(self, other: Probability | float) -> Probability:
        """Subtract probabilities.

        Args:
            other: Other probability or float

        Returns:
            Difference probability

        Raises:
            ProbabilityError: If result is outside [0, 1]

        Example:
            >>> result = p1 - p2
        """
        if isinstance(other, Probability):
            value = self._value - other._value
        else:
            value = self._value - other
        return Probability(value)

    def __mul__(self, other: Probability | float) -> Probability:
        """Multiply probabilities.

        Args:
            other: Other probability or float

        Returns:
            Product probability

        Raises:
            ProbabilityError: If result is outside [0, 1]

        Example:
            >>> result = p1 * p2
        """
        if isinstance(other, Probability):
            value = self._value * other._value
        else:
            value = self._value * other
        return Probability(value)

    def complement(self) -> Probability:
        """Get the complement probability (1 - p).

        Returns:
            Complement probability

        Example:
            >>> complement = p.complement()
        """
        return Probability(1.0 - self._value)

    def to_float(self) -> float:
        """Convert to float.

        Returns:
            Float value

        Example:
            >>> value = p.to_float()
        """
        return self._value


class Event:
    """Concrete implementation of a probability event.

    This class represents an event in a probability space.

    Scientific Meaning
    ------------------
    In probability theory, an event is a set of outcomes to which a probability is assigned.

    Attributes:
        _name: Event name
        _probability: Event probability

    Example:
        >>> event = Event("heads", 0.5)
    """

    def __init__(self, name: str, probability: float) -> None:
        """Initialize an Event.

        Args:
            name: Event name
            probability: Event probability

        Example:
            >>> event = Event("heads", 0.5)
        """
        self._name = name
        self._probability = Probability(probability)

    @property
    def name(self) -> str:
        """Get the event name.

        Returns:
            Event name

        Example:
            >>> print(f"Name: {event.name}")
        """
        return self._name

    @property
    def probability(self) -> Probability:
        """Get the event probability.

        Returns:
            Event probability

        Example:
            >>> print(f"Probability: {event.probability}")
        """
        return self._probability

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(event)
        """
        return f"Event({self._name}, {self._probability})"

    def __str__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> str(event)
        """
        return f"{self._name}: {self._probability}"


class RandomVariable:
    """Concrete implementation of a random variable.

    This class represents a random variable mapping outcomes to numerical values.

    Scientific Meaning
    ------------------
    In probability theory, a random variable is a function that assigns a numerical
    value to each outcome in a probability space.

    Attributes:
        _name: Variable name
        _values: Possible values
        _probabilities: Associated probabilities

    Example:
        >>> rv = RandomVariable("X", [1, 2, 3], [0.2, 0.5, 0.3])
    """

    def __init__(self, name: str, values: list[Scalar], probabilities: list[float]) -> None:
        """Initialize a RandomVariable.

        Args:
            name: Variable name
            values: Possible values
            probabilities: Associated probabilities

        Raises:
            ProbabilityError: If probabilities are invalid

        Example:
            >>> rv = RandomVariable("X", [1, 2, 3], [0.2, 0.5, 0.3])
        """
        if len(values) != len(probabilities):
            raise ProbabilityError("Values and probabilities must have same length")

        if abs(sum(probabilities) - 1.0) > 1e-10:
            raise ProbabilityError("Probabilities must sum to 1")

        self._name = name
        self._values = values.copy()
        self._probabilities = [Probability(p) for p in probabilities]

    @property
    def name(self) -> str:
        """Get the variable name.

        Returns:
            Variable name

        Example:
            >>> print(f"Name: {rv.name}")
        """
        return self._name

    @property
    def values(self) -> list[Scalar]:
        """Get the possible values.

        Returns:
            List of values

        Example:
            >>> print(f"Values: {rv.values}")
        """
        return self._values.copy()

    @property
    def probabilities(self) -> list[Probability]:
        """Get the associated probabilities.

        Returns:
            List of probabilities

        Example:
            >>> print(f"Probabilities: {rv.probabilities}")
        """
        return self._probabilities.copy()

    def expected_value(self) -> float:
        """Calculate the expected value.

        Returns:
            Expected value

        Example:
            >>> ev = rv.expected_value()
        """
        return sum(v * p.value for v, p in zip(self._values, self._probabilities, strict=False))

    def variance(self) -> float:
        """Calculate the variance.

        Returns:
            Variance

        Example:
            >>> var = rv.variance()
        """
        ev = self.expected_value()
        return sum(p.value * (v - ev) ** 2 for v, p in zip(self._values, self._probabilities, strict=False))

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> rv
        """
        return f"RandomVariable({self._name})"


class Distribution:
    """Base class for probability distributions.

    This class provides a base for all probability distributions.

    Example:
        >>> class NormalDistribution(Distribution):
        ...     def pdf(self, x: float) -> float:
        ...         # Implementation
        ...         pass
    """

    def __init__(self, name: str) -> None:
        """Initialize a Distribution.

        Args:
            name: Distribution name

        Example:
            >>> dist = Distribution("normal")
        """
        self._name = name

    @property
    def name(self) -> str:
        """Get the distribution name.

        Returns:
            Distribution name

        Example:
            >>> print(f"Name: {dist.name}")
        """
        return self._name

    def pdf(self, x: float) -> float:
        """Calculate probability density function.

        Args:
            x: Value

        Returns:
            PDF value

        Raises:
            NotImplementedError: If not implemented by subclass

        Example:
            >>> pdf = dist.pdf(0.0)
        """
        raise NotImplementedError("Subclasses must implement pdf method")

    def cdf(self, x: float) -> float:
        """Calculate cumulative distribution function.

        Args:
            x: Value

        Returns:
            CDF value

        Raises:
            NotImplementedError: If not implemented by subclass

        Example:
            >>> cdf = dist.cdf(0.0)
        """
        raise NotImplementedError("Subclasses must implement cdf method")


class ConditionalProbability:
    """Concrete implementation of conditional probability.

    This class represents P(A|B), the probability of A given B.

    Scientific Meaning
    ------------------
    In probability theory, conditional probability represents the probability of an
    event given that another event has occurred.

    Attributes:
        _p_a: Probability of A
        _p_b: Probability of B
        _p_a_given_b: Conditional probability P(A|B)

    Example:
        >>> cp = ConditionalProbability(0.5, 0.6, 0.3)
    """

    def __init__(self, p_a: float, p_b: float, p_a_given_b: float) -> None:
        """Initialize a ConditionalProbability.

        Args:
            p_a: Probability of A
            p_b: Probability of B
            p_a_given_b: Conditional probability P(A|B)

        Example:
            >>> cp = ConditionalProbability(0.5, 0.6, 0.3)
        """
        self._p_a = Probability(p_a)
        self._p_b = Probability(p_b)
        self._p_a_given_b = Probability(p_a_given_b)

    @property
    def p_a(self) -> Probability:
        """Get P(A).

        Returns:
            Probability of A

        Example:
            >>> print(f"P(A): {cp.p_a}")
        """
        return self._p_a

    @property
    def p_b(self) -> Probability:
        """Get P(B).

        Returns:
            Probability of B

        Example:
            >>> print(f"P(B): {cp.p_b}")
        """
        return self._p_b

    @property
    def p_a_given_b(self) -> Probability:
        """Get P(A|B).

        Returns:
            Conditional probability

        Example:
            >>> print(f"P(A|B): {cp.p_a_given_b}")
        """
        return self._p_a_given_b

    def p_b_given_a(self) -> Probability:
        """Calculate P(B|A) using Bayes' theorem.

        Returns:
            P(B|A)

        Example:
            >>> p_b_given_a = cp.p_b_given_a()
        """
        p_a_and_b = self._p_a.value * self._p_a_given_b.value
        if self._p_a.value == 0:
            raise ProbabilityError("Cannot calculate P(B|A) when P(A) = 0")
        return Probability(p_a_and_b / self._p_a.value)


class BayesianProbability:
    """Concrete implementation of Bayesian probability.

    This class provides Bayesian inference tools.

    Scientific Meaning
    ------------------
    In probability theory, Bayesian probability represents the application of
    Bayes' theorem for updating probabilities based on evidence.

    Example:
        >>> bp = BayesianProbability()
        >>> posterior = bp.update(prior, likelihood, evidence)
    """

    @staticmethod
    def bayes_theorem(prior: float, likelihood: float, evidence: float) -> float:
        """Apply Bayes' theorem.

        Args:
            prior: Prior probability P(H)
            likelihood: Likelihood P(E|H)
            evidence: Evidence probability P(E)

        Returns:
            Posterior probability P(H|E)

        Raises:
            ProbabilityError: If evidence is zero

        Example:
            >>> posterior = BayesianProbability.bayes_theorem(0.5, 0.8, 0.6)
        """
        if evidence == 0:
            raise ProbabilityError("Evidence probability cannot be zero")
        posterior = (prior * likelihood) / evidence
        return posterior

    @staticmethod
    def update(prior: Probability, likelihood: Probability, evidence: Probability) -> Probability:
        """Update probability using Bayes' theorem.

        Args:
            prior: Prior probability
            likelihood: Likelihood
            evidence: Evidence probability

        Returns:
            Posterior probability

        Example:
            >>> posterior = BayesianProbability.update(prior, likelihood, evidence)
        """
        posterior = BayesianProbability.bayes_theorem(
            prior.value, likelihood.value, evidence.value
        )
        return Probability(posterior)


# Export
__all__ = [
    "Probability",
    "Event",
    "RandomVariable",
    "Distribution",
    "ConditionalProbability",
    "BayesianProbability",
]

