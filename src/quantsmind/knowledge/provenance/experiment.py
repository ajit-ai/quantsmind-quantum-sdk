"""
Experiment Module

This module provides experiment definitions for the Knowledge package.

Purpose
-------
Provide experiment management for provenance tracking.

Responsibilities
----------------
- Define experiment structure
- Support experiment operations
- Support experiment validation
- Support experiment metadata

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from quantsmind.knowledge.exceptions import ProvenanceError
from quantsmind.knowledge.types import ExperimentID, ValidationResult


class Experiment:
    """Concrete implementation of an experiment.

    This class provides experiment functionality for provenance tracking.

    Attributes:
        _id: Experiment ID
        _name: Experiment name
        _description: Experiment description
        _start_time: Start timestamp
        _end_time: End timestamp
        _parameters: Experiment parameters
        _results: Experiment results
        _metadata: Experiment metadata

    Example:
        >>> experiment = Experiment("exp_001", "Quantum Simulation")
        >>> experiment.start()
    """

    def __init__(
        self,
        experiment_id: ExperimentID,
        name: str,
        description: str | None = None,
        parameters: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an Experiment.

        Args:
            experiment_id: Experiment ID
            name: Experiment name
            description: Experiment description
            parameters: Experiment parameters
            metadata: Experiment metadata

        Example:
            >>> experiment = Experiment("exp_001", "Quantum Simulation")
        """
        if not experiment_id:
            raise ProvenanceError("Experiment ID cannot be empty", {"experiment_id": experiment_id})

        if not name:
            raise ProvenanceError("Experiment name cannot be empty", {"name": name})

        self._id = experiment_id
        self._name = name
        self._description = description
        self._start_time: datetime | None = None
        self._end_time: datetime | None = None
        self._parameters = parameters or {}
        self._results: dict[str, Any] = {}
        self._metadata = metadata or {}

    @property
    def id(self) -> ExperimentID:
        """Get the experiment ID.

        Returns:
            Experiment ID

        Example:
            >>> eid = experiment.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the experiment name.

        Returns:
            Experiment name

        Example:
            >>> name = experiment.name
        """
        return self._name

    @property
    def description(self) -> str | None:
        """Get the experiment description.

        Returns:
            Experiment description

        Example:
            >>> description = experiment.description
        """
        return self._description

    @property
    def start_time(self) -> datetime | None:
        """Get the start timestamp.

        Returns:
            Start timestamp

        Example:
            >>> start = experiment.start_time
        """
        return self._start_time

    @property
    def end_time(self) -> datetime | None:
        """Get the end timestamp.

        Returns:
            End timestamp

        Example:
            >>> end = experiment.end_time
        """
        return self._end_time

    @property
    def parameters(self) -> dict[str, Any]:
        """Get the experiment parameters.

        Returns:
            Experiment parameters

        Example:
            >>> params = experiment.parameters
        """
        return self._parameters.copy()

    @property
    def results(self) -> dict[str, Any]:
        """Get the experiment results.

        Returns:
            Experiment results

        Example:
            >>> results = experiment.results
        """
        return self._results.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the experiment metadata.

        Returns:
            Experiment metadata

        Example:
            >>> metadata = experiment.metadata
        """
        return self._metadata.copy()

    def start(self) -> None:
        """Start the experiment.

        Example:
            >>> experiment.start()
        """
        self._start_time = datetime.utcnow()

    def end(self) -> None:
        """End the experiment.

        Example:
            >>> experiment.end()
        """
        self._end_time = datetime.utcnow()

    def set_parameter(self, key: str, value: Any) -> None:
        """Set an experiment parameter.

        Args:
            key: Parameter key
            value: Parameter value

        Example:
            >>> experiment.set_parameter("temperature", 300)
        """
        self._parameters[key] = value

    def add_result(self, key: str, value: Any) -> None:
        """Add a result to the experiment.

        Args:
            key: Result key
            value: Result value

        Example:
            >>> experiment.add_result("success_rate", 0.95)
        """
        self._results[key] = value

    def get_duration(self) -> float | None:
        """Get the experiment duration in seconds.

        Returns:
            Duration in seconds or None

        Example:
            >>> duration = experiment.get_duration()
        """
        if self._start_time and self._end_time:
            return (self._end_time - self._start_time).total_seconds()
        return None

    def is_running(self) -> bool:
        """Check if the experiment is running.

        Returns:
            True if running

        Example:
            >>> running = experiment.is_running()
        """
        return self._start_time is not None and self._end_time is None

    def validate(self) -> ValidationResult:
        """Validate the experiment.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = experiment.validate()
        """
        errors = []

        if not self._id:
            errors.append("Experiment ID cannot be empty")

        if not self._name:
            errors.append("Experiment name cannot be empty")

        if self._start_time and self._end_time and self._end_time < self._start_time:
            errors.append("End time cannot be before start time")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Experiment definition

        Example:
            >>> data = experiment.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "description": self._description,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "end_time": self._end_time.isoformat() if self._end_time else None,
            "duration": self.get_duration(),
            "parameters": self._parameters,
            "results": self._results,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(experiment)
        """
        return f"Experiment(id={self._id}, name={self._name}, running={self.is_running()})"


