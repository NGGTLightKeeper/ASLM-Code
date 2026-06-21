# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import json
import logging
from typing import Any

from django.http import JsonResponse, StreamingHttpResponse

from Runtime.run_manager import get_run_manager
from Runtime.types import ConfigError, RunOverrides, RunSpec, RunStatus

logger = logging.getLogger(__name__)


# Parse the JSON request body into a mapping, tolerating empty payloads.
def _read_json_body(request) -> dict[str, Any]:
    raw = request.body or b""
    if not raw:
        return {}
    try:
        data = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


# Build per-run overrides from the request payload.
def _overrides_from_request(data: dict[str, Any]) -> RunOverrides:
    return RunOverrides(
        engine=data.get("engine") or None,
        sub_engine=data.get("sub_engine") or None,
        model=data.get("model") or None,
        limits=data.get("limits") if isinstance(data.get("limits"), dict) else None,
        tool_server_ids=data.get("tool_server_ids") if isinstance(data.get("tool_server_ids"), list) else None,
        options=data.get("options") if isinstance(data.get("options"), dict) else None,
    )


# Start one background run and return its identifier without blocking.
def run_start_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    data = _read_json_body(request)
    message = str(data.get("message") or "").strip()
    manager = get_run_manager()

    try:
        resolved = manager.config.resolve(_overrides_from_request(data))
    except ConfigError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    spec = RunSpec(
        resolved=resolved,
        messages=[{"role": "user", "content": message}] if message else [],
        chat_id=str(data.get("chat_id") or ""),
        parent_run_id=data.get("parent_run_id") or None,
    )
    run_id = manager.start(spec)
    return JsonResponse({"run_id": run_id, "status": RunStatus.RUNNING.value})


# Stream one run's events as newline-delimited JSON, resuming from a sequence.
def run_stream_api(request, run_id):
    manager = get_run_manager()
    if manager.get(run_id) is None:
        return JsonResponse({"error": "Unknown run"}, status=404)

    try:
        from_seq = int(request.GET.get("from_seq", 0))
    except (TypeError, ValueError):
        from_seq = 0

    # Serialize each event as one NDJSON line so a reconnecting client resumes cleanly.
    def event_lines():
        for event in manager.subscribe(run_id, from_seq):
            yield json.dumps(event.as_dict(), ensure_ascii=False) + "\n"

    response = StreamingHttpResponse(event_lines(), content_type="application/x-ndjson")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


# Return one run's current metadata snapshot.
def run_info_api(request, run_id):
    info = get_run_manager().get(run_id)
    if info is None:
        return JsonResponse({"error": "Unknown run"}, status=404)
    return JsonResponse(info.as_dict())


# Request cooperative cancellation of one run.
def run_abort_api(request, run_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)
    aborted = get_run_manager().abort(run_id)
    return JsonResponse({"run_id": run_id, "aborted": bool(aborted)})
