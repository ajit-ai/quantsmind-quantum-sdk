"""
Loss Functions Module

This module provides loss function implementations for the QuantsMind SDK.

Purpose
-------
Provide common loss functions used in machine learning.

Classes
-------
LossFunction: Base loss function class
MSELoss: Mean Squared Error loss
MAELoss: Mean Absolute Error loss
CrossEntropyLoss: Cross Entropy loss
HingeLoss: Hinge loss
HuberLoss: Huber loss

Responsibilities
----------------
- Compute loss values
- Compute gradients
- Support batch operations
- Handle different loss types

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import math


class LossFunction:
    """Base loss function class.

    This class provides the base functionality for loss functions.

    Attributes:
        _name: Loss function name
        _reduction: Reduction method (none, mean, sum)
        _metadata: Additional metadata

    Example:
        >>> loss_fn = LossFunction("base")
        >>> loss = loss_fn.compute([1, 2], [1.1, 1.9])
    """

    def __init__(
        self,
        name: str,
        reduction: str = "mean",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a LossFunction.

        Args:
            name: Loss function name
            reduction: Reduction method (none, mean, sum)
            metadata: Additional metadata

        Example:
            >>> loss_fn = LossFunction("base")
        """
        self._name = name
        self._reduction = reduction
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the loss function name.

        Returns:
            Loss function name

        Example:
            >>> name = loss_fn.name
        """
        return self._name

    @property
    def reduction(self) -> str:
        """Get the reduction method.

        Returns:
            Reduction method

        Example:
            >>> reduction = loss_fn.reduction
        """
        return self._reduction

    def compute(
        self,
        predictions: List[float],
        targets: List[float],
    ) -> float:
        """Compute the loss.

        Args:
            predictions: Predicted values
            targets: Target values

        Returns:
            Loss value

        Example:
            >>> loss = loss_fn.compute([1, 2], [1.1, 1.9])
        """
        if len(predictions) != len(targets):
            raise ValueError("Predictions and targets must have same length")

        losses = self._compute_elementwise(predictions, targets)

        if self._reduction == "mean":
            return sum(losses) / len(losses)
        elif self._reduction == "sum":
            return sum(losses)
        else:
            return losses[0] if len(losses) == 1 else losses

    def _compute_elementwise(
        self,
        predictions: List[float],
        targets: List[float],
    ) -> List[float]:
        """Compute elementwise losses.

        Args:
            predictions: Predicted values
            targets: Target values

        Returns:
            List of elementwise losses

        Example:
            >>> losses = loss_fn._compute_elementwise([1, 2], [1.1, 1.9])
        """
        raise NotImplementedError("Subclasses must implement _compute_elementwise")

    def gradient(
        self,
        predictions: List[float],
        targets: List[float],
    ) -> List[float]:
        """Compute the gradient of the loss.

        Args:
            predictions: Predicted values
            targets: Target values

        Returns:
            Gradient values

        Example:
            >>> grad = loss_fn.gradient([1, 2], [1.1, 1.9])
        """
        raise NotImplementedError("Subclasses must implement gradient")

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(loss_fn)
        """
        return f"LossFunction(name={self._name}, reduction={self._reduction})"


