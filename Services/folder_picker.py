# Copyright NGGT.LightKeeper. All Rights Reserved.

"""Native folder picker invoked from the Django backend."""

from __future__ import annotations

from pathlib import Path


class FolderPickerUnavailable(Exception):
    """Raised when the native folder picker cannot be opened."""


# Show a native folder picker and return the selected absolute path.
def pick_folder(
    *,
    title: str = "Select workspace folder",
    initial_dir: str | None = None,
) -> str | None:
    """Return an absolute directory path, or None when the user cancels."""

    try:
        import crossfiledialog
    except ImportError as exc:
        raise FolderPickerUnavailable(
            "crossfiledialog is not installed in the server venv."
        ) from exc

    kwargs: dict[str, str] = {"title": title}
    if initial_dir:
        kwargs["start_dir"] = initial_dir

    try:
        selected = crossfiledialog.choose_folder(**kwargs)
    except Exception as exc:
        raise FolderPickerUnavailable(str(exc)) from exc

    cleaned = str(selected or "").strip()
    return cleaned or None


# Normalize a picked folder path for persistence.
def normalize_workspace_path(raw_path: str) -> str:
    path = Path(raw_path).expanduser()
    resolved = path.resolve()
    if not resolved.is_dir():
        raise ValueError("Selected path is not an existing directory.")
    return str(resolved)
