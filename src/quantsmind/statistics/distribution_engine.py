"""
Distribution Engine Module

This module provides probability distribution functionality for the QuantsMind SDK.

Purpose
-------
Provide probability distribution classes for statistical modeling.

Classes
-------
DistributionEngine: Distribution management engine
NormalDistribution: Normal (Gaussian) distribution
BinomialDistribution: Binomial distribution
PoissonDistribution: Poisson distribution
GammaDistribution: Gamma distribution
BetaDistribution: Beta distribution
ExponentialDistribution: Exponential distribution

Responsibilities
----------------
- Represent probability distributions
- Compute PDF/PMF
- Compute CDF
- Generate random samples
- Compute statistics

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

import math
import random
from typing import Any


class DistributionEngine:
    """Base distribution engine.

    This class provides the base functionality for probability distributions.

    Attributes:
        _name: Distribution name
        _parameters: Distribution parameters
        _metadata: Additional metadata

    Example:
        >>> engine = DistributionEngine("normal", {"mean": 0, "std": 1})
    """

    def __init__(
        self,
        name: str,
        parameters: dict[str, float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a DistributionEngine.

        Args:
            name: Distribution name
            parameters: Distribution parameters
            metadata: Additional metadata

        Example:
            >>> engine = DistributionEngine("normal", {"mean": 0, "std": 1})
        """
        self._name = name
        self._parameters = parameters or {}
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the distribution name.

        Returns:
            Distribution name

        Example:
            >>> name = engine.name
        """
        return self._name

    @property
    def parameters(self) -> dict[str, float]:
        """Get the distribution parameters.

        Returns:
            Parameters dictionary

        Example:
            >>> params = engine.parameters
        """
        return self._parameters.copy()

    def pdf(self, x: float) -> float:
        """Compute probability density function.

        Args:
            x: Point to evaluate at

        Returns:
            PDF value

        Example:
            >>> pdf = engine.pdf(0.0)
        """
        raise NotImplementedError("Subclasses must implement pdf")

    def cdf(self, x: float) -> float:
        """Compute cumulative distribution function.

        Args:
            x: Point to evaluate at

        Returns:
            CDF value

        Example:
            >>> cdf = engine.cdf(0.0)
        """
        raise NotImplementedError("Subclasses must implement cdf")

    def sample(self, n: int = 1) -> list[float]:
        """Generate random samples.

        Args:
            n: Number of samples

        Returns:
            List of samples

        Example:
            >>> samples = engine.sample(10)
        """
        raise NotImplementedError("Subclasses must implement sample")

    def mean(self) -> float:
        """Compute the mean.

        Returns:
            Mean value

        Example:
            >>> mean = engine.mean()
        """
        raise NotImplementedError("Subclasses must implement mean")

    def variance(self) -> float:
        """Compute the variance.

        Returns:
            Variance value

        Example:
            >>> var = engine.variance()
        """
        raise NotImplementedError("Subclasses must implement variance")

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(engine)
        """
        return f"DistributionEngine(name={self._name})"


