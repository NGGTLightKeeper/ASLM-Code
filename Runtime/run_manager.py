# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import threading
import uuid
from typing import Iterator

from Runtime.backends.base import RunBackend, RunExecutor
from Runtime.backends.thread_backend import ThreadRunBackend
from Runtime.config.aggregator import ConfigAggregator
from Runtime.event_log import EventLog
from Runtime.executors.stub_executor import execute_stub
from Runtime.types import RunEvent, RunInfo, RunSpec, RunStatus

# How long one subscribe loop blocks while following a live run.
_SUBSCRIBE_POLL_TIMEOUT_S = 2.0


# In-memory registry of run metadata, independent of the event stream.
class RunStore:

    # Initialize the empty run registry.
    def __init__(self) -> None:
        self._runs: dict[str, RunInfo] = {}
        self._lock = threading.RLock()

    # Register one new run in the pending state.
    def create(self, run_id: str, spec: RunSpec) -> RunInfo:
        with self._lock:
            info = RunInfo(run_id=run_id, status=RunStatus.PENDING, spec=spec)
            self._runs[run_id] = info
            return info

    # Update the status (and optional error) of one run.
    def set_status(self, run_id: str, status: RunStatus, error: str | None = None) -> None:
        with self._lock:
            info = self._runs.get(run_id)
            if info is None:
                return
            info.status = status
            if error is not None:
                info.error = error

    # Return one run's metadata, or None when it is unknown.
    def get(self, run_id: str) -> RunInfo | None:
        with self._lock:
            return self._runs.get(run_id)

    # Return runs matching an optional chat id and status filter.
    def list(self, chat_id: str | None = None, status: RunStatus | None = None) -> list[RunInfo]:
        with self._lock:
            runs = list(self._runs.values())
        if chat_id is not None:
            runs = [info for info in runs if info.spec.chat_id == chat_id]
        if status is not None:
            runs = [info for info in runs if info.status == status]
        return runs


# Process-wide facade the whole system uses to drive and observe runs.
class RunManager:

    # Compose the manager from its config, event log, store, and backend.
    def __init__(
        self,
        executor: RunExecutor,
        config: ConfigAggregator | None = None,
        event_log: EventLog | None = None,
        store: RunStore | None = None,
        backend: RunBackend | None = None,
    ) -> None:
        self.config = config or ConfigAggregator()
        self.event_log = event_log or EventLog()
        self.store = store or RunStore()
        self.backend = backend or ThreadRunBackend(self.event_log, executor, self.store)

    # Start one run in the background and return its identifier immediately.
    def start(self, spec: RunSpec) -> str:
        run_id = uuid.uuid4().hex
        self.store.create(run_id, spec)
        self.backend.spawn(run_id, spec)
        return run_id

    # Yield run events from a sequence offset, then follow the live stream.
    def subscribe(self, run_id: str, from_seq: int = 0) -> Iterator[RunEvent]:
        last_seq = from_seq
        while True:
            for event in self.event_log.read(run_id, last_seq):
                last_seq = event.seq
                yield event

            if self.event_log.is_closed(run_id):
                for event in self.event_log.read(run_id, last_seq):
                    last_seq = event.seq
                    yield event
                return

            self.event_log.wait(run_id, last_seq, timeout=_SUBSCRIBE_POLL_TIMEOUT_S)

    # Return one run's metadata with its current last sequence number.
    def get(self, run_id: str) -> RunInfo | None:
        info = self.store.get(run_id)
        if info is not None:
            info.last_seq = self.event_log.last_seq(run_id)
        return info

    # Return runs matching an optional chat id and status filter.
    def list(self, chat_id: str | None = None, status: RunStatus | None = None) -> list[RunInfo]:
        return self.store.list(chat_id=chat_id, status=status)

    # Request cooperative cancellation of one run.
    def abort(self, run_id: str) -> bool:
        return self.backend.abort(run_id)


_manager_lock = threading.Lock()
_manager: RunManager | None = None


# Return the process-wide run manager, creating it on first use.
def get_run_manager() -> RunManager:
    global _manager
    with _manager_lock:
        if _manager is None:
            # The stub executor is swapped for the real ASLM-Chat executor later;
            # the manager and backends do not change when that happens.
            _manager = RunManager(executor=execute_stub)
        return _manager
