"""
Simulation Engine Module

This module provides simulation engine functionality for the QuantsMind SDK.

Purpose
-------
Provide comprehensive simulation capabilities for mathematical and scientific modeling.

Classes
-------
SimulationEngine: Simulation engine
Simulator: Base simulator class
SimulationResult: Simulation result container
Experiment: Experiment management

Responsibilities
----------------
- Manage simulation execution
- Track simulation state
- Store simulation results
- Support experiment design

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class SimulationEngine:
    """Simulation engine.

    This class provides the core simulation engine for running simulations.

    Attributes:
        _name: Engine name
        _simulators: Registered simulators
        _simulation_history: History of simulations
        _metadata: Additional metadata

    Example:
        >>> engine = SimulationEngine()
        >>> result = engine.run_simulation("my_sim", {"param": 1.0})
    """

    def __init__(
        self,
        name: str = "default",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a SimulationEngine.

        Args:
            name: Engine name
            metadata: Additional metadata

        Example:
            >>> engine = SimulationEngine()
        """
        self._name = name
        self._simulators: dict[str, Callable] = {}
        self._simulation_history: list[dict[str, Any]] = []
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the engine name.

        Returns:
            Engine name

        Example:
            >>> name = engine.name
        """
        return self._name

    def register_simulator(
        self,
        simulator_name: str,
        simulator: Callable,
    ) -> None:
        """Register a simulator.

        Args:
            simulator_name: Name of the simulator
            simulator: Simulator function

        Example:
            >>> engine.register_simulator("my_sim", my_simulator_func)
        """
        self._simulators[simulator_name] = simulator

    def run_simulation(
        self,
        simulator_name: str,
        parameters: dict[str, Any],
    ) -> SimulationResult:
        """Run a simulation.

        Args:
            simulator_name: Name of the simulator
            parameters: Simulation parameters

        Returns:
            Simulation result

        Example:
            >>> result = engine.run_simulation("my_sim", {"param": 1.0})
        """
        if simulator_name not in self._simulators:
            raise ValueError(f"Simulator {simulator_name} not registered")

        start_time = time.time()
        simulator = self._simulators[simulator_name]

        try:
            output = simulator(parameters)
            success = True
            error = None
        except Exception as e:
            output = None
            success = False
            error = str(e)

        end_time = time.time()
        duration = end_time - start_time

        result = SimulationResult(
            simulator_name=simulator_name,
            parameters=parameters,
            output=output,
            success=success,
            error=error,
            duration=duration,
        )

        self._simulation_history.append({
            "simulator_name": simulator_name,
            "parameters": parameters,
            "result": result,
            "timestamp": end_time,
        })

        return result

    def get_simulation_history(self) -> list[dict[str, Any]]:
        """Get the simulation history.

        Returns:
            List of past simulations

        Example:
            >>> history = engine.get_simulation_history()
        """
        return self._simulation_history.copy()

    def clear_history(self) -> None:
        """Clear the simulation history.

        Example:
            >>> engine.clear_history()
        """
        self._simulation_history = []

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(engine)
        """
        return f"SimulationEngine(name={self._name}, simulators={len(self._simulators)})"


