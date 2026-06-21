# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

from typing import Callable, Protocol

from Runtime.types import RunSpec

# An executor performs the actual work of one run.
# It receives the frozen spec, an ``emit(event_type, payload)`` sink, and a
# ``should_abort()`` predicate it must poll cooperatively. It never returns a
# result directly; all output flows through ``emit``.
RunExecutor = Callable[[RunSpec, "EmitFn", Callable[[], bool]], None]

# Sink used by an executor to publish one event into the run's event log.
EmitFn = Callable[[str, dict], object]


# Contract every run backend implements, regardless of threads or processes.
class RunBackend(Protocol):

    # Start executing one run; must return immediately without blocking.
    def spawn(self, run_id: str, spec: RunSpec) -> None: ...

    # Request cooperative cancellation of one run.
    def abort(self, run_id: str) -> bool: ...
