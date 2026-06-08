# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import tempfile
from pathlib import Path

from Apps.Data.models import Chat, Workspace

_test_workspace_counter = 0


# Create one workspace row for tests.
def create_test_workspace(*, name: str = "Test Workspace", path: str | None = None) -> Workspace:
    global _test_workspace_counter
    _test_workspace_counter += 1
    workspace_path = path or str(Path(tempfile.gettempdir()) / f"aslm-test-workspace-{_test_workspace_counter}")
    Path(workspace_path).mkdir(parents=True, exist_ok=True)
    return Workspace.objects.create(name=name, path=workspace_path)


# Create one chat row bound to a workspace for tests.
def create_test_chat(*, workspace: Workspace | None = None, **kwargs) -> Chat:
    bound_workspace = workspace or create_test_workspace()
    return Chat.objects.create(workspace=bound_workspace, **kwargs)
