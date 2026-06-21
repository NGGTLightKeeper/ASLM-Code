# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import threading
from typing import Any

from Runtime.types import RunEvent


# Append-only buffer of events for one run, guarded by a single condition.
class _RunBuffer:

    # Initialize an empty, open event buffer.
    def __init__(self) -> None:
        self.events: list[RunEvent] = []
        self.closed = False
        self.condition = threading.Condition()


# In-memory event store that lets subscribers replay and follow live events.
class EventLog:

    # Initialize the per-run buffer registry.
    def __init__(self) -> None:
        self._buffers: dict[str, _RunBuffer] = {}
        self._lock = threading.Lock()

    # Return the buffer for one run, creating it on first use.
    def _buffer(self, run_id: str) -> _RunBuffer:
        with self._lock:
            buffer = self._buffers.get(run_id)
            if buffer is None:
                buffer = _RunBuffer()
                self._buffers[run_id] = buffer
            return buffer

    # Append one event, assign its sequence number, and wake subscribers.
    def append(self, run_id: str, event_type: str, payload: dict[str, Any] | None = None) -> RunEvent:
        buffer = self._buffer(run_id)
        with buffer.condition:
            seq = len(buffer.events) + 1
            event = RunEvent(seq=seq, type=str(event_type), payload=dict(payload or {}))
            buffer.events.append(event)
            buffer.condition.notify_all()
            return event

    # Return all events recorded after one sequence number.
    def read(self, run_id: str, after_seq: int = 0) -> list[RunEvent]:
        buffer = self._buffer(run_id)
        with buffer.condition:
            return [event for event in buffer.events if event.seq > after_seq]

    # Block until new events arrive after one sequence number or the wait times out.
    def wait(self, run_id: str, after_seq: int, timeout: float = 2.0) -> list[RunEvent]:
        buffer = self._buffer(run_id)
        with buffer.condition:
            pending = [event for event in buffer.events if event.seq > after_seq]
            if pending or buffer.closed:
                return pending
            buffer.condition.wait(timeout)
            return [event for event in buffer.events if event.seq > after_seq]

    # Mark one run as finished so subscribers can stop following it.
    def mark_closed(self, run_id: str) -> None:
        buffer = self._buffer(run_id)
        with buffer.condition:
            buffer.closed = True
            buffer.condition.notify_all()

    # Return whether one run has been marked finished.
    def is_closed(self, run_id: str) -> bool:
        buffer = self._buffer(run_id)
        with buffer.condition:
            return buffer.closed

    # Return the highest sequence number recorded for one run.
    def last_seq(self, run_id: str) -> int:
        buffer = self._buffer(run_id)
        with buffer.condition:
            return buffer.events[-1].seq if buffer.events else 0

    # Drop the buffer for one run once nobody needs its history.
    def discard(self, run_id: str) -> None:
        with self._lock:
            self._buffers.pop(run_id, None)
