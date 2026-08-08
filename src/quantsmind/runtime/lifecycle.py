"""
Runtime Lifecycle Module

This module provides lifecycle management for the Runtime package.

Purpose
-------
Provide lifecycle management for the QuantsMind SDK.

Responsibilities
----------------
- Manage lifecycle states
- Handle lifecycle transitions
- Track lifecycle events
- Support lifecycle hooks

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
from typing import Any, Callable, Dict, List, Optional

from quantsmind.runtime.constants import RUNTIME_VERSION
from quantsmind.runtime.enums import ExecutionState
from quantsmind.runtime.exceptions import StateMachineError
from quantsmind.runtime.types import State, StateTransition

logger = logging.getLogger(__name__)


class LifecycleManager:
    """Concrete implementation of a lifecycle manager.

    This class provides lifecycle management capabilities.

    Attributes:
        _state: Current state
        _state_history: State history
        _transitions: Valid transitions
        _hooks: Lifecycle hooks
        _metadata: Lifecycle metadata

    Example:
        >>> manager = LifecycleManager()
        >>> manager.initialize()
        >>> manager.start()
    """

    def __init__(
        self,
        initial_state: ExecutionState = ExecutionState.CREATED,
        transitions: Optional[Dict[State, List[State]]] = None,
    ) -> None:
        """Initialize a LifecycleManager.

        Args:
            initial_state: Initial state
            transitions: Valid state transitions

        Example:
            >>> manager = LifecycleManager()
        """
        self._state = initial_state
        self._state_history: List[State] = [initial_state.value]
        self._transitions = transitions or self._default_transitions()
        self._hooks: Dict[StateTransition, List[Callable]] = {}
        self._metadata: Dict[str, Any] = {
            "runtime_version": RUNTIME_VERSION,
        }
        logger.debug(f"Created lifecycle manager with initial state: {initial_state.value}")

    def _default_transitions(self) -> Dict[State, List[State]]:
        """Get default state transitions.

        Returns:
            Default transitions
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
    def state(self) -> ExecutionState:
        """Get the current state.

        Returns:
            Current state

        Example:
            >>> print(f"State: {manager.state}")
        """
        return self._state

    @property
    def state_history(self) -> List[State]:
        """Get the state history.

        Returns:
            State history

        Example:
            >>> print(f"State history: {manager.state_history}")
        """
        return self._state_history.copy()

    def transition_to(self, new_state: ExecutionState) -> bool:
        """Transition to a new state.

        Args:
            new_state: New state

        Returns:
            True if transition succeeded, False otherwise

        Raises:
            StateMachineError: If transition is invalid

        Example:
            >>> manager.transition_to(ExecutionState.INITIALIZED)
        """
        current_state = self._state.value
        target_state = new_state.value

        if target_state not in self._transitions.get(current_state, []):
            raise StateMachineError(
                f"Invalid transition from {current_state} to {target_state}",
                from_state=current_state,
                to_state=target_state,
            )

        # Execute before hooks
        transition = (current_state, target_state)
        self._execute_hooks(transition, "before")

        self._state = new_state
        self._state_history.append(target_state)
        logger.debug(f"Transitioned from {current_state} to {target_state}")

        # Execute after hooks
        self._execute_hooks(transition, "after")

        return True

    def can_transition_to(self, new_state: ExecutionState) -> bool:
        """Check if transition is possible.

        Args:
            new_state: New state

        Returns:
            True if transition is possible, False otherwise

        Example:
            >>> if manager.can_transition_to(ExecutionState.INITIALIZED):
            ...     print("Can transition")
        """
        current_state = self._state.value
        target_state = new_state.value
        return target_state in self._transitions.get(current_state, [])

    def add_hook(
        self,
        from_state: ExecutionState,
        to_state: ExecutionState,
        hook: Callable,
        when: str = "after",
    ) -> None:
        """Add a lifecycle hook.

        Args:
            from_state: Source state
            to_state: Target state
            hook: Hook function
            when: When to execute (before or after)

        Example:
            >>> manager.add_hook(ExecutionState.CREATED, ExecutionState.INITIALIZED, lambda: print("Initializing"))
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
        """Reset the lifecycle manager.

        Example:
            >>> manager.reset()
        """
        self._state = ExecutionState.CREATED
        self._state_history = [ExecutionState.CREATED.value]
        logger.debug("Reset lifecycle manager")

    def get_status(self) -> Dict[str, Any]:
        """Get lifecycle status.

        Returns:
            Lifecycle status

        Example:
            >>> status = manager.get_status()
        """
        return {
            "state": self._state.value,
            "state_history": self._state_history.copy(),
            "valid_transitions": self._transitions.get(self._state.value, []),
            "metadata": self._metadata.copy(),
        }


# Export
__all__ = [
    "LifecycleManager",
]
