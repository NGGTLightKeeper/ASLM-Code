# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

from typing import Any, Callable

from Tools.file_system import fs_tools, shell_tool
from Tools.file_system.responses import error_response, exception_response

# Tool definitions in a neutral schema (id/name/description/parameters).
# parameters follow JSON Schema, ready to project into any provider format.
TOOLS: list[dict[str, Any]] = [
    {
        "id": "read_file",
        "name": "Read File",
        "description": (
            "Read a UTF-8 text file from the workspace. "
            "Pass start_line/end_line (1-based, inclusive) to read only a slice. "
            "Returns content, total_lines, and size_bytes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "start_line": {"type": "integer"},
                "end_line": {"type": "integer"},
            },
            "required": ["path"],
        },
    },
    {
        "id": "write_file",
        "name": "Write File",
        "description": (
            "Create a new UTF-8 text file or fully overwrite an existing one. "
            "Use relative paths inside the workspace. "
            "Use edit_file for small surgical changes instead of rewriting."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "id": "edit_file",
        "name": "Edit File",
        "description": (
            "Replace an exact substring old_str with new_str in a file. "
            "Fails if old_str is missing or matches multiple times unless replace_all=true."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_str": {"type": "string"},
                "new_str": {"type": "string"},
                "replace_all": {"type": "boolean", "default": False},
            },
            "required": ["path", "old_str", "new_str"],
        },
    },
    {
        "id": "list_dir",
        "name": "List Directory",
        "description": (
            "List files and directories under a workspace path. "
            "Pass recursive=true to walk the whole subtree."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "."},
                "recursive": {"type": "boolean", "default": False},
            },
            "required": [],
        },
    },
    {
        "id": "run_command",
        "name": "Run Command",
        "description": (
            "Run a shell command inside the workspace and capture its output. "
            "Best for builds, tests, git, installs, and inspection. "
            "Returns exit_code, stdout, stderr, and elapsed_ms. "
            "Raise timeout_s for long-running commands."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "cwd": {"type": "string", "default": "."},
                "timeout_s": {"type": "integer", "default": 60},
            },
            "required": ["command"],
        },
    },
]


# Dispatch table mapping each tool id to its implementing callable.
_HANDLERS: dict[str, Callable[..., dict[str, Any]]] = {
    "read_file": fs_tools.read_file,
    "write_file": fs_tools.write_file,
    "edit_file": fs_tools.edit_file,
    "list_dir": fs_tools.list_dir,
    "run_command": shell_tool.run_command,
}


# Execute one tool by id with keyword arguments, wrapping every failure.
def handle_tool(tool_id: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    handler = _HANDLERS.get(tool_id)
    if handler is None:
        return error_response(tool_id, "unknown_tool", f"Unknown tool: {tool_id}")
    try:
        return handler(**(arguments or {}))
    except TypeError as exc:
        return error_response(tool_id, "invalid_arguments", str(exc))
    except Exception as exc:
        return exception_response(tool_id, exc)


# Return the tool catalog projected into the OpenAI "tools" wire format.
def openai_tool_schemas() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": tool["id"],
                "description": tool["description"],
                "parameters": tool["parameters"],
            },
        }
        for tool in TOOLS
    ]
