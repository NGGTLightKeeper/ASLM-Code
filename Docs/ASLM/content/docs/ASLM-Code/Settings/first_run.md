---
title: "first_run"
draft: false
---

## Module `first_run`

`Settings/first_run.py` — ASLM Code Python module.

---

## Overview

Part of `Settings`. See **Related** for package index and callers.

---

## Public functions

#### `def run(log=…, ui_port=…, api_port=…) -> None`

**Purpose:** Run the first-run setup workflow.

**Steps:**

1. Execute the implementation in the source module.

---

## Private functions

#### `def _build_initial_settings(existing, ui_port, api_port) -> dict[str, Any]`

**Purpose:** Build the initial settings payload for the first run.

**Steps:**

1. Return the computed result to the caller.

#### `def _print_warning(message) -> None`

**Purpose:** Print a standardized bootstrap warning.

#### `def _run_tool_bootstrap(log) -> None`

**Purpose:** Run post-dependency bootstrap tasks for bundled tools.

**Steps:**

1. Execute the implementation in the source module.

#### `def _print_summary(settings_file, initial) -> None`

**Purpose:** Print a short summary of the written first-run settings.

**Steps:**

1. Execute the implementation in the source module.

---

## Related

- [Settings/_index](../_index/)
