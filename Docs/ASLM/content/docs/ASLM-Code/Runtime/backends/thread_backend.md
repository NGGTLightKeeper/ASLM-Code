---
title: "thread_backend"
draft: false
---

## Module `thread_backend`

`Runtime/backends/thread_backend.py` — ASLM Code Python module.

---

## Overview

Part of `Runtime\backends`. See **Related** for package index and callers.

---

## Classes

### `class ThreadRunBackend`

**Purpose:** Type `ThreadRunBackend` defined in `thread_backend.py`.

---

## Public functions

#### `def ThreadRunBackend.__init__(event_log, executor, store) -> None`

**Purpose:** Bind the backend to the shared event log, executor, and status store.

**Steps:**

1. Execute the implementation in the source module.

#### `def ThreadRunBackend.spawn(run_id, spec) -> None`

**Purpose:** Start one run on a background thread and return immediately.

**Steps:**

1. Execute the implementation in the source module.

#### `def ThreadRunBackend.abort(run_id) -> bool`

**Purpose:** Request cooperative cancellation for one running thread.

**Steps:**

1. Return the computed result to the caller.

---

## Private functions

#### `def ThreadRunBackend._run(run_id, spec, abort_event) -> None`

**Purpose:** Execute one run, funneling its output and status into shared state.

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.

#### `def ThreadRunBackend._finish(run_id, status, emit, error=…) -> None`

**Purpose:** Record the terminal status, emit closing events, and release run state.

**Steps:**

1. Execute the implementation in the source module.

---

## Related

- [backends/_index](../_index/)
