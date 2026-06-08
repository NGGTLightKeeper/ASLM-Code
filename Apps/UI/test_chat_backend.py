# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import unittest
import http.cookiejar

from Apps.UI.chat_backend import build_chat_generate_payload, partition_tool_server_ids
from Services import aslm_chat_client, aslm_chat_stream
from Services.aslm_chat_client import (
    _ChatHttpSession,
    _parse_csrf_from_html,
    _parse_csrf_from_set_cookie,
)


class ChatBackendTests(unittest.TestCase):
    def test_build_chat_generate_payload_splits_system_and_user(self) -> None:
        payload = build_chat_generate_payload(
            engine="ollama-service",
            model_name="llama3",
            llm_messages=[
                {"role": "system", "content": "System prompt"},
                {"role": "user", "content": "Hello"},
            ],
            system_prompt="System prompt",
            session_id="session-1",
            chat_tool_server_ids=["web-search"],
        )
        self.assertEqual(payload["message"], "Hello")
        self.assertEqual(payload["messages"], [])
        self.assertTrue(payload["stream"])
        self.assertFalse(payload["consume_skill_notifications"])
        self.assertNotIn("tool_sources", payload)
        self.assertEqual(payload["tool_server_ids"], ["web-search"])

    def test_partition_tool_server_ids_routes_all_tools_to_chat_without_local_registry(self) -> None:
        local_ids, chat_ids = partition_tool_server_ids(
            "ollama-service",
            "llama3",
            ["web-search", "sandbox"],
        )
        self.assertEqual(local_ids, [])
        self.assertEqual(chat_ids, ["web-search", "sandbox"])

    def test_parse_completed_stream_extracts_visible_text(self) -> None:
        visible, thinking, transcript = aslm_chat_stream.parse_completed_stream(
            "Hello <think>Reason</think> world",
            emit_thinking=True,
        )
        self.assertEqual(visible, "Hello  world")
        self.assertEqual(thinking, "Reason")
        self.assertEqual(transcript, [])

    def test_chat_http_session_adds_csrf_headers_for_post(self) -> None:
        session = _ChatHttpSession("http://127.0.0.1:18080")
        session._store_csrf_token("token-123")

        headers = session.post_headers()

        self.assertEqual(headers["X-CSRFToken"], "token-123")
        self.assertEqual(headers["Cookie"], "csrftoken=token-123")
        self.assertEqual(headers["Referer"], "http://127.0.0.1:18080/")
        self.assertEqual(headers["Origin"], "http://127.0.0.1:18080")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")

    def test_parse_csrf_from_set_cookie_header(self) -> None:
        self.assertEqual(
            _parse_csrf_from_set_cookie("csrftoken=abc123; Path=/; SameSite=Lax"),
            "abc123",
        )

    def test_parse_csrf_from_html_input(self) -> None:
        html = '<input type="hidden" name="csrfmiddlewaretoken" value="html-token">'
        self.assertEqual(_parse_csrf_from_html(html), "html-token")

    def test_invalidate_http_session_clears_cached_csrf_state(self) -> None:
        aslm_chat_client._active_session = _ChatHttpSession("http://127.0.0.1:18080")
        aslm_chat_client._active_session_base = "http://127.0.0.1:18080"

        aslm_chat_client.invalidate_http_session()

        self.assertIsNone(aslm_chat_client._active_session)
        self.assertEqual(aslm_chat_client._active_session_base, "")


if __name__ == "__main__":
    unittest.main()
