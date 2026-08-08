"""
Simulation Dataset Module

This module provides simulation dataset definitions for the Knowledge package.

Purpose
-------
Provide simulation dataset management with simulation output support.

Responsibilities
----------------
- Define simulation dataset structure
- Support simulation data
- Support simulation metadata
- Support simulation operations
- Support simulation validation

Dependencies
------------
typing (standard library)
quantsmind.knowledge.dataset.dataset (dataset)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.knowledge.dataset.dataset import Dataset
from quantsmind.knowledge.enums import DatasetType
from quantsmind.knowledge.exceptions import DatasetError
from quantsmind.knowledge.types import (
    DatasetData,
    DatasetSchema,
    ValidationResult,
)


class SimulationDataset(Dataset):
    """Concrete implementation of a simulation dataset.

    This class provides simulation dataset functionality with simulation output support.

    Attributes:
        _simulations: Simulation records
        _simulation_type: Simulation type
        _time_steps: Number of time steps
        _parameters: Simulation parameters

    Example:
        >>> dataset = SimulationDataset("simulation_data", simulation_type="monte_carlo")
        >>> dataset.add_simulation({"parameters": {"n": 1000}, "results": [1, 2, 3]})
    """

    def __init__(
        self,
        name: str,
        simulation_type: str = "generic",
        schema: Optional[DatasetSchema] = None,
        data: Optional[DatasetData] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a SimulationDataset.

        Args:
            name: Dataset name
            simulation_type: Simulation type
            schema: Dataset schema
            data: Dataset data
            metadata: Dataset metadata

        Example:
            >>> dataset = SimulationDataset("simulation_data", simulation_type="monte_carlo")
        """
        super().__init__(
            name=name,
            dataset_type=DatasetType.SIMULATION,
            schema=schema,
            data=data,
            metadata=metadata,
        )
        self._simulation_type = simulation_type
        self._time_steps = 0
        self._parameters: Dict[str, Any] = {}
        self._simulations: List[Dict[str, Any]] = []

    @property
    def simulation_type(self) -> str:
        """Get the simulation type.

        Returns:
            Simulation type

        Example:
            >>> sim_type = dataset.simulation_type
        """
        return self._simulation_type

    @property
    def time_steps(self) -> int:
        """Get the number of time steps.

        Returns:
            Number of time steps

        Example:
            >>> steps = dataset.time_steps
        """
        return self._time_steps

    @property
    def parameters(self) -> Dict[str, Any]:
        """Get the simulation parameters.

        Returns:
            Simulation parameters

        Example:
            >>> params = dataset.parameters
        """
        return self._parameters.copy()

    @property
    def simulations(self) -> List[Dict[str, Any]]:
        """Get the simulations.

        Returns:
            Simulation records

        Example:
            >>> simulations = dataset.simulations
        """
        return self._simulations.copy()

    def add_simulation(self, simulation: Dict[str, Any]) -> None:
        """Add a simulation to the dataset.

        Args:
            simulation: Simulation data

        Raises:
            DatasetError: If simulation is invalid

        Example:
            >>> dataset.add_simulation({"parameters": {"n": 1000}, "results": [1, 2, 3]})
        """
        if not isinstance(simulation, dict):
            raise DatasetError("Simulation must be a dictionary", {"simulation": simulation})

        parameters = simulation.get("parameters")
        results = simulation.get("results")

        if parameters is None:
            raise DatasetError("Simulation must have parameters", {"simulation": simulation})

        if results is None:
            raise DatasetError("Simulation must have results", {"simulation": simulation})

        self._simulations.append(simulation)
        self._time_steps = max(self._time_steps, len(results) if isinstance(results, list) else 1)
        self._updated_at = self._updated_at

    def add_simulations(self, simulations: List[Dict[str, Any]]) -> None:
        """Add multiple simulations to the dataset.

        Args:
            simulations: Simulation data list

        Example:
            >>> dataset.add_simulations([{"parameters": {"n": 1000}, "results": [1, 2, 3]}])
        """
        for simulation in simulations:
            self.add_simulation(simulation)

    def set_parameter(self, key: str, value: Any) -> None:
        """Set a simulation parameter.

        Args:
            key: Parameter key
            value: Parameter value

        Example:
            >>> dataset.set_parameter("n", 1000)
        """
        self._parameters[key] = value

    def get_simulation_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Get simulation by index.

        Args:
            index: Simulation index

        Returns:
            Simulation data or None

        Example:
            >>> simulation = dataset.get_simulation_by_index(0)
        """
        if 0 <= index < len(self._simulations):
            return self._simulations[index]
        return None

    def get_simulations_by_parameter(self, key: str, value: Any) -> List[Dict[str, Any]]:
        """Get simulations with specific parameter value.

        Args:
            key: Parameter key
            value: Parameter value

        Returns:
            Simulation records

        Example:
            >>> simulations = dataset.get_simulations_by_parameter("n", 1000)
        """
        return [
            sim for sim in self._simulations
            if sim.get("parameters", {}).get(key) == value
        ]

    def calculate_aggregate_statistics(self) -> Dict[str, Any]:
        """Calculate aggregate statistics across all simulations.

        Returns:
            Statistics dictionary

        Example:
            >>> stats = dataset.calculate_aggregate_statistics()
        """
        if not self._simulations:
            return {}

        all_results = []
        for sim in self._simulations:
            results = sim.get("results", [])
            if isinstance(results, list):
                all_results.extend(results)
            else:
                all_results.append(results)

        if not all_results:
            return {}

        numeric_results = [r for r in all_results if isinstance(r, (int, float))]

        if not numeric_results:
            return {}

        return {
            "total_simulations": len(self._simulations),
            "total_results": len(all_results),
            "mean": sum(numeric_results) / len(numeric_results),
            "min": min(numeric_results),
            "max": max(numeric_results),
            "std": (sum((x - sum(numeric_results) / len(numeric_results)) ** 2 for x in numeric_results) / len(numeric_results)) ** 0.5,
        }

    def get_parameter_sensitivity(self, parameter: str) -> Dict[str, float]:
        """Analyze sensitivity to a parameter.

        Args:
            parameter: Parameter name

        Returns:
            Sensitivity analysis results

        Example:
            >>> sensitivity = dataset.get_parameter_sensitivity("n")
        """
        param_values = {}
        for sim in self._simulations:
            params = sim.get("parameters", {})
            if parameter in params:
                param_value = params[parameter]
                results = sim.get("results", [])
                if isinstance(results, list) and results:
                    mean_result = sum(results) / len(results)
                    if param_value not in param_values:
                        param_values[param_value] = []
                    param_values[param_value].append(mean_result)

        if not param_values:
            return {}

        # Calculate sensitivity
        sensitivity = {}
        for param_value, results in param_values.items():
            sensitivity[str(param_value)] = sum(results) / len(results) if results else 0

        return sensitivity

    def validate(self) -> ValidationResult:
        """Validate the simulation dataset.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = dataset.validate()
        """
        errors = []

        # Validate base dataset
        base_valid, base_errors = super().validate()
        errors.extend(base_errors)

        # Validate simulations
        for i, simulation in enumerate(self._simulations):
            if "parameters" not in simulation:
                errors.append(f"Simulation {i} missing parameters")

            if "results" not in simulation:
                errors.append(f"Simulation {i} missing results")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dataset definition

        Example:
            >>> data = dataset.to_dict()
        """
        data = super().to_dict()
        data.update({
            "simulation_type": self._simulation_type,
            "time_steps": self._time_steps,
            "parameters": self._parameters,
            "simulations_count": len(self._simulations),
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(dataset)
        """
        return f"SimulationDataset(id={self._id}, name={self._name}, type={self._simulation_type}, time_steps={self._time_steps}, simulations={len(self._simulations)})"


# Export
__all__ = [
    "SimulationDataset",
]
