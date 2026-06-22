---
title: "ASLM-Code"
draft: false
icon: "developer_board"
weight: 101
---

Python and JavaScript sources for the **ASLM Code** module (`aslm-code`).

| Section | Doc |
| --- | --- |
| [main](main/) | Host CLI entry (`runserver`, `first_run`, settings bridge, server venv re-exec) |
| [manage](manage/) | Django `manage.py` shim |
| [API](API/) | MCP tool registry exposed to the UI |
| [ASLM](ASLM/) | Django project package (`settings`, `urls`, ASGI/WSGI) |
| [Apps](Apps/) | Django apps and client static assets |
| [Runtime](Runtime/) | Run manager, execution backends, and engine executors |
| [Services](Services/) | ASLM-Chat interop, venvs, MCP workers, host bridges |
| [Settings](Settings/) | `settings.json`, first run, MCP, skills, host snapshots |
| [Tools](Tools/) | File-system tool server and runtime metadata helpers |

---

## Architecture overview

ASLM Code runs as a Django app inside the ASLM host. The host launches `main.py`, which re-execs into the server venv and starts `runserver`. The browser loads `Apps/UI` templates and `static/js` modules. Coding turns flow through `Apps/UI/views.py`, which persists messages in `Apps/Data`, composes prompts (skills, uploads, workspace context), and dispatches a run through [Runtime](Runtime/). The run manager selects an executor — primarily [`aslm_chat_executor`](Runtime/executors/aslm_chat_executor/), which streams generation from the sibling **ASLM-Chat** module via [Services](Services/) (`aslm_chat_client`, `aslm_chat_resolver`, `aslm_chat_stream`). Tool calls go through [`API/mcp`](API/mcp/) and the file-system tools under [`Tools/file_system`](Tools/file_system/), executed by `Services/tool_worker.py` or external user MCP servers.

---

## Documentation conventions

Documentation paths **mirror** the repository tree: `path/to/module.py` → `Docs/.../ASLM-Code/path/to/module.md` (or `file.js` → `file.md`).

| Artifact | Rule |
| --- | --- |
| Package directory | `_index.md` with **Module map** so Hugo keeps full menu depth |
| `tests/test_*.py` | `tests/test_foo.md` with **## Test methods** |
| Single `tests.py` | `tests.md` with **## Test methods** and `####` per test |
| `__init__.py` | Not documented — no `__init__.md` |
| Migrations | Not documented |

Reference pages follow the same outline as [ASLM C# documentation](https://github.com/nickel-grove/ASLM) (`Docs/ASLM` in the ASLM repo):

| Level | Use for |
| --- | --- |
| `## Module \`name\`` / `## File \`name.js\`` | Leaf page title |
| `## Overview` | Pipeline or role for large modules |
| `## Classes` | Types; `### \`class Name\`` for summary |
| `## Public functions` / `## Private functions` | Grouped members |
| `#### \`signature\`` | One block per function with **Purpose:** and **Steps:** when non-trivial |
| `## Test methods` | Test modules (`test_*.py`) |
| `## Related` | Parent `_index` first |

**Markdown:** use normal Hugo markdown — no blank lines between rows of one table or items in one list; blank lines only between sections or adjacent `####` blocks.

Do **not** use `## \`function_name\`` in the sidebar (use `####` under Public/Private only).

---

## Related

- [Documentation home](../)
