---
title: "lms_direct_executor"
draft: false
---

## Module `lms_direct_executor`

`Runtime/executors/lms_direct_executor.py` — ASLM Code Python module.

---

## Overview

Part of `Runtime\executors`. See **Related** for package index and callers.

---

## Public functions

#### `def list_models(base_url) -> list[str]`

**Purpose:** Return the list of model ids currently loaded in a local OpenAI-compat provider.

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.
3. Parse or serialize JSON payloads.

#### `def execute_lms_direct(spec, emit, should_abort) -> None`

**Purpose:** Emits "token" events as deltas arrive and a final "message" event on completion.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Handle errors and map them to a safe response.
3. Iterate and transform or accumulate state.
4. Parse or serialize JSON payloads.

---

## Private functions

#### `def _base_http_url(raw) -> str`

**Purpose:** Normalize one raw engine base_url (may lack scheme) to a full http:// URL.

**Steps:**

1. Return the computed result to the caller.

#### `def _parse_sse_line(line) -> dict | None`

**Purpose:** Parse one SSE "data: ..." line into a dict; return None for control lines or [DONE].

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.
3. Parse or serialize JSON payloads.

---

## Related

- [executors/_index](../_index/)
