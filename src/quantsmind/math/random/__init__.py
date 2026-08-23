"""
Random Module

This module provides random number generation for the Mathematics package.
Random represents stochastic processes and random number generation.

Purpose
-------
Provide random number generation for the Mathematics package.

Scientific Meaning
------------------
Random number generation represents the generation of sequences of numbers that
cannot be reasonably predicted better than by random chance, essential for
Monte Carlo methods, simulations, and cryptography.

Responsibilities
----------------
- Support random number generation
- Enable random sampling
- Support random distributions
- Handle random validation

Dependencies
------------
typing (standard library)
random (standard library)
quantsmind.math.exceptions (exception hierarchy)
quantsmind.math.types (type definitions)

Future Extensions
-----------------
- Advanced random generators
- Quasi-random sequences
- Cryptographic random
"""

from __future__ import annotations

import logging
import random
from typing import Any, List, Optional, Tuple, Union

from quantsmind.math.exceptions import ValueError as MathValueError
from quantsmind.math.types import Scalar

logger = logging.getLogger(__name__)


class RandomGenerator:
    """Concrete implementation of a random number generator.

    This class provides random number generation with various distributions.

    Scientific Meaning
    ------------------
    In scientific computing, random number generators provide sequences of
    pseudo-random numbers for simulations, Monte Carlo methods, and stochastic processes.

    Example:
        >>> rng = RandomGenerator(seed=42)
        >>> value = rng.uniform(0.0, 1.0)
    """

    def __init__(self, seed: int | None = None) -> None:
        """Initialize a RandomGenerator.

        Args:
            seed: Optional seed for reproducibility

        Example:
            >>> rng = RandomGenerator(seed=42)
        """
        self._random = random.Random(seed)
        logger.debug(f"Created random generator with seed={seed}")

    def uniform(self, a: float, b: float) -> float:
        """Generate a uniform random number.

        Args:
            a: Lower bound
            b: Upper bound

        Returns:
            Random number in [a, b]

        Example:
            >>> value = rng.uniform(0.0, 1.0)
        """
        return self._random.uniform(a, b)

    def normal(self, mean: float = 0.0, std: float = 1.0) -> float:
        """Generate a normal random number.

        Args:
            mean: Mean
            std: Standard deviation

        Returns:
            Random number from normal distribution

        Example:
            >>> value = rng.normal(0.0, 1.0)
        """
        return self._random.gauss(mean, std)

    def exponential(self, scale: float = 1.0) -> float:
        """Generate an exponential random number.

        Args:
            scale: Scale parameter

        Returns:
            Random number from exponential distribution

        Example:
            >>> value = rng.exponential(1.0)
        """
        return self._random.expovariate(1.0 / scale) if scale > 0 else 0.0

    def poisson(self, lam: float = 1.0) -> int:
        """Generate a Poisson random number.

        Args:
            lam: Rate parameter

        Returns:
            Random number from Poisson distribution

        Example:
            >>> value = rng.poisson(5.0)
        """
        return self._random.poisson(lam)

    def bernoulli(self, p: float = 0.5) -> int:
        """Generate a Bernoulli random number.

        Args:
            p: Probability of success

        Returns:
            0 or 1

        Raises:
            ValueError: If p is outside [0, 1]

        Example:
            >>> value = rng.bernoulli(0.5)
        """
        if p < 0 or p > 1:
            raise MathValueError("Probability must be in [0, 1]")
        return 1 if self._random.random() < p else 0

    def binomial(self, n: int, p: float = 0.5) -> int:
        """Generate a binomial random number.

        Args:
            n: Number of trials
            p: Probability of success

        Returns:
            Random number from binomial distribution

        Raises:
            ValueError: If parameters are invalid

        Example:
            >>> value = rng.binomial(10, 0.5)
        """
        if n < 0:
            raise MathValueError("Number of trials must be non-negative")
        if p < 0 or p > 1:
            raise MathValueError("Probability must be in [0, 1]")
        return sum(self.bernoulli(p) for _ in range(n))

    def choice(self, sequence: list[Any]) -> Any:
        """Choose a random element from a sequence.

        Args:
            sequence: Sequence to choose from

        Returns:
            Random element

        Example:
            >>> value = rng.choice([1, 2, 3, 4, 5])
        """
        return self._random.choice(sequence)

    def sample(self, sequence: list[Any], k: int) -> list[Any]:
        """Sample k elements from a sequence without replacement.

        Args:
            sequence: Sequence to sample from
            k: Number of elements to sample

        Returns:
            Sampled elements

        Example:
            >>> values = rng.sample([1, 2, 3, 4, 5], 3)
        """
        return self._random.sample(sequence, k)

    def shuffle(self, sequence: list[Any]) -> None:
        """Shuffle a sequence in place.

        Args:
            sequence: Sequence to shuffle

        Example:
            >>> rng.shuffle([1, 2, 3, 4, 5])
        """
        self._random.shuffle(sequence)

    def seed(self, seed: int) -> None:
        """Set the seed.

        Args:
            seed: Seed value

        Example:
            >>> rng.seed(42)
        """
        self._random.seed(seed)


