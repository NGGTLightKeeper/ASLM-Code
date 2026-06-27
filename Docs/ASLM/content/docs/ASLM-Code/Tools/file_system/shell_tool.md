---
title: "shell_tool"
draft: false
---

## Module `shell_tool`

`Tools/file_system/shell_tool.py` — ASLM Code Python module.

---

## Overview

Part of `Tools\file_system`. See **Related** for package index and callers.

---

## Public functions

#### `def run_command(command, cwd=…, timeout_s=…) -> dict[str, Any]`

**Purpose:** Returns exit_code, stdout, stderr, elapsed_ms, and the resolved cwd.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.
3. Handle errors and map them to a safe response.
4. Spawn or communicate with a child process.

---

## Private functions

#### `def _resolve_shell() -> tuple[list[str], str]`

**Purpose:** POSIX prefers bash, then falls back to sh.

**Steps:**

1. Return the computed result to the caller.

#### `def _build_argv(command) -> tuple[list[str], str]`

**Purpose:** PowerShell appends the user command after its UTF-8 bootstrap in the same -Command string.

**Steps:**

1. Return the computed result to the caller.

#### `def _truncate(text) -> tuple[str, bool]`

**Purpose:** Trim one output stream to the byte cap, returning the text and a truncated flag.

**Steps:**

1. Return the computed result to the caller.

---

## Related

- [file_system/_index](../_index/)