class ExperimentRegistry:
    """Registry for experiments.

    This class provides experiment registry functionality.

    Attributes:
        _experiments: Registered experiments

    Example:
        >>> registry = ExperimentRegistry()
        >>> registry.register(Experiment("exp_001", "Quantum Simulation"))
    """

    def __init__(self) -> None:
        """Initialize an ExperimentRegistry.

        Example:
            >>> registry = ExperimentRegistry()
        """
        self._experiments: dict[ExperimentID, Experiment] = {}

    def register(self, experiment: Experiment) -> None:
        """Register an experiment.

        Args:
            experiment: Experiment to register

        Example:
            >>> registry.register(Experiment("exp_001", "Quantum Simulation"))
        """
        self._experiments[experiment.id] = experiment

    def unregister(self, experiment_id: ExperimentID) -> bool:
        """Unregister an experiment.

        Args:
            experiment_id: Experiment ID

        Returns:
            True if unregistered

        Example:
            >>> unregistered = registry.unregister("exp_001")
        """
        if experiment_id in self._experiments:
            del self._experiments[experiment_id]
            return True
        return False

    def get(self, experiment_id: ExperimentID) -> Experiment | None:
        """Get an experiment by ID.

        Args:
            experiment_id: Experiment ID

        Returns:
            Experiment or None

        Example:
            >>> experiment = registry.get("exp_001")
        """
        return self._experiments.get(experiment_id)

    def get_running(self) -> list[Experiment]:
        """Get running experiments.

        Returns:
            List of running experiments

        Example:
            >>> running = registry.get_running()
        """
        return [exp for exp in self._experiments.values() if exp.is_running()]

    def get_completed(self) -> list[Experiment]:
        """Get completed experiments.

        Returns:
            List of completed experiments

        Example:
            >>> completed = registry.get_completed()
        """
        return [exp for exp in self._experiments.values() if exp.start_time and exp.end_time]

    def list_all(self) -> list[Experiment]:
        """List all registered experiments.

        Returns:
            List of experiments

        Example:
            >>> experiments = registry.list_all()
        """
        return list(self._experiments.values())

    def count(self) -> int:
        """Get the number of registered experiments.

        Returns:
            Number of experiments

        Example:
            >>> count = registry.count()
        """
        return len(self._experiments)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Registry state

        Example:
            >>> data = registry.to_dict()
        """
        return {
            "experiments": [exp.to_dict() for exp in self._experiments.values()],
            "count": len(self._experiments),
            "running": len(self.get_running()),
            "completed": len(self.get_completed()),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(registry)
        """
        return f"ExperimentRegistry(experiments={len(self._experiments)}, running={len(self.get_running())})"


# Export
__all__ = [
    "Experiment",
    "ExperimentRegistry",
]
