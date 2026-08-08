"""
Feature Transformation Module

This module provides feature transformation implementations for the QuantsMind SDK.

Purpose
-------
Provide common feature transformations used in machine learning.

Classes
-------
FeatureTransformer: Base feature transformer class
Normalization: Min-max normalization
Standardization: Z-score standardization
OneHotEncoder: One-hot encoding
PolynomialFeatures: Polynomial feature expansion

Responsibilities
----------------
- Transform features
- Fit transformation parameters
 Support inverse transformation
- Handle different transformation types

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import math


class FeatureTransformer:
    """Base feature transformer class.

    This class provides the base functionality for feature transformations.

    Attributes:
        _name: Transformer name
        _fitted: Whether transformer has been fitted
        _metadata: Additional metadata

    Example:
        >>> transformer = FeatureTransformer("base")
        >>> transformed = transformer.transform([[1, 2], [3, 4]])
    """

    def __init__(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a FeatureTransformer.

        Args:
            name: Transformer name
            metadata: Additional metadata

        Example:
            >>> transformer = FeatureTransformer("base")
        """
        self._name = name
        self._fitted = False
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the transformer name.

        Returns:
            Transformer name

        Example:
            >>> name = transformer.name
        """
        return self._name

    @property
    def fitted(self) -> bool:
        """Check if transformer has been fitted.

        Returns:
            True if fitted

        Example:
            >>> is_fitted = transformer.fitted
        """
        return self._fitted

    def fit(self, data: List[List[float]]) -> "FeatureTransformer":
        """Fit the transformer to data.

        Args:
            data: Training data

        Returns:
            Self for method chaining

        Example:
            >>> transformer.fit([[1, 2], [3, 4]])
        """
        raise NotImplementedError("Subclasses must implement fit")

    def transform(self, data: List[List[float]]) -> List[List[float]]:
        """Transform the data.

        Args:
            data: Data to transform

        Returns:
            Transformed data

        Example:
            >>> transformed = transformer.transform([[1, 2], [3, 4]])
        """
        raise NotImplementedError("Subclasses must implement transform")

    def fit_transform(self, data: List[List[float]]) -> List[List[float]]:
        """Fit and transform in one step.

        Args:
            data: Data to fit and transform

        Returns:
            Transformed data

        Example:
            >>> transformed = transformer.fit_transform([[1, 2], [3, 4]])
        """
        self.fit(data)
        return self.transform(data)

    def inverse_transform(self, data: List[List[float]]) -> List[List[float]]:
        """Inverse transform the data.

        Args:
            data: Data to inverse transform

        Returns:
            Inverse transformed data

        Example:
            >>> original = transformer.inverse_transform(transformed)
        """
        raise NotImplementedError("Subclasses must implement inverse_transform")

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(transformer)
        """
        return f"FeatureTransformer(name={self._name}, fitted={self._fitted})"


