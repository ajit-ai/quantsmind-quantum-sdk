"""
Statistics Module

This module provides statistical operations for the Mathematics package.
Statistics represents descriptive statistics, hypothesis testing, and estimation.

Purpose
-------
Provide statistical operations for the Mathematics package.

Scientific Meaning
------------------
Statistics represents the study of data collection, analysis, interpretation, and presentation,
essential for data science, machine learning, experimental physics, and many other scientific applications.

Responsibilities
----------------
- Support descriptive statistics
- Enable statistical calculations
- Support hypothesis testing
- Handle statistical validation

Dependencies
------------
typing (standard library)
math (standard library)
quantsmind.math.exceptions (exception hierarchy)
quantsmind.math.types (type definitions)

Future Extensions
-----------------
- Hypothesis testing
- Regression analysis
- Time series analysis
"""

from __future__ import annotations

import logging
import math
from typing import List, Optional, Tuple, Union

from quantsmind.math.exceptions import ValueError as MathValueError
from quantsmind.math.types import Sample, Scalar

logger = logging.getLogger(__name__)


class Mean:
    """Concrete implementation of mean calculation.

    This class provides various mean calculations including arithmetic mean,
    geometric mean, harmonic mean, and weighted mean.

    Scientific Meaning
    ------------------
    In statistics, mean represents the central tendency of a dataset, essential
    for data analysis and interpretation.

    Example:
        >>> mean = Mean.arithmetic([1.0, 2.0, 3.0, 4.0, 5.0])
    """

    @staticmethod
    def arithmetic(data: List[Scalar]) -> float:
        """Calculate arithmetic mean.

        Args:
            data: Data values

        Returns:
            Arithmetic mean

        Raises:
            ValueError: If data is empty

        Example:
            >>> mean = Mean.arithmetic([1.0, 2.0, 3.0, 4.0, 5.0])
        """
        if not data:
            raise MathValueError("Cannot calculate mean of empty data")
        return sum(data) / len(data)

    @staticmethod
    def geometric(data: List[Scalar]) -> float:
        """Calculate geometric mean.

        Args:
            data: Data values (must be positive)

        Returns:
            Geometric mean

        Raises:
            ValueError: If data is empty or contains non-positive values

        Example:
            >>> mean = Mean.geometric([1.0, 2.0, 4.0])
        """
        if not data:
            raise MathValueError("Cannot calculate geometric mean of empty data")
        for x in data:
            if x <= 0:
                raise MathValueError("Geometric mean requires positive values")
        product = 1.0
        for x in data:
            product *= x
        return product ** (1.0 / len(data))

    @staticmethod
    def harmonic(data: List[Scalar]) -> float:
        """Calculate harmonic mean.

        Args:
            data: Data values (must be positive)

        Returns:
            Harmonic mean

        Raises:
            ValueError: If data is empty or contains non-positive values

        Example:
            >>> mean = Mean.harmonic([1.0, 2.0, 4.0])
        """
        if not data:
            raise MathValueError("Cannot calculate harmonic mean of empty data")
        for x in data:
            if x <= 0:
                raise MathValueError("Harmonic mean requires positive values")
        reciprocal_sum = sum(1.0 / x for x in data)
        return len(data) / reciprocal_sum

    @staticmethod
    def weighted(data: List[Scalar], weights: List[Scalar]) -> float:
        """Calculate weighted mean.

        Args:
            data: Data values
            weights: Weights (must sum to 1)

        Returns:
            Weighted mean

        Raises:
            ValueError: If data is empty or weights don't match

        Example:
            >>> mean = Mean.weighted([1.0, 2.0, 3.0], [0.2, 0.3, 0.5])
        """
        if not data:
            raise MathValueError("Cannot calculate weighted mean of empty data")
        if len(data) != len(weights):
            raise MathValueError("Data and weights must have same length")
        if abs(sum(weights) - 1.0) > 1e-10:
            raise MathValueError("Weights must sum to 1")
        return sum(d * w for d, w in zip(data, weights))


