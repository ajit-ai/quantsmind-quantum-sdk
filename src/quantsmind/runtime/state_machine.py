"""
Runtime State Machine Module

This module provides state machine management for the Runtime package.

Purpose
-------
Provide state machine management for the QuantsMind SDK.

Responsibilities
----------------
- Manage state transitions
- Validate state changes
- Support state hooks
- Handle state history

Dependencies
------------
typing (standard library)
logging (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
quantsmind.runtime.exceptions (runtime exceptions)
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from quantsmind.runtime.enums import ExecutionState
from quantsmind.runtime.exceptions import StateMachineError
from quantsmind.runtime.types import State, StateTransition

logger = logging.getLogger(__name__)


class StateMachine:
    """Concrete implementation of a state machine.

    This class provides state machine capabilities.

    Attributes:
        _current_state: Current state
        _states: Valid states
        _transitions: Valid transitions
        _state_history: State history
        _hooks: State transition hooks

    Example:
        >>> sm = StateMachine(initial_state=ExecutionState.CREATED)
        >>> sm.transition_to(ExecutionState.INITIALIZED)
    """

    def __init__(
        self,
        initial_state: ExecutionState = ExecutionState.CREATED,
        states: list[ExecutionState] | None = None,
        transitions: dict[State, list[State]] | None = None,
    ) -> None:
        """Initialize a StateMachine.

        Args:
            initial_state: Initial state
            states: Valid states
            transitions: Valid transitions

        Example:
            >>> sm = StateMachine(initial_state=ExecutionState.CREATED)
        """
        self._current_state = initial_state
        self._states = states or list(ExecutionState)
        self._transitions = transitions or self._default_transitions()
        self._state_history: list[State] = [initial_state.value]
        self._hooks: dict[StateTransition, list[Callable]] = {}
        logger.debug(f"Created state machine with initial state: {initial_state.value}")

    def _default_transitions(self) -> dict[State, list[State]]:
        """Get default state transitions.

        Returns:
            Default transitions

        Example:
            >>> transitions = sm._default_transitions()
        """
        return {
            ExecutionState.CREATED.value: [
                ExecutionState.INITIALIZED.value,
                ExecutionState.DESTROYED.value,
            ],
            ExecutionState.INITIALIZED.value: [
                ExecutionState.VALIDATED.value,
                ExecutionState.DESTROYED.value,
            ],
            ExecutionState.VALIDATED.value: [
                ExecutionState.QUEUED.value,
                ExecutionState.DESTROYED.value,
            ],
            ExecutionState.QUEUED.value: [
                ExecutionState.RUNNING.value,
                ExecutionState.CANCELLED.value,
            ],
            ExecutionState.RUNNING.value: [
                ExecutionState.PAUSED.value,
                ExecutionState.COMPLETED.value,
                ExecutionState.FAILED.value,
                ExecutionState.CANCELLED.value,
            ],
            ExecutionState.PAUSED.value: [
                ExecutionState.RUNNING.value,
                ExecutionState.CANCELLED.value,
            ],
            ExecutionState.COMPLETED.value: [
                ExecutionState.ARCHIVED.value,
            ],
            ExecutionState.FAILED.value: [
                ExecutionState.ARCHIVED.value,
            ],
            ExecutionState.CANCELLED.value: [
                ExecutionState.ARCHIVED.value,
            ],
            ExecutionState.ARCHIVED.value: [
                ExecutionState.DESTROYED.value,
            ],
            ExecutionState.DESTROYED.value: [],
        }

    @property
    def current_state(self) -> ExecutionState:
        """Get the current state.

        Returns:
            Current state

        Example:
            >>> print(f"Current state: {sm.current_state}")
        """
        return self._current_state

    @property
    def state_history(self) -> list[State]:
        """Get the state history.

        Returns:
            State history

        Example:
            >>> print(f"State history: {sm.state_history}")
        """
        return self._state_history.copy()

    def can_transition_to(self, new_state: ExecutionState) -> bool:
        """Check if transition is possible.

        Args:
            new_state: New state

        Returns:
            True if transition is possible, False otherwise

        Example:
            >>> if sm.can_transition_to(ExecutionState.INITIALIZED):
            ...     print("Can transition")
        """
        current_state = self._current_state.value
        target_state = new_state.value
        return target_state in self._transitions.get(current_state, [])

    def transition_to(self, new_state: ExecutionState) -> bool:
        """Transition to a new state.

        Args:
            new_state: New state

        Returns:
            True if transition succeeded, False otherwise

        Raises:
            StateMachineError: If transition is invalid

        Example:
            >>> sm.transition_to(ExecutionState.INITIALIZED)
        """
        if not self.can_transition_to(new_state):
            raise StateMachineError(
                f"Invalid transition from {self._current_state.value} to {new_state.value}",
                from_state=self._current_state.value,
                to_state=new_state.value,
            )

        # Execute before hooks
        transition = (self._current_state.value, new_state.value)
        self._execute_hooks(transition, "before")

        old_state = self._current_state
        self._current_state = new_state
        self._state_history.append(new_state.value)
        logger.debug(f"Transitioned from {old_state.value} to {new_state.value}")

        # Execute after hooks
        self._execute_hooks(transition, "after")

        return True

    def add_hook(
        self,
        from_state: ExecutionState,
        to_state: ExecutionState,
        hook: Callable,
        when: str = "after",
    ) -> None:
        """Add a transition hook.

        Args:
            from_state: Source state
            to_state: Target state
            hook: Hook function
            when: When to execute (before or after)

        Example:
            >>> sm.add_hook(ExecutionState.CREATED, ExecutionState.INITIALIZED, lambda: print("Initializing"))
        """
        transition = (from_state.value, to_state.value)
        hook_key = f"{when}_{transition[0]}_{transition[1]}"
        
        if hook_key not in self._hooks:
            self._hooks[hook_key] = []
        
        self._hooks[hook_key].append(hook)
        logger.debug(f"Added hook for transition {transition[0]} -> {transition[1]}")

    def _execute_hooks(self, transition: StateTransition, when: str) -> None:
        """Execute hooks for a transition.

        Args:
            transition: State transition
            when: When to execute (before or after)
        """
        hook_key = f"{when}_{transition[0]}_{transition[1]}"
        
        if hook_key in self._hooks:
            for hook in self._hooks[hook_key]:
                try:
                    hook()
                except Exception as e:
                    logger.error(f"Hook execution failed: {e}", exc_info=True)

    def reset(self) -> None:
        """Reset the state machine.

        Example:
            >>> sm.reset()
        """
        self._current_state = ExecutionState.CREATED
        self._state_history = [ExecutionState.CREATED.value]
        logger.debug("Reset state machine")

    def get_valid_transitions(self) -> list[State]:
        """Get valid transitions from current state.

        Returns:
            List of valid target states

        Example:
            >>> transitions = sm.get_valid_transitions()
        """
        return self._transitions.get(self._current_state.value, []).copy()

    def get_status(self) -> dict[str, Any]:
        """Get state machine status.

        Returns:
            State machine status

        Example:
            >>> status = sm.get_status()
        """
        return {
            "current_state": self._current_state.value,
            "state_history": self._state_history.copy(),
            "valid_transitions": self.get_valid_transitions(),
        }


# Export
__all__ = [
    "StateMachine",
]
