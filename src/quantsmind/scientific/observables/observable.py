"""
Observable Module

This module provides observable definitions for the Scientific package.

Purpose
-------
Provide observable definitions and operations.

Responsibilities
----------------
- Define observable structure
- Support observable registration
- Support observable state
- Support observable metadata

Dependencies
------------
typing (standard library)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from quantsmind.scientific.interfaces import IMeasurement, IObservable
from quantsmind.scientific.types import ObservableID


class Observable(IObservable):
    """Concrete implementation of an observable.

    This class provides observable functionality.

    Attributes:
        _observable_id: Observable identifier
        _name: Observable name
        _description: Observable description
        _observers: Registered observers
        _metadata: Observable metadata

    Example:
        >>> observable = Observable("temp_001", "Temperature", "Room temperature")
        >>> observable.observe()
    """

    def __init__(
        self,
        observable_id: ObservableID,
        name: str,
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an Observable.

        Args:
            observable_id: Observable identifier
            name: Observable name
            description: Observable description
            metadata: Observable metadata

        Example:
            >>> observable = Observable("temp_001", "Temperature", "Room temperature")
        """
        self._observable_id = observable_id
        self._name = name
        self._description = description
        self._observers: list[Callable] = []
        self._metadata = metadata or {}

    @property
    def observable_id(self) -> ObservableID:
        """Get the observable identifier.

        Returns:
            Observable identifier

        Example:
            >>> print(f"ID: {observable.observable_id}")
        """
        return self._observable_id

    @property
    def name(self) -> str:
        """Get the observable name.

        Returns:
            Observable name

        Example:
            >>> print(f"Name: {observable.name}")
        """
        return self._name

    @property
    def description(self) -> str:
        """Get the observable description.

        Returns:
            Observable description

        Example:
            >>> print(f"Description: {observable.description}")
        """
        return self._description

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the observable metadata.

        Returns:
            Observable metadata

        Example:
            >>> print(f"Metadata: {observable.metadata}")
        """
        return self._metadata.copy()

    def register_observer(self, observer: Callable) -> None:
        """Register an observer callback.

        Args:
            observer: Observer callback function

        Example:
            >>> observable.register_observer(callback)
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister_observer(self, observer: Callable) -> bool:
        """Unregister an observer callback.

        Args:
            observer: Observer callback function

        Returns:
            True if unregistered, False otherwise

        Example:
            >>> unregistered = observable.unregister_observer(callback)
        """
        if observer in self._observers:
            self._observers.remove(observer)
            return True
        return False

    def notify_observers(self, measurement: IMeasurement) -> None:
        """Notify all observers of a measurement.

        Args:
            measurement: Measurement to notify

        Example:
            >>> observable.notify_observers(measurement)
        """
        for observer in self._observers:
            try:
                observer(measurement)
            except Exception:
                pass  # Handle observer errors gracefully

    def observe(self) -> IMeasurement:
        """Perform an observation.

        Returns:
            Measurement result

        Note:
            This is a placeholder implementation. Subclasses should override.

        Example:
            >>> measurement = observable.observe()
        """
        raise NotImplementedError("Subclasses must implement observe()")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Observable definition

        Example:
            >>> data = observable.to_dict()
        """
        return {
            "observable_id": self._observable_id,
            "name": self._name,
            "description": self._description,
            "observer_count": len(self._observers),
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(observable)
        """
        return f"Observable(id={self._observable_id}, name={self._name})"


# Export
__all__ = [
    "Observable",
]
