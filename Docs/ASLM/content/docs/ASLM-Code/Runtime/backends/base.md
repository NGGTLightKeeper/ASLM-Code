---
title: "base"
draft: false
---

## Module `base`

`Runtime/backends/base.py` — ASLM Code Python module.

---

## Overview

Part of `Runtime\backends`. See **Related** for package index and callers.

---

## Classes

### `class RunBackend`

**Purpose:** Type `RunBackend` defined in `base.py`.

---

## Public functions

#### `def RunBackend.spawn(run_id, spec) -> None`

**Purpose:** Start executing one run; must return immediately without blocking.

#### `def RunBackend.abort(run_id) -> bool`

**Purpose:** Request cooperative cancellation of one run.

---

## Related

- [backends/_index](../_index/)
