"""
Runtime Pipeline Module

This module provides pipeline management for the Runtime package.

Purpose
-------
Provide pipeline management for the QuantsMind SDK.

Responsibilities
----------------
- Manage pipeline lifecycle
- Execute pipelines with stages
- Track pipeline progress
- Handle pipeline dependencies

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
quantsmind.runtime.workflow (workflow)
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from quantsmind.runtime.constants import RUNTIME_VERSION
from quantsmind.runtime.enums import ExecutionState, TaskPriority
from quantsmind.runtime.exceptions import PipelineError
from quantsmind.runtime.types import ExecutionResult, PipelineID, WorkflowID
from quantsmind.runtime.workflow import Workflow

logger = logging.getLogger(__name__)


class Pipeline:
    """Concrete implementation of a pipeline.

    This class provides pipeline management for execution operations.

    Attributes:
        _pipeline_id: Pipeline identifier
        _name: Pipeline name
        _stages: Pipeline stages
        _state: Pipeline state
        _priority: Pipeline priority
        _dependencies: Pipeline dependencies
        _results: Stage results
        _created_at: Creation timestamp
        _started_at: Start timestamp
        _completed_at: Completion timestamp
        _metadata: Pipeline metadata

    Example:
        >>> pipeline = Pipeline(name="my_pipeline")
        >>> pipeline.add_stage(workflow)
        >>> pipeline.execute()
    """

    def __init__(
        self,
        name: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: list[PipelineID] | None = None,
        pipeline_id: PipelineID | None = None,
    ) -> None:
        """Initialize a Pipeline.

        Args:
            name: Pipeline name
            priority: Pipeline priority
            dependencies: Pipeline dependencies
            pipeline_id: Optional pipeline identifier

        Example:
            >>> pipeline = Pipeline(name="my_pipeline")
        """
        self._pipeline_id = pipeline_id or str(uuid.uuid4())
        self._name = name
        self._stages: list[Workflow] = []
        self._state = ExecutionState.CREATED
        self._priority = priority
        self._dependencies = dependencies or []
        self._results: dict[str, ExecutionResult] = {}
        self._created_at = datetime.now(UTC).replace(tzinfo=None)
        self._started_at: datetime | None = None
        self._completed_at: datetime | None = None
        self._metadata: dict[str, Any] = {
            "runtime_version": RUNTIME_VERSION,
        }
        logger.debug(f"Created pipeline: {self._pipeline_id}")

    @property
    def pipeline_id(self) -> PipelineID:
        """Get the pipeline ID.

        Returns:
            Pipeline identifier

        Example:
            >>> print(f"Pipeline ID: {pipeline.pipeline_id}")
        """
        return self._pipeline_id

    @property
    def name(self) -> str:
        """Get the pipeline name.

        Returns:
            Pipeline name

        Example:
            >>> print(f"Name: {pipeline.name}")
        """
        return self._name

    @property
    def state(self) -> ExecutionState:
        """Get the pipeline state.

        Returns:
            Pipeline state

        Example:
            >>> print(f"State: {pipeline.state}")
        """
        return self._state

    @property
    def priority(self) -> TaskPriority:
        """Get the pipeline priority.

        Returns:
            Pipeline priority

        Example:
            >>> print(f"Priority: {pipeline.priority}")
        """
        return self._priority

    @property
    def dependencies(self) -> list[PipelineID]:
        """Get the pipeline dependencies.

        Returns:
            Pipeline dependencies

        Example:
            >>> print(f"Dependencies: {pipeline.dependencies}")
        """
        return self._dependencies.copy()

    @property
    def stage_count(self) -> int:
        """Get the number of stages.

        Returns:
            Number of stages

        Example:
            >>> print(f"Stage count: {pipeline.stage_count}")
        """
        return len(self._stages)

    @property
    def is_completed(self) -> bool:
        """Check if the pipeline is completed.

        Returns:
            True if completed, False otherwise

        Example:
            >>> if pipeline.is_completed:
            ...     print("Pipeline completed")
        """
        return self._state in [ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED]

    def add_stage(self, workflow: Workflow) -> None:
        """Add a stage to the pipeline.

        Args:
            workflow: Workflow to add as a stage

        Example:
            >>> pipeline.add_stage(workflow)
        """
        self._stages.append(workflow)
        logger.debug(f"Added stage to pipeline: {workflow.workflow_id}")

    def remove_stage(self, workflow_id: WorkflowID) -> None:
        """Remove a stage from the pipeline.

        Args:
            workflow_id: Workflow identifier

        Example:
            >>> pipeline.remove_stage("workflow_123")
        """
        self._stages = [stage for stage in self._stages if stage.workflow_id != workflow_id]
        logger.debug(f"Removed stage from pipeline: {workflow_id}")

    def get_stage(self, index: int) -> Workflow | None:
        """Get a stage by index.

        Args:
            index: Stage index

        Returns:
            Workflow or None

        Example:
            >>> stage = pipeline.get_stage(0)
        """
        if 0 <= index < len(self._stages):
            return self._stages[index]
        return None

    def get_stages(self) -> list[Workflow]:
        """Get all stages.

        Returns:
            List of workflows

        Example:
            >>> stages = pipeline.get_stages()
        """
        return self._stages.copy()

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the pipeline.

        Returns:
            Tuple of (is_valid, errors)

        Example:
            >>> is_valid, errors = pipeline.validate()
        """
        errors = []

        if not self._name:
            errors.append("Pipeline name is required")

        if not self._stages:
            errors.append("Pipeline must have at least one stage")

        for i, stage in enumerate(self._stages):
            is_valid, stage_errors = stage.validate()
            if not is_valid:
                errors.extend([f"Stage {i}: {err}" for err in stage_errors])

        return (len(errors) == 0, errors)

    def execute(self) -> dict[str, ExecutionResult]:
        """Execute the pipeline.

        Returns:
            Dictionary of stage results

        Raises:
            PipelineError: If execution fails

        Example:
            >>> results = pipeline.execute()
        """
        if self._state != ExecutionState.QUEUED and self._state != ExecutionState.CREATED:
            raise PipelineError(f"Cannot execute pipeline in state: {self._state}", pipeline_id=self._pipeline_id)

        self._state = ExecutionState.RUNNING
        self._started_at = datetime.now(UTC).replace(tzinfo=None)
        logger.info(f"Executing pipeline: {self._pipeline_id}")

        try:
            for i, stage in enumerate(self._stages):
                stage._state = ExecutionState.QUEUED
                results = stage.execute()
                self._results[f"stage_{i}"] = results

            self._state = ExecutionState.COMPLETED
            self._completed_at = datetime.now(UTC).replace(tzinfo=None)
            logger.info(f"Pipeline completed: {self._pipeline_id}")
            return self._results
        except Exception as e:
            self._state = ExecutionState.FAILED
            self._completed_at = datetime.now(UTC).replace(tzinfo=None)
            logger.error(f"Pipeline failed: {self._pipeline_id}", exc_info=True)
            raise PipelineError(f"Pipeline execution failed: {str(e)}", pipeline_id=self._pipeline_id) from e

    def cancel(self) -> None:
        """Cancel the pipeline.

        Example:
            >>> pipeline.cancel()
        """
        if self._state not in [ExecutionState.CREATED, ExecutionState.QUEUED, ExecutionState.RUNNING]:
            logger.warning(f"Cancelling pipeline in state: {self._state}")
        
        for stage in self._stages:
            stage.cancel()
        
        self._state = ExecutionState.CANCELLED
        self._completed_at = datetime.now(UTC).replace(tzinfo=None)
        logger.info(f"Cancelled pipeline: {self._pipeline_id}")

    def set_metadata(self, key: str, value: Any) -> None:
        """Set pipeline metadata.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> pipeline.set_metadata("description", "My pipeline")
        """
        self._metadata[key] = value
        logger.debug(f"Set pipeline metadata: {key}")

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get pipeline metadata.

        Args:
            key: Metadata key
            default: Default value

        Returns:
            Metadata value or default

        Example:
            >>> value = pipeline.get_metadata("description")
        """
        return self._metadata.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Convert pipeline to dictionary.

        Returns:
            Dictionary representation

        Example:
            >>> data = pipeline.to_dict()
        """
        return {
            "pipeline_id": self._pipeline_id,
            "name": self._name,
            "state": self._state.value,
            "priority": self._priority.value,
            "dependencies": self._dependencies.copy(),
            "stage_count": self.stage_count,
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
            >>> repr(pipeline)
        """
        return f"Pipeline(pipeline_id={self._pipeline_id}, name={self._name}, state={self._state.value})"


# Export
__all__ = [
    "Pipeline",
]
