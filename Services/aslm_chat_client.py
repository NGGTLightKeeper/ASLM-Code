# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import http.cookiejar
import json
import logging
import re
import threading
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterator

from Services import aslm_chat_resolver

logger = logging.getLogger(__name__)

_CSRF_PREFETCH_PATHS = (
    "/api/runtime_settings/",
    "/api/models/?engine=ollama-service",
    "/",
)
_CSRF_COOKIE_RE = re.compile(r"(?:^|,\s*)csrftoken=([^;,\s]+)", re.IGNORECASE)
_CSRF_INPUT_RE = re.compile(
    r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']',
    re.IGNORECASE,
)

_session_lock = threading.Lock()
_active_session: _ChatHttpSession | None = None
_active_session_base = ""


class ChatRequestError(RuntimeError):
    """Raised when ASLM-Chat returns an HTTP or protocol error."""


# Extract csrftoken from one response Set-Cookie header value.
def _parse_csrf_from_set_cookie(header_value: str) -> str:
    match = _CSRF_COOKIE_RE.search(str(header_value or ""))
    if not match:
        return ""
    return urllib.parse.unquote(match.group(1).strip())


# Extract csrftoken from one HTML page body.
def _parse_csrf_from_html(body: str) -> str:
    match = _CSRF_INPUT_RE.search(str(body or ""))
    if not match:
        return ""
    return match.group(1).strip()


# Collect every Set-Cookie header value from one HTTP response.
def _iter_set_cookie_headers(resp: Any) -> list[str]:
    headers = getattr(resp, "headers", None)
    if headers is None:
        return []

    values: list[str] = []
    if hasattr(headers, "get_all"):
        values.extend(str(value) for value in headers.get_all("Set-Cookie") or [])
    single = headers.get("Set-Cookie")
    if single:
        values.append(str(single))
    return values


