# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import json
import re
from typing import Any

THINKING_START = "<think>"
THINKING_END = "</think>"
TOOL_CALL_RE = re.compile(r"<tool_call>(.*?)</tool_call>", re.DOTALL)
TOOL_RESULT_RE = re.compile(r"<tool_result>(.*?)</tool_result>", re.DOTALL)
CONTEXT_COMPRESSION_RE = re.compile(r"<context_compression>(.*?)</context_compression>", re.DOTALL)


# Strip control markers from one assistant-visible string.
def strip_stream_markers(text: str) -> str:
    cleaned = str(text or "")
    cleaned = TOOL_CALL_RE.sub("", cleaned)
    cleaned = TOOL_RESULT_RE.sub("", cleaned)
    cleaned = CONTEXT_COMPRESSION_RE.sub("", cleaned)
    cleaned = cleaned.replace(THINKING_START, "").replace(THINKING_END, "")
    return cleaned.strip()


# Parse one tool marker JSON payload safely.
def _parse_marker_json(raw: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(str(raw or "").strip())
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


# Extract visible text, thinking text, and transcript entries from a full stream body.
def parse_completed_stream(text: str, *, emit_thinking: bool = True) -> tuple[str, str, list[dict[str, Any]]]:
    source = str(text or "")
    thinking_parts: list[str] = []
    visible_parts: list[str] = []
    transcript_entries: list[dict[str, Any]] = []

    cursor = 0
    while cursor < len(source):
        next_thinking = source.find(THINKING_START, cursor)
        next_tool_call = source.find("<tool_call>", cursor)
        next_tool_result = source.find("<tool_result>", cursor)
        next_compression = source.find("<context_compression>", cursor)
        candidates = [
            pos
            for pos in (next_thinking, next_tool_call, next_tool_result, next_compression)
            if pos >= 0
        ]
        if not candidates:
            visible_parts.append(source[cursor:])
            break

        next_pos = min(candidates)
        if next_pos > cursor:
            visible_parts.append(source[cursor:next_pos])

        if next_pos == next_thinking:
            end = source.find(THINKING_END, next_pos + len(THINKING_START))
            if end < 0:
                thinking_parts.append(source[next_pos + len(THINKING_START):])
                break
            thinking_parts.append(source[next_pos + len(THINKING_START):end])
            cursor = end + len(THINKING_END)
            continue

        if next_pos == next_tool_call:
            match = TOOL_CALL_RE.search(source, next_pos)
            if not match:
                break
            payload = _parse_marker_json(match.group(1))
            if payload:
                transcript_entries.append({"role": "assistant", "tool_calls": [payload]})
            cursor = match.end()
            continue

        if next_pos == next_tool_result:
            match = TOOL_RESULT_RE.search(source, next_pos)
            if not match:
                break
            payload = _parse_marker_json(match.group(1))
            if payload:
                transcript_entries.append({"role": "tool", **payload})
            cursor = match.end()
            continue

        match = CONTEXT_COMPRESSION_RE.search(source, next_pos)
        if match:
            payload = _parse_marker_json(match.group(1))
            if payload:
                transcript_entries.append(payload)
            cursor = match.end()
            continue

        break

    visible = strip_stream_markers("".join(visible_parts)).strip()
    thinking = "".join(thinking_parts).strip()
    if not emit_thinking:
        thinking = ""
    return visible, thinking, transcript_entries


# Track in-progress stream parsing state for live snapshots.
class ChatStreamAccumulator:
    """Accumulate ASLM-Chat plain-text stream chunks for relay persistence."""

    def __init__(self, *, emit_thinking: bool = True) -> None:
        self.emit_thinking = emit_thinking
        self.buffer = ""

    # Append one streamed chunk and return the updated buffer length.
    def append(self, chunk: str) -> int:
        self.buffer += str(chunk or "")
        return len(self.buffer)

    # Return the latest parsed visible/thinking/transcript snapshot.
    def snapshot(self) -> tuple[str, str, list[dict[str, Any]]]:
        return parse_completed_stream(self.buffer, emit_thinking=self.emit_thinking)
