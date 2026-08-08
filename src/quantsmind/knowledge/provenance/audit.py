"""
Audit Module

This module provides audit definitions for the Knowledge package.

Purpose
-------
Provide audit management for provenance tracking.

Responsibilities
----------------
- Define audit structure
- Support audit operations
- Support audit validation
- Support audit metadata

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
from quantsmind.knowledge.types import ValidationResult


class AuditRecord:
    """Concrete implementation of an audit record.

    This class provides audit record functionality.

    Attributes:
        _id: Record ID
        _timestamp: Record timestamp
        _event_type: Event type
        _user: User who performed the action
        _resource: Resource affected
        _action: Action performed
        _details: Event details
        _metadata: Record metadata

    Example:
        >>> record = AuditRecord("record_001", "access", "user_001", "dataset_001")
        >>> record.event_type
    """

    def __init__(
        self,
        record_id: str,
        event_type: str,
        user: str,
        resource: str,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an AuditRecord.

        Args:
            record_id: Record ID
            event_type: Event type
            user: User who performed the action
            resource: Resource affected
            action: Action performed
            details: Event details
            metadata: Record metadata

        Example:
            >>> record = AuditRecord("record_001", "access", "user_001", "dataset_001", "read")
        """
        if not record_id:
            raise ProvenanceError("Record ID cannot be empty", {"record_id": record_id})

        if not event_type:
            raise ProvenanceError("Event type cannot be empty", {"event_type": event_type})

        if not user:
            raise ProvenanceError("User cannot be empty", {"user": user})

        if not resource:
            raise ProvenanceError("Resource cannot be empty", {"resource": resource})

        self._id = record_id
        self._timestamp = datetime.utcnow()
        self._event_type = event_type
        self._user = user
        self._resource = resource
        self._action = action
        self._details = details or {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the record ID.

        Returns:
            Record ID

        Example:
            >>> rid = record.id
        """
        return self._id

    @property
    def timestamp(self) -> datetime:
        """Get the record timestamp.

        Returns:
            Timestamp

        Example:
            >>> timestamp = record.timestamp
        """
        return self._timestamp

    @property
    def event_type(self) -> str:
        """Get the event type.

        Returns:
            Event type

        Example:
            >>> event_type = record.event_type
        """
        return self._event_type

    @property
    def user(self) -> str:
        """Get the user.

        Returns:
            User who performed the action

        Example:
            >>> user = record.user
        """
        return self._user

    @property
    def resource(self) -> str:
        """Get the resource.

        Returns:
            Resource affected

        Example:
            >>> resource = record.resource
        """
        return self._resource

    @property
    def action(self) -> str:
        """Get the action.

        Returns:
            Action performed

        Example:
            >>> action = record.action
        """
        return self._action

    @property
    def details(self) -> Dict[str, Any]:
        """Get the details.

        Returns:
            Event details

        Example:
            >>> details = record.details
        """
        return self._details.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the record metadata.

        Returns:
            Record metadata

        Example:
            >>> metadata = record.metadata
        """
        return self._metadata.copy()

    def add_detail(self, key: str, value: Any) -> None:
        """Add a detail to the record.

        Args:
            key: Detail key
            value: Detail value

        Example:
            >>> record.add_detail("ip_address", "192.168.1.1")
        """
        self._details[key] = value

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the record.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> record.add_metadata("session_id", "session_001")
        """
        self._metadata[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Record definition

        Example:
            >>> data = record.to_dict()
        """
        return {
            "id": self._id,
            "timestamp": self._timestamp.isoformat(),
            "event_type": self._event_type,
            "user": self._user,
            "resource": self._resource,
            "action": self._action,
            "details": self._details,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(record)
        """
        return f"AuditRecord(id={self._id}, event_type={self._event_type}, user={self._user}, resource={self._resource})"


class AuditLog:
    """Concrete implementation of an audit log.

    This class provides audit log functionality for tracking events.

    Attributes:
        _id: Audit log ID
        _records: Audit records
        _metadata: Audit log metadata

    Example:
        >>> log = AuditLog("audit_log_001")
        >>> log.add_record(AuditRecord("record_001", "access", "user_001", "dataset_001", "read"))
    """

    def __init__(
        self,
        audit_log_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an AuditLog.

        Args:
            audit_log_id: Audit log ID
            metadata: Audit log metadata

        Example:
            >>> log = AuditLog("audit_log_001")
        """
        if not audit_log_id:
            raise ProvenanceError("Audit log ID cannot be empty", {"audit_log_id": audit_log_id})

        self._id = audit_log_id
        self._records: List[AuditRecord] = []
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the audit log ID.

        Returns:
            Audit log ID

        Example:
            >>> aid = log.id
        """
        return self._id

    @property
    def records(self) -> List[AuditRecord]:
        """Get the audit records.

        Returns:
            Audit records

        Example:
            >>> records = log.records
        """
        return self._records.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the audit log metadata.

        Returns:
            Audit log metadata

        Example:
            >>> metadata = log.metadata
        """
        return self._metadata.copy()

    def add_record(self, record: AuditRecord) -> None:
        """Add a record to the audit log.

        Args:
            record: Audit record

        Example:
            >>> log.add_record(AuditRecord("record_001", "access", "user_001", "dataset_001", "read"))
        """
        self._records.append(record)

    def remove_record(self, record_id: str) -> bool:
        """Remove a record from the audit log.

        Args:
            record_id: Record ID

        Returns:
            True if removed

        Example:
            >>> removed = log.remove_record("record_001")
        """
        for i, record in enumerate(self._records):
            if record.id == record_id:
                del self._records[i]
                return True
        return False

    def get_record(self, record_id: str) -> Optional[AuditRecord]:
        """Get a record by ID.

        Args:
            record_id: Record ID

        Returns:
            Audit record or None

        Example:
            >>> record = log.get_record("record_001")
        """
        for record in self._records:
            if record.id == record_id:
                return record
        return None

    def get_records_by_event_type(self, event_type: str) -> List[AuditRecord]:
        """Get records by event type.

        Args:
            event_type: Event type

        Returns:
            List of records

        Example:
            >>> records = log.get_records_by_event_type("access")
        """
        return [record for record in self._records if record.event_type == event_type]

    def get_records_by_user(self, user: str) -> List[AuditRecord]:
        """Get records by user.

        Args:
            user: User ID

        Returns:
            List of records

        Example:
            >>> records = log.get_records_by_user("user_001")
        """
        return [record for record in self._records if record.user == user]

    def get_records_by_resource(self, resource: str) -> List[AuditRecord]:
        """Get records by resource.

        Args:
            resource: Resource ID

        Returns:
            List of records

        Example:
            >>> records = log.get_records_by_resource("dataset_001")
        """
        return [record for record in self._records if record.resource == resource]

    def get_records_by_time_range(self, start: datetime, end: datetime) -> List[AuditRecord]:
        """Get records within a time range.

        Args:
            start: Start timestamp
            end: End timestamp

        Returns:
            List of records

        Example:
            >>> records = log.get_records_by_time_range(start, end)
        """
        return [record for record in self._records if start <= record.timestamp <= end]

    def get_records_by_action(self, action: str) -> List[AuditRecord]:
        """Get records by action.

        Args:
            action: Action type

        Returns:
            List of records

        Example:
            >>> records = log.get_records_by_action("read")
        """
        return [record for record in self._records if record.action == action]

    def get_recent_records(self, limit: int = 10) -> List[AuditRecord]:
        """Get recent records.

        Args:
            limit: Number of records to return

        Returns:
            List of recent records

        Example:
            >>> recent = log.get_recent_records(10)
        """
        sorted_records = sorted(self._records, key=lambda r: r.timestamp, reverse=True)
        return sorted_records[:limit]

    def get_audit_trail(self, resource: str) -> List[AuditRecord]:
        """Get the audit trail for a resource.

        Args:
            resource: Resource ID

        Returns:
            List of records for the resource

        Example:
            >>> trail = log.get_audit_trail("dataset_001")
        """
        resource_records = self.get_records_by_resource(resource)
        return sorted(resource_records, key=lambda r: r.timestamp)

    def validate(self) -> ValidationResult:
        """Validate the audit log.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = log.validate()
        """
        errors = []

        if not self._id:
            errors.append("Audit log ID cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Audit log definition

        Example:
            >>> data = log.to_dict()
        """
        return {
            "id": self._id,
            "records": [record.to_dict() for record in self._records],
            "record_count": len(self._records),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(log)
        """
        return f"AuditLog(id={self._id}, records={len(self._records)})"


# Export
__all__ = [
    "AuditRecord",
    "AuditLog",
]
