# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import os
from pathlib import Path

from Tools.file_system.responses import ToolError

# Project root is three levels up from this file (Tools/file_system/<file>).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Environment override for the agent's sandboxed workspace root.
_WORKSPACE_ENV_KEY = "ASLM_CODE_WORKSPACE"


# Return the absolute workspace root the agent is allowed to touch.
# Defaults to a dedicated Workspace/ directory unless overridden by env.
def workspace_root() -> Path:
    raw = (os.environ.get(_WORKSPACE_ENV_KEY) or "").strip()
    root = Path(raw).expanduser() if raw else (_PROJECT_ROOT / "Workspace")
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


# Resolve one model-supplied path against the workspace and reject any escape.
# Accepts plain relative paths; absolute paths must stay within the workspace.
def resolve_in_workspace(path: str) -> Path:
    raw = str(path or "").strip()
    if not raw:
        raise ToolError("invalid_arguments", "A non-empty path is required.")

    root = workspace_root()
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = root / candidate

    # Resolve symlinks and '..' so the final location cannot leave the root.
    resolved = candidate.resolve()
    if resolved != root and root not in resolved.parents:
        raise ToolError(
            "path_escape",
            f"Path '{raw}' resolves outside the workspace root and is not allowed.",
        )
    return resolved


# Return one absolute workspace path as a clean root-relative POSIX string.
def to_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(workspace_root()).as_posix() or "."
    except ValueError:
        return path.as_posix()
