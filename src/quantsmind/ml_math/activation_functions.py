"""
Activation Functions Module

This module provides activation function implementations for the QuantsMind SDK.

Purpose
-------
Provide common activation functions used in neural networks.

Classes
-------
ActivationFunction: Base activation function class
ReLU: Rectified Linear Unit
Sigmoid: Sigmoid activation
Tanh: Hyperbolic tangent activation
Softmax: Softmax activation
LeakyReLU: Leaky ReLU activation

Responsibilities
----------------
- Compute activation values
- Compute derivatives
- Support batch operations
- Handle different activation types

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import math


class ActivationFunction:
    """Base activation function class.

    This class provides the base functionality for activation functions.

    Attributes:
        _name: Activation function name
        _metadata: Additional metadata

    Example:
        >>> act_fn = ActivationFunction("base")
        >>> output = act_fn.forward([1, -1, 2])
    """

    def __init__(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an ActivationFunction.

        Args:
            name: Activation function name
            metadata: Additional metadata

        Example:
            >>> act_fn = ActivationFunction("base")
        """
        self._name = name
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the activation function name.

        Returns:
            Activation function name

        Example:
            >>> name = act_fn.name
        """
        return self._name

    def forward(self, x: List[float]) -> List[float]:
        """Compute forward pass.

        Args:
            x: Input values

        Returns:
            Activated values

        Example:
            >>> output = act_fn.forward([1, -1, 2])
        """
        raise NotImplementedError("Subclasses must implement forward")

    def backward(self, x: List[float]) -> List[float]:
        """Compute backward pass (derivative).

        Args:
            x: Input values

        Returns:
            Derivative values

        Example:
            >>> grad = act_fn.backward([1, -1, 2])
        """
        raise NotImplementedError("Subclasses must implement backward")

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(act_fn)
        """
        return f"ActivationFunction(name={self._name})"


