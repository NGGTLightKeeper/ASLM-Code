---
title: "aslm_chat_client"
draft: false
---

## Module `aslm_chat_client`

`Services/aslm_chat_client.py` — ASLM Code Python module.

---

## Overview

Part of `Services`. See **Related** for package index and callers.

---

## Classes

### `class ChatRequestError`

**Purpose:** Raised when ASLM-Chat returns an HTTP or protocol error.

### `class _ChatHttpSession`

**Purpose:** Type `_ChatHttpSession` defined in `aslm_chat_client.py`.

---

## Public functions

#### `def _ChatHttpSession.__init__(base_url) -> None`

**Purpose:** Implements `_ChatHttpSession.__init__` in `aslm_chat_client.py`.

**Steps:**

1. Execute the implementation in the source module.

#### `def _ChatHttpSession.ensure_csrf(*, timeout=…) -> str`

**Purpose:** Prime Django CSRF state with one lightweight GET request.

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.
3. Iterate and transform or accumulate state.

#### `def _ChatHttpSession.post_headers(*, timeout=…) -> dict[str, str]`

**Purpose:** Build headers required for Django-protected POST requests.

**Steps:**

1. Return the computed result to the caller.

#### `def _ChatHttpSession.request_json(method, url, *, body=…, timeout=…) -> tuple[int, dict[str, Any], dict[str, str]]`

**Purpose:** Perform one HTTP request and return status, parsed JSON, and headers.

**Steps:**

1. Return the computed result to the caller.
2. Parse or serialize JSON payloads.

#### `def _ChatHttpSession.open_stream(url, *, body, timeout=…) -> urllib.response.addinfourl`

**Purpose:** Open one streaming POST request against ASLM-Chat.

**Steps:**

1. Return the computed result to the caller.

#### `def invalidate_http_session() -> None`

**Purpose:** Drop cached cookies when ASLM-Chat moves to another host/port.

**Steps:**

1. Execute the implementation in the source module.

#### `def get_models(engine) -> list[Any]`

**Purpose:** Return the model list for one engine from ASLM-Chat.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.

#### `def get_model_info(engine, model_name) -> dict[str, Any]`

**Purpose:** Return normalized model metadata from ASLM-Chat.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.

#### `def get_tool_servers(engine, model_name=…) -> list[dict[str, Any]]`

**Purpose:** Return tool servers exposed by ASLM-Chat for one engine/model pair.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.
3. Iterate and transform or accumulate state.

#### `def abort_generation(*, engine, generation_id=…) -> dict[str, Any]`

**Purpose:** Ask ASLM-Chat to abort one in-flight generation.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.

#### `def iter_generate_stream(payload) -> Iterator[str]`

**Purpose:** Stream plain-text chunks from ASLM-Chat /api/generate/.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Handle errors and map them to a safe response.
3. Iterate and transform or accumulate state.
4. Parse or serialize JSON payloads.

#### `def generate_sync(payload) -> str`

**Purpose:** Collect one non-streaming generate response from ASLM-Chat.

**Steps:**

1. Return the computed result to the caller.
2. Iterate and transform or accumulate state.

#### `def decide_compression(payload) -> dict[str, Any]`

**Purpose:** Ask ASLM-Chat whether stateless history compression should run.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.

#### `def build_compression_event(payload) -> dict[str, Any]`

**Purpose:** Build one compression timeline event via ASLM-Chat.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.

#### `def get_backend_status(*, ensure=…) -> dict[str, Any]`

**Purpose:** Return backend status information for the UI health indicator.

**Steps:**

1. Return the computed result to the caller.
2. Handle errors and map them to a safe response.

#### `def get_chat_sub_engines() -> list[dict[str, str]]`

**Purpose:** Return sub-engine options enabled inside ASLM-Chat.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.
3. Handle errors and map them to a safe response.
4. Iterate and transform or accumulate state.

---

## Private functions

#### `def _parse_csrf_from_set_cookie(header_value) -> str`

**Purpose:** Extract csrftoken from one response Set-Cookie header value.

**Steps:**

1. Return the computed result to the caller.

#### `def _parse_csrf_from_html(body) -> str`

**Purpose:** Extract csrftoken from one HTML page body.

**Steps:**

1. Return the computed result to the caller.

#### `def _iter_set_cookie_headers(resp) -> list[str]`

**Purpose:** Collect every Set-Cookie header value from one HTTP response.

**Steps:**

1. Return the computed result to the caller.

#### `def _ChatHttpSession._read_cached_csrf_token() -> str`

**Purpose:** Read a cached or cookie-jar csrftoken value.

**Steps:**

1. Return the computed result to the caller.
2. Iterate and transform or accumulate state.

#### `def _ChatHttpSession._store_csrf_token(token) -> str`

**Purpose:** Store one CSRF token and mirror it into the cookie jar.

**Steps:**

1. Return the computed result to the caller.

#### `def _ChatHttpSession._parse_csrf_from_response(resp, body) -> str`

**Purpose:** Parse csrftoken from one prefetch response.

**Steps:**

1. Return the computed result to the caller.
2. Iterate and transform or accumulate state.

#### `def _get_session() -> _ChatHttpSession`

**Purpose:** Return the HTTP session for the currently resolved ASLM-Chat base URL.

**Steps:**

1. Return the computed result to the caller.

#### `def _chat_url(path) -> str`

**Purpose:** Build one absolute URL against the resolved ASLM-Chat base URL.

**Steps:**

1. Return the computed result to the caller.

#### `def _request_json(method, path, *, body=…, timeout=…) -> tuple[int, dict[str, Any], dict[str, str]]`

**Purpose:** Perform one HTTP request against ASLM-Chat and decode JSON responses.

**Steps:**

1. Raise on invalid input or failure conditions.
2. Return the computed result to the caller.
3. Handle errors and map them to a safe response.
4. Parse or serialize JSON payloads.

---

## Related

- [Services/_index](../_index/)