class NormalDistribution(DistributionEngine):
    """Normal (Gaussian) distribution.

    Attributes:
        _mean: Mean parameter
        _std: Standard deviation parameter

    Example:
        >>> dist = NormalDistribution(mean=0, std=1)
        >>> pdf = dist.pdf(0.0)
    """

    def __init__(
        self,
        mean: float = 0.0,
        std: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a NormalDistribution.

        Args:
            mean: Mean parameter
            std: Standard deviation parameter
            metadata: Additional metadata

        Example:
            >>> dist = NormalDistribution(mean=0, std=1)
        """
        super().__init__("normal", {"mean": mean, "std": std}, metadata)
        self._mean = mean
        self._std = std

    def pdf(self, x: float) -> float:
        """Compute PDF.

        Args:
            x: Point to evaluate at

        Returns:
            PDF value

        Example:
            >>> pdf = dist.pdf(0.0)
        """
        coefficient = 1.0 / (self._std * math.sqrt(2 * math.pi))
        exponent = -0.5 * ((x - self._mean) / self._std) ** 2
        return coefficient * math.exp(exponent)

    def cdf(self, x: float) -> float:
        """Compute CDF.

        Args:
            x: Point to evaluate at

        Returns:
            CDF value

        Example:
            >>> cdf = dist.cdf(0.0)
        """
        # Error function approximation
        z = (x - self._mean) / (self._std * math.sqrt(2))
        return 0.5 * (1 + math.erf(z))

    def sample(self, n: int = 1) -> list[float]:
        """Generate random samples using Box-Muller transform.

        Args:
            n: Number of samples

        Returns:
            List of samples

        Example:
            >>> samples = dist.sample(10)
        """
        samples = []
        for _ in range(n):
            u1 = random.random()
            u2 = random.random()
            z0 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            samples.append(self._mean + self._std * z0)
        return samples

    def mean(self) -> float:
        """Compute the mean.

        Returns:
            Mean value

        Example:
            >>> mean = dist.mean()
        """
        return self._mean

    def variance(self) -> float:
        """Compute the variance.

        Returns:
            Variance value

        Example:
            >>> var = dist.variance()
        """
        return self._std ** 2


class BinomialDistribution(DistributionEngine):
    """Binomial distribution.

    Attributes:
        _n: Number of trials
        _p: Success probability

    Example:
        >>> dist = BinomialDistribution(n=10, p=0.5)
        >>> pmf = dist.pdf(5)
    """

    def __init__(
        self,
        n: int,
        p: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a BinomialDistribution.

        Args:
            n: Number of trials
            p: Success probability
            metadata: Additional metadata

        Example:
            >>> dist = BinomialDistribution(n=10, p=0.5)
        """
        super().__init__("binomial", {"n": n, "p": p}, metadata)
        self._n = n
        self._p = p

    def pdf(self, k: int) -> float:
        """Compute PMF (probability mass function).

        Args:
            k: Number of successes

        Returns:
            PMF value

        Example:
            >>> pmf = dist.pdf(5)
        """
        if k < 0 or k > self._n:
            return 0.0

        # Binomial coefficient
        def binomial_coeff(n: int, k: int) -> int:
            if k > n - k:
                k = n - k
            result = 1
            for i in range(k):
                result = result * (n - i) // (i + 1)
            return result

        coeff = binomial_coeff(self._n, k)
        return coeff * (self._p ** k) * ((1 - self._p) ** (self._n - k))

    def cdf(self, k: int) -> float:
        """Compute CDF.

        Args:
            k: Number of successes

        Returns:
            CDF value

        Example:
            >>> cdf = dist.cdf(5)
        """
        return sum(self.pdf(i) for i in range(k + 1))

    def sample(self, n: int = 1) -> list[int]:
        """Generate random samples.

        Args:
            n: Number of samples

        Returns:
            List of samples

        Example:
            >>> samples = dist.sample(10)
        """
        samples = []
        for _ in range(n):
            count = sum(1 for _ in range(self._n) if random.random() < self._p)
            samples.append(count)
        return samples

    def mean(self) -> float:
        """Compute the mean.

        Returns:
            Mean value

        Example:
            >>> mean = dist.mean()
        """
        return self._n * self._p

    def variance(self) -> float:
        """Compute the variance.

        Returns:
            Variance value

        Example:
            >>> var = dist.variance()
        """
        return self._n * self._p * (1 - self._p)


class PoissonDistribution(DistributionEngine):
    """Poisson distribution.

    Attributes:
        _lambda: Rate parameter

    Example:
        >>> dist = PoissonDistribution(lambda_param=5)
        >>> pmf = dist.pdf(3)
    """

    def __init__(
        self,
        lambda_param: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a PoissonDistribution.

        Args:
            lambda_param: Rate parameter
            metadata: Additional metadata

        Example:
            >>> dist = PoissonDistribution(lambda_param=5)
        """
        super().__init__("poisson", {"lambda": lambda_param}, metadata)
        self._lambda = lambda_param

    def pdf(self, k: int) -> float:
        """Compute PMF.

        Args:
            k: Number of events

        Returns:
            PMF value

        Example:
            >>> pmf = dist.pdf(3)
        """
        if k < 0:
            return 0.0

        # Poisson PMF: e^(-λ) * λ^k / k!
        return math.exp(-self._lambda) * (self._lambda ** k) / math.factorial(k)

    def cdf(self, k: int) -> float:
        """Compute CDF.

        Args:
            k: Number of events

        Returns:
            CDF value

        Example:
            >>> cdf = dist.cdf(3)
        """
        return sum(self.pdf(i) for i in range(k + 1))

    def sample(self, n: int = 1) -> list[int]:
        """Generate random samples using Knuth's algorithm.

        Args:
            n: Number of samples

        Returns:
            List of samples

        Example:
            >>> samples = dist.sample(10)
        """
        samples = []
        for _ in range(n):
            limit = math.exp(-self._lambda)
            k = 0
            p = 1.0
            while p > limit:
                k += 1
                p *= random.random()
            samples.append(k - 1)
        return samples

    def mean(self) -> float:
        """Compute the mean.

        Returns:
            Mean value

        Example:
            >>> mean = dist.mean()
        """
        return self._lambda

    def variance(self) -> float:
        """Compute the variance.

        Returns:
            Variance value

        Example:
            >>> var = dist.variance()
        """
        return self._lambda


class GammaDistribution(DistributionEngine):
    """Gamma distribution.

    Attributes:
        _shape: Shape parameter (k)
        _scale: Scale parameter (θ)

    Example:
        >>> dist = GammaDistribution(shape=2, scale=1)
        >>> pdf = dist.pdf(1.0)
    """

    def __init__(
        self,
        shape: float,
        scale: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a GammaDistribution.

        Args:
            shape: Shape parameter (k)
            scale: Scale parameter (θ)
            metadata: Additional metadata

        Example:
            >>> dist = GammaDistribution(shape=2, scale=1)
        """
        super().__init__("gamma", {"shape": shape, "scale": scale}, metadata)
        self._shape = shape
        self._scale = scale

    def pdf(self, x: float) -> float:
        """Compute PDF.

        Args:
            x: Point to evaluate at

        Returns:
            PDF value

        Example:
            >>> pdf = dist.pdf(1.0)
        """
        if x <= 0:
            return 0.0

        # Gamma PDF: x^(k-1) * e^(-x/θ) / (Γ(k) * θ^k)
        k = self._shape
        theta = self._scale

        # Gamma function approximation
        def gamma_func(z: float) -> float:
            if z == 1:
                return 1.0
            elif z == 0.5:
                return math.sqrt(math.pi)
            else:
                # Lanczos approximation (simplified)
                return math.gamma(z)

        coefficient = 1.0 / (gamma_func(k) * (theta ** k))
        return coefficient * (x ** (k - 1)) * math.exp(-x / theta)

    def cdf(self, x: float) -> float:
        """Compute CDF (simplified).

        Args:
            x: Point to evaluate at

        Returns:
            CDF value

        Example:
            >>> cdf = dist.cdf(1.0)
        """
        # Placeholder - real implementation would use incomplete gamma function
        return 0.5  # Simplified

    def sample(self, n: int = 1) -> list[float]:
        """Generate random samples (simplified).

        Args:
            n: Number of samples

        Returns:
            List of samples

        Example:
            >>> samples = dist.sample(10)
        """
        # Placeholder - real implementation would use Marsaglia and Tsang's method
        return [random.random() for _ in range(n)]

    def mean(self) -> float:
        """Compute the mean.

        Returns:
            Mean value

        Example:
            >>> mean = dist.mean()
        """
        return self._shape * self._scale

    def variance(self) -> float:
        """Compute the variance.

        Returns:
            Variance value

        Example:
            >>> var = dist.variance()
        """
        return self._shape * (self._scale ** 2)


class BetaDistribution(DistributionEngine):
    """Beta distribution.

    Attributes:
        _alpha: Alpha parameter
        _beta: Beta parameter

    Example:
        >>> dist = BetaDistribution(alpha=2, beta=5)
        >>> pdf = dist.pdf(0.5)
    """

    def __init__(
        self,
        alpha: float,
        beta: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a BetaDistribution.

        Args:
            alpha: Alpha parameter
            beta: Beta parameter
            metadata: Additional metadata

        Example:
            >>> dist = BetaDistribution(alpha=2, beta=5)
        """
        super().__init__("beta", {"alpha": alpha, "beta": beta}, metadata)
        self._alpha = alpha
        self._beta = beta

    def pdf(self, x: float) -> float:
        """Compute PDF.

        Args:
            x: Point to evaluate at (0-1)

        Returns:
            PDF value

        Example:
            >>> pdf = dist.pdf(0.5)
        """
        if x <= 0 or x >= 1:
            return 0.0

        # Beta PDF: x^(α-1) * (1-x)^(β-1) / B(α, β)
        # B(α, β) = Γ(α)Γ(β) / Γ(α+β)
        numerator = (x ** (self._alpha - 1)) * ((1 - x) ** (self._beta - 1))
        denominator = math.gamma(self._alpha) * math.gamma(self._beta) / math.gamma(self._alpha + self._beta)
        return numerator / denominator

    def cdf(self, x: float) -> float:
        """Compute CDF (simplified).

        Args:
            x: Point to evaluate at

        Returns:
            CDF value

        Example:
            >>> cdf = dist.cdf(0.5)
        """
        # Placeholder - real implementation would use incomplete beta function
        return 0.5  # Simplified

    def sample(self, n: int = 1) -> list[float]:
        """Generate random samples (simplified).

        Args:
            n: Number of samples

        Returns:
            List of samples

        Example:
            >>> samples = dist.sample(10)
        """
        # Placeholder - real implementation would use rejection sampling
        return [random.random() for _ in range(n)]

    def mean(self) -> float:
        """Compute the mean.

        Returns:
            Mean value

        Example:
            >>> mean = dist.mean()
        """
        return self._alpha / (self._alpha + self._beta)

    def variance(self) -> float:
        """Compute the variance.

        Returns:
            Variance value

        Example:
            >>> var = dist.variance()
        """
        total = self._alpha + self._beta
        return (self._alpha * self._beta) / (total ** 2 * (total + 1))


class ExponentialDistribution(DistributionEngine):
    """Exponential distribution.

    Attributes:
        _lambda: Rate parameter

    Example:
        >>> dist = ExponentialDistribution(lambda_param=2)
        >>> pdf = dist.pdf(1.0)
    """

    def __init__(
        self,
        lambda_param: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an ExponentialDistribution.

        Args:
            lambda_param: Rate parameter
            metadata: Additional metadata

        Example:
            >>> dist = ExponentialDistribution(lambda_param=2)
        """
        super().__init__("exponential", {"lambda": lambda_param}, metadata)
        self._lambda = lambda_param

    def pdf(self, x: float) -> float:
        """Compute PDF.

        Args:
            x: Point to evaluate at

        Returns:
            PDF value

        Example:
            >>> pdf = dist.pdf(1.0)
        """
        if x < 0:
            return 0.0

        return self._lambda * math.exp(-self._lambda * x)

    def cdf(self, x: float) -> float:
        """Compute CDF.

        Args:
            x: Point to evaluate at

        Returns:
            CDF value

        Example:
            >>> cdf = dist.cdf(1.0)
        """
        if x < 0:
            return 0.0

        return 1 - math.exp(-self._lambda * x)

    def sample(self, n: int = 1) -> list[float]:
        """Generate random samples using inverse transform.

        Args:
            n: Number of samples

        Returns:
            List of samples

        Example:
            >>> samples = dist.sample(10)
        """
        samples = []
        for _ in range(n):
            u = random.random()
            samples.append(-math.log(1 - u) / self._lambda)
        return samples

    def mean(self) -> float:
        """Compute the mean.

        Returns:
            Mean value

        Example:
            >>> mean = dist.mean()
        """
        return 1.0 / self._lambda

    def variance(self) -> float:
        """Compute the variance.

        Returns:
            Variance value

        Example:
            >>> var = dist.variance()
        """
        return 1.0 / (self._lambda ** 2)


__all__ = [
    "DistributionEngine",
    "NormalDistribution",
    "BinomialDistribution",
    "PoissonDistribution",
    "GammaDistribution",
    "BetaDistribution",
    "ExponentialDistribution",
]
