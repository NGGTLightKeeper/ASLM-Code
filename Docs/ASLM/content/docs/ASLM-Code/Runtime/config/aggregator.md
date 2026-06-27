---
title: "aggregator"
draft: false
---

## Module `aggregator`

`Runtime/config/aggregator.py` — ASLM Code Python module.

---

## Overview

Part of `Runtime\config`. See **Related** for package index and callers.

---

## Classes

### `class ConfigAggregator`

**Purpose:** Type `ConfigAggregator` defined in `aggregator.py`.

---

## Public functions

#### `def ConfigAggregator.__init__(settings_source=…, metadata_source=…, core_source=…) -> None`

**Purpose:** Compose the aggregator from its backing sources.

**Steps:**

1. Execute the implementation in the source module.

#### `def ConfigAggregator.active_engine() -> str`

**Purpose:** Return the effective backend engine the user is currently driving.

#### `def ConfigAggregator.active_model(engine=…) -> str`

**Purpose:** Return the active model for one engine, defaulting to the current engine.

**Steps:**

1. Return the computed result to the caller.

#### `def ConfigAggregator.available_engines() -> list[str]`

**Purpose:** Return the list of engine ids the user has enabled.

#### `def ConfigAggregator.model_caps(engine, model) -> dict[str, Any]`

**Purpose:** Return the capability flags for one engine/model pair.

#### `def ConfigAggregator.model_limits(engine, model) -> dict[str, Any]`

**Purpose:** Return the limit values for one engine/model pair.

#### `def ConfigAggregator.resolve(overrides=…) -> ResolvedConfig`

**Purpose:** Freeze defaults and overrides into one validated run configuration.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.

#### `def main() -> None`

**Purpose:** Print a resolved snapshot of the current active configuration for smoke testing.

**Steps:**

1. Handle errors and map them to a safe response.
2. Parse or serialize JSON payloads.

---

## Private functions

#### `def ConfigAggregator._limits_summary(engine, model) -> LimitsSummary`

**Purpose:** Build the frozen model-capability summary for one engine/model pair.

**Steps:**

1. Return the computed result to the caller.

#### `def ConfigAggregator._engine_config(engine, sub_engine) -> EngineConfig`

**Purpose:** Build the frozen engine coordinates for one engine.

#### `def ConfigAggregator._run_limits(overrides) -> RunLimits`

**Purpose:** Merge built-in limits with the core source and per-run overrides.

**Steps:**

1. Return the computed result to the caller.

---

## Related

- [config/_index](../_index/)
