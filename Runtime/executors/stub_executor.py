# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import time
from typing import Callable

from Runtime.types import RunSpec


# Simulated executor that streams fake tokens to validate the run daemon.
# It is a placeholder for the real ASLM-Chat executor and deliberately depends
# on nothing in the web layer.
def execute_stub(spec: RunSpec, emit: Callable[[str, dict], object], should_abort: Callable[[], bool]) -> None:
    engine = spec.resolved.engine.engine
    model = spec.resolved.model
    prompt = ""
    if spec.messages:
        prompt = str(spec.messages[-1].get("content") or "")

    intro = (
        f"[stub:{engine}:{model}] simulated streamed response for: {prompt or '(empty prompt)'}. "
        "This text validates resume and abort handling in the run daemon."
    )

    for word in intro.split(" "):
        if should_abort():
            return
        emit("token", {"text": word + " "})
        time.sleep(0.05)

    emit("message", {"text": intro})
