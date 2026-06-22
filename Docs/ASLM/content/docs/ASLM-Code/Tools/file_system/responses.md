---
title: "responses"
draft: false
---

## Module `responses`

`Tools/file_system/responses.py` — ASLM Code Python module.

---

## Overview

Part of `Tools\file_system`. See **Related** for package index and callers.

---

## Classes

### `class ToolError`

**Purpose:** Type `ToolError` defined in `responses.py`.

---

## Public functions

#### `def ToolError.__str__() -> str`

**Purpose:** Return the human-readable message for this error.

#### `def success_response(tool, result=…, *, warnings=…, truncated=…) -> dict[str, Any]`

**Purpose:** Wrap a successful tool result in the shared tool envelope.

#### `def error_response(tool, error_type, message, *, result=…, warnings=…) -> dict[str, Any]`

**Purpose:** Wrap a failed tool result in the shared tool envelope.

#### `def exception_response(tool, exc) -> dict[str, Any]`

**Purpose:** Map a raised Python exception into a typed tool error envelope.

**Steps:**

1. Return the computed result to the caller.

---

## Related

- [file_system/_index](../_index/)
