---
title: "workspace_paths"
draft: false
---

## Module `workspace_paths`

`Tools/file_system/workspace_paths.py` — ASLM Code Python module.

---

## Overview

Part of `Tools\file_system`. See **Related** for package index and callers.

---

## Public functions

#### `def workspace_root() -> Path`

**Purpose:** Defaults to a dedicated Workspace/ directory unless overridden by env.

**Steps:**

1. Return the computed result to the caller.

#### `def resolve_in_workspace(path) -> Path`

**Purpose:** Accepts plain relative paths; absolute paths must stay within the workspace.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.

#### `def to_relative(path) -> str`

**Purpose:** Return one absolute workspace path as a clean root-relative POSIX string.

---

## Related

- [file_system/_index](../_index/)
