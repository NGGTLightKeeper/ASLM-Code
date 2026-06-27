---
title: "run_views"
draft: false
---

## Module `run_views`

`Apps/UI/run_views.py` — ASLM Code Python module.

---

## Overview

Part of `Apps\UI`. See **Related** for package index and callers.

---

## Public functions

#### `def run_start_api(request)`

**Purpose:** Start one background run and return its identifier without blocking.

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.

#### `def run_stream_api(request, run_id)`

**Purpose:** Stream one run's events as newline-delimited JSON, resuming from a sequence.

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.
3. Iterate and transform or accumulate state.
4. Parse or serialize JSON payloads.

#### `def run_info_api(request, run_id)`

**Purpose:** Return one run's current metadata snapshot.

**Steps:**

1. Return the computed result to the caller.

#### `def run_abort_api(request, run_id)`

**Purpose:** Request cooperative cancellation of one run.

**Steps:**

1. Return the computed result to the caller.

---

## Private functions

#### `def _read_json_body(request) -> dict[str, Any]`

**Purpose:** Parse the JSON request body into a mapping, tolerating empty payloads.

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.
3. Parse or serialize JSON payloads.

#### `def _overrides_from_request(data) -> RunOverrides`

**Purpose:** Build per-run overrides from the request payload.

---

## Related

- [UI/_index](../_index/)
