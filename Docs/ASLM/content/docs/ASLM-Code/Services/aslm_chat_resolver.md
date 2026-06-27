---
title: "aslm_chat_resolver"
draft: false
---

## Module `aslm_chat_resolver`

`Services/aslm_chat_resolver.py` — ASLM Code Python module.

---

## Overview

Part of `Services`. See **Related** for package index and callers.

---

## Classes

### `class ChatNotAvailableError`

**Purpose:** Raised when ASLM-Chat cannot be resolved or reached.

---

## Public functions

#### `def invalidate_chat_base_url_cache() -> None`

**Purpose:** Clear the cached ASLM-Chat base URL.

**Steps:**

1. Execute the implementation in the source module.

#### `def resolve_chat_base_url(*, force_refresh=…) -> str`

**Purpose:** Resolve the ASLM-Chat HTTP base URL via the host interop registry.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.

#### `def ensure_chat_running(*, timeout_seconds=…) -> str`

**Purpose:** Ask the host to start ASLM-Chat when it is not already running.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.
3. Handle errors and map them to a safe response.
4. Iterate and transform or accumulate state.

#### `def ping_chat_backend(*, base_url=…) -> dict[str, Any]`

**Purpose:** Perform a lightweight health check against ASLM-Chat.

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.

#### `def is_chat_available() -> bool`

**Purpose:** Return whether ASLM-Chat appears reachable right now.

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.

---

## Private functions

#### `def _pick_host_url(host) -> str`

**Purpose:** Return the direct module HTTP base URL for one running module host entry.

**Steps:**

1. Return the computed result to the caller.

#### `def _extract_chat_base_url(registry) -> str`

**Purpose:** Find the ASLM-Chat base URL inside one interop registry payload.

**Steps:**

1. Return the computed result to the caller.
2. Iterate and transform or accumulate state.

---

## Related

- [Services/_index](../_index/)
