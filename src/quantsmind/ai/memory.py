"""Conversation memory with a sliding window.

Keeps system messages pinned while trimming the oldest non-system
messages to fit a configurable window. Deterministic and dependency-free.
"""

from __future__ import annotations

from quantsmind.ai.messages import SYSTEM, Message

__all__ = [
    "ConversationMemory",
]


class ConversationMemory:
    """Ordered message store with windowed recall.

    Args:
        max_messages: Maximum messages retained on recall (system
            messages always retained).
    """

    def __init__(self, max_messages: int = 20) -> None:
        """Initialize empty memory."""
        if max_messages < 1:
            raise ValueError(f"max_messages must be >= 1, got {max_messages!r}")
        self._max_messages = max_messages
        self._messages: list[Message] = []

    @property
    def size(self) -> int:
        """Number of stored messages."""
        return len(self._messages)

    def store(self, message: Message) -> None:
        """Append a message."""
        self._messages.append(message)

    def recall(self) -> list[Message]:
        """Return pinned system messages plus the newest window remainder."""
        system = [message for message in self._messages if message.role == SYSTEM]
        rest = [message for message in self._messages if message.role != SYSTEM]
        room = max(0, self._max_messages - len(system))
        return system + rest[-room:] if room else system

    def clear(self) -> None:
        """Drop all stored messages."""
        self._messages.clear()
