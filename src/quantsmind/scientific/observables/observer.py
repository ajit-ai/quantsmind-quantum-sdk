"""
Observer Module

This module provides observer definitions for the Scientific package.

Purpose
-------
Provide observer definitions and operations.

Responsibilities
----------------
- Define observer structure
- Support observation execution
- Support observer state
- Support observer metadata

Dependencies
------------
typing (standard library)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from quantsmind.scientific.interfaces import IMeasurement, IObservable, IObserver
from quantsmind.scientific.types import ObserverID


class Observer(IObserver):
    """Concrete implementation of an observer.

    This class provides observer functionality.

    Attributes:
        _observer_id: Observer identifier
        _name: Observer name
        _description: Observer description
        _observation_function: Observation function
        _metadata: Observer metadata

    Example:
        >>> observer = Observer("sensor_001", "Temperature Sensor", "Room temperature sensor")
        >>> observer.observe(observable)
    """

    def __init__(
        self,
        observer_id: ObserverID,
        name: str,
        description: str = "",
        observation_function: Optional[Callable[[IObservable], IMeasurement]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an Observer.

        Args:
            observer_id: Observer identifier
            name: Observer name
            description: Observer description
            observation_function: Custom observation function
            metadata: Observer metadata

        Example:
            >>> observer = Observer("sensor_001", "Temperature Sensor", "Room temperature sensor")
        """
        self._observer_id = observer_id
        self._name = name
        self._description = description
        self._observation_function = observation_function
        self._metadata = metadata or {}

    @property
    def observer_id(self) -> ObserverID:
        """Get the observer identifier.

        Returns:
            Observer identifier

        Example:
            >>> print(f"ID: {observer.observer_id}")
        """
        return self._observer_id

    @property
    def name(self) -> str:
        """Get the observer name.

        Returns:
            Observer name

        Example:
            >>> print(f"Name: {observer.name}")
        """
        return self._name

    @property
    def description(self) -> str:
        """Get the observer description.

        Returns:
            Observer description

        Example:
            >>> print(f"Description: {observer.description}")
        """
        return self._description

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the observer metadata.

        Returns:
            Observer metadata

        Example:
            >>> print(f"Metadata: {observer.metadata}")
        """
        return self._metadata.copy()

    def observe(self, observable: IObservable) -> IMeasurement:
        """Observe an observable.

        Args:
            observable: Observable to observe

        Returns:
            Measurement result

        Example:
            >>> measurement = observer.observe(observable)
        """
        if self._observation_function:
            return self._observation_function(observable)
        else:
            # Default: use the observable's observe method
            return observable.observe()

    def set_observation_function(self, function: Callable[[IObservable], IMeasurement]) -> None:
        """Set a custom observation function.

        Args:
            function: Observation function

        Example:
            >>> observer.set_observation_function(custom_function)
        """
        self._observation_function = function

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Observer definition

        Example:
            >>> data = observer.to_dict()
        """
        return {
            "observer_id": self._observer_id,
            "name": self._name,
            "description": self._description,
            "has_custom_function": self._observation_function is not None,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(observer)
        """
        return f"Observer(id={self._observer_id}, name={self._name})"


# Export
__all__ = [
    "Observer",
]
