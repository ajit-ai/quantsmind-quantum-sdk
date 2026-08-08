"""
Quantum Job Module

This module provides quantum job definitions for the Quantum package.

Purpose
-------
Provide quantum job management for quantum computing operations.

Responsibilities
----------------
- Define quantum job structure
- Support quantum job operations
- Support quantum job validation
- Support quantum job metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.enums (quantum enumerations)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.interfaces (quantum interfaces)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.execution.execution_context (execution context module)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from quantsmind.quantum.algorithms.enums import JobStatus
from quantsmind.quantum.algorithms.exceptions import ExecutionError
from quantsmind.quantum.algorithms.interfaces import IQuantumJob
from quantsmind.quantum.algorithms.types import JobResult, ValidationResult
from quantsmind.quantum.execution.execution_context import ExecutionContext


class QuantumJob(IQuantumJob):
    """Concrete implementation of a quantum job.

    This class provides quantum job functionality for quantum computing.

    Attributes:
        _job_id: Job ID
        _context: Execution context
        _status: Job status
        _result: Job result
        _metadata: Job metadata

    Example:
        >>> job = QuantumJob("job_001", context)
        >>> result = job.wait()
    """

    def __init__(
        self,
        job_id: str,
        context: ExecutionContext,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a QuantumJob.

        Args:
            job_id: Job ID
            context: Execution context
            metadata: Job metadata

        Example:
            >>> job = QuantumJob("job_001", context)
        """
        if not job_id:
            raise ExecutionError("Job ID cannot be empty", {"job_id": job_id})

        if context is None:
            raise ExecutionError("Context cannot be None", {"context": None})

        self._job_id = job_id
        self._context = context
        self._status = JobStatus.INITIALIZING
        self._result: Optional[JobResult] = None
        self._metadata = metadata or {}

    @property
    def job_id(self) -> str:
        """Get the job ID.

        Returns:
            Job ID

        Example:
            >>> jid = job.job_id
        """
        return self._job_id

    @property
    def context(self) -> ExecutionContext:
        """Get the execution context.

        Returns:
            Execution context

        Example:
            >>> context = job.context
        """
        return self._context

    @property
    def status(self) -> JobStatus:
        """Get the job status.

        Returns:
            Job status

        Example:
            >>> status = job.status
        """
        return self._status

    @property
    def result(self) -> Optional[JobResult]:
        """Get the job result.

        Returns:
            Job result or None

        Example:
            >>> result = job.result
        """
        return self._result

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the job metadata.

        Returns:
            Job metadata

        Example:
            >>> metadata = job.metadata
        """
        return self._metadata.copy()

    def set_status(self, status: JobStatus) -> None:
        """Set the job status.

        Args:
            status: Job status

        Example:
            >>> job.set_status(JobStatus.RUNNING)
        """
        self._status = status

    def set_result(self, result: JobResult) -> None:
        """Set the job result.

        Args:
            result: Job result

        Example:
            >>> job.set_result(result)
        """
        self._result = result
        self._status = JobStatus.COMPLETED

    def cancel(self) -> bool:
        """Cancel the job.

        Returns:
            True if cancelled

        Example:
            >>> cancelled = job.cancel()
        """
        if self._status in [JobStatus.INITIALIZING, JobStatus.QUEUED, JobStatus.RUNNING]:
            self._status = JobStatus.CANCELLED
            return True
        return False

    def wait(self, timeout: Optional[int] = None) -> JobResult:
        """Wait for the job to complete.

        Args:
            timeout: Timeout in seconds

        Returns:
            Job result

        Example:
            >>> result = job.wait(timeout=300)
        """
        # Placeholder implementation - actual waiting requires async job monitoring
        if self._result is None:
            # Simulate job completion
            self._result = {
                "job_id": self._job_id,
                "status": "completed",
                "counts": {},
            }
            self._status = JobStatus.COMPLETED

        return self._result

    def validate(self) -> ValidationResult:
        """Validate the job.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = job.validate()
        """
        errors = []

        if not self._job_id:
            errors.append("Job ID cannot be empty")

        if self._context is None:
            errors.append("Context cannot be None")

        # Validate context
        if self._context:
            is_valid, context_errors = self._context.validate()
            errors.extend(context_errors)

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Job definition

        Example:
            >>> data = job.to_dict()
        """
        return {
            "job_id": self._job_id,
            "status": self._status.value,
            "has_result": self._result is not None,
            "context": self._context.name,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(job)
        """
        return f"QuantumJob(job_id={self._job_id}, status={self._status.value})"
