# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import logging
import threading

from Runtime.backends.base import RunExecutor
from Runtime.event_log import EventLog
from Runtime.types import RunSpec, RunStatus

logger = logging.getLogger(__name__)


# Run backend that executes each run on its own daemon thread in-process.
class ThreadRunBackend:

    # Bind the backend to the shared event log, executor, and status store.
    def __init__(self, event_log: EventLog, executor: RunExecutor, store: "RunStore") -> None:
        self._event_log = event_log
        self._executor = executor
        self._store = store
        self._lock = threading.Lock()
        self._aborts: dict[str, threading.Event] = {}

    # Start one run on a background thread and return immediately.
    def spawn(self, run_id: str, spec: RunSpec) -> None:
        abort_event = threading.Event()
        with self._lock:
            self._aborts[run_id] = abort_event

        thread = threading.Thread(
            target=self._run,
            args=(run_id, spec, abort_event),
            name=f"aslm-run-{run_id}",
            daemon=True,
        )
        thread.start()

    # Request cooperative cancellation for one running thread.
    def abort(self, run_id: str) -> bool:
        with self._lock:
            abort_event = self._aborts.get(run_id)
        if abort_event is None:
            return False
        abort_event.set()
        return True

    # Execute one run, funneling its output and status into shared state.
    def _run(self, run_id: str, spec: RunSpec, abort_event: threading.Event) -> None:
        # Bind the emit sink to this run so the executor stays backend-agnostic.
        def emit(event_type: str, payload: dict | None = None) -> object:
            return self._event_log.append(run_id, event_type, payload or {})

        self._store.set_status(run_id, RunStatus.RUNNING)
        emit("status", {"status": RunStatus.RUNNING.value})

        try:
            self._executor(spec, emit, abort_event.is_set)
        except Exception as exc:
            logger.exception("Run %s failed", run_id)
            self._finish(run_id, RunStatus.FAILED, emit, error=str(exc))
            return

        if abort_event.is_set():
            self._finish(run_id, RunStatus.ABORTED, emit)
        else:
            self._finish(run_id, RunStatus.DONE, emit)

    # Record the terminal status, emit closing events, and release run state.
    def _finish(self, run_id: str, status: RunStatus, emit, error: str | None = None) -> None:
        self._store.set_status(run_id, status, error=error)
        if error:
            emit("error", {"message": error})
        emit("status", {"status": status.value})
        emit("done", {"status": status.value})
        self._event_log.mark_closed(run_id)
        with self._lock:
            self._aborts.pop(run_id, None)