class MSELoss(LossFunction):
    """Mean Squared Error loss.

    This class implements the MSE loss function: (y_pred - y_target)^2

    Example:
        >>> loss_fn = MSELoss()
        >>> loss = loss_fn.compute([1, 2], [1.1, 1.9])
    """

    def __init__(reduction: str = "mean", metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize an MSELoss.

        Args:
            reduction: Reduction method
            metadata: Additional metadata

        Example:
            >>> loss_fn = MSELoss()
        """
        super().__init__("mse", reduction, metadata)

    def _compute_elementwise(
        self,
        predictions: List[float],
        targets: List[float],
    ) -> List[float]:
        """Compute elementwise MSE losses.

        Args:
            predictions: Predicted values
            targets: Target values

        Returns:
            List of elementwise losses

        Example:
            >>> losses = loss_fn._compute_elementwise([1, 2], [1.1, 1.9])
        """
        return [(p - t) ** 2 for p, t in zip(predictions, targets)]

    def gradient(
        self,
        predictions: List[float],
        targets: List[float],
    ) -> List[float]:
        """Compute the gradient.

        Args:
            predictions: Predicted values
            targets: Target values

        Returns:
            Gradient values

        Example:
            >>> grad = loss_fn.gradient([1, 2], [1.1, 1.9])
        """
        grad = [2 * (p - t) for p, t in zip(predictions, targets)]

        if self._reduction == "mean":
            n = len(predictions)
            grad = [g / n for g in grad]

        return grad


class MAELoss(LossFunction):
    """Mean Absolute Error loss.

    This class implements the MAE loss function: |y_pred - y_target|

    Example:
        >>> loss_fn = MAELoss()
        >>> loss = loss_fn.compute([1, 2], [1.1, 1.9])
    """

    def __init__(reduction: str = "mean", metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize an MAELoss.

        Args:
            reduction: Reduction method
            metadata: Additional metadata

        Example:
            >>> loss_fn = MAELoss()
        """
        super().__init__("mae", reduction, metadata)

    def _compute_elementwise(
        self,
        predictions: List[float],
        targets: List[float],
    ) -> List[float]:
        """Compute elementwise MAE losses.

        Args:
            predictions: Predicted values
            targets: Target values

        Returns:
            List of elementwise losses

        Example:
            >>> losses = loss_fn._compute_elementwise([1, 2], [1.1, 1.9])
        """
        return [abs(p - t) for p, t in zip(predictions, targets)]

    def gradient(
        self,
        predictions: List[float],
        targets: List[float],
    ) -> List[float]:
        """Compute the gradient.

        Args:
            predictions: Predicted values
            targets: Target values

        Returns:
            Gradient values

        Example:
            >>> grad = loss_fn.gradient([1, 2], [1.1, 1.9])
        """
        grad = [1.0 if p > t else -1.0 if p < t else 0.0 for p, t in zip(predictions, targets)]

        if self._reduction == "mean":
            n = len(predictions)
            grad = [g / n for g in grad]

        return grad


class CrossEntropyLoss(LossFunction):
    """Cross Entropy loss.

    This class implements the cross entropy loss for classification.

    Attributes:
        _epsilon: Small constant for numerical stability

    Example:
        >>> loss_fn = CrossEntropyLoss()
        >>> loss = loss_fn.compute([0.9, 0.1], [1, 0])
    """

    def __init__(
        epsilon: float = 1e-10,
        reduction: str = "mean",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a CrossEntropyLoss.

        Args:
            epsilon: Small constant for numerical stability
            reduction: Reduction method
            metadata: Additional metadata

        Example:
            >>> loss_fn = CrossEntropyLoss()
        """
        super().__init__("cross_entropy", reduction, metadata)
        self._epsilon = epsilon

    def _compute_elementwise(
        self,
        predictions: List[float],
        targets: List[float],
    ) -> List[float]:
        """Compute elementwise cross entropy losses.

        Args:
            predictions: Predicted probabilities
            targets: Target labels (0 or 1)

        Returns:
            List of elementwise losses

        Example:
            >>> losses = loss_fn._compute_elementwise([0.9, 0.1], [1, 0])
        """
        losses = []
        for p, t in zip(predictions, targets):
            p_clipped = max(self._epsilon, min(1 - self._epsilon, p))
            if t == 1:
                losses.append(-math.log(p_clipped))
            else:
                losses.append(-math.log(1 - p_clipped))
        return losses

    def gradient(
        self,
        predictions: List[float],
        targets: List[float],
    ) -> List[float]:
        """Compute the gradient.

        Args:
            predictions: Predicted probabilities
            targets: Target labels

        Returns:
            Gradient values

        Example:
            >>> grad = loss_fn.gradient([0.9, 0.1], [1, 0])
        """
        grad = []
        for p, t in zip(predictions, targets):
            p_clipped = max(self._epsilon, min(1 - self._epsilon, p))
            if t == 1:
                grad.append(-1 / p_clipped)
            else:
                grad.append(1 / (1 - p_clipped))

        if self._reduction == "mean":
            n = len(predictions)
            grad = [g / n for g in grad]

        return grad


class HingeLoss(LossFunction):
    """Hinge loss for SVM.

    This class implements the hinge loss: max(0, 1 - y * y_pred)

    Example:
        >>> loss_fn = HingeLoss()
        >>> loss = loss_fn.compute([0.8, -0.3], [1, -1])
    """

    def __init__(reduction: str = "mean", metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a HingeLoss.

        Args:
            reduction: Reduction method
            metadata: Additional metadata

        Example:
            >>> loss_fn = HingeLoss()
        """
        super().__init__("hinge", reduction, metadata)

    def _compute_elementwise(
        self,
        predictions: List[float],
        targets: List[float],
    ) -> List[float]:
        """Compute elementwise hinge losses.

        Args:
            predictions: Predicted values
            targets: Target labels (-1 or 1)

        Returns:
            List of elementwise losses

        Example:
            >>> losses = loss_fn._compute_elementwise([0.8, -0.3], [1, -1])
        """
        return [max(0, 1 - t * p) for p, t in zip(predictions, targets)]

    def gradient(
        self,
        predictions: List[float],
        targets: List[float],
    ) -> List[float]:
        """Compute the gradient.

        Args:
            predictions: Predicted values
            targets: Target labels

        Returns:
            Gradient values

        Example:
            >>> grad = loss_fn.gradient([0.8, -0.3], [1, -1])
        """
        grad = []
        for p, t in zip(predictions, targets):
            if 1 - t * p > 0:
                grad.append(-t)
            else:
                grad.append(0.0)

        if self._reduction == "mean":
            n = len(predictions)
            grad = [g / n for g in grad]

        return grad


class HuberLoss(LossFunction):
    """Huber loss.

    This class implements the Huber loss, which is less sensitive to outliers.

    Attributes:
        _delta: Threshold parameter

    Example:
        >>> loss_fn = HuberLoss(delta=1.0)
        >>> loss = loss_fn.compute([1, 2], [1.1, 1.9])
    """

    def __init__(
        delta: float = 1.0,
        reduction: str = "mean",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a HuberLoss.

        Args:
            delta: Threshold parameter
            reduction: Reduction method
            metadata: Additional metadata

        Example:
            >>> loss_fn = HuberLoss(delta=1.0)
        """
        super().__init__("huber", reduction, metadata)
        self._delta = delta

    def _compute_elementwise(
        self,
        predictions: List[float],
        targets: List[float],
    ) -> List[float]:
        """Compute elementwise Huber losses.

        Args:
            predictions: Predicted values
            targets: Target values

        Returns:
            List of elementwise losses

        Example:
            >>> losses = loss_fn._compute_elementwise([1, 2], [1.1, 1.9])
        """
        losses = []
        for p, t in zip(predictions, targets):
            diff = abs(p - t)
            if diff <= self._delta:
                losses.append(0.5 * diff ** 2)
            else:
                losses.append(self._delta * diff - 0.5 * self._delta ** 2)
        return losses

    def gradient(
        self,
        predictions: List[float],
        targets: List[float],
    ) -> List[float]:
        """Compute the gradient.

        Args:
            predictions: Predicted values
            targets: Target values

        Returns:
            Gradient values

        Example:
            >>> grad = loss_fn.gradient([1, 2], [1.1, 1.9])
        """
        grad = []
        for p, t in zip(predictions, targets):
            diff = p - t
            if abs(diff) <= self._delta:
                grad.append(diff)
            else:
                grad.append(self._delta if diff > 0 else -self._delta)

        if self._reduction == "mean":
            n = len(predictions)
            grad = [g / n for g in grad]

        return grad


__all__ = [
    "LossFunction",
    "MSELoss",
    "MAELoss",
    "CrossEntropyLoss",
    "HingeLoss",
    "HuberLoss",
]