class Normalization(FeatureTransformer):
    """Min-max normalization.

    This class implements min-max normalization to scale features to [0, 1].

    Attributes:
        _min: Minimum values per feature
        _max: Maximum values per feature

    Example:
        >>> transformer = Normalization()
        >>> transformed = transformer.fit_transform([[1, 2], [3, 4]])
    """

    def __init__(metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a Normalization.

        Args:
            metadata: Additional metadata

        Example:
            >>> transformer = Normalization()
        """
        super().__init__("normalization", metadata)
        self._min: List[float] = []
        self._max: List[float] = []

    def fit(self, data: List[List[float]]) -> "Normalization":
        """Fit the normalizer to data.

        Args:
            data: Training data

        Returns:
            Self for method chaining

        Example:
            >>> transformer.fit([[1, 2], [3, 4]])
        """
        if not data:
            raise ValueError("Data cannot be empty")

        n_features = len(data[0])
        self._min = [min(row[i] for row in data) for i in range(n_features)]
        self._max = [max(row[i] for row in data) for i in range(n_features)]
        self._fitted = True
        return self

    def transform(self, data: List[List[float]]) -> List[List[float]]:
        """Transform the data.

        Args:
            data: Data to transform

        Returns:
            Transformed data

        Example:
            >>> transformed = transformer.transform([[1, 2], [3, 4]])
        """
        if not self._fitted:
            raise ValueError("Transformer must be fitted before transform")

        transformed = []
        for row in data:
            transformed_row = []
            for i, val in enumerate(row):
                if self._max[i] == self._min[i]:
                    transformed_row.append(0.0)
                else:
                    transformed_row.append((val - self._min[i]) / (self._max[i] - self._min[i]))
            transformed.append(transformed_row)
        return transformed

    def inverse_transform(self, data: List[List[float]]) -> List[List[float]]:
        """Inverse transform the data.

        Args:
            data: Data to inverse transform

        Returns:
            Inverse transformed data

        Example:
            >>> original = transformer.inverse_transform(transformed)
        """
        if not self._fitted:
            raise ValueError("Transformer must be fitted before inverse_transform")

        original = []
        for row in data:
            original_row = []
            for i, val in enumerate(row):
                original_row.append(val * (self._max[i] - self._min[i]) + self._min[i])
            original.append(original_row)
        return original


class Standardization(FeatureTransformer):
    """Z-score standardization.

    This class implements z-score standardization to scale features to mean=0, std=1.

    Attributes:
        _mean: Mean values per feature
        _std: Standard deviation values per feature

    Example:
        >>> transformer = Standardization()
        >>> transformed = transformer.fit_transform([[1, 2], [3, 4]])
    """

    def __init__(metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a Standardization.

        Args:
            metadata: Additional metadata

        Example:
            >>> transformer = Standardization()
        """
        super().__init__("standardization", metadata)
        self._mean: List[float] = []
        self._std: List[float] = []

    def fit(self, data: List[List[float]]) -> "Standardization":
        """Fit the standardizer to data.

        Args:
            data: Training data

        Returns:
            Self for method chaining

        Example:
            >>> transformer.fit([[1, 2], [3, 4]])
        """
        if not data:
            raise ValueError("Data cannot be empty")

        n_features = len(data[0])
        self._mean = [sum(row[i] for row in data) / len(data) for i in range(n_features)]
        self._std = [
            math.sqrt(sum((row[i] - self._mean[i]) ** 2 for row in data) / len(data))
            for i in range(n_features)
        ]
        self._fitted = True
        return self

    def transform(self, data: List[List[float]]) -> List[List[float]]:
        """Transform the data.

        Args:
            data: Data to transform

        Returns:
            Transformed data

        Example:
            >>> transformed = transformer.transform([[1, 2], [3, 4]])
        """
        if not self._fitted:
            raise ValueError("Transformer must be fitted before transform")

        transformed = []
        for row in data:
            transformed_row = []
            for i, val in enumerate(row):
                if self._std[i] == 0:
                    transformed_row.append(0.0)
                else:
                    transformed_row.append((val - self._mean[i]) / self._std[i])
            transformed.append(transformed_row)
        return transformed

    def inverse_transform(self, data: List[List[float]]) -> List[List[float]]:
        """Inverse transform the data.

        Args:
            data: Data to inverse transform

        Returns:
            Inverse transformed data

        Example:
            >>> original = transformer.inverse_transform(transformed)
        """
        if not self._fitted:
            raise ValueError("Transformer must be fitted before inverse_transform")

        original = []
        for row in data:
            original_row = []
            for i, val in enumerate(row):
                original_row.append(val * self._std[i] + self._mean[i])
            original.append(original_row)
        return original


class OneHotEncoder(FeatureTransformer):
    """One-hot encoding.

    This class implements one-hot encoding for categorical features.

    Attributes:
        _categories: Categories per feature
        _n_features: Number of features to encode

    Example:
        >>> transformer = OneHotEncoder()
        >>> transformed = transformer.fit_transform([[0], [1], [2]])
    """

    def __init__(metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a OneHotEncoder.

        Args:
            metadata: Additional metadata

        Example:
            >>> transformer = OneHotEncoder()
        """
        super().__init__("one_hot_encoder", metadata)
        self._categories: List[List[Any]] = []
        self._n_features: int = 0

    def fit(self, data: List[List[Any]]) -> "OneHotEncoder":
        """Fit the encoder to data.

        Args:
            data: Training data (categorical)

        Returns:
            Self for method chaining

        Example:
            >>> transformer.fit([[0], [1], [2]])
        """
        if not data:
            raise ValueError("Data cannot be empty")

        self._n_features = len(data[0])
        self._categories = []

        for i in range(self._n_features):
            unique_values = sorted(set(row[i] for row in data))
            self._categories.append(unique_values)

        self._fitted = True
        return self

    def transform(self, data: List[List[Any]]) -> List[List[float]]:
        """Transform the data.

        Args:
            data: Data to transform

        Returns:
            Transformed data (one-hot encoded)

        Example:
            >>> transformed = transformer.transform([[0], [1], [2]])
        """
        if not self._fitted:
            raise ValueError("Transformer must be fitted before transform")

        transformed = []
        for row in data:
            encoded_row = []
            for i, val in enumerate(row):
                categories = self._categories[i]
                one_hot = [0.0] * len(categories)
                if val in categories:
                    one_hot[categories.index(val)] = 1.0
                encoded_row.extend(one_hot)
            transformed.append(encoded_row)
        return transformed

    def inverse_transform(self, data: List[List[float]]) -> List[List[Any]]:
        """Inverse transform the data.

        Args:
            data: Data to inverse transform

        Returns:
            Inverse transformed data

        Example:
            >>> original = transformer.inverse_transform(transformed)
        """
        if not self._fitted:
            raise ValueError("Transformer must be fitted before inverse_transform")

        original = []
        for row in data:
            original_row = []
            idx = 0
            for i in range(self._n_features):
                categories = self._categories[i]
                one_hot = row[idx:idx + len(categories)]
                original_row.append(categories[one_hot.index(1.0)])
                idx += len(categories)
            original.append(original_row)
        return original


class PolynomialFeatures(FeatureTransformer):
    """Polynomial feature expansion.

    This class implements polynomial feature expansion.

    Attributes:
        _degree: Polynomial degree
        _include_bias: Whether to include bias term

    Example:
        >>> transformer = PolynomialFeatures(degree=2)
        >>> transformed = transformer.fit_transform([[1], [2], [3]])
    """

    def __init__(
        degree: int = 2,
        include_bias: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a PolynomialFeatures.

        Args:
            degree: Polynomial degree
            include_bias: Whether to include bias term
            metadata: Additional metadata

        Example:
            >>> transformer = PolynomialFeatures(degree=2)
        """
        super().__init__("polynomial_features", metadata)
        self._degree = degree
        self._include_bias = include_bias

    @property
    def degree(self) -> int:
        """Get the polynomial degree.

        Returns:
            Polynomial degree

        Example:
            >>> degree = transformer.degree
        """
        return self._degree

    def fit(self, data: List[List[float]]) -> "PolynomialFeatures":
        """Fit the transformer to data.

        Args:
            data: Training data

        Returns:
            Self for method chaining

        Example:
            >>> transformer.fit([[1], [2], [3]])
        """
        self._fitted = True
        return self

    def transform(self, data: List[List[float]]) -> List[List[float]]:
        """Transform the data.

        Args:
            data: Data to transform

        Returns:
            Transformed data with polynomial features

        Example:
            >>> transformed = transformer.transform([[1], [2], [3]])
        """
        if not self._fitted:
            raise ValueError("Transformer must be fitted before transform")

        transformed = []
        for row in data:
            poly_row = []

            if self._include_bias:
                poly_row.append(1.0)

            # Add polynomial features
            for d in range(1, self._degree + 1):
                for val in row:
                    poly_row.append(val ** d)

            # Add interaction terms (simplified)
            if self._degree >= 2:
                for i in range(len(row)):
                    for j in range(i + 1, len(row)):
                        poly_row.append(row[i] * row[j])

            transformed.append(poly_row)
        return transformed

    def inverse_transform(self, data: List[List[float]]) -> List[List[float]]:
        """Inverse transform is not supported for polynomial features.

        Args:
            data: Data to inverse transform

        Returns:
            Original data (first n_features columns)

        Example:
            >>> original = transformer.inverse_transform(transformed)
        """
        raise NotImplementedError("Inverse transform not supported for polynomial features")


__all__ = [
    "FeatureTransformer",
    "Normalization",
    "Standardization",
    "OneHotEncoder",
    "PolynomialFeatures",
]
