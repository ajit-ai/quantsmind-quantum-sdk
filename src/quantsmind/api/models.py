"""
API Models Module

This module provides Pydantic models for API validation in the QuantsMind SDK.

Purpose
-------
Provide data models for API request/response validation.

Classes
-------
- PolynomialRequest: Polynomial operation request
- MatrixRequest: Matrix operation request
- OptimizationRequest: Optimization request
- SimulationRequest: Simulation request

Responsibilities
----------------
- Validate API requests
- Define response schemas
- Provide type safety for API

Dependencies
------------
typing (standard library)
pydantic (external)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator


class PolynomialRequest(BaseModel):
    """Polynomial operation request model.

    Attributes:
        coefficients: Polynomial coefficients
        operation: Operation to perform
        x: Evaluation point (for evaluation)

    Example:
        >>> request = PolynomialRequest(coefficients=[1, 0, -4], operation="evaluate", x=2)
    """

    coefficients: List[float] = Field(..., description="Polynomial coefficients")
    operation: str = Field(..., description="Operation to perform")
    x: Optional[float] = Field(None, description="Evaluation point")

    @validator("operation")
    def validate_operation(cls, v: str) -> str:
        """Validate operation type.

        Args:
            v: Operation value

        Returns:
            Validated operation

        Raises:
            ValueError: If operation is invalid
        """
        valid_operations = ["evaluate", "differentiate", "integrate", "find_roots"]
        if v not in valid_operations:
            raise ValueError(f"Invalid operation. Must be one of {valid_operations}")
        return v


class MatrixRequest(BaseModel):
    """Matrix operation request model.

    Attributes:
        data: Matrix data
        operation: Operation to perform
        other_data: Other matrix data (for binary operations)

    Example:
        >>> request = MatrixRequest(data=[[1, 2], [3, 4]], operation="determinant")
    """

    data: List[List[float]] = Field(..., description="Matrix data")
    operation: str = Field(..., description="Operation to perform")
    other_data: Optional[List[List[float]]] = Field(None, description="Other matrix data")

    @validator("operation")
    def validate_operation(cls, v: str) -> str:
        """Validate operation type.

        Args:
            v: Operation value

        Returns:
            Validated operation

        Raises:
            ValueError: If operation is invalid
        """
        valid_operations = ["determinant", "inverse", "transpose", "multiply", "add", "subtract"]
        if v not in valid_operations:
            raise ValueError(f"Invalid operation. Must be one of {valid_operations}")
        return v


class OptimizationRequest(BaseModel):
    """Optimization request model.

    Attributes:
        function: Objective function (as string representation)
        method: Optimization method
        initial_point: Initial point for optimization
        bounds: Optimization bounds
        parameters: Additional parameters

    Example:
        >>> request = OptimizationRequest(function="x**2", method="gradient_descent", initial_point=1.0)
    """

    function: str = Field(..., description="Objective function")
    method: str = Field(..., description="Optimization method")
    initial_point: Optional[float] = Field(None, description="Initial point")
    bounds: Optional[List[float]] = Field(None, description="Optimization bounds")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional parameters")

    @validator("method")
    def validate_method(cls, v: str) -> str:
        """Validate optimization method.

        Args:
            v: Method value

        Returns:
            Validated method

        Raises:
            ValueError: If method is invalid
        """
        valid_methods = ["gradient_descent", "newton", "adam", "genetic", "particle_swarm"]
        if v not in valid_methods:
            raise ValueError(f"Invalid method. Must be one of {valid_methods}")
        return v


class SimulationRequest(BaseModel):
    """Simulation request model.

    Attributes:
        simulator_name: Name of simulator
        parameters: Simulation parameters
        steps: Number of simulation steps

    Example:
        >>> request = SimulationRequest(simulator_name="my_sim", parameters={"param": 1.0}, steps=100)
    """

    simulator_name: str = Field(..., description="Name of simulator")
    parameters: Dict[str, Any] = Field(..., description="Simulation parameters")
    steps: Optional[int] = Field(1, description="Number of simulation steps")

    @validator("steps")
    def validate_steps(cls, v: int) -> int:
        """Validate number of steps.

        Args:
            v: Steps value

        Returns:
            Validated steps

        Raises:
            ValueError: If steps is invalid
        """
        if v < 1:
            raise ValueError("Steps must be at least 1")
        return v


class APIResponse(BaseModel):
    """API response model.

    Attributes:
        success: Whether the operation succeeded
        data: Response data
        error: Error message if failed
        metadata: Additional metadata

    Example:
        >>> response = APIResponse(success=True, data={"result": 4}, error=None)
    """

    success: bool = Field(..., description="Whether the operation succeeded")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class HealthResponse(BaseModel):
    """Health check response model.

    Attributes:
        status: Health status
        version: SDK version
        services: Service status

    Example:
        >>> response = HealthResponse(status="healthy", version="1.0.0", services={})
    """

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="SDK version")
    services: Dict[str, str] = Field(default_factory=dict, description="Service status")


__all__ = [
    "PolynomialRequest",
    "MatrixRequest",
    "OptimizationRequest",
    "SimulationRequest",
    "APIResponse",
    "HealthResponse",
]
