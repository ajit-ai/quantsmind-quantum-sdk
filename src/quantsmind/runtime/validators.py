"""
Runtime Validators Module

This module provides validation functions for the Runtime package.

Purpose
-------
Provide validation functions for the QuantsMind SDK.

Responsibilities
----------------
- Validate configuration
- Validate tasks
- Validate jobs
- Validate workflows

Dependencies
------------
typing (standard library)
logging (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.exceptions (runtime exceptions)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from quantsmind.runtime.exceptions import ValidationError
from quantsmind.runtime.types import ValidationResult, ValidationErrors

logger = logging.getLogger(__name__)


class RuntimeValidator:
    """Concrete implementation of a runtime validator.

    This class provides validation capabilities.

    Example:
        >>> validator = RuntimeValidator()
        >>> is_valid, errors = validator.validate_config({"timeout": 300.0})
    """

    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate configuration.

        Args:
            config: Configuration to validate

        Returns:
            Tuple of (is_valid, errors)

        Example:
            >>> is_valid, errors = validator.validate_config({"timeout": 300.0})
        """
        errors: ValidationErrors = []

        if not isinstance(config, dict):
            errors.append("Configuration must be a dictionary")
            return (False, errors)

        # Validate timeout
        if "timeout" in config:
            if not isinstance(config["timeout"], (int, float)):
                errors.append("Timeout must be a number")
            elif config["timeout"] <= 0:
                errors.append("Timeout must be positive")

        # Validate max_workers
        if "max_workers" in config:
            if not isinstance(config["max_workers"], int):
                errors.append("Max workers must be an integer")
            elif config["max_workers"] <= 0:
                errors.append("Max workers must be positive")

        # Validate retry_count
        if "retry_count" in config:
            if not isinstance(config["retry_count"], int):
                errors.append("Retry count must be an integer")
            elif config["retry_count"] < 0:
                errors.append("Retry count must be non-negative")

        return (len(errors) == 0, errors)

    def validate_task(self, task: Any) -> ValidationResult:
        """Validate a task.

        Args:
            task: Task to validate

        Returns:
            Tuple of (is_valid, errors)

        Example:
            >>> is_valid, errors = validator.validate_task(task)
        """
        errors: ValidationErrors = []

        if not hasattr(task, "task_id"):
            errors.append("Task must have task_id attribute")

        if not hasattr(task, "name"):
            errors.append("Task must have name attribute")
        elif not task.name:
            errors.append("Task name cannot be empty")

        if not hasattr(task, "func"):
            errors.append("Task must have func attribute")
        elif not callable(task.func):
            errors.append("Task func must be callable")

        if hasattr(task, "validate"):
            is_valid, task_errors = task.validate()
            if not is_valid:
                errors.extend(task_errors)

        return (len(errors) == 0, errors)

    def validate_job(self, job: Any) -> ValidationResult:
        """Validate a job.

        Args:
            job: Job to validate

        Returns:
            Tuple of (is_valid, errors)

        Example:
            >>> is_valid, errors = validator.validate_job(job)
        """
        errors: ValidationErrors = []

        if not hasattr(job, "job_id"):
            errors.append("Job must have job_id attribute")

        if not hasattr(job, "name"):
            errors.append("Job must have name attribute")
        elif not job.name:
            errors.append("Job name cannot be empty")

        if not hasattr(job, "tasks"):
            errors.append("Job must have tasks attribute")
        elif not job.tasks:
            errors.append("Job must have at least one task")

        if hasattr(job, "validate"):
            is_valid, job_errors = job.validate()
            if not is_valid:
                errors.extend(job_errors)

        return (len(errors) == 0, errors)

    def validate_workflow(self, workflow: Any) -> ValidationResult:
        """Validate a workflow.

        Args:
            workflow: Workflow to validate

        Returns:
            Tuple of (is_valid, errors)

        Example:
            >>> is_valid, errors = validator.validate_workflow(workflow)
        """
        errors: ValidationErrors = []

        if not hasattr(workflow, "workflow_id"):
            errors.append("Workflow must have workflow_id attribute")

        if not hasattr(workflow, "name"):
            errors.append("Workflow must have name attribute")
        elif not workflow.name:
            errors.append("Workflow name cannot be empty")

        if not hasattr(workflow, "jobs"):
            errors.append("Workflow must have jobs attribute")
        elif not workflow.jobs:
            errors.append("Workflow must have at least one job")

        if hasattr(workflow, "validate"):
            is_valid, workflow_errors = workflow.validate()
            if not is_valid:
                errors.extend(workflow_errors)

        return (len(errors) == 0, errors)

    def validate_pipeline(self, pipeline: Any) -> ValidationResult:
        """Validate a pipeline.

        Args:
            pipeline: Pipeline to validate

        Returns:
            Tuple of (is_valid, errors)

        Example:
            >>> is_valid, errors = validator.validate_pipeline(pipeline)
        """
        errors: ValidationErrors = []

        if not hasattr(pipeline, "pipeline_id"):
            errors.append("Pipeline must have pipeline_id attribute")

        if not hasattr(pipeline, "name"):
            errors.append("Pipeline must have name attribute")
        elif not pipeline.name:
            errors.append("Pipeline name cannot be empty")

        if not hasattr(pipeline, "stages"):
            errors.append("Pipeline must have stages attribute")
        elif not pipeline.stages:
            errors.append("Pipeline must have at least one stage")

        if hasattr(pipeline, "validate"):
            is_valid, pipeline_errors = pipeline.validate()
            if not is_valid:
                errors.extend(pipeline_errors)

        return (len(errors) == 0, errors)

    def validate_resource(self, resource: Any) -> ValidationResult:
        """Validate a resource.

        Args:
            resource: Resource to validate

        Returns:
            Tuple of (is_valid, errors)

        Example:
            >>> is_valid, errors = validator.validate_resource(resource)
        """
        errors: ValidationErrors = []

        if not hasattr(resource, "resource_id"):
            errors.append("Resource must have resource_id attribute")

        if not hasattr(resource, "resource_type"):
            errors.append("Resource must have resource_type attribute")

        if not hasattr(resource, "capacity"):
            errors.append("Resource must have capacity attribute")
        elif resource.capacity <= 0:
            errors.append("Resource capacity must be positive")

        return (len(errors) == 0, errors)


# Export
__all__ = [
    "RuntimeValidator",
]