class Simulator:
    """Base simulator class.

    This class provides the base functionality for simulators.

    Attributes:
        _name: Simulator name
        _parameters: Simulator parameters
        _state: Simulator state
        _metadata: Additional metadata

    Example:
        >>> sim = Simulator("my_sim")
        >>> result = sim.run({"param": 1.0})
    """

    def __init__(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Simulator.

        Args:
            name: Simulator name
            metadata: Additional metadata

        Example:
            >>> sim = Simulator("my_sim")
        """
        self._name = name
        self._parameters: dict[str, Any] = {}
        self._state: dict[str, Any] = {}
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the simulator name.

        Returns:
            Simulator name

        Example:
            >>> name = sim.name
        """
        return self._name

    def set_parameters(self, parameters: dict[str, Any]) -> None:
        """Set simulator parameters.

        Args:
            parameters: Parameters to set

        Example:
            >>> sim.set_parameters({"param": 1.0})
        """
        self._parameters.update(parameters)

    def get_state(self) -> dict[str, Any]:
        """Get the simulator state.

        Returns:
            Current state

        Example:
            >>> state = sim.get_state()
        """
        return self._state.copy()

    def initialize(self, parameters: dict[str, Any]) -> None:
        """Initialize the simulator.

        Args:
            parameters: Initialization parameters

        Example:
            >>> sim.initialize({"param": 1.0})
        """
        self._parameters = parameters.copy()
        self._state = {"initialized": True}

    def step(self) -> dict[str, Any]:
        """Perform one simulation step.

        Returns:
            Step result

        Example:
            >>> result = sim.step()
        """
        raise NotImplementedError("Subclasses must implement step")

    def run(self, parameters: dict[str, Any], steps: int = 1) -> SimulationResult:
        """Run the simulation.

        Args:
            parameters: Simulation parameters
            steps: Number of steps

        Returns:
            Simulation result

        Example:
            >>> result = sim.run({"param": 1.0}, steps=100)
        """
        self.initialize(parameters)

        outputs = []
        for _ in range(steps):
            output = self.step()
            outputs.append(output)

        return SimulationResult(
            simulator_name=self._name,
            parameters=parameters,
            output=outputs,
            success=True,
            error=None,
            duration=0.0,
        )

    def reset(self) -> None:
        """Reset the simulator.

        Example:
            >>> sim.reset()
        """
        self._state = {}
        self._parameters = {}

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(sim)
        """
        return f"Simulator(name={self._name})"


class SimulationResult:
    """Simulation result container.

    This class stores the results of a simulation.

    Attributes:
        _simulator_name: Name of the simulator
        _parameters: Simulation parameters
        _output: Simulation output
        _success: Whether simulation succeeded
        _error: Error message if failed
        _duration: Simulation duration

    Example:
        >>> result = SimulationResult("my_sim", {"param": 1.0}, [1, 2, 3], True, None, 1.5)
    """

    def __init__(
        self,
        simulator_name: str,
        parameters: dict[str, Any],
        output: Any,
        success: bool,
        error: str | None,
        duration: float,
    ) -> None:
        """Initialize a SimulationResult.

        Args:
            simulator_name: Name of the simulator
            parameters: Simulation parameters
            output: Simulation output
            success: Whether simulation succeeded
            error: Error message if failed
            duration: Simulation duration

        Example:
            >>> result = SimulationResult("my_sim", {"param": 1.0}, [1, 2, 3], True, None, 1.5)
        """
        self._simulator_name = simulator_name
        self._parameters = parameters
        self._output = output
        self._success = success
        self._error = error
        self._duration = duration

    @property
    def simulator_name(self) -> str:
        """Get the simulator name.

        Returns:
            Simulator name

        Example:
            >>> name = result.simulator_name
        """
        return self._simulator_name

    @property
    def parameters(self) -> dict[str, Any]:
        """Get the simulation parameters.

        Returns:
            Parameters

        Example:
            >>> params = result.parameters
        """
        return self._parameters.copy()

    @property
    def output(self) -> Any:
        """Get the simulation output.

        Returns:
            Output

        Example:
            >>> output = result.output
        """
        return self._output

    @property
    def success(self) -> bool:
        """Check if simulation succeeded.

        Returns:
            Success status

        Example:
            >>> success = result.success
        """
        return self._success

    @property
    def error(self) -> str | None:
        """Get the error message.

        Returns:
            Error message

        Example:
            >>> error = result.error
        """
        return self._error

    @property
    def duration(self) -> float:
        """Get the simulation duration.

        Returns:
            Duration in seconds

        Example:
            >>> duration = result.duration
        """
        return self._duration

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary.

        Returns:
            Dictionary representation

        Example:
            >>> data = result.to_dict()
        """
        return {
            "simulator_name": self._simulator_name,
            "parameters": self._parameters,
            "output": self._output,
            "success": self._success,
            "error": self._error,
            "duration": self._duration,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(result)
        """
        return f"SimulationResult(simulator={self._simulator_name}, success={self._success})"


class Experiment:
    """Experiment management.

    This class manages experimental simulations with parameter sweeps.

    Attributes:
        _name: Experiment name
        _parameter_sweeps: Parameter sweep configurations
        _results: Experiment results
        _metadata: Additional metadata

    Example:
        >>> exp = Experiment("my_exp")
        >>> exp.add_parameter_sweep("param", [1.0, 2.0, 3.0])
        >>> results = exp.run(engine, "my_sim")
    """

    def __init__(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an Experiment.

        Args:
            name: Experiment name
            metadata: Additional metadata

        Example:
            >>> exp = Experiment("my_exp")
        """
        self._name = name
        self._parameter_sweeps: dict[str, list[Any]] = {}
        self._results: list[SimulationResult] = []
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the experiment name.

        Returns:
            Experiment name

        Example:
            >>> name = exp.name
        """
        return self._name

    def add_parameter_sweep(
        self,
        parameter_name: str,
        values: list[Any],
    ) -> None:
        """Add a parameter sweep.

        Args:
            parameter_name: Parameter to sweep
            values: Parameter values

        Example:
            >>> exp.add_parameter_sweep("param", [1.0, 2.0, 3.0])
        """
        self._parameter_sweeps[parameter_name] = values

    def generate_parameter_combinations(self) -> list[dict[str, Any]]:
        """Generate all parameter combinations.

        Returns:
            List of parameter dictionaries

        Example:
            >>> combinations = exp.generate_parameter_combinations()
        """
        if not self._parameter_sweeps:
            return [{}]

        # Generate Cartesian product of parameter values
        combinations = [{}]

        for param, values in self._parameter_sweeps.items():
            new_combinations = []
            for combo in combinations:
                for value in values:
                    new_combo = combo.copy()
                    new_combo[param] = value
                    new_combinations.append(new_combo)
            combinations = new_combinations

        return combinations

    def run(
        self,
        engine: SimulationEngine,
        simulator_name: str,
        base_parameters: dict[str, Any] | None = None,
    ) -> list[SimulationResult]:
        """Run the experiment.

        Args:
            engine: Simulation engine
            simulator_name: Name of simulator
            base_parameters: Base parameters

        Returns:
            List of simulation results

        Example:
            >>> results = exp.run(engine, "my_sim")
        """
        if base_parameters is None:
            base_parameters = {}

        combinations = self.generate_parameter_combinations()
        results = []

        for combo in combinations:
            parameters = base_parameters.copy()
            parameters.update(combo)

            result = engine.run_simulation(simulator_name, parameters)
            results.append(result)
            self._results.append(result)

        return results

    def get_results(self) -> list[SimulationResult]:
        """Get experiment results.

        Returns:
            List of results

        Example:
            >>> results = exp.get_results()
        """
        return self._results.copy()

    def clear_results(self) -> None:
        """Clear experiment results.

        Example:
            >>> exp.clear_results()
        """
        self._results = []

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(exp)
        """
        return f"Experiment(name={self._name}, results={len(self._results)})"


__all__ = [
    "SimulationEngine",
    "Simulator",
    "SimulationResult",
    "Experiment",
]
