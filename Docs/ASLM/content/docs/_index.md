---
title: "ASLM Code documentation"
draft: false
---

**ASLM Code** (`aslm-code`) is an official **ASLM host module** for local coding assistance: a Django web UI, SQLite data layer, a run/execution runtime, file-system tools, and MCP integration. It does **not** run model inference itself — it delegates LLM generation to the **ASLM-Chat** module over the ASLM module-interop protocol. The host loads the module from `ASLM_Module.json` and runs [`main`](../ASLM-Code/main/) inside the ASLM desktop shell.

This site documents the **ASLM-Code repository** (Python and client-side JavaScript) and **patch notes**.

---

## Terminology

| Name | Meaning |
| --- | --- |
| **ASLM** (host) | The Windows desktop host in the main ASLM repository |
| **ASLM Code** (module) | This coding-assistant module (`aslm-code`) |
| **ASLM Chat** (module) | The sibling chat module (`aslm-chat`) that ASLM-Code delegates inference to |
| **`ASLM/` package** | Django project package in this repo — not the MAUI host application |
