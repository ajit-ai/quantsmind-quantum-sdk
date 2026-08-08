"""
Machine Learning Mathematics Package

This package provides machine learning mathematics functionality for the QuantsMind SDK.

Purpose
-------
Provide mathematical foundations for machine learning including loss functions,
activation functions, and feature transformations.

Modules
-------
- loss_functions: Loss function implementations
- activation_functions: Activation function implementations
- feature_transformation: Feature transformation implementations
"""

from __future__ import annotations

from quantsmind.ml_math.activation_functions import ActivationFunction, LeakyReLU, ReLU, Sigmoid, Softmax, Tanh
from quantsmind.ml_math.feature_transformation import (
    FeatureTransformer,
    Normalization,
    OneHotEncoder,
    PolynomialFeatures,
    Standardization,
)
from quantsmind.ml_math.loss_functions import CrossEntropyLoss, HingeLoss, HuberLoss, LossFunction, MAELoss, MSELoss

__all__: list[str] = [
    "LossFunction",
    "MSELoss",
    "MAELoss",
    "CrossEntropyLoss",
    "HingeLoss",
    "HuberLoss",
    "ActivationFunction",
    "ReLU",
    "Sigmoid",
    "Tanh",
    "Softmax",
    "LeakyReLU",
    "FeatureTransformer",
    "Normalization",
    "Standardization",
    "OneHotEncoder",
    "PolynomialFeatures",
]
