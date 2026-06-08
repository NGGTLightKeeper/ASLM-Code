# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import secrets
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = BASE_DIR / "Tools"


# Build the initial settings payload for the first run.
def _build_initial_settings(
    existing: dict[str, Any],
    ui_port: int,
    api_port: int,
) -> dict[str, Any]:
    initial: dict[str, Any] = dict(existing)
    initial.update(
        {
            "secret_key": existing.get("secret_key") or secrets.token_urlsafe(50),
            "ui-port": existing.get("ui-port", ui_port),
            "api-port": existing.get("api-port", api_port),
            "allowed_hosts": existing.get("allowed_hosts", ["127.0.0.1", "localhost"]),
            "debug": existing.get("debug", False),
            "llm-engine": existing.get("llm-engine", "aslm-chat"),
            "llm-sub-engine": existing.get("llm-sub-engine", "ollama-service"),
        }
    )
    return initial


# Print a standardized bootstrap warning.
def _print_warning(message: str) -> None:
    print(f"[ASLM-Code] Warning: {message}")


# Run post-dependency bootstrap tasks for bundled tools.
def _run_tool_bootstrap(log: bool) -> None:
    from Services import venv_manager

    if not venv_manager.ensure_all(log=log):
        _print_warning("One or more ASLM-Code venvs did not install successfully.")

    upload_root = BASE_DIR / "Data" / "uploads" / "User"
    upload_root.mkdir(parents=True, exist_ok=True)
    if log:
        print(f"[ASLM-Code] Ensured upload root: {upload_root}")


# Print a short summary of the written first-run settings.
def _print_summary(settings_file: Path, initial: dict[str, Any]) -> None:
    print(f"[ASLM-Code] Settings written to: {settings_file}")
    print(f"[ASLM-Code]   ui-port    : {initial['ui-port']}")
    print(f"[ASLM-Code]   api-port   : {initial['api-port']}")
    print(f"[ASLM-Code]   debug      : {initial['debug']}")
    print(f"[ASLM-Code]   llm-engine     : {initial['llm-engine']}")
    print(f"[ASLM-Code]   llm-sub-engine : {initial.get('llm-sub-engine', 'ollama-service')}")
    print("[ASLM-Code] First-run setup complete.")


# Run the first-run setup workflow.
def run(
    log: bool = False,
    ui_port: int = 20010,
    api_port: int = 20011,
) -> None:
    from Settings.settings import SETTINGS_FILE, load_settings, save_settings

    existing = load_settings()
    initial = _build_initial_settings(existing, ui_port, api_port)
    save_settings(initial)

    from Settings.mcp_json import ensure_default_mcp_json

    ensure_default_mcp_json()
    from Settings.skills import ensure_skills_dir

    ensure_skills_dir()

    _run_tool_bootstrap(log)

    if log:
        _print_summary(SETTINGS_FILE, initial)
