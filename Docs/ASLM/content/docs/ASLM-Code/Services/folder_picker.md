---
title: "folder_picker"
draft: false
---

## Module `folder_picker`

`Services/folder_picker.py` — Native folder picker invoked from the Django backend.

---

## Overview

Part of `Services`. See **Related** for package index and callers.

---

## Classes

### `class FolderPickerUnavailable`

**Purpose:** Raised when the native folder picker cannot be opened.

---

## Public functions

#### `def pick_folder(*, title=…, initial_dir=…) -> str | None`

**Purpose:** Return an absolute directory path, or None when the user cancels.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.
3. Handle errors and map them to a safe response.

#### `def normalize_workspace_path(raw_path) -> str`

**Purpose:** Normalize a picked folder path for persistence.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.

---

## Related

- [Services/_index](../_index/)
