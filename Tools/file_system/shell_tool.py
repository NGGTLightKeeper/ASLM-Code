# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import os
import shutil
import subprocess
import time
from typing import Any

from Tools.file_system.responses import ToolError, error_response, success_response
from Tools.file_system.workspace_paths import resolve_in_workspace, to_relative, workspace_root

# Default and maximum command timeouts in seconds.
_DEFAULT_TIMEOUT_S = 60
_MAX_TIMEOUT_S = 600

# Cap on captured stdout/stderr size before an inline truncation marker is added.
_MAX_OUTPUT_BYTES = 64 * 1024

# Cached resolved shell so the system probe runs only once per process.
_SHELL_CACHE: tuple[list[str], str] | None = None


# Probe the host system and pick the native interactive shell.
# Windows prefers PowerShell 7 (pwsh), then Windows PowerShell, never cmd.exe;
# POSIX prefers bash, then falls back to sh.
def _resolve_shell() -> tuple[list[str], str]:
    global _SHELL_CACHE
    if _SHELL_CACHE is not None:
        return _SHELL_CACHE

    if os.name == "nt":
        pwsh = shutil.which("pwsh")
        if pwsh:
            # Force UTF-8 on the output pipe so captured text decodes cleanly.
            prefix = [pwsh, "-NoProfile", "-NonInteractive", "-Command",
                      "$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();"]
            resolved = (prefix, "pwsh")
        else:
            powershell = shutil.which("powershell") or "powershell"
            prefix = [powershell, "-NoProfile", "-NonInteractive", "-Command",
                      "[Console]::OutputEncoding=[Text.UTF8Encoding]::new();"]
            resolved = (prefix, "powershell")
    else:
        bash = shutil.which("bash")
        if bash:
            resolved = ([bash, "-c"], "bash")
        else:
            resolved = ([shutil.which("sh") or "/bin/sh", "-c"], "sh")

    _SHELL_CACHE = resolved
    return resolved


# Build the full argv for one command under the resolved shell.
# PowerShell appends the user command after its UTF-8 bootstrap in the same -Command string.
def _build_argv(command: str) -> tuple[list[str], str]:
    prefix, label = _resolve_shell()
    if label in {"pwsh", "powershell"}:
        argv = prefix[:-1] + [prefix[-1] + " " + command]
    else:
        argv = prefix + [command]
    return argv, label


# Trim one output stream to the byte cap, returning the text and a truncated flag.
def _truncate(text: str) -> tuple[str, bool]:
    encoded = text.encode("utf-8", errors="replace")
    if len(encoded) <= _MAX_OUTPUT_BYTES:
        return text, False
    clipped = encoded[:_MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")
    return clipped + "\n...[output truncated]...", True


# Run one shell command inside the workspace and capture its result.
# Returns exit_code, stdout, stderr, elapsed_ms, and the resolved cwd.
def run_command(command: str, cwd: str = ".", timeout_s: int = _DEFAULT_TIMEOUT_S) -> dict[str, Any]:
    command = str(command or "").strip()
    if not command:
        raise ToolError("invalid_arguments", "A non-empty command is required.")

    work_dir = workspace_root() if cwd in {"", "."} else resolve_in_workspace(cwd)
    if not work_dir.is_dir():
        raise ToolError("not_a_directory", f"cwd '{cwd}' is not a directory.")

    timeout = max(1, min(int(timeout_s or _DEFAULT_TIMEOUT_S), _MAX_TIMEOUT_S))
    argv, shell_label = _build_argv(command)
    started = time.monotonic()

    try:
        completed = subprocess.run(
            argv,
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        return error_response(
            "run_command",
            "timeout",
            f"Command timed out after {timeout}s.",
            result={"command": command, "cwd": to_relative(work_dir), "shell": shell_label, "elapsed_ms": elapsed_ms},
        )

    elapsed_ms = int((time.monotonic() - started) * 1000)
    stdout, trunc_out = _truncate(completed.stdout or "")
    stderr, trunc_err = _truncate(completed.stderr or "")
    truncated = trunc_out or trunc_err

    result = {
        "command": command,
        "cwd": to_relative(work_dir),
        "shell": shell_label,
        "exit_code": completed.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "elapsed_ms": elapsed_ms,
    }

    warnings = ["Command output was truncated."] if truncated else None
    if completed.returncode == 0:
        return success_response("run_command", result, warnings=warnings, truncated=truncated)

    return error_response(
        "run_command",
        "process_error",
        f"Command exited with code {completed.returncode}.",
        result=result,
        warnings=warnings,
    )
