# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import logging
from typing import Callable

from Apps.UI.chat_backend import build_chat_generate_payload, partition_tool_server_ids
from Services import aslm_chat_client, aslm_chat_stream
from Runtime.types import RunSpec

logger = logging.getLogger(__name__)


# Real executor that streams one generation from ASLM-Chat into the event log.
# It reuses the existing clean generation plumbing (chat_backend + Services) and
# never imports the large views module.
def execute_aslm_chat(spec: RunSpec, emit: Callable[[str, dict], object], should_abort: Callable[[], bool]) -> None:
    resolved = spec.resolved
    engine = resolved.engine.engine
    model = resolved.model
    session_id = spec.chat_id or "run"

    # Split the requested tools into local Code tools and Chat-hosted tools.
    local_tool_ids, chat_tool_ids = partition_tool_server_ids(engine, model, list(resolved.tool_server_ids))

    payload = build_chat_generate_payload(
        engine=engine,
        model_name=model,
        llm_messages=list(spec.messages),
        system_prompt=spec.system_prompt,
        session_id=session_id,
        clean_options=dict(resolved.options),
        local_tool_server_ids=local_tool_ids,
        chat_tool_server_ids=chat_tool_ids,
    )

    accumulator = aslm_chat_stream.ChatStreamAccumulator()
    last_visible = ""

    # Stream chunks, emitting visible-text deltas as token events.
    for chunk in aslm_chat_client.iter_generate_stream(payload):
        if should_abort():
            return

        accumulator.append(chunk)
        visible, _thinking, _transcript = accumulator.snapshot()

        if visible == last_visible:
            continue
        if visible.startswith(last_visible):
            emit("token", {"text": visible[len(last_visible):]})
        else:
            # The parsed visible text was rewritten; resend it as a replacement.
            emit("token", {"text": visible, "replace": True})
        last_visible = visible

    visible, thinking, transcript = accumulator.snapshot()
    emit("message", {"text": visible, "thinking": thinking, "transcript": transcript})
