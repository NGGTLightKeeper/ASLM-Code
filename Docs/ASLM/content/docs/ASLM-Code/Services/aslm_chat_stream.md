---
title: "aslm_chat_stream"
draft: false
---

## Module `aslm_chat_stream`

`Services/aslm_chat_stream.py` — ASLM Code Python module.

---

## Overview

Part of `Services`. See **Related** for package index and callers.

---

## Classes

### `class ChatStreamAccumulator`

**Purpose:** Accumulate ASLM-Chat plain-text stream chunks for relay persistence.

---

## Public functions

#### `def strip_stream_markers(text) -> str`

**Purpose:** Strip control markers from one assistant-visible string.

**Steps:**

1. Return the computed result to the caller.

#### `def parse_completed_stream(text, *, emit_thinking=…) -> tuple[str, str, list[dict[str, Any]]]`

**Purpose:** Extract visible text, thinking text, and transcript entries from a full stream body.

**Steps:**

1. Return the computed result to the caller.
2. Iterate and transform or accumulate state.

#### `def ChatStreamAccumulator.__init__(*, emit_thinking=…) -> None`

**Purpose:** Implements `ChatStreamAccumulator.__init__` in `aslm_chat_stream.py`.

**Steps:**

1. Execute the implementation in the source module.

#### `def ChatStreamAccumulator.append(chunk) -> int`

**Purpose:** Append one streamed chunk and return the updated buffer length.

**Steps:**

1. Return the computed result to the caller.

#### `def ChatStreamAccumulator.snapshot() -> tuple[str, str, list[dict[str, Any]]]`

**Purpose:** Return the latest parsed visible/thinking/transcript snapshot.

---

## Private functions

#### `def _parse_marker_json(raw) -> dict[str, Any] | None`

**Purpose:** Parse one tool marker JSON payload safely.

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.
3. Parse or serialize JSON payloads.

---

## Related

- [Services/_index](../_index/)
