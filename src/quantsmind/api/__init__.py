"""
API Package

This package provides API layer functionality for the QuantsMind SDK.

Purpose
-------
Provide REST API endpoints for accessing SDK functionality.

Modules
-------
- models: Pydantic models for API validation
- endpoints: FastAPI endpoint definitions
"""

from __future__ import annotations

from quantsmind.api.endpoints import (
    MatrixEndpoints,
    OptimizationEndpoints,
    PolynomialEndpoints,
    SimulationEndpoints,
    router,
)
from quantsmind.api.models import (
    APIResponse,
    HealthResponse,
    MatrixRequest,
    OptimizationRequest,
    PolynomialRequest,
    SimulationRequest,
)

__all__: list[str] = [
    "PolynomialRequest",
    "MatrixRequest",
    "OptimizationRequest",
    "SimulationRequest",
    "APIResponse",
    "HealthResponse",
    "router",
    "PolynomialEndpoints",
    "MatrixEndpoints",
    "OptimizationEndpoints",
    "SimulationEndpoints",
]
