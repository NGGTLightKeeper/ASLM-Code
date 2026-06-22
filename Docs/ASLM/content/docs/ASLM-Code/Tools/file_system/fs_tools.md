---
title: "fs_tools"
draft: false
---

## Module `fs_tools`

`Tools/file_system/fs_tools.py` — ASLM Code Python module.

---

## Overview

Part of `Tools\file_system`. See **Related** for package index and callers.

---

## Public functions

#### `def read_file(path, start_line=…, end_line=…) -> dict[str, Any]`

**Purpose:** Read a UTF-8 text file from the workspace, optionally a 1-based line slice.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.

#### `def write_file(path, content) -> dict[str, Any]`

**Purpose:** Create a new UTF-8 text file or fully overwrite an existing one.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.

#### `def edit_file(path, old_str, new_str, replace_all=…) -> dict[str, Any]`

**Purpose:** Replace an exact substring in a file; fail on missing or ambiguous matches.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.

#### `def list_dir(path=…, recursive=…) -> dict[str, Any]`

**Purpose:** List entries under a workspace directory, optionally walking recursively.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.
3. Iterate and transform or accumulate state.

---

## Related

- [file_system/_index](../_index/)
