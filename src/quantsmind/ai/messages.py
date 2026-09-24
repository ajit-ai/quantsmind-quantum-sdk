"""Conversation message primitives.

Provider-independent chat messages: validated roles, content, and
round-trip serialization. No model calls happen here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "MessageRole",
    "Message",
]

#: Valid message roles.
MessageRole = str

SYSTEM = "system"
USER = "user"
ASSISTANT = "assistant"
TOOL = "tool"

_VALID_ROLES = frozenset({SYSTEM, USER, ASSISTANT, TOOL})


@dataclass(frozen=True)
class Message:
    """One conversation message.

    Args:
        role: One of ``"system"``, ``"user"``, ``"assistant"``, ``"tool"``.
        content: Message text.
        metadata: Free-form extra fields (e.g. ``tool_call_id``).
    """

    role: MessageRole
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.role not in _VALID_ROLES:
            raise ValueError(f"invalid role {self.role!r}; expected one of {sorted(_VALID_ROLES)}")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {"role": self.role, "content": self.content, "metadata": dict(self.metadata)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Message:
        """Rebuild a message from :meth:`to_dict` output."""
        return cls(
            role=str(data["role"]),
            content=str(data["content"]),
            metadata=dict(data.get("metadata", {})),
        )
