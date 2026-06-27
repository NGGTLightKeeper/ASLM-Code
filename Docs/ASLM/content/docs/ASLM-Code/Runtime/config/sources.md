---
title: "sources"
draft: false
---

## Module `sources`

`Runtime/config/sources.py` — ASLM Code Python module.

---

## Overview

Part of `Runtime\config`. See **Related** for package index and callers.

---

## Classes

### `class SettingsSource`

**Purpose:** Type `SettingsSource` defined in `sources.py`.

### `class ModelMetadataSource`

**Purpose:** Type `ModelMetadataSource` defined in `sources.py`.

### `class RuntimeCoreSource`

**Purpose:** Type `RuntimeCoreSource` defined in `sources.py`.

---

## Public functions

#### `def SettingsSource.active_engine() -> str`

**Purpose:** Return the effective backend engine the user is currently driving.

#### `def SettingsSource.facade_engine() -> str`

**Purpose:** Return the configured facade engine name.

#### `def SettingsSource.sub_engine() -> str`

**Purpose:** Return the backend sub-engine resolved behind the facade.

#### `def SettingsSource.engine_url(engine) -> str`

**Purpose:** Return the resolved base URL for one engine.

#### `def SettingsSource.engine_api_key(engine) -> str`

**Purpose:** Return the resolved API key for one engine.

#### `def SettingsSource.runtime_engine_settings() -> dict[str, Any]`

**Purpose:** Return per-engine runtime settings shared with the frontend.

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.

#### `def SettingsSource.enabled_engines() -> list[str]`

**Purpose:** Return the list of engine ids the user has enabled.

#### `def ModelMetadataSource.__init__(path=…) -> None`

**Purpose:** Bind the source to the metadata file and prepare its mtime cache.

**Steps:**

1. Execute the implementation in the source module.

#### `def ModelMetadataSource.active() -> dict[str, str]`

**Purpose:** Return the recorded active engine and model selection.

**Steps:**

1. Return the computed result to the caller.

#### `def ModelMetadataSource.model_entry(engine, model) -> dict[str, Any]`

**Purpose:** Return the raw catalog entry for one engine/model pair.

**Steps:**

1. Return the computed result to the caller.

#### `def ModelMetadataSource.capabilities(engine, model) -> dict[str, Any]`

**Purpose:** Return the capability flags recorded for one engine/model pair.

**Steps:**

1. Return the computed result to the caller.

#### `def ModelMetadataSource.limits(engine, model) -> dict[str, Any]`

**Purpose:** Return the limit values recorded for one engine/model pair.

**Steps:**

1. Return the computed result to the caller.

#### `def RuntimeCoreSource.__init__(path=…) -> None`

**Purpose:** Bind the source to the optional override file.

#### `def RuntimeCoreSource.values() -> dict[str, Any]`

**Purpose:** Return the merged core settings (defaults overlaid with the override file).

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.
3. Parse or serialize JSON payloads.

#### `def RuntimeCoreSource.get(key, default=…) -> Any`

**Purpose:** Return one core setting value with a fallback default.

---

## Private functions

#### `def ModelMetadataSource._load() -> dict[str, Any]`

**Purpose:** Return the parsed metadata document, refreshing only when the file changes.

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.
3. Parse or serialize JSON payloads.

#### `def ModelMetadataSource._model_key(engine, model) -> str`

**Purpose:** Build the catalog key used to look up one engine/model pair.

---

## Related

- [config/_index](../_index/)