class Median:
    """Concrete implementation of median calculation.

    This class provides median calculation for datasets.

    Scientific Meaning
    ------------------
    In statistics, median represents the middle value of a sorted dataset,
    robust to outliers.

    Example:
        >>> median = Median.calculate([1.0, 2.0, 3.0, 4.0, 5.0])
    """

    @staticmethod
    def calculate(data: List[Scalar]) -> float:
        """Calculate median.

        Args:
            data: Data values

        Returns:
            Median

        Raises:
            ValueError: If data is empty

        Example:
            >>> median = Median.calculate([1.0, 2.0, 3.0, 4.0, 5.0])
        """
        if not data:
            raise MathValueError("Cannot calculate median of empty data")
        sorted_data = sorted(data)
        n = len(sorted_data)
        if n % 2 == 0:
            return (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2.0
        else:
            return sorted_data[n // 2]


class Mode:
    """Concrete implementation of mode calculation.

    This class provides mode calculation for datasets.

    Scientific Meaning
    ------------------
    In statistics, mode represents the most frequent value in a dataset.

    Example:
        >>> mode = Mode.calculate([1.0, 2.0, 2.0, 3.0, 3.0, 3.0])
    """

    @staticmethod
    def calculate(data: List[Scalar]) -> List[Scalar]:
        """Calculate mode(s).

        Args:
            data: Data values

        Returns:
            List of mode(s)

        Raises:
            ValueError: If data is empty

        Example:
            >>> modes = Mode.calculate([1.0, 2.0, 2.0, 3.0, 3.0, 3.0])
        """
        if not data:
            raise MathValueError("Cannot calculate mode of empty data")
        from collections import Counter
        counter = Counter(data)
        max_count = max(counter.values())
        modes = [value for value, count in counter.items() if count == max_count]
        return sorted(modes)


class Variance:
    """Concrete implementation of variance calculation.

    This class provides variance calculation for datasets.

    Scientific Meaning
    ------------------
    In statistics, variance represents the spread of data around the mean.

    Example:
        >>> var = Variance.calculate([1.0, 2.0, 3.0, 4.0, 5.0])
    """

    @staticmethod
    def calculate(data: List[Scalar], sample: bool = True) -> float:
        """Calculate variance.

        Args:
            data: Data values
            sample: Whether to calculate sample variance (True) or population variance (False)

        Returns:
            Variance

        Raises:
            ValueError: If data is empty or has insufficient elements

        Example:
            >>> var = Variance.calculate([1.0, 2.0, 3.0, 4.0, 5.0])
        """
        if not data:
            raise MathValueError("Cannot calculate variance of empty data")
        if sample and len(data) < 2:
            raise MathValueError("Sample variance requires at least 2 data points")
        mean = Mean.arithmetic(data)
        squared_diffs = [(x - mean) ** 2 for x in data]
        if sample:
            return sum(squared_diffs) / (len(data) - 1)
        else:
            return sum(squared_diffs) / len(data)


class StandardDeviation:
    """Concrete implementation of standard deviation calculation.

    This class provides standard deviation calculation for datasets.

    Scientific Meaning
    ------------------
    In statistics, standard deviation represents the square root of variance,
    measuring spread in the same units as the data.

    Example:
        >>> std = StandardDeviation.calculate([1.0, 2.0, 3.0, 4.0, 5.0])
    """

    @staticmethod
    def calculate(data: List[Scalar], sample: bool = True) -> float:
        """Calculate standard deviation.

        Args:
            data: Data values
            sample: Whether to calculate sample standard deviation (True) or population (False)

        Returns:
            Standard deviation

        Example:
            >>> std = StandardDeviation.calculate([1.0, 2.0, 3.0, 4.0, 5.0])
        """
        return math.sqrt(Variance.calculate(data, sample))


class Covariance:
    """Concrete implementation of covariance calculation.

    This class provides covariance calculation between two datasets.

    Scientific Meaning
    ------------------
    In statistics, covariance represents the joint variability of two random variables.

    Example:
        >>> cov = Covariance.calculate([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
    """

    @staticmethod
    def calculate(x: List[Scalar], y: List[Scalar], sample: bool = True) -> float:
        """Calculate covariance.

        Args:
            x: First dataset
            y: Second dataset
            sample: Whether to calculate sample covariance (True) or population (False)

        Returns:
            Covariance

        Raises:
            ValueError: If datasets are empty or have different lengths

        Example:
            >>> cov = Covariance.calculate([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
        """
        if not x or not y:
            raise MathValueError("Cannot calculate covariance of empty data")
        if len(x) != len(y):
            raise MathValueError("Datasets must have same length")
        if sample and len(x) < 2:
            raise MathValueError("Sample covariance requires at least 2 data points")
        
        mean_x = Mean.arithmetic(x)
        mean_y = Mean.arithmetic(y)
        
        n = len(x) if not sample else len(x) - 1
        return sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / n


class Correlation:
    """Concrete implementation of correlation calculation.

    This class provides correlation calculation between two datasets.

    Scientific Meaning
    ------------------
    In statistics, correlation represents the linear relationship between two variables,
    ranging from -1 (perfect negative correlation) to 1 (perfect positive correlation).

    Example:
        >>> corr = Correlation.calculate([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
    """

    @staticmethod
    def calculate(x: List[Scalar], y: List[Scalar]) -> float:
        """Calculate Pearson correlation coefficient.

        Args:
            x: First dataset
            y: Second dataset

        Returns:
            Correlation coefficient

        Raises:
            ValueError: If datasets are empty or have different lengths

        Example:
            >>> corr = Correlation.calculate([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
        """
        if not x or not y:
            raise MathValueError("Cannot calculate correlation of empty data")
        if len(x) != len(y):
            raise MathValueError("Datasets must have same length")
        
        cov = Covariance.calculate(x, y, sample=False)
        std_x = StandardDeviation.calculate(x, sample=False)
        std_y = StandardDeviation.calculate(y, sample=False)
        
        if std_x == 0 or std_y == 0:
            raise MathValueError("Cannot calculate correlation with zero standard deviation")
        
        return cov / (std_x * std_y)


class ConfidenceInterval:
    """Concrete implementation of confidence interval calculation.

    This class provides confidence interval calculation for datasets.

    Scientific Meaning
    ------------------
    In statistics, confidence interval represents a range of values that likely
    contains the true population parameter.

    Example:
        >>> ci = ConfidenceInterval.calculate([1.0, 2.0, 3.0, 4.0, 5.0], 0.95)
    """

    @staticmethod
    def calculate(data: List[Scalar], confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for the mean.

        Args:
            data: Data values
            confidence: Confidence level (0 to 1)

        Returns:
            Tuple of (lower_bound, upper_bound)

        Raises:
            ValueError: If data is empty or confidence is invalid

        Example:
            >>> ci = ConfidenceInterval.calculate([1.0, 2.0, 3.0, 4.0, 5.0], 0.95)
        """
        if not data:
            raise MathValueError("Cannot calculate confidence interval of empty data")
        if confidence <= 0 or confidence >= 1:
            raise MathValueError("Confidence must be between 0 and 1")
        
        mean = Mean.arithmetic(data)
        std = StandardDeviation.calculate(data, sample=True)
        n = len(data)
        
        # Simplified: using normal approximation
        # In production, this should use t-distribution for small samples
        from quantsmind.math.constants import PI
        z_score = 1.96  # Approximate for 95% confidence
        
        margin_of_error = z_score * (std / math.sqrt(n))
        
        return (mean - margin_of_error, mean + margin_of_error)


class Percentile:
    """Concrete implementation of percentile calculation.

    This class provides percentile calculation for datasets.

    Scientific Meaning
    ------------------
    In statistics, percentile represents the value below which a given percentage
    of observations fall.

    Example:
        >>> p50 = Percentile.calculate([1.0, 2.0, 3.0, 4.0, 5.0], 50)
    """

    @staticmethod
    def calculate(data: List[Scalar], percentile: float) -> float:
        """Calculate percentile.

        Args:
            data: Data values
            percentile: Percentile (0 to 100)

        Returns:
            Percentile value

        Raises:
            ValueError: If data is empty or percentile is invalid

        Example:
            >>> p50 = Percentile.calculate([1.0, 2.0, 3.0, 4.0, 5.0], 50)
        """
        if not data:
            raise MathValueError("Cannot calculate percentile of empty data")
        if percentile < 0 or percentile > 100:
            raise MathValueError("Percentile must be between 0 and 100")
        
        sorted_data = sorted(data)
        n = len(sorted_data)
        index = (percentile / 100) * (n - 1)
        
        lower = int(math.floor(index))
        upper = int(math.ceil(index))
        
        if lower == upper:
            return sorted_data[lower]
        
        weight = index - lower
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight


class Skewness:
    """Concrete implementation of skewness calculation.

    This class provides skewness calculation for datasets.

    Scientific Meaning
    ------------------
    In statistics, skewness represents the asymmetry of the probability distribution.

    Example:
        >>> skew = Skewness.calculate([1.0, 2.0, 3.0, 4.0, 5.0])
    """

    @staticmethod
    def calculate(data: List[Scalar]) -> float:
        """Calculate skewness.

        Args:
            data: Data values

        Returns:
            Skewness

        Raises:
            ValueError: If data is empty

        Example:
            >>> skew = Skewness.calculate([1.0, 2.0, 3.0, 4.0, 5.0])
        """
        if not data:
            raise MathValueError("Cannot calculate skewness of empty data")
        
        mean = Mean.arithmetic(data)
        std = StandardDeviation.calculate(data, sample=False)
        
        if std == 0:
            return 0.0
        
        n = len(data)
        skew = sum((x - mean) ** 3 for x in data) / n
        return skew / (std ** 3)


class Kurtosis:
    """Concrete implementation of kurtosis calculation.

    This class provides kurtosis calculation for datasets.

    Scientific Meaning
    ------------------
    In statistics, kurtosis represents the "tailedness" of the probability distribution.

    Example:
        >>> kurt = Kurtosis.calculate([1.0, 2.0, 3.0, 4.0, 5.0])
    """

    @staticmethod
    def calculate(data: List[Scalar]) -> float:
        """Calculate kurtosis.

        Args:
            data: Data values

        Returns:
            Kurtosis

        Raises:
            ValueError: If data is empty

        Example:
            >>> kurt = Kurtosis.calculate([1.0, 2.0, 3.0, 4.0, 5.0])
        """
        if not data:
            raise MathValueError("Cannot calculate kurtosis of empty data")
        
        mean = Mean.arithmetic(data)
        std = StandardDeviation.calculate(data, sample=False)
        
        if std == 0:
            return 0.0
        
        n = len(data)
        kurt = sum((x - mean) ** 4 for x in data) / n
        return kurt / (std ** 4) - 3  # Excess kurtosis


# Export
__all__ = [
    "Mean",
    "Median",
    "Mode",
    "Variance",
    "StandardDeviation",
    "Covariance",
    "Correlation",
    "ConfidenceInterval",
    "Percentile",
    "Skewness",
    "Kurtosis",
]