class ReLU(ActivationFunction):
    """Rectified Linear Unit activation.

    This class implements the ReLU activation: max(0, x)

    Example:
        >>> act_fn = ReLU()
        >>> output = act_fn.forward([1, -1, 2])
    """

    def __init__(metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a ReLU.

        Args:
            metadata: Additional metadata

        Example:
            >>> act_fn = ReLU()
        """
        super().__init__("relu", metadata)

    def forward(self, x: List[float]) -> List[float]:
        """Compute forward pass.

        Args:
            x: Input values

        Returns:
            Activated values

        Example:
            >>> output = act_fn.forward([1, -1, 2])
        """
        return [max(0, val) for val in x]

    def backward(self, x: List[float]) -> List[float]:
        """Compute backward pass.

        Args:
            x: Input values

        Returns:
            Derivative values

        Example:
            >>> grad = act_fn.backward([1, -1, 2])
        """
        return [1.0 if val > 0 else 0.0 for val in x]


class Sigmoid(ActivationFunction):
    """Sigmoid activation.

    This class implements the sigmoid activation: 1 / (1 + exp(-x))

    Example:
        >>> act_fn = Sigmoid()
        >>> output = act_fn.forward([0, 1, -1])
    """

    def __init__(metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a Sigmoid.

        Args:
            metadata: Additional metadata

        Example:
            >>> act_fn = Sigmoid()
        """
        super().__init__("sigmoid", metadata)

    def forward(self, x: List[float]) -> List[float]:
        """Compute forward pass.

        Args:
            x: Input values

        Returns:
            Activated values

        Example:
            >>> output = act_fn.forward([0, 1, -1])
        """
        return [1.0 / (1.0 + math.exp(-val)) for val in x]

    def backward(self, x: List[float]) -> List[float]:
        """Compute backward pass.

        Args:
            x: Input values

        Returns:
            Derivative values

        Example:
            >>> grad = act_fn.backward([0, 1, -1])
        """
        sigmoid_x = self.forward(x)
        return [s * (1 - s) for s in sigmoid_x]


class Tanh(ActivationFunction):
    """Hyperbolic tangent activation.

    This class implements the tanh activation: tanh(x)

    Example:
        >>> act_fn = Tanh()
        >>> output = act_fn.forward([0, 1, -1])
    """

    def __init__(metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a Tanh.

        Args:
            metadata: Additional metadata

        Example:
            >>> act_fn = Tanh()
        """
        super().__init__("tanh", metadata)

    def forward(self, x: List[float]) -> List[float]:
        """Compute forward pass.

        Args:
            x: Input values

        Returns:
            Activated values

        Example:
            >>> output = act_fn.forward([0, 1, -1])
        """
        return [math.tanh(val) for val in x]

    def backward(self, x: List[float]) -> List[float]:
        """Compute backward pass.

        Args:
            x: Input values

        Returns:
            Derivative values

        Example:
            >>> grad = act_fn.backward([0, 1, -1])
        """
        tanh_x = self.forward(x)
        return [1 - t ** 2 for t in tanh_x]


class Softmax(ActivationFunction):
    """Softmax activation.

    This class implements the softmax activation for multi-class classification.

    Example:
        >>> act_fn = Softmax()
        >>> output = act_fn.forward([1, 2, 3])
    """

    def __init__(metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a Softmax.

        Args:
            metadata: Additional metadata

        Example:
            >>> act_fn = Softmax()
        """
        super().__init__("softmax", metadata)

    def forward(self, x: List[float]) -> List[float]:
        """Compute forward pass.

        Args:
            x: Input values

        Returns:
            Activated values (probabilities)

        Example:
            >>> output = act_fn.forward([1, 2, 3])
        """
        # Subtract max for numerical stability
        max_x = max(x)
        exp_x = [math.exp(val - max_x) for val in x]
        sum_exp = sum(exp_x)
        return [e / sum_exp for e in exp_x]

    def backward(self, x: List[float]) -> List[List[float]]:
        """Compute backward pass (Jacobian).

        Args:
            x: Input values

        Returns:
            Jacobian matrix

        Example:
            >>> jacobian = act_fn.backward([1, 2, 3])
        """
        softmax_x = self.forward(x)
        n = len(softmax_x)
        jacobian = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i == j:
                    jacobian[i][j] = softmax_x[i] * (1 - softmax_x[j])
                else:
                    jacobian[i][j] = -softmax_x[i] * softmax_x[j]

        return jacobian


class LeakyReLU(ActivationFunction):
    """Leaky ReLU activation.

    This class implements the Leaky ReLU activation with a small slope for negative values.

    Attributes:
        _alpha: Slope for negative values

    Example:
        >>> act_fn = LeakyReLU(alpha=0.01)
        >>> output = act_fn.forward([1, -1, 2])
    """

    def __init__(
        alpha: float = 0.01,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a LeakyReLU.

        Args:
            alpha: Slope for negative values
            metadata: Additional metadata

        Example:
            >>> act_fn = LeakyReLU(alpha=0.01)
        """
        super().__init__("leaky_relu", metadata)
        self._alpha = alpha

    @property
    def alpha(self) -> float:
        """Get the alpha parameter.

        Returns:
            Alpha value

        Example:
            >>> alpha = act_fn.alpha
        """
        return self._alpha

    def forward(self, x: List[float]) -> List[float]:
        """Compute forward pass.

        Args:
            x: Input values

        Returns:
            Activated values

        Example:
            >>> output = act_fn.forward([1, -1, 2])
        """
        return [val if val > 0 else self._alpha * val for val in x]

    def backward(self, x: List[float]) -> List[float]:
        """Compute backward pass.

        Args:
            x: Input values

        Returns:
            Derivative values

        Example:
            >>> grad = act_fn.backward([1, -1, 2])
        """
        return [1.0 if val > 0 else self._alpha for val in x]


__all__ = [
    "ActivationFunction",
    "ReLU",
    "Sigmoid",
    "Tanh",
    "Softmax",
    "LeakyReLU",
]
