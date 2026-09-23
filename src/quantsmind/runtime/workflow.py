"""
Runtime Workflow Module

This module provides workflow management for the Runtime package.

Purpose
-------
Provide workflow management for the QuantsMind SDK.

Responsibilities
----------------
- Manage workflow lifecycle
- Execute workflows with conditional logic
- Track workflow progress
- Handle workflow dependencies

Dependencies
------------
typing (standard library)
logging (standard library)
uuid (standard library)
datetime (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
quantsmind.runtime.exceptions (runtime exceptions)
quantsmind.runtime.job (job)
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from quantsmind.runtime.constants import RUNTIME_VERSION
from quantsmind.runtime.enums import ExecutionState, TaskPriority
from quantsmind.runtime.exceptions import WorkflowError
from quantsmind.runtime.job import Job
from quantsmind.runtime.types import ExecutionResult, JobID, WorkflowID

logger = logging.getLogger(__name__)


class Workflow:
    """Concrete implementation of a workflow.

    This class provides workflow management for execution operations.

    Attributes:
        _workflow_id: Workflow identifier
        _name: Workflow name
        _jobs: Workflow jobs
        _state: Workflow state
        _priority: Workflow priority
        _dependencies: Workflow dependencies
        _execution_mode: Execution mode (sequential, parallel)
        _results: Job results
        _created_at: Creation timestamp
        _started_at: Start timestamp
        _completed_at: Completion timestamp
        _metadata: Workflow metadata

    Example:
        >>> workflow = Workflow(name="my_workflow")
        >>> workflow.add_job(job)
        >>> workflow.execute()
    """

    def __init__(
        self,
        name: str,
        execution_mode: str = "sequential",
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: list[WorkflowID] | None = None,
        workflow_id: WorkflowID | None = None,
    ) -> None:
        """Initialize a Workflow.

        Args:
            name: Workflow name
            execution_mode: Execution mode (sequential, parallel)
            priority: Workflow priority
            dependencies: Workflow dependencies
            workflow_id: Optional workflow identifier

        Example:
            >>> workflow = Workflow(name="my_workflow")
        """
        self._workflow_id = workflow_id or str(uuid.uuid4())
        self._name = name
        self._jobs: dict[JobID, Job] = {}
        self._state = ExecutionState.CREATED
        self._priority = priority
        self._dependencies = dependencies or []
        self._execution_mode = execution_mode
        self._results: dict[JobID, ExecutionResult] = {}
        self._created_at = datetime.now(UTC).replace(tzinfo=None)
        self._started_at: datetime | None = None
        self._completed_at: datetime | None = None
        self._metadata: dict[str, Any] = {
            "runtime_version": RUNTIME_VERSION,
        }
        logger.debug(f"Created workflow: {self._workflow_id}")

    @property
    def workflow_id(self) -> WorkflowID:
        """Get the workflow ID.

        Returns:
            Workflow identifier

        Example:
            >>> print(f"Workflow ID: {workflow.workflow_id}")
        """
        return self._workflow_id

    @property
    def name(self) -> str:
        """Get the workflow name.

        Returns:
            Workflow name

        Example:
            >>> print(f"Name: {workflow.name}")
        """
        return self._name

    @property
    def state(self) -> ExecutionState:
        """Get the workflow state.

        Returns:
            Workflow state

        Example:
            >>> print(f"State: {workflow.state}")
        """
        return self._state

    @property
    def priority(self) -> TaskPriority:
        """Get the workflow priority.

        Returns:
            Workflow priority

        Example:
            >>> print(f"Priority: {workflow.priority}")
        """
        return self._priority

    @property
    def execution_mode(self) -> str:
        """Get the execution mode.

        Returns:
            Execution mode

        Example:
            >>> print(f"Execution mode: {workflow.execution_mode}")
        """
        return self._execution_mode

    @property
    def dependencies(self) -> list[WorkflowID]:
        """Get the workflow dependencies.

        Returns:
            Workflow dependencies

        Example:
            >>> print(f"Dependencies: {workflow.dependencies}")
        """
        return self._dependencies.copy()

    @property
    def job_count(self) -> int:
        """Get the number of jobs.

        Returns:
            Number of jobs

        Example:
            >>> print(f"Job count: {workflow.job_count}")
        """
        return len(self._jobs)

    @property
    def is_completed(self) -> bool:
        """Check if the workflow is completed.

        Returns:
            True if completed, False otherwise

        Example:
            >>> if workflow.is_completed:
            ...     print("Workflow completed")
        """
        return self._state in [ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED]

    def add_job(self, job: Job) -> None:
        """Add a job to the workflow.

        Args:
            job: Job to add

        Raises:
            WorkflowError: If job already exists

        Example:
            >>> workflow.add_job(job)
        """
        if job.job_id in self._jobs:
            raise WorkflowError(f"Job already exists: {job.job_id}", workflow_id=self._workflow_id)
        self._jobs[job.job_id] = job
        logger.debug(f"Added job to workflow: {job.job_id}")

    def remove_job(self, job_id: JobID) -> None:
        """Remove a job from the workflow.

        Args:
            job_id: Job identifier

        Example:
            >>> workflow.remove_job("job_123")
        """
        if job_id in self._jobs:
            del self._jobs[job_id]
            logger.debug(f"Removed job from workflow: {job_id}")

    def get_job(self, job_id: JobID) -> Job | None:
        """Get a job by ID.

        Args:
            job_id: Job identifier

        Returns:
            Job or None

        Example:
            >>> job = workflow.get_job("job_123")
        """
        return self._jobs.get(job_id)

    def get_jobs(self) -> list[Job]:
        """Get all jobs.

        Returns:
            List of jobs

        Example:
            >>> jobs = workflow.get_jobs()
        """
        return list(self._jobs.values())

    def validate(self) -> Tuple[bool, list[str]]:
        """Validate the workflow.

        Returns:
            Tuple of (is_valid, errors)

        Example:
            >>> is_valid, errors = workflow.validate()
        """
        errors = []

        if not self._name:
            errors.append("Workflow name is required")

        if not self._jobs:
            errors.append("Workflow must have at least one job")

        if self._execution_mode not in ["sequential", "parallel"]:
            errors.append("Execution mode must be 'sequential' or 'parallel'")

        for job in self._jobs.values():
            is_valid, job_errors = job.validate()
            if not is_valid:
                errors.extend([f"Job {job.job_id}: {err}" for err in job_errors])

        return (len(errors) == 0, errors)

    def execute(self) -> dict[JobID, ExecutionResult]:
        """Execute the workflow.

        Returns:
            Dictionary of job results

        Raises:
            WorkflowError: If execution fails

        Example:
            >>> results = workflow.execute()
        """
        if self._state != ExecutionState.QUEUED and self._state != ExecutionState.CREATED:
            raise WorkflowError(f"Cannot execute workflow in state: {self._state}", workflow_id=self._workflow_id)

        self._state = ExecutionState.RUNNING
        self._started_at = datetime.now(UTC).replace(tzinfo=None)
        logger.info(f"Executing workflow: {self._workflow_id}")

        try:
            if self._execution_mode == "sequential":
                self._execute_sequential()
            else:
                self._execute_parallel()

            self._state = ExecutionState.COMPLETED
            self._completed_at = datetime.now(UTC).replace(tzinfo=None)
            logger.info(f"Workflow completed: {self._workflow_id}")
            return self._results
        except Exception as e:
            self._state = ExecutionState.FAILED
            self._completed_at = datetime.now(UTC).replace(tzinfo=None)
            logger.error(f"Workflow failed: {self._workflow_id}", exc_info=True)
            raise WorkflowError(f"Workflow execution failed: {str(e)}", workflow_id=self._workflow_id) from e

    def _execute_sequential(self) -> None:
        """Execute jobs sequentially.

        Raises:
            WorkflowError: If execution fails
        """
        for job in self._jobs.values():
            job._state = ExecutionState.QUEUED
            results = job.execute()
            self._results.update(results)

    def _execute_parallel(self) -> None:
        """Execute jobs in parallel.

        Raises:
            WorkflowError: If execution fails
        """
        # Simplified parallel execution
        # In production, this should use threading or asyncio
        for job in self._jobs.values():
            job._state = ExecutionState.QUEUED
            results = job.execute()
            self._results.update(results)

    def cancel(self) -> None:
        """Cancel the workflow.

        Example:
            >>> workflow.cancel()
        """
        if self._state not in [ExecutionState.CREATED, ExecutionState.QUEUED, ExecutionState.RUNNING]:
            logger.warning(f"Cancelling workflow in state: {self._state}")
        
        for job in self._jobs.values():
            job.cancel()
        
        self._state = ExecutionState.CANCELLED
        self._completed_at = datetime.now(UTC).replace(tzinfo=None)
        logger.info(f"Cancelled workflow: {self._workflow_id}")

    def set_metadata(self, key: str, value: Any) -> None:
        """Set workflow metadata.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> workflow.set_metadata("description", "My workflow")
        """
        self._metadata[key] = value
        logger.debug(f"Set workflow metadata: {key}")

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get workflow metadata.

        Args:
            key: Metadata key
            default: Default value

        Returns:
            Metadata value or default

        Example:
            >>> value = workflow.get_metadata("description")
        """
        return self._metadata.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Convert workflow to dictionary.

        Returns:
            Dictionary representation

        Example:
            >>> data = workflow.to_dict()
        """
        return {
            "workflow_id": self._workflow_id,
            "name": self._name,
            "state": self._state.value,
            "execution_mode": self._execution_mode,
            "priority": self._priority.value,
            "dependencies": self._dependencies.copy(),
            "job_count": self.job_count,
            "created_at": self._created_at.isoformat(),
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "completed_at": self._completed_at.isoformat() if self._completed_at else None,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(workflow)
        """
        return f"Workflow(workflow_id={self._workflow_id}, name={self._name}, state={self._state.value})"


# Export
__all__ = [
    "Workflow",
]
