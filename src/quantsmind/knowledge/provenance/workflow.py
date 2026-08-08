"""
Workflow Module

This module provides workflow definitions for the Knowledge package.

Purpose
-------
Provide workflow management for provenance tracking.

Responsibilities
----------------
- Define workflow structure
- Support workflow operations
- Support workflow validation
- Support workflow metadata

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
from typing import Any, Dict, List, Optional

from quantsmind.knowledge.enums import ProvenanceType
from quantsmind.knowledge.exceptions import ProvenanceError
from quantsmind.knowledge.types import ValidationResult, WorkflowID


class Workflow:
    """Concrete implementation of a workflow.

    This class provides workflow functionality for provenance tracking.

    Attributes:
        _id: Workflow ID
        _name: Workflow name
        _description: Workflow description
        _steps: Workflow steps
        _status: Workflow status
        _start_time: Start timestamp
        _end_time: End timestamp
        _metadata: Workflow metadata

    Example:
        >>> workflow = Workflow("workflow_001", "Data Processing Pipeline")
        >>> workflow.add_step("step_001", "Load Data")
    """

    def __init__(
        self,
        workflow_id: WorkflowID,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Workflow.

        Args:
            workflow_id: Workflow ID
            name: Workflow name
            description: Workflow description
            metadata: Workflow metadata

        Example:
            >>> workflow = Workflow("workflow_001", "Data Processing Pipeline")
        """
        if not workflow_id:
            raise ProvenanceError("Workflow ID cannot be empty", {"workflow_id": workflow_id})

        if not name:
            raise ProvenanceError("Workflow name cannot be empty", {"name": name})

        self._id = workflow_id
        self._name = name
        self._description = description
        self._steps: List[Dict[str, Any]] = []
        self._status = "pending"
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None
        self._metadata = metadata or {}

    @property
    def id(self) -> WorkflowID:
        """Get the workflow ID.

        Returns:
            Workflow ID

        Example:
            >>> wid = workflow.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the workflow name.

        Returns:
            Workflow name

        Example:
            >>> name = workflow.name
        """
        return self._name

    @property
    def description(self) -> Optional[str]:
        """Get the workflow description.

        Returns:
            Workflow description

        Example:
            >>> description = workflow.description
        """
        return self._description

    @property
    def steps(self) -> List[Dict[str, Any]]:
        """Get the workflow steps.

        Returns:
            Workflow steps

        Example:
            >>> steps = workflow.steps
        """
        return self._steps.copy()

    @property
    def status(self) -> str:
        """Get the workflow status.

        Returns:
            Workflow status

        Example:
            >>> status = workflow.status
        """
        return self._status

    @property
    def start_time(self) -> Optional[datetime]:
        """Get the start timestamp.

        Returns:
            Start timestamp

        Example:
            >>> start = workflow.start_time
        """
        return self._start_time

    @property
    def end_time(self) -> Optional[datetime]:
        """Get the end timestamp.

        Returns:
            End timestamp

        Example:
            >>> end = workflow.end_time
        """
        return self._end_time

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the workflow metadata.

        Returns:
            Workflow metadata

        Example:
            >>> metadata = workflow.metadata
        """
        return self._metadata.copy()

    def add_step(self, step_id: str, step_name: str, step_type: str = "process", parameters: Optional[Dict[str, Any]] = None) -> None:
        """Add a step to the workflow.

        Args:
            step_id: Step ID
            step_name: Step name
            step_type: Step type
            parameters: Step parameters

        Example:
            >>> workflow.add_step("step_001", "Load Data")
        """
        self._steps.append({
            "step_id": step_id,
            "step_name": step_name,
            "step_type": step_type,
            "parameters": parameters or {},
            "status": "pending",
            "start_time": None,
            "end_time": None,
        })

    def remove_step(self, step_id: str) -> bool:
        """Remove a step from the workflow.

        Args:
            step_id: Step ID

        Returns:
            True if removed

        Example:
            >>> removed = workflow.remove_step("step_001")
        """
        for i, step in enumerate(self._steps):
            if step.get("step_id") == step_id:
                del self._steps[i]
                return True
        return False

    def start_step(self, step_id: str) -> None:
        """Start a workflow step.

        Args:
            step_id: Step ID

        Example:
            >>> workflow.start_step("step_001")
        """
        for step in self._steps:
            if step.get("step_id") == step_id:
                step["status"] = "running"
                step["start_time"] = datetime.utcnow()
                break

    def complete_step(self, step_id: str, results: Optional[Dict[str, Any]] = None) -> None:
        """Complete a workflow step.

        Args:
            step_id: Step ID
            results: Step results

        Example:
            >>> workflow.complete_step("step_001", {"records": 1000})
        """
        for step in self._steps:
            if step.get("step_id") == step_id:
                step["status"] = "completed"
                step["end_time"] = datetime.utcnow()
                if results:
                    step["results"] = results
                break

    def fail_step(self, step_id: str, error: Optional[str] = None) -> None:
        """Fail a workflow step.

        Args:
            step_id: Step ID
            error: Error message

        Example:
            >>> workflow.fail_step("step_001", "Connection error")
        """
        for step in self._steps:
            if step.get("step_id") == step_id:
                step["status"] = "failed"
                step["end_time"] = datetime.utcnow()
                if error:
                    step["error"] = error
                break

    def start(self) -> None:
        """Start the workflow.

        Example:
            >>> workflow.start()
        """
        self._status = "running"
        self._start_time = datetime.utcnow()

    def complete(self) -> None:
        """Complete the workflow.

        Example:
            >>> workflow.complete()
        """
        self._status = "completed"
        self._end_time = datetime.utcnow()

    def fail(self, error: Optional[str] = None) -> None:
        """Fail the workflow.

        Args:
            error: Error message

        Example:
            >>> workflow.fail("Step failed")
        """
        self._status = "failed"
        self._end_time = datetime.utcnow()
        if error:
            self._metadata["error"] = error

    def get_step_status(self, step_id: str) -> Optional[str]:
        """Get the status of a step.

        Args:
            step_id: Step ID

        Returns:
            Step status or None

        Example:
            >>> status = workflow.get_step_status("step_001")
        """
        for step in self._steps:
            if step.get("step_id") == step_id:
                return step.get("status")
        return None

    def get_duration(self) -> Optional[float]:
        """Get the workflow duration in seconds.

        Returns:
            Duration in seconds or None

        Example:
            >>> duration = workflow.get_duration()
        """
        if self._start_time and self._end_time:
            return (self._end_time - self._start_time).total_seconds()
        return None

    def validate(self) -> ValidationResult:
        """Validate the workflow.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = workflow.validate()
        """
        errors = []

        if not self._id:
            errors.append("Workflow ID cannot be empty")

        if not self._name:
            errors.append("Workflow name cannot be empty")

        if self._start_time and self._end_time and self._end_time < self._start_time:
            errors.append("End time cannot be before start time")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Workflow definition

        Example:
            >>> data = workflow.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "description": self._description,
            "steps": self._steps,
            "status": self._status,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "end_time": self._end_time.isoformat() if self._end_time else None,
            "duration": self.get_duration(),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(workflow)
        """
        return f"Workflow(id={self._id}, name={self._name}, status={self._status}, steps={len(self._steps)})"


# Export
__all__ = [
    "Workflow",
]
