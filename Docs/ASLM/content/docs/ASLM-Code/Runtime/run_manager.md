---
title: "run_manager"
draft: false
---

## Module `run_manager`

`Runtime/run_manager.py` — ASLM Code Python module.

---

## Overview

Part of `Runtime`. See **Related** for package index and callers.

---

## Classes

### `class RunStore`

**Purpose:** Type `RunStore` defined in `run_manager.py`.

### `class RunManager`

**Purpose:** Type `RunManager` defined in `run_manager.py`.

---

## Public functions

#### `def RunStore.__init__() -> None`

**Purpose:** Initialize the empty run registry.

**Steps:**

1. Execute the implementation in the source module.

#### `def RunStore.create(run_id, spec) -> RunInfo`

**Purpose:** Register one new run in the pending state.

#### `def RunStore.set_status(run_id, status, error=…) -> None`

**Purpose:** Update the status (and optional error) of one run.

#### `def RunStore.get(run_id) -> RunInfo | None`

**Purpose:** Return one run's metadata, or None when it is unknown.

#### `def RunStore.list(chat_id=…, status=…) -> list[RunInfo]`

**Purpose:** Return runs matching an optional chat id and status filter.

**Steps:**

1. Return the computed result to the caller.

#### `def RunManager.__init__(executor, config=…, event_log=…, store=…, backend=…) -> None`

**Purpose:** Compose the manager from its config, event log, store, and backend.

**Steps:**

1. Execute the implementation in the source module.

#### `def RunManager.start(spec) -> str`

**Purpose:** Start one run in the background and return its identifier immediately.

**Steps:**

1. Return the computed result to the caller.

#### `def RunManager.subscribe(run_id, from_seq=…) -> Iterator[RunEvent]`

**Purpose:** Yield run events from a sequence offset, then follow the live stream.

**Steps:**

1. Iterate and transform or accumulate state.

#### `def RunManager.get(run_id) -> RunInfo | None`

**Purpose:** Return one run's metadata with its current last sequence number.

**Steps:**

1. Return the computed result to the caller.

#### `def RunManager.list(chat_id=…, status=…) -> list[RunInfo]`

**Purpose:** Return runs matching an optional chat id and status filter.

#### `def RunManager.abort(run_id) -> bool`

**Purpose:** Request cooperative cancellation of one run.

#### `def get_run_manager() -> RunManager`

**Purpose:** Return the process-wide run manager, creating it on first use.

**Steps:**

1. Return the computed result to the caller.

---

## Related

- [Runtime/_index](../_index/)
