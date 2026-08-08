"""
Statistical Analyzer Module

This module provides statistical analysis functionality for the QuantsMind SDK.

Purpose
-------
Provide comprehensive statistical analysis capabilities.

Classes
-------
StatisticalAnalyzer: Statistical analysis engine

Responsibilities
----------------
- Compute descriptive statistics
- Compute correlation and covariance
- Perform regression analysis
- Perform hypothesis testing
- Compute confidence intervals

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import math


class StatisticalAnalyzer:
    """Statistical analysis engine.

    This class provides functionality for statistical analysis of data.

    Attributes:
        _name: Analyzer name
        _data: Data samples
        _metadata: Additional metadata

    Example:
        >>> analyzer = StatisticalAnalyzer()
        >>> analyzer.set_data([1, 2, 3, 4, 5])
        >>> mean = analyzer.mean()
    """

    def __init__(
        self,
        name: str = "default",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a StatisticalAnalyzer.

        Args:
            name: Analyzer name
            metadata: Additional metadata

        Example:
            >>> analyzer = StatisticalAnalyzer()
        """
        self._name = name
        self._data: List[float] = []
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the analyzer name.

        Returns:
            Analyzer name

        Example:
            >>> name = analyzer.name
        """
        return self._name

    def set_data(self, data: List[float]) -> None:
        """Set the data for analysis.

        Args:
            data: Data samples

        Example:
            >>> analyzer.set_data([1, 2, 3, 4, 5])
        """
        self._data = data

    def add_data_point(self, value: float) -> None:
        """Add a data point.

        Args:
            value: Data value

        Example:
            >>> analyzer.add_data_point(6.0)
        """
        self._data.append(value)

    def mean(self) -> float:
        """Compute the mean.

        Returns:
            Mean value

        Example:
            >>> mean = analyzer.mean()
        """
        if not self._data:
            raise ValueError("No data available")
        return sum(self._data) / len(self._data)

    def median(self) -> float:
        """Compute the median.

        Returns:
            Median value

        Example:
            >>> median = analyzer.median()
        """
        if not self._data:
            raise ValueError("No data available")

        sorted_data = sorted(self._data)
        n = len(sorted_data)

        if n % 2 == 0:
            return (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
        else:
            return sorted_data[n // 2]

    def mode(self) -> float:
        """Compute the mode.

        Returns:
            Mode value

        Example:
            >>> mode = analyzer.mode()
        """
        if not self._data:
            raise ValueError("No data available")

        from collections import Counter
        counts = Counter(self._data)
        return counts.most_common(1)[0][0]

    def variance(self, sample: bool = True) -> float:
        """Compute the variance.

        Args:
            sample: If True, compute sample variance (n-1 denominator)

        Returns:
            Variance

        Example:
            >>> var = analyzer.variance()
        """
        if not self._data:
            raise ValueError("No data available")

        n = len(self._data)
        if sample and n > 1:
            denominator = n - 1
        else:
            denominator = n

        mean_val = self.mean()
        return sum((x - mean_val) ** 2 for x in self._data) / denominator

    def standard_deviation(self, sample: bool = True) -> float:
        """Compute the standard deviation.

        Args:
            sample: If True, compute sample standard deviation

        Returns:
            Standard deviation

        Example:
            >>> std = analyzer.standard_deviation()
        """
        return math.sqrt(self.variance(sample))

    def correlation(self, other_data: List[float]) -> float:
        """Compute Pearson correlation coefficient.

        Args:
            other_data: Other data series

        Returns:
            Correlation coefficient

        Example:
            >>> corr = analyzer.correlation([2, 3, 4, 5, 6])
        """
        if len(self._data) != len(other_data):
            raise ValueError("Data series must have same length")

        n = len(self._data)
        if n < 2:
            raise ValueError("Need at least 2 data points")

        mean_x = sum(self._data) / n
        mean_y = sum(other_data) / n

        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(self._data, other_data))
        denominator_x = math.sqrt(sum((x - mean_x) ** 2 for x in self._data))
        denominator_y = math.sqrt(sum((y - mean_y) ** 2 for y in other_data))

        if denominator_x == 0 or denominator_y == 0:
            return 0.0

        return numerator / (denominator_x * denominator_y)

    def covariance(self, other_data: List[float], sample: bool = True) -> float:
        """Compute covariance.

        Args:
            other_data: Other data series
           (sample): If True, compute sample covariance

        Returns:
            Covariance

        Example:
            >>> cov = analyzer.covariance([2, 3, 4, 5, 6])
        """
        if len(self._data) != len(other_data):
            raise ValueError("Data series must have same length")

        n = len(self._data)
        if sample and n > 1:
            denominator = n - 1
        else:
            denominator = n

        mean_x = sum(self._data) / n
        mean_y = sum(other_data) / n

        return sum((x - mean_x) * (y - mean_y) for x, y in zip(self._data, other_data)) / denominator

    def linear_regression(self, x_data: List[float]) -> Tuple[float, float]:
        """Perform simple linear regression.

        Args:
            x_data: X data (independent variable)

        Returns:
            Tuple of (slope, intercept)

        Example:
            >>> slope, intercept = analyzer.linear_regression(x_data)
        """
        if len(self._data) != len(x_data):
            raise ValueError("Data series must have same length")

        n = len(self._data)
        sum_x = sum(x_data)
        sum_y = sum(self._data)
        sum_xy = sum(x * y for x, y in zip(x_data, self._data))
        sum_x2 = sum(x ** 2 for x in x_data)

        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            raise ValueError("Cannot compute regression (zero denominator)")

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n

        return (slope, intercept)

    def hypothesis_test_mean(
        self,
        null_hypothesis: float,
        alpha: float = 0.05,
    ) -> Dict[str, Any]:
        """Perform one-sample t-test for mean.

        Args:
            null_hypothesis: Null hypothesis value
            alpha: Significance level

        Returns:
            Dictionary with test results

        Example:
            >>> result = analyzer.hypothesis_test_mean(0.0)
        """
        if not self._data:
            raise ValueError("No data available")

        n = len(self._data)
        sample_mean = self.mean()
        sample_std = self.standard_deviation(sample=True)

        # t-statistic
        t_stat = (sample_mean - null_hypothesis) / (sample_std / math.sqrt(n))

        # Degrees of freedom
        df = n - 1

        # Critical value (two-tailed) - simplified approximation
        # Real implementation would use t-distribution table or scipy
        critical_value = 1.96  # Approximate for large samples

        # p-value (simplified)
        p_value = 2 * (1 - 0.5 * (1 + math.erf(abs(t_stat) / math.sqrt(2))))

        reject_null = abs(t_stat) > critical_value or p_value < alpha

        return {
            "t_statistic": t_stat,
            "degrees_of_freedom": df,
            "p_value": p_value,
            "critical_value": critical_value,
            "reject_null": reject_null,
            "sample_mean": sample_mean,
            "null_hypothesis": null_hypothesis,
        }

    def confidence_interval_mean(
        self,
        confidence_level: float = 0.95,
    ) -> Tuple[float, float]:
        """Compute confidence interval for the mean.

        Args:
            confidence_level: Confidence level (0-1)

        Returns:
            Tuple of (lower_bound, upper_bound)

        Example:
            >>> lower, upper = analyzer.confidence_interval_mean(0.95)
        """
        if not self._data:
            raise ValueError("No data available")

        n = len(self._data)
        sample_mean = self.mean()
        sample_std = self.standard_deviation(sample=True)

        # Z-score for confidence level (simplified)
        alpha = 1 - confidence_level
        z_score = 1.96 if confidence_level == 0.95 else 1.645  # Approximate

        margin_of_error = z_score * sample_std / math.sqrt(n)

        return (sample_mean - margin_of_error, sample_mean + margin_of_error)

    def percentile(self, percentile: float) -> float:
        """Compute a percentile.

        Args:
            percentile: Percentile (0-100)

        Returns:
            Percentile value

        Example:
            >>> p95 = analyzer.percentile(95)
        """
        if not self._data:
            raise ValueError("No data available")

        if percentile < 0 or percentile > 100:
            raise ValueError("Percentile must be between 0 and 100")

        sorted_data = sorted(self._data)
        n = len(sorted_data)
        index = (percentile / 100) * (n - 1)

        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    def skewness(self) -> float:
        """Compute skewness.

        Returns:
            Skewness value

        Example:
            >>> skew = analyzer.skewness()
        """
        if not self._data:
            raise ValueError("No data available")

        n = len(self._data)
        mean_val = self.mean()
        std_val = self.standard_deviation(sample=False)

        if std_val == 0:
            return 0.0

        skew = sum((x - mean_val) ** 3 for x in self._data) / (n * std_val ** 3)
        return skew

    def kurtosis(self) -> float:
        """Compute kurtosis.

        Returns:
            Kurtosis value

        Example:
            >>> kurt = analyzer.kurtosis()
        """
        if not self._data:
            raise ValueError("No data available")

        n = len(self._data)
        mean_val = self.mean()
        std_val = self.standard_deviation(sample=False)

        if std_val == 0:
            return 0.0

        kurt = sum((x - mean_val) ** 4 for x in self._data) / (n * std_val ** 4) - 3
        return kurt

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(analyzer)
        """
        return f"StatisticalAnalyzer(name={self._name}, samples={len(self._data)})"


__all__ = [
    "StatisticalAnalyzer",
]
