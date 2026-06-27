---
title: "chat_backend"
draft: false
---

## Module `chat_backend`

`Apps/UI/chat_backend.py` — ASLM Code Python module.

---

## Overview

Part of `Apps\UI`. See **Related** for package index and callers.

---

## Public functions

#### `def is_supported_runtime_option_key(option_name) -> bool`

**Purpose:** Return whether one Ollama Modelfile option can be forwarded as runtime options.

**Steps:**

1. Return the computed result to the caller.

#### `def list_local_tool_server_ids(engine, model_name, tool_server_ids) -> list[str]`

**Purpose:** Return tool ids that exist in the local Code registry.

**Steps:**

1. Return the computed result to the caller.
2. Iterate and transform or accumulate state.

#### `def partition_tool_server_ids(engine, model_name, tool_server_ids) -> tuple[list[str], list[str]]`

**Purpose:** Split one tool selection into local Code tools and Chat-hosted tools.

**Steps:**

1. Return the computed result to the caller.

#### `def resolve_local_tool_servers(engine, model_name, tool_server_ids) -> list[dict[str, Any]]`

**Purpose:** Resolve selected local tool servers for validation and UI metadata.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.
3. Iterate and transform or accumulate state.

#### `def build_chat_generate_payload(*, engine, model_name, llm_messages, system_prompt, session_id, think_value=…, think_level_value=…, clean_options=…, local_tool_server_ids=…, chat_tool_server_ids=…, uploaded_file_ids=…, project_dir=…) -> dict[str, Any]`

**Purpose:** Build the JSON payload for ASLM-Chat /api/generate/.

**Steps:**

1. Return the computed result to the caller.
2. Iterate and transform or accumulate state.

#### `def fetch_model_info(engine, model_name) -> dict[str, Any]`

**Purpose:** Proxy model metadata from ASLM-Chat.

#### `def fetch_model_settings(engine, model_name) -> dict[str, Any]`

**Purpose:** Proxy model settings used by legacy metadata extractors.

**Steps:**

1. Return the computed result to the caller.

---

## Private functions

#### `def _serialize_llm_messages_for_chat(llm_messages) -> tuple[list[dict[str, Any]], dict[str, Any] | None]`

**Purpose:** Convert internal LLM messages into ASLM-Chat /api/generate/ payload shape.

**Steps:**

1. Return the computed result to the caller.
2. Iterate and transform or accumulate state.

---

## Related

- [UI/_index](../_index/)
