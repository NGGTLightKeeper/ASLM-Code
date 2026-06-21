# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Callable

from Runtime.types import RunSpec

logger = logging.getLogger(__name__)

_COMPLETIONS_PATH = "/v1/chat/completions"
_MODELS_PATH = "/v1/models"


# Normalize one raw engine base_url (may lack scheme) to a full http:// URL.
def _base_http_url(raw: str) -> str:
    raw = str(raw or "").strip()
    if not raw:
        raw = "127.0.0.1:1234"
    if "://" not in raw:
        raw = "http://" + raw
    return raw.rstrip("/")


# Parse one SSE "data: ..." line into a dict; return None for control lines or [DONE].
def _parse_sse_line(line: str) -> dict | None:
    line = line.strip()
    if not line.startswith("data:"):
        return None
    payload = line[5:].strip()
    if payload == "[DONE]":
        return None
    try:
        parsed = json.loads(payload)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        logger.debug("Unparseable SSE payload: %r", payload[:120])
        return None


# Return the list of model ids currently loaded in a local OpenAI-compat provider.
def list_models(base_url: str) -> list[str]:
    url = _base_http_url(base_url) + _MODELS_PATH
    req = urllib.request.Request(url, method="GET",
                                 headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            payload = json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception as exc:
        logger.debug("list_models failed for %s: %s", url, exc)
        return []
    data = payload.get("data") or []
    return [str(entry.get("id") or "") for entry in data if entry.get("id")]


# Stream one generation from an OpenAI-compatible /v1/chat/completions endpoint.
# Emits "token" events as deltas arrive and a final "message" event on completion.
def execute_lms_direct(
    spec: RunSpec,
    emit: Callable[[str, dict], object],
    should_abort: Callable[[], bool],
) -> None:
    resolved = spec.resolved
    base_url = _base_http_url(resolved.engine.base_url)
    model = resolved.model
    url = base_url + _COMPLETIONS_PATH
    timeout = resolved.limits.request_timeout_s

    # Prepend the system prompt as a system message when one is provided.
    messages = list(spec.messages)
    if spec.system_prompt:
        messages = [{"role": "system", "content": spec.system_prompt}] + messages

    body = json.dumps(
        {"model": model, "messages": messages, "stream": True},
        ensure_ascii=False,
    ).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
    )

    logger.debug("execute_lms_direct → POST %s model=%r", url, model)

    accumulated = ""
    buffer = ""

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            while True:
                if should_abort():
                    logger.debug("execute_lms_direct: abort requested, stopping stream")
                    return

                chunk = resp.read(1024)
                if not chunk:
                    break

                buffer += chunk.decode("utf-8", errors="replace")

                # Consume complete SSE lines from the buffer.
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    parsed = _parse_sse_line(line)
                    if parsed is None:
                        continue

                    choices = parsed.get("choices") or []
                    if not choices:
                        continue

                    delta = (choices[0].get("delta") or {})
                    content = delta.get("content")
                    if not content:
                        continue

                    emit("token", {"text": content})
                    accumulated += content

    except urllib.error.URLError as exc:
        raise RuntimeError(f"LMS connection failed ({url}): {exc}") from exc

    emit("message", {"text": accumulated})
