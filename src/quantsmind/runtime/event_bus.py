"""
Runtime Event Bus Module

This module provides event bus management for the Runtime package.

Purpose
-------
Provide event bus management for the QuantsMind SDK.

Responsibilities
----------------
- Manage event subscriptions
- Dispatch events to subscribers
- Handle event filtering
- Support async event processing

Dependencies
------------
typing (standard library)
logging (standard library)
threading (standard library)
queue (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
quantsmind.runtime.exceptions (runtime exceptions)
quantsmind.runtime.event (event)
"""

from __future__ import annotations

import logging
import queue
import threading
from typing import Any

from quantsmind.runtime.constants import DEFAULT_EVENT_QUEUE_SIZE, DEFAULT_EVENT_TIMEOUT
from quantsmind.runtime.enums import EventType
from quantsmind.runtime.event import Event
from quantsmind.runtime.exceptions import EventError
from quantsmind.runtime.types import EventCallback

logger = logging.getLogger(__name__)


class EventBus:
    """Concrete implementation of an event bus.

    This class provides event bus capabilities.

    Attributes:
        _subscribers: Event subscribers
        _event_queue: Event queue
        _running: Running state
        _worker_thread: Worker thread
        _lock: Thread lock

    Example:
        >>> bus = EventBus()
        >>> bus.subscribe(EventType.ENTITY_CREATED, lambda event: print(event))
        >>> bus.publish(Event(EventType.ENTITY_CREATED, {"task_id": "task_123"}))
    """

    def __init__(self, queue_size: int = DEFAULT_EVENT_QUEUE_SIZE) -> None:
        """Initialize an EventBus.

        Args:
            queue_size: Event queue size

        Example:
            >>> bus = EventBus()
        """
        self._subscribers: dict[EventType, list[EventCallback]] = {}
        self._event_queue: queue.Queue = queue.Queue(maxsize=queue_size)
        self._running = False
        self._worker_thread: threading.Thread | None = None
        self._lock = threading.Lock()
        logger.debug("Created event bus")

    @property
    def subscriber_count(self) -> int:
        """Get the number of subscribers.

        Returns:
            Number of subscribers

        Example:
            >>> print(f"Subscriber count: {bus.subscriber_count}")
        """
        with self._lock:
            return sum(len(subs) for subs in self._subscribers.values())

    @property
    def queue_size(self) -> int:
        """Get the current queue size.

        Returns:
            Current queue size

        Example:
            >>> print(f"Queue size: {bus.queue_size}")
        """
        return self._event_queue.qsize()

    def subscribe(self, event_type: EventType, callback: EventCallback) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Event type to subscribe to
            callback: Callback function

        Example:
            >>> bus.subscribe(EventType.ENTITY_CREATED, lambda event: print(event))
        """
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to event type: {event_type.value}")

    def unsubscribe(self, event_type: EventType, callback: EventCallback) -> bool:
        """Unsubscribe from an event type.

        Args:
            event_type: Event type to unsubscribe from
            callback: Callback function

        Returns:
            True if unsubscribed, False otherwise

        Example:
            >>> unsubscribed = bus.unsubscribe(EventType.ENTITY_CREATED, callback)
        """
        with self._lock:
            if event_type in self._subscribers:
                if callback in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(callback)
                    logger.debug(f"Unsubscribed from event type: {event_type.value}")
                    return True
        return False

    def publish(self, event: Event) -> None:
        """Publish an event.

        Args:
            event: Event to publish

        Raises:
            EventError: If queue is full

        Example:
            >>> bus.publish(Event(EventType.ENTITY_CREATED, {"task_id": "task_123"}))
        """
        try:
            self._event_queue.put(event, timeout=DEFAULT_EVENT_TIMEOUT)
            logger.debug(f"Published event: {event.event_id}")
        except queue.Full:
            raise EventError("Event queue is full", event_id=event.event_id) from None

    def publish_sync(self, event: Event) -> None:
        """Publish an event synchronously.

        Args:
            event: Event to publish

        Example:
            >>> bus.publish_sync(Event(EventType.ENTITY_CREATED, {"task_id": "task_123"}))
        """
        self._dispatch_event(event)

    def _dispatch_event(self, event: Event) -> None:
        """Dispatch an event to subscribers.

        Args:
            event: Event to dispatch
        """
        with self._lock:
            callbacks = self._subscribers.get(event.event_type, []).copy()

        for callback in callbacks:
            try:
                callback(event.to_dict())
            except Exception as e:
                logger.error(f"Event callback failed: {e}", exc_info=True)

    def _process_events(self) -> None:
        """Process events from the queue.

        Example:
            >>> bus._process_events()
        """
        while self._running:
            try:
                event = self._event_queue.get(timeout=1.0)
                self._dispatch_event(event)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Event processing failed: {e}", exc_info=True)

    def start(self) -> None:
        """Start the event bus.

        Example:
            >>> bus.start()
        """
        if self._running:
            return

        self._running = True
        self._worker_thread = threading.Thread(target=self._process_events, daemon=True)
        self._worker_thread.start()
        logger.info("Event bus started")

    def stop(self) -> None:
        """Stop the event bus.

        Example:
            >>> bus.stop()
        """
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5.0)
        logger.info("Event bus stopped")

    def clear_queue(self) -> None:
        """Clear the event queue.

        Example:
            >>> bus.clear_queue()
        """
        while not self._event_queue.empty():
            try:
                self._event_queue.get_nowait()
            except queue.Empty:
                break
        logger.debug("Cleared event queue")

    def get_status(self) -> dict[str, Any]:
        """Get event bus status.

        Returns:
            Event bus status

        Example:
            >>> status = bus.get_status()
        """
        with self._lock:
            return {
                "running": self._running,
                "subscriber_count": self.subscriber_count,
                "queue_size": self.queue_size,
                "subscribed_event_types": [et.value for et in self._subscribers],
            }


# Export
__all__ = [
    "EventBus",
]
