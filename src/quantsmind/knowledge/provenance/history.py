"""
History Module

This module provides history definitions for the Knowledge package.

Purpose
-------
Provide history management for provenance tracking.

Responsibilities
----------------
- Define history structure
- Support history operations
- Support history validation
- Support history metadata

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
from typing import Any

from quantsmind.knowledge.exceptions import ProvenanceError
from quantsmind.knowledge.types import ValidationResult


class HistoryEntry:
    """Concrete implementation of a history entry.

    This class provides history entry functionality.

    Attributes:
        _id: Entry ID
        _timestamp: Entry timestamp
        _action: Action performed
        _actor: Actor who performed the action
        _changes: Changes made
        _metadata: Entry metadata

    Example:
        >>> entry = HistoryEntry("entry_001", "create", "user_001")
        >>> entry.action
    """

    def __init__(
        self,
        entry_id: str,
        action: str,
        actor: str,
        changes: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a HistoryEntry.

        Args:
            entry_id: Entry ID
            action: Action performed
            actor: Actor who performed the action
            changes: Changes made
            metadata: Entry metadata

        Example:
            >>> entry = HistoryEntry("entry_001", "create", "user_001")
        """
        if not entry_id:
            raise ProvenanceError("Entry ID cannot be empty", {"entry_id": entry_id})

        if not action:
            raise ProvenanceError("Action cannot be empty", {"action": action})

        if not actor:
            raise ProvenanceError("Actor cannot be empty", {"actor": actor})

        self._id = entry_id
        self._timestamp = datetime.utcnow()
        self._action = action
        self._actor = actor
        self._changes = changes or {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the entry ID.

        Returns:
            Entry ID

        Example:
            >>> eid = entry.id
        """
        return self._id

    @property
    def timestamp(self) -> datetime:
        """Get the entry timestamp.

        Returns:
            Timestamp

        Example:
            >>> timestamp = entry.timestamp
        """
        return self._timestamp

    @property
    def action(self) -> str:
        """Get the action.

        Returns:
            Action performed

        Example:
            >>> action = entry.action
        """
        return self._action

    @property
    def actor(self) -> str:
        """Get the actor.

        Returns:
            Actor who performed the action

        Example:
            >>> actor = entry.actor
        """
        return self._actor

    @property
    def changes(self) -> dict[str, Any]:
        """Get the changes.

        Returns:
            Changes made

        Example:
            >>> changes = entry.changes
        """
        return self._changes.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the entry metadata.

        Returns:
            Entry metadata

        Example:
            >>> metadata = entry.metadata
        """
        return self._metadata.copy()

    def add_change(self, key: str, value: Any) -> None:
        """Add a change to the entry.

        Args:
            key: Change key
            value: Change value

        Example:
            >>> entry.add_change("field", "new_value")
        """
        self._changes[key] = value

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the entry.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> entry.add_metadata("source", "api")
        """
        self._metadata[key] = value

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Entry definition

        Example:
            >>> data = entry.to_dict()
        """
        return {
            "id": self._id,
            "timestamp": self._timestamp.isoformat(),
            "action": self._action,
            "actor": self._actor,
            "changes": self._changes,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(entry)
        """
        return f"HistoryEntry(id={self._id}, action={self._action}, actor={self._actor}, timestamp={self._timestamp.isoformat()})"


class History:
    """Concrete implementation of a history.

    This class provides history functionality for tracking changes over time.

    Attributes:
        _id: History ID
        _target_id: Target entity ID
        _entries: History entries
        _metadata: History metadata

    Example:
        >>> history = History("history_001", "entity_001")
        >>> history.add_entry(HistoryEntry("entry_001", "create", "user_001"))
    """

    def __init__(
        self,
        history_id: str,
        target_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a History.

        Args:
            history_id: History ID
            target_id: Target entity ID
            metadata: History metadata

        Example:
            >>> history = History("history_001", "entity_001")
        """
        if not history_id:
            raise ProvenanceError("History ID cannot be empty", {"history_id": history_id})

        if not target_id:
            raise ProvenanceError("Target ID cannot be empty", {"target_id": target_id})

        self._id = history_id
        self._target_id = target_id
        self._entries: list[HistoryEntry] = []
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the history ID.

        Returns:
            History ID

        Example:
            >>> hid = history.id
        """
        return self._id

    @property
    def target_id(self) -> str:
        """Get the target ID.

        Returns:
            Target entity ID

        Example:
            >>> target_id = history.target_id
        """
        return self._target_id

    @property
    def entries(self) -> list[HistoryEntry]:
        """Get the history entries.

        Returns:
            History entries

        Example:
            >>> entries = history.entries
        """
        return self._entries.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the history metadata.

        Returns:
            History metadata

        Example:
            >>> metadata = history.metadata
        """
        return self._metadata.copy()

    def add_entry(self, entry: HistoryEntry) -> None:
        """Add an entry to the history.

        Args:
            entry: History entry

        Example:
            >>> history.add_entry(HistoryEntry("entry_001", "create", "user_001"))
        """
        self._entries.append(entry)

    def remove_entry(self, entry_id: str) -> bool:
        """Remove an entry from the history.

        Args:
            entry_id: Entry ID

        Returns:
            True if removed

        Example:
            >>> removed = history.remove_entry("entry_001")
        """
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id:
                del self._entries[i]
                return True
        return False

    def get_entry(self, entry_id: str) -> HistoryEntry | None:
        """Get an entry by ID.

        Args:
            entry_id: Entry ID

        Returns:
            History entry or None

        Example:
            >>> entry = history.get_entry("entry_001")
        """
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        return None

    def get_entries_by_action(self, action: str) -> list[HistoryEntry]:
        """Get entries by action.

        Args:
            action: Action type

        Returns:
            List of entries

        Example:
            >>> entries = history.get_entries_by_action("create")
        """
        return [entry for entry in self._entries if entry.action == action]

    def get_entries_by_actor(self, actor: str) -> list[HistoryEntry]:
        """Get entries by actor.

        Args:
            actor: Actor ID

        Returns:
            List of entries

        Example:
            >>> entries = history.get_entries_by_actor("user_001")
        """
        return [entry for entry in self._entries if entry.actor == actor]

    def get_entries_by_time_range(self, start: datetime, end: datetime) -> list[HistoryEntry]:
        """Get entries within a time range.

        Args:
            start: Start timestamp
            end: End timestamp

        Returns:
            List of entries

        Example:
            >>> entries = history.get_entries_by_time_range(start, end)
        """
        return [entry for entry in self._entries if start <= entry.timestamp <= end]

    def get_latest_entry(self) -> HistoryEntry | None:
        """Get the latest entry.

        Returns:
            Latest entry or None

        Example:
            >>> latest = history.get_latest_entry()
        """
        if not self._entries:
            return None
        return max(self._entries, key=lambda e: e.timestamp)

    def get_timeline(self) -> list[dict[str, Any]]:
        """Get the history timeline.

        Returns:
            Timeline as list of dictionaries

        Example:
            >>> timeline = history.get_timeline()
        """
        sorted_entries = sorted(self._entries, key=lambda e: e.timestamp)
        return [entry.to_dict() for entry in sorted_entries]

    def validate(self) -> ValidationResult:
        """Validate the history.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = history.validate()
        """
        errors = []

        if not self._id:
            errors.append("History ID cannot be empty")

        if not self._target_id:
            errors.append("Target ID cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            History definition

        Example:
            >>> data = history.to_dict()
        """
        return {
            "id": self._id,
            "target_id": self._target_id,
            "entries": [entry.to_dict() for entry in self._entries],
            "entry_count": len(self._entries),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(history)
        """
        return f"History(id={self._id}, target={self._target_id}, entries={len(self._entries)})"


# Export
__all__ = [
    "HistoryEntry",
    "History",
]
