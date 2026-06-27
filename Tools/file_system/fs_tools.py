# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

from typing import Any

from Tools.file_system.responses import ToolError, success_response
from Tools.file_system.workspace_paths import resolve_in_workspace, to_relative, workspace_root

# Cap on how many bytes one read_file call returns before truncating.
_MAX_READ_BYTES = 256 * 1024

# Cap on how many directory entries one list_dir call returns.
_MAX_LIST_ENTRIES = 1000


# Read a UTF-8 text file from the workspace, optionally a 1-based line slice.
def read_file(path: str, start_line: int | None = None, end_line: int | None = None) -> dict[str, Any]:
    target = resolve_in_workspace(path)
    if not target.exists():
        raise ToolError("not_found", f"File '{path}' does not exist.")
    if target.is_dir():
        raise ToolError("is_a_directory", f"Path '{path}' is a directory, not a file.")

    raw = target.read_bytes()
    truncated = len(raw) > _MAX_READ_BYTES
    text = raw[:_MAX_READ_BYTES].decode("utf-8", errors="replace")

    lines = text.split("\n")
    total_lines = len(lines)

    # Apply an optional 1-based inclusive line window over the decoded text.
    if start_line is not None or end_line is not None:
        lo = max(1, int(start_line or 1))
        hi = min(total_lines, int(end_line or total_lines))
        if lo > hi:
            raise ToolError("invalid_arguments", f"Invalid line range {lo}:{hi}.")
        text = "\n".join(lines[lo - 1:hi])
    else:
        lo = 1
        hi = total_lines

    return success_response(
        "read_file",
        {
            "path": to_relative(target),
            "content": text,
            "start_line": lo,
            "end_line": hi,
            "total_lines": total_lines,
            "size_bytes": len(raw),
        },
        warnings=["File truncated at read limit."] if truncated else None,
        truncated=truncated,
    )


# Create a new UTF-8 text file or fully overwrite an existing one.
def write_file(path: str, content: str) -> dict[str, Any]:
    target = resolve_in_workspace(path)
    if target.is_dir():
        raise ToolError("is_a_directory", f"Path '{path}' is a directory.")

    existed = target.exists()
    target.parent.mkdir(parents=True, exist_ok=True)
    data = str(content or "")
    target.write_text(data, encoding="utf-8", newline="")

    return success_response(
        "write_file",
        {
            "path": to_relative(target),
            "created": not existed,
            "size_bytes": len(data.encode("utf-8")),
            "lines": data.count("\n") + 1 if data else 0,
        },
    )


# Replace an exact substring in a file; fail on missing or ambiguous matches.
def edit_file(path: str, old_str: str, new_str: str, replace_all: bool = False) -> dict[str, Any]:
    target = resolve_in_workspace(path)
    if not target.exists():
        raise ToolError("not_found", f"File '{path}' does not exist.")
    if target.is_dir():
        raise ToolError("is_a_directory", f"Path '{path}' is a directory.")

    text = target.read_text(encoding="utf-8", errors="replace")
    old = str(old_str or "")
    if not old:
        raise ToolError("invalid_arguments", "old_str must be non-empty.")

    count = text.count(old)
    if count == 0:
        raise ToolError("no_match", f"old_str was not found in '{path}'.")
    if count > 1 and not replace_all:
        raise ToolError(
            "ambiguous_match",
            f"old_str matches {count} locations in '{path}'; pass replace_all=true or add more context.",
        )

    updated = text.replace(old, str(new_str or "")) if replace_all else text.replace(old, str(new_str or ""), 1)
    target.write_text(updated, encoding="utf-8", newline="")

    return success_response(
        "edit_file",
        {
            "path": to_relative(target),
            "replacements": count if replace_all else 1,
            "size_bytes": len(updated.encode("utf-8")),
        },
    )


# List entries under a workspace directory, optionally walking recursively.
def list_dir(path: str = ".", recursive: bool = False) -> dict[str, Any]:
    target = resolve_in_workspace(path) if path not in {"", "."} else workspace_root()
    if not target.exists():
        raise ToolError("not_found", f"Directory '{path}' does not exist.")
    if not target.is_dir():
        raise ToolError("not_a_directory", f"Path '{path}' is not a directory.")

    entries: list[dict[str, Any]] = []
    truncated = False

    # Walk either one level or the whole subtree, capped at the entry limit.
    iterator = target.rglob("*") if recursive else target.iterdir()
    for item in sorted(iterator, key=lambda p: p.as_posix()):
        if len(entries) >= _MAX_LIST_ENTRIES:
            truncated = True
            break
        entries.append(
            {
                "path": to_relative(item),
                "type": "dir" if item.is_dir() else "file",
                "size_bytes": item.stat().st_size if item.is_file() else None,
            }
        )

    return success_response(
        "list_dir",
        {"path": to_relative(target), "entries": entries, "count": len(entries)},
        warnings=["Directory listing truncated."] if truncated else None,
        truncated=truncated,
    )
