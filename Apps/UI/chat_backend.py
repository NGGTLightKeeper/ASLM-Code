# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

from pathlib import Path
from typing import Any

from django.conf import settings as django_settings

from API import mcp as local_tool_registry
from Services import aslm_chat_client

OLLAMA_UNSUPPORTED_OPTION_KEYS = {
    "template",
    "system",
    "license",
    "from",
    "parameter",
    "message",
    "adapter",
}


# Return whether one Ollama Modelfile option can be forwarded as runtime options.
def is_supported_runtime_option_key(option_name: Any) -> bool:
    normalized = str(option_name or "").strip()
    return bool(normalized) and normalized not in OLLAMA_UNSUPPORTED_OPTION_KEYS


# Return tool ids that exist in the local Code registry.
def list_local_tool_server_ids(
    engine: str,
    model_name: str | None,
    tool_server_ids: list[str],
) -> list[str]:
    local_ids: list[str] = []
    for raw_id in tool_server_ids:
        normalized = str(raw_id or "").strip()
        if not normalized:
            continue
        server = local_tool_registry.get_server(normalized, engine=engine, model_name=model_name)
        if server is not None:
            local_ids.append(normalized)
    return local_ids


# Split one tool selection into local Code tools and Chat-hosted tools.
def partition_tool_server_ids(
    engine: str,
    model_name: str | None,
    tool_server_ids: list[str],
) -> tuple[list[str], list[str]]:
    local_ids = list_local_tool_server_ids(engine, model_name, tool_server_ids)
    local_set = set(local_ids)
    chat_ids = [tool_id for tool_id in tool_server_ids if tool_id not in local_set]
    return local_ids, chat_ids


# Resolve selected local tool servers for validation and UI metadata.
def resolve_local_tool_servers(
    engine: str,
    model_name: str,
    tool_server_ids: list[str],
) -> list[dict[str, Any]]:
    resolved: list[dict[str, Any]] = []
    for raw_id in tool_server_ids:
        normalized = str(raw_id or "").strip()
        if not normalized:
            continue
        server = local_tool_registry.get_server(normalized, engine=engine, model_name=model_name)
        if server is None:
            raise ValueError(f"Unknown or unsupported local tool server: {normalized}")
        resolved.append(server)
    return resolved


# Convert internal LLM messages into ASLM-Chat /api/generate/ payload shape.
def _serialize_llm_messages_for_chat(llm_messages: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    if not llm_messages:
        return [], None

    history: list[dict[str, Any]] = []
    current_entry: dict[str, Any] | None = None

    for index, entry in enumerate(llm_messages):
        if not isinstance(entry, dict):
            continue
        role = str(entry.get("role") or "").strip().lower()
        if role == "system":
            continue
        serialized = dict(entry)
        if index == len(llm_messages) - 1 and role == "user":
            current_entry = serialized
        else:
            history.append(serialized)

    return history, current_entry


# Build the JSON payload for ASLM-Chat /api/generate/.
def build_chat_generate_payload(
    *,
    engine: str,
    model_name: str,
    llm_messages: list[dict[str, Any]],
    system_prompt: str,
    session_id: str,
    think_value: Any = None,
    think_level_value: Any = None,
    clean_options: dict[str, Any] | None = None,
    local_tool_server_ids: list[str] | None = None,
    chat_tool_server_ids: list[str] | None = None,
    uploaded_file_ids: list[str] | None = None,
    project_dir: str | Path | None = None,
) -> dict[str, Any]:
    history_messages, current_entry = _serialize_llm_messages_for_chat(llm_messages)
    payload: dict[str, Any] = {
        "engine": engine,
        "model": model_name,
        "session_id": session_id,
        "messages": history_messages,
        "stream": True,
        "consume_skill_notifications": False,
        "include_skills_baseline": False,
    }

    if system_prompt:
        payload["system_prompt"] = system_prompt
    if isinstance(clean_options, dict) and clean_options:
        payload["options"] = clean_options
    if think_value is not None:
        payload["think"] = think_value
    if think_level_value is not None:
        payload["think_level"] = think_level_value
    if uploaded_file_ids:
        payload["uploaded_file_ids"] = list(uploaded_file_ids)

    if isinstance(current_entry, dict):
        message_text = str(current_entry.get("content") or "").strip()
        if message_text:
            payload["message"] = message_text
        for key in ("attachments", "images", "uploaded_file_ids", "llm_transcript"):
            if key in current_entry and current_entry.get(key):
                payload[key] = current_entry[key]

    module_dir = str(django_settings.BASE_DIR)
    resolved_project_dir = str(project_dir or module_dir)
    tool_server_ids = list(local_tool_server_ids or []) + list(chat_tool_server_ids or [])
    if tool_server_ids:
        payload["tool_server_ids"] = tool_server_ids

    tool_sources: list[dict[str, Any]] = []
    if local_tool_server_ids:
        tool_sources.append(
            {
                "module_dir": module_dir,
                "tools_dir": str(Path(module_dir) / "Tools"),
                "tool_server_ids": list(local_tool_server_ids),
            }
        )
    if tool_sources:
        payload["tool_sources"] = tool_sources

    payload["tool_context"] = {
        "module_dir": module_dir,
        "project_dir": resolved_project_dir,
        "chat_id": str(session_id),
        "engine": engine,
        "model_name": model_name,
        "selected_tool_server_ids": tool_server_ids,
    }
    return payload


# Proxy model metadata from ASLM-Chat.
def fetch_model_info(engine: str, model_name: str) -> dict[str, Any]:
    return aslm_chat_client.get_model_info(engine, model_name)


# Proxy model settings used by legacy metadata extractors.
def fetch_model_settings(engine: str, model_name: str) -> dict[str, Any]:
    payload = fetch_model_info(engine, model_name)
    settings_data = payload.get("settings") or payload.get("model_settings") or payload
    return settings_data if isinstance(settings_data, dict) else payload
