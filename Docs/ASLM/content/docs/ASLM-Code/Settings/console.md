---
title: "console"
draft: false
---

## Module `console`

`Settings/console.py` — ASLM Code Python module.

---

## Overview

Part of `Settings`. See **Related** for package index and callers.

---

## Classes

### `class PrintTechData`

**Purpose:** Type `PrintTechData` defined in `console.py`.

---

## Public functions

#### `def PrintTechData.PTD_Print() -> None`

**Purpose:** Print module manifest details and the current startup timestamp.

**Steps:**

1. Execute the implementation in the source module.

---

## Private functions

#### `def _load_module_manifest() -> dict[str, Any] | None`

**Purpose:** Load the local module manifest when it exists and is valid JSON.

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.
3. Parse or serialize JSON payloads.

#### `def _print_separator() -> None`

**Purpose:** Print a standard separator line for console output.

---

## Related

- [Settings/_index](../_index/)
