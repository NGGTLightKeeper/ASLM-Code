---
title: "main"
draft: false
---

## Module `main`

`main.py` — ASLM Code Python module.

---

## Overview

Top-level module of the ASLM-Code repository. See **Related** for package index and callers.

---

## Classes

### `class LazyDjangoApplication`

**Purpose:** Bind the UI port first, then hand requests to Django once it is ready.

---

## Public functions

#### `def run_django_command(*args, log=…) -> None`

**Purpose:** Execute a Django management command.

**Steps:**

1. Execute the implementation in the source module.

#### `def LazyDjangoApplication.__init__() -> None`

**Purpose:** Implements `LazyDjangoApplication.__init__` in `main.py`.

**Steps:**

1. Execute the implementation in the source module.

#### `def LazyDjangoApplication.load_in_background() -> None`

**Purpose:** Start loading Django without blocking the listening socket.

**Steps:**

1. Execute the implementation in the source module.

#### `def LazyDjangoApplication.__call__(environ, start_response)`

**Purpose:** Implements `LazyDjangoApplication.__call__` in `main.py`.

**Steps:**

1. Return the computed result to the caller.

#### `def cmd_runserver(port, log) -> None`

**Purpose:** Start the Django development server on the requested port.

**Steps:**

1. Return the computed result to the caller.

#### `def cmd_migrate(log) -> None`

**Purpose:** Apply all pending database migrations.

**Steps:**

1. Execute the implementation in the source module.

#### `def cmd_makemigrations(app, log) -> None`

**Purpose:** Create migration files for changed models.

**Steps:**

1. Execute the implementation in the source module.

#### `def cmd_collectstatic(log) -> None`

**Purpose:** Collect static files into ``STATIC_ROOT``.

#### `def cmd_first_run(log=…, ui_port=…, api_port=…) -> None`

**Purpose:** Generate settings and apply initial migrations.

**Steps:**

1. Execute the implementation in the source module.

#### `def cmd_get_setting(key) -> None`

**Purpose:** Print a single setting value for ASLM integration hooks.

**Steps:**

1. Execute the implementation in the source module.

#### `def cmd_set_setting(key, value) -> None`

**Purpose:** Update a single setting key from string input.

**Steps:**

1. Execute the implementation in the source module.

#### `def cmd_apply_aslm_host_theme(theme_file) -> None`

**Purpose:** Apply a JSON theme snapshot written by ASLM (temp file path in ``--file``).

**Steps:**

1. Handle errors and map them to a safe response.
2. Parse or serialize JSON payloads.

#### `def cmd_apply_aslm_locale(locale_file) -> None`

**Purpose:** Apply a JSON locale snapshot written by ASLM (temp file path in ``--file``).

**Steps:**

1. Handle errors and map them to a safe response.
2. Parse or serialize JSON payloads.

#### `def main() -> None`

**Purpose:** Parse CLI arguments and dispatch the requested command.

**Steps:**

1. Execute the implementation in the source module.

---

## Private functions

#### `def _maybe_reexec_in_server_venv(command) -> None`

**Purpose:** Delegate the current command to ASLM-Code's server venv when required.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Handle errors and map them to a safe response.
3. Spawn or communicate with a child process.

#### `def LazyDjangoApplication._load() -> None`

**Purpose:** Implements `LazyDjangoApplication._load` in `main.py`.

#### `def _build_parser() -> argparse.ArgumentParser`

**Purpose:** Return the command-line parser for the project entry point.

**Steps:**

1. Return the computed result to the caller.

#### `def _maybe_print_banner(command) -> None`

**Purpose:** Print technical module data once for interactive commands.

#### `def _resolve_runserver_port(requested_port) -> int`

**Purpose:** Return the effective UI port for ``runserver``.

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.

---

## Related

- [ASLM-Code/_index](../_index/)
