---
title: "registry"
draft: false
---

## Module `registry`

`Tools/file_system/registry.py` — ASLM Code Python module.

---

## Overview

Part of `Tools\file_system`. See **Related** for package index and callers.

---

## Public functions

#### `def handle_tool(tool_id, arguments=…) -> dict[str, Any]`

**Purpose:** Execute one tool by id with keyword arguments, wrapping every failure.

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.

#### `def openai_tool_schemas() -> list[dict[str, Any]]`

**Purpose:** Return the tool catalog projected into the OpenAI "tools" wire format.

---

## Related

- [file_system/_index](../_index/)
