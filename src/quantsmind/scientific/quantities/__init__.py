"""
Quantities Package

This package provides quantity management for the Scientific package.

Purpose
-------
Provide comprehensive quantity definitions and operations.

Modules
-------
- quantity: Base quantity class
- scalar: Scalar quantity
- vector_quantity: Vector quantity
- tensor_quantity: Tensor quantity
"""

from __future__ import annotations

from quantsmind.scientific.quantities.quantity import Quantity
from quantsmind.scientific.quantities.scalar import ScalarQuantity
from quantsmind.scientific.quantities.tensor_quantity import TensorQuantity
from quantsmind.scientific.quantities.vector_quantity import VectorQuantity

__all__ = [
    "Quantity",
    "ScalarQuantity",
    "VectorQuantity",
    "TensorQuantity",
]
