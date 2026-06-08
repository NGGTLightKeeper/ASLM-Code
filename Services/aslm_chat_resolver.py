# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import logging
import os
import time
import urllib.error
import urllib.request
from typing import Any

from Services import aslm_interop_client

logger = logging.getLogger(__name__)

CHAT_MODULE_ID = "aslm-chat"
_CALLER_MODULE_ID = os.environ.get("ASLM_MODULE_ID", "aslm-code").strip() or "aslm-code"

_cached_base_url: str | None = None
_cached_at: float = 0.0
_CACHE_TTL_SECONDS = 5.0


class ChatNotAvailableError(RuntimeError):
    """Raised when ASLM-Chat cannot be resolved or reached."""


# Return the direct module HTTP base URL for one running module host entry.
def _pick_host_url(host: dict[str, Any]) -> str:
    raw = str(host.get("targetUrl") or "").strip().rstrip("/")
    if raw:
        return raw
    port = host.get("port")
    if port:
        return f"http://127.0.0.1:{int(port)}"
    return ""


# Find the ASLM-Chat base URL inside one interop registry payload.
def _extract_chat_base_url(registry: dict[str, Any]) -> str:
    running_modules = registry.get("runningModules")
    if not isinstance(running_modules, list):
        return ""

    for module in running_modules:
        if not isinstance(module, dict):
            continue
        if str(module.get("id") or "").strip().lower() != CHAT_MODULE_ID:
            continue
        hosts = module.get("hosts")
        if isinstance(hosts, list):
            for host in hosts:
                if not isinstance(host, dict):
                    continue
                url = _pick_host_url(host)
                if url:
                    return url
        page_url = str(module.get("pageUrl") or "").strip().rstrip("/")
        if page_url:
            return page_url
    return ""


# Clear the cached ASLM-Chat base URL.
def invalidate_chat_base_url_cache() -> None:
    global _cached_base_url, _cached_at

    _cached_base_url = None
    _cached_at = 0.0

    from Services import aslm_chat_client

    aslm_chat_client.invalidate_http_session()


# Resolve the ASLM-Chat HTTP base URL via the host interop registry.
def resolve_chat_base_url(*, force_refresh: bool = False) -> str:
    global _cached_base_url, _cached_at

    now = time.monotonic()
    if (
        not force_refresh
        and _cached_base_url
        and now - _cached_at < _CACHE_TTL_SECONDS
    ):
        return _cached_base_url

    if not aslm_interop_client.is_available():
        raise ChatNotAvailableError(
            "ASLM module interop is not configured. Launch ASLM-Code from the ASLM host."
        )

    registry = aslm_interop_client.get_registry()
    base_url = _extract_chat_base_url(registry)
    if not base_url:
        raise ChatNotAvailableError("ASLM-Chat is not running.")

    _cached_base_url = base_url.rstrip("/")
    _cached_at = now
    return _cached_base_url


# Ask the host to start ASLM-Chat when it is not already running.
def ensure_chat_running(*, timeout_seconds: float = 120.0) -> str:
    try:
        return resolve_chat_base_url()
    except ChatNotAvailableError:
        pass

    if not aslm_interop_client.is_available():
        raise ChatNotAvailableError(
            "ASLM module interop is not configured. Launch ASLM-Code from the ASLM host."
        )

    response = aslm_interop_client.request_start(
        caller_module_id=_CALLER_MODULE_ID,
        module_ids=[CHAT_MODULE_ID],
    )
    results = response.get("results")
    if isinstance(results, list):
        for entry in results:
            if not isinstance(entry, dict):
                continue
            status = str(entry.get("status") or "").strip().lower()
            if status in {"error", "notfound", "firstrunfailed"}:
                message = str(entry.get("message") or status)
                raise ChatNotAvailableError(f"ASLM-Chat could not be started: {message}")

    deadline = time.monotonic() + max(1.0, timeout_seconds)
    last_error = "ASLM-Chat is not running."
    while time.monotonic() < deadline:
        invalidate_chat_base_url_cache()
        try:
            return resolve_chat_base_url(force_refresh=True)
        except ChatNotAvailableError as exc:
            last_error = str(exc)
            time.sleep(0.5)

    raise ChatNotAvailableError(last_error)


# Perform a lightweight health check against ASLM-Chat.
def ping_chat_backend(*, base_url: str | None = None) -> dict[str, Any]:
    url = (base_url or ensure_chat_running()).rstrip("/") + "/api/models/?engine=ollama-service"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return {"ok": True, "status_code": resp.status, "url": url, "body_preview": raw[:240]}
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "status_code": exc.code,
            "url": url,
            "error": payload[:500] or str(exc),
        }
    except Exception as exc:
        return {"ok": False, "url": url, "error": str(exc)}


# Return whether ASLM-Chat appears reachable right now.
def is_chat_available() -> bool:
    try:
        base_url = resolve_chat_base_url()
    except ChatNotAvailableError:
        return False
    return bool(ping_chat_backend(base_url=base_url).get("ok"))