# Maintain cookies and CSRF tokens for server-side ASLM-Chat API calls.
class _ChatHttpSession:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._csrf_token = ""
        self._jar = http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self._jar)
        )

    # Read a cached or cookie-jar csrftoken value.
    def _read_cached_csrf_token(self) -> str:
        if self._csrf_token:
            return self._csrf_token
        for cookie in self._jar:
            if cookie.name == "csrftoken":
                return str(cookie.value or "")
        return ""

    # Store one CSRF token and mirror it into the cookie jar.
    def _store_csrf_token(self, token: str) -> str:
        normalized = str(token or "").strip()
        if not normalized:
            return ""
        self._csrf_token = normalized

        parsed = urllib.parse.urlparse(self.base_url)
        host = parsed.hostname or "127.0.0.1"
        self._jar.set_cookie(
            http.cookiejar.Cookie(
                version=0,
                name="csrftoken",
                value=normalized,
                port=None,
                port_specified=False,
                domain=host,
                domain_specified=True,
                domain_initial_dot=False,
                path="/",
                path_specified=True,
                secure=parsed.scheme == "https",
                expires=None,
                discard=True,
                comment=None,
                comment_url=None,
                rest={},
                rfc2109=False,
            )
        )
        return normalized

    # Parse csrftoken from one prefetch response.
    def _parse_csrf_from_response(self, resp: Any, body: str) -> str:
        for header_value in _iter_set_cookie_headers(resp):
            token = _parse_csrf_from_set_cookie(header_value)
            if token:
                return token
        return _parse_csrf_from_html(body)

    # Prime Django CSRF state with one lightweight GET request.
    def ensure_csrf(self, *, timeout: float = 30.0) -> str:
        token = self._read_cached_csrf_token()
        if token:
            return self._store_csrf_token(token)

        last_error = ""
        for path in _CSRF_PREFETCH_PATHS:
            url = f"{self.base_url}{path}"
            req = urllib.request.Request(url, method="GET")
            try:
                with self._opener.open(req, timeout=timeout) as resp:
                    body = resp.read().decode("utf-8", errors="replace")
                token = self._parse_csrf_from_response(resp, body)
                if not token:
                    token = self._read_cached_csrf_token()
                if token:
                    return self._store_csrf_token(token)
            except urllib.error.HTTPError as exc:
                last_error = exc.read().decode("utf-8", errors="replace") or str(exc)
            except urllib.error.URLError as exc:
                last_error = str(exc)

        if last_error:
            logger.warning("ASLM-Chat CSRF prefetch failed: %s", last_error[:240])
        else:
            logger.warning("ASLM-Chat did not return a csrftoken cookie after CSRF prefetch.")
        return ""

    # Build headers required for Django-protected POST requests.
    def post_headers(self, *, timeout: float = 30.0) -> dict[str, str]:
        token = self.ensure_csrf(timeout=timeout)
        parsed = urllib.parse.urlparse(self.base_url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Referer": f"{self.base_url}/",
            "Origin": origin,
        }
        if token:
            headers["X-CSRFToken"] = token
            headers["Cookie"] = f"csrftoken={token}"
        return headers

    # Perform one HTTP request and return status, parsed JSON, and headers.
    def request_json(
        self,
        method: str,
        url: str,
        *,
        body: dict[str, Any] | None = None,
        timeout: float = 120.0,
    ) -> tuple[int, dict[str, Any], dict[str, str]]:
        headers: dict[str, str] = {}
        data: bytes | None = None
        if body is not None:
            headers.update(self.post_headers(timeout=min(timeout, 30.0)))
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif method not in {"GET", "HEAD"}:
            headers.update(self.post_headers(timeout=min(timeout, 30.0)))

        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        with self._opener.open(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            response_headers = {key: value for key, value in resp.headers.items()}
            if not raw.strip():
                return resp.status, {}, response_headers
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                parsed = {"value": parsed}
            return resp.status, parsed, response_headers

    # Open one streaming POST request against ASLM-Chat.
    def open_stream(
        self,
        url: str,
        *,
        body: bytes,
        timeout: float = 3600.0,
    ) -> urllib.response.addinfourl:
        headers = self.post_headers(timeout=30.0)
        req = urllib.request.Request(url, data=body, method="POST", headers=headers)
        return self._opener.open(req, timeout=timeout)


# Return the HTTP session for the currently resolved ASLM-Chat base URL.
def _get_session() -> _ChatHttpSession:
    global _active_session, _active_session_base

    base = aslm_chat_resolver.ensure_chat_running().rstrip("/")
    with _session_lock:
        if _active_session is None or _active_session_base != base:
            _active_session = _ChatHttpSession(base)
            _active_session_base = base
        return _active_session


# Drop cached cookies when ASLM-Chat moves to another host/port.
def invalidate_http_session() -> None:
    global _active_session, _active_session_base

    with _session_lock:
        _active_session = None
        _active_session_base = ""


# Build one absolute URL against the resolved ASLM-Chat base URL.
def _chat_url(path: str) -> str:
    base = aslm_chat_resolver.ensure_chat_running().rstrip("/")
    normalized = str(path or "").strip()
    if not normalized.startswith("/"):
        normalized = "/" + normalized
    return base + normalized


# Perform one HTTP request against ASLM-Chat and decode JSON responses.
def _request_json(
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    timeout: float = 120.0,
) -> tuple[int, dict[str, Any], dict[str, str]]:
    url = _chat_url(path)
    session = _get_session()
    try:
        return session.request_json(method, url, body=body, timeout=timeout)
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(payload)
            if not isinstance(parsed, dict):
                parsed = {"error": payload}
        except json.JSONDecodeError:
            parsed = {"error": payload or str(exc)}
        raise ChatRequestError(parsed.get("error") or payload or str(exc)) from exc
    except urllib.error.URLError as exc:
        aslm_chat_resolver.invalidate_chat_base_url_cache()
        invalidate_http_session()
        raise ChatRequestError(str(exc)) from exc


# Return the model list for one engine from ASLM-Chat.
def get_models(engine: str) -> list[Any]:
    status, payload, _headers = _request_json(
        "GET",
        f"/api/models/?engine={urllib.parse.quote(str(engine or '').strip())}",
        timeout=60.0,
    )
    if status >= 400:
        raise ChatRequestError(payload.get("error") or f"HTTP {status}")
    models = payload.get("models")
    return models if isinstance(models, list) else []


# Return normalized model metadata from ASLM-Chat.
def get_model_info(engine: str, model_name: str) -> dict[str, Any]:
    query = urllib.parse.urlencode({"engine": engine, "model": model_name})
    status, payload, _headers = _request_json("GET", f"/api/model_info/?{query}", timeout=60.0)
    if status >= 400:
        raise ChatRequestError(payload.get("error") or f"HTTP {status}")
    return payload


# Return tool servers exposed by ASLM-Chat for one engine/model pair.
def get_tool_servers(engine: str, model_name: str | None = None) -> list[dict[str, Any]]:
    params: dict[str, str] = {"engine": str(engine or "").strip()}
    if model_name:
        params["model"] = str(model_name).strip()
    query = urllib.parse.urlencode(params)
    status, payload, _headers = _request_json("GET", f"/api/tools/?{query}", timeout=60.0)
    if status >= 400:
        raise ChatRequestError(payload.get("error") or f"HTTP {status}")
    servers = payload.get("tool_servers") or payload.get("servers") or payload.get("tools") or []
    if not isinstance(servers, list):
        return []
    annotated: list[dict[str, Any]] = []
    for entry in servers:
        if isinstance(entry, dict):
            annotated.append({**entry, "source": "chat"})
    return annotated


# Ask ASLM-Chat to abort one in-flight generation.
def abort_generation(*, engine: str, generation_id: str = "") -> dict[str, Any]:
    body: dict[str, Any] = {"engine": engine}
    if generation_id:
        body["generation_id"] = generation_id
    status, payload, _headers = _request_json("POST", "/api/chat/abort/", body=body, timeout=30.0)
    if status >= 400:
        raise ChatRequestError(payload.get("error") or f"HTTP {status}")
    return payload


# Stream plain-text chunks from ASLM-Chat /api/generate/.
def iter_generate_stream(payload: dict[str, Any]) -> Iterator[str]:
    url = _chat_url("/api/generate/")
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    session = _get_session()
    try:
        with session.open_stream(url, body=body, timeout=3600.0) as resp:
            read_chunk = getattr(resp, "read1", None)
            while True:
                if callable(read_chunk):
                    chunk = read_chunk(1024)
                else:
                    chunk = resp.read(1024)
                if not chunk:
                    break
                yield chunk.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        payload_text = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(payload_text)
            message = parsed.get("error") if isinstance(parsed, dict) else payload_text
        except json.JSONDecodeError:
            message = payload_text or str(exc)
        raise ChatRequestError(message) from exc
    except urllib.error.URLError as exc:
        aslm_chat_resolver.invalidate_chat_base_url_cache()
        invalidate_http_session()
        raise ChatRequestError(str(exc)) from exc


# Collect one non-streaming generate response from ASLM-Chat.
def generate_sync(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    for chunk in iter_generate_stream(payload):
        parts.append(chunk)
    return "".join(parts)


# Ask ASLM-Chat whether stateless history compression should run.
def decide_compression(payload: dict[str, Any]) -> dict[str, Any]:
    status, response_payload, _headers = _request_json(
        "POST",
        "/api/context_compression/decide/",
        body=payload,
        timeout=60.0,
    )
    if status >= 400:
        raise ChatRequestError(response_payload.get("error") or f"HTTP {status}")
    return response_payload


# Build one compression timeline event via ASLM-Chat.
def build_compression_event(payload: dict[str, Any]) -> dict[str, Any]:
    status, response_payload, _headers = _request_json(
        "POST",
        "/api/context_compression/build_event/",
        body=payload,
        timeout=600.0,
    )
    if status >= 400:
        raise ChatRequestError(response_payload.get("error") or f"HTTP {status}")
    return response_payload


# Return backend status information for the UI health indicator.
def get_backend_status(*, ensure: bool = False) -> dict[str, Any]:
    try:
        base_url = (
            aslm_chat_resolver.ensure_chat_running()
            if ensure
            else aslm_chat_resolver.resolve_chat_base_url()
        )
    except aslm_chat_resolver.ChatNotAvailableError as exc:
        return {
            "ok": False,
            "status": "unavailable",
            "error": str(exc),
        }

    ping = aslm_chat_resolver.ping_chat_backend(base_url=base_url)
    return {
        "ok": bool(ping.get("ok")),
        "status": "connected" if ping.get("ok") else "degraded",
        "base_url": base_url,
        "details": ping,
    }


# Return sub-engine options enabled inside ASLM-Chat.
def get_chat_sub_engines() -> list[dict[str, str]]:
    try:
        status, payload, _headers = _request_json("GET", "/api/runtime_settings/", timeout=30.0)
        if status >= 400:
            raise ChatRequestError(payload.get("error") or f"HTTP {status}")
        options = payload.get("engine_options")
        if isinstance(options, list) and options:
            normalized: list[dict[str, str]] = []
            for entry in options:
                if not isinstance(entry, dict):
                    continue
                engine_id = str(entry.get("id") or "").strip()
                if not engine_id:
                    continue
                normalized.append(
                    {
                        "id": engine_id,
                        "label": str(entry.get("label") or engine_id).strip(),
                    }
                )
            if normalized:
                return normalized
    except Exception as exc:
        logger.warning("Failed to load ASLM-Chat sub-engines: %s", exc)

    from Settings import settings as runtime_settings

    return runtime_settings.get_sub_engines()
