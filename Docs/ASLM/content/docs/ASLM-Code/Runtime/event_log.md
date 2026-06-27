---
title: "event_log"
draft: false
---

## Module `event_log`

`Runtime/event_log.py` — ASLM Code Python module.

---

## Overview

Part of `Runtime`. See **Related** for package index and callers.

---

## Classes

### `class _RunBuffer`

**Purpose:** Type `_RunBuffer` defined in `event_log.py`.

### `class EventLog`

**Purpose:** Type `EventLog` defined in `event_log.py`.

---

## Public functions

#### `def _RunBuffer.__init__() -> None`

**Purpose:** Initialize an empty, open event buffer.

**Steps:**

1. Execute the implementation in the source module.

#### `def EventLog.__init__() -> None`

**Purpose:** Initialize the per-run buffer registry.

**Steps:**

1. Execute the implementation in the source module.

#### `def EventLog.append(run_id, event_type, payload=…) -> RunEvent`

**Purpose:** Append one event, assign its sequence number, and wake subscribers.

**Steps:**

1. Return the computed result to the caller.

#### `def EventLog.read(run_id, after_seq=…) -> list[RunEvent]`

**Purpose:** Return all events recorded after one sequence number.

**Steps:**

1. Return the computed result to the caller.

#### `def EventLog.wait(run_id, after_seq, timeout=…) -> list[RunEvent]`

**Purpose:** Block until new events arrive after one sequence number or the wait times out.

**Steps:**

1. Return the computed result to the caller.

#### `def EventLog.mark_closed(run_id) -> None`

**Purpose:** Mark one run as finished so subscribers can stop following it.

**Steps:**

1. Execute the implementation in the source module.

#### `def EventLog.is_closed(run_id) -> bool`

**Purpose:** Return whether one run has been marked finished.

**Steps:**

1. Return the computed result to the caller.

#### `def EventLog.last_seq(run_id) -> int`

**Purpose:** Return the highest sequence number recorded for one run.

**Steps:**

1. Return the computed result to the caller.

#### `def EventLog.discard(run_id) -> None`

**Purpose:** Drop the buffer for one run once nobody needs its history.

---

## Private functions

#### `def EventLog._buffer(run_id) -> _RunBuffer`

**Purpose:** Return the buffer for one run, creating it on first use.

---

## Related

- [Runtime/_index](../_index/)