class RandomSampler:
    """Concrete implementation of a random sampler.

    This class provides random sampling from distributions.

    Scientific Meaning
    ------------------
    In statistics, random sampling represents selecting a subset of individuals
    from a larger population, essential for statistical inference.

    Example:
        >>> sampler = RandomSampler()
        >>> sample = sampler.sample([1, 2, 3, 4, 5], 3)
    """

    def __init__(self, seed: int | None = None) -> None:
        """Initialize a RandomSampler.

        Args:
            seed: Optional seed for reproducibility

        Example:
            >>> sampler = RandomSampler(seed=42)
        """
        self._rng = RandomGenerator(seed)
        logger.debug("Created random sampler")

    def sample(self, population: list[Any], k: int, replace: bool = False) -> list[Any]:
        """Sample from a population.

        Args:
            population: Population to sample from
            k: Sample size
            replace: Whether to sample with replacement

        Returns:
            Sample

        Raises:
            ValueError: If sample size is invalid

        Example:
            >>> sample = sampler.sample([1, 2, 3, 4, 5], 3)
        """
        if k < 0:
            raise MathValueError("Sample size must be non-negative")
        if not replace and k > len(population):
            raise MathValueError("Sample size cannot exceed population size without replacement")

        if replace:
            return [self._rng.choice(population) for _ in range(k)]
        else:
            return self._rng.sample(population, k)


class RandomWalk:
    """Concrete implementation of a random walk.

    This class represents a random walk process.

    Scientific Meaning
    ------------------
    In stochastic processes, a random walk represents a path consisting of a succession
    of random steps, essential for modeling diffusion and Brownian motion.

    Example:
        >>> walk = RandomWalk(step_size=1.0)
        >>> path = walk.generate(100)
    """

    def __init__(self, step_size: float = 1.0, seed: int | None = None) -> None:
        """Initialize a RandomWalk.

        Args:
            step_size: Step size
            seed: Optional seed for reproducibility

        Example:
            >>> walk = RandomWalk(step_size=1.0)
        """
        self._step_size = step_size
        self._rng = RandomGenerator(seed)
        logger.debug(f"Created random walk with step_size={step_size}")

    def generate(self, steps: int, start: float = 0.0) -> list[float]:
        """Generate a random walk.

        Args:
            steps: Number of steps
            start: Starting value

        Returns:
            Random walk path

        Example:
            >>> path = walk.generate(100)
        """
        path = [start]
        for _ in range(steps):
            step = self._rng.uniform(-self._step_size, self._step_size)
            path.append(path[-1] + step)
        return path


# Export
__all__ = [
    "RandomGenerator",
    "RandomSampler",
    "RandomWalk",
]
