"""send_webhook の HTTP 200/204/429/5xx ハンドリング検証。urllib は mock する。"""
from __future__ import annotations

import io
import json
import unittest
from email.message import Message
from typing import Any
from unittest import mock
from urllib import error as urllib_error

from tools.agentops_monitor.__main__ import send_webhook


def _make_response(status: int, headers: dict[str, str] | None = None) -> mock.MagicMock:
    """urlopen の context manager 戻り値を mock する。"""
    cm = mock.MagicMock()
    cm.__enter__.return_value.status = status
    cm.__enter__.return_value.headers = headers or {}
    cm.__exit__.return_value = False
    return cm


class SendWebhookTests(unittest.TestCase):
    def test_200_returns_status(self) -> None:
        opener = mock.MagicMock(return_value=_make_response(200))
        status, headers = send_webhook(
            "https://discord.invalid/webhooks/0/dummy",
            {"x": 1},
            opener=opener,
        )
        self.assertEqual(status, 200)
        self.assertEqual(headers, {})

    def test_request_includes_custom_user_agent(self) -> None:
        # urllib の default `Python-urllib/<ver>` は Cloudflare WAF (Discord 前段)
        # に bot として block され HTTP 403 + error code 1010 を返す。本 CLI は
        # 識別可能な独自 UA を送ることで Cloudflare bot fingerprint heuristics を
        # avoid する。回帰防止テスト。
        opener = mock.MagicMock(return_value=_make_response(204))
        send_webhook(
            "https://discord.invalid/webhooks/0/dummy",
            {"x": 1},
            opener=opener,
        )
        # opener (urlopen) に渡された Request 引数を取り出して header を検証
        called_args, _ = opener.call_args
        req = called_args[0]
        ua = req.get_header("User-agent") or req.get_header("User-Agent")
        self.assertIsNotNone(ua, "User-Agent header must be set explicitly")
        self.assertNotIn("Python-urllib", ua)
        self.assertIn("agentops-watch", ua)

    def test_request_includes_browser_like_baseline_headers(self) -> None:
        # urllib の minimum header (Content-Type + UA のみ) では Cloudflare bot
        # heuristics で連続送信時に断続的に block されるため、通常の HTTP client が
        # 送る Accept / Accept-Language / Connection を明示する。
        opener = mock.MagicMock(return_value=_make_response(204))
        send_webhook(
            "https://discord.invalid/webhooks/0/dummy",
            {"x": 1},
            opener=opener,
        )
        called_args, _ = opener.call_args
        req = called_args[0]
        # Request.get_header は title-cased lookup を要するため両方試す
        accept = req.get_header("Accept")
        accept_lang = req.get_header("Accept-language") or req.get_header("Accept-Language")
        connection = req.get_header("Connection")
        self.assertIsNotNone(accept, "Accept header must be set")
        self.assertIn("application/json", accept)
        self.assertIsNotNone(accept_lang, "Accept-Language header must be set")
        self.assertIsNotNone(connection, "Connection header must be set")
        self.assertEqual(connection, "close")

    def test_204_returns_status(self) -> None:
        opener = mock.MagicMock(return_value=_make_response(204))
        status, _ = send_webhook(
            "https://discord.invalid/webhooks/0/dummy",
            {"x": 1},
            opener=opener,
        )
        self.assertEqual(status, 204)

    def test_429_returns_status_with_retry_after(self) -> None:
        msg = Message()
        msg["Retry-After"] = "12"
        err = urllib_error.HTTPError(
            url="https://discord.invalid/webhooks/0/dummy",
            code=429,
            msg="Too Many Requests",
            hdrs=msg,  # type: ignore[arg-type]
            fp=io.BytesIO(b""),
        )
        opener = mock.MagicMock(side_effect=err)
        status, headers = send_webhook(
            "https://discord.invalid/webhooks/0/dummy",
            {"x": 1},
            opener=opener,
        )
        self.assertEqual(status, 429)
        self.assertIn("Retry-After", headers)
        self.assertEqual(headers["Retry-After"], "12")

    def test_5xx_returns_status(self) -> None:
        msg = Message()
        err = urllib_error.HTTPError(
            url="https://discord.invalid/webhooks/0/dummy",
            code=503,
            msg="Service Unavailable",
            hdrs=msg,  # type: ignore[arg-type]
            fp=io.BytesIO(b""),
        )
        opener = mock.MagicMock(side_effect=err)
        status, _ = send_webhook(
            "https://discord.invalid/webhooks/0/dummy",
            {"x": 1},
            opener=opener,
        )
        self.assertEqual(status, 503)

    def test_payload_serialized_as_json(self) -> None:
        opener = mock.MagicMock(return_value=_make_response(204))
        send_webhook(
            "https://discord.invalid/webhooks/0/dummy",
            {"username": "x", "allowed_mentions": {"parse": []}},
            opener=opener,
        )
        # opener に渡される Request の body が JSON である
        called_with: Any = opener.call_args.args[0]
        body_bytes = called_with.data
        body = json.loads(body_bytes.decode("utf-8"))
        self.assertEqual(body["username"], "x")
        self.assertEqual(body["allowed_mentions"], {"parse": []})

    def test_url_error_returns_status_zero(self) -> None:
        """DNS / connection refused 等の URLError は status=0 + 擬似 header で返す。"""
        err = urllib_error.URLError("Name or service not known")
        opener = mock.MagicMock(side_effect=err)
        status, headers = send_webhook(
            "https://discord.invalid/webhooks/0/dummy",
            {"x": 1},
            opener=opener,
        )
        self.assertEqual(status, 0)
        self.assertIn("X-AgentOps-NetworkError", headers)
        self.assertIn("Name or service not known", headers["X-AgentOps-NetworkError"])

    def test_timeout_returns_status_zero(self) -> None:
        """socket レベル TimeoutError も network error として正規化される。"""
        opener = mock.MagicMock(side_effect=TimeoutError("connect timed out"))
        status, headers = send_webhook(
            "https://discord.invalid/webhooks/0/dummy",
            {"x": 1},
            opener=opener,
        )
        self.assertEqual(status, 0)
        self.assertIn("X-AgentOps-NetworkError", headers)

    def test_oserror_returns_status_zero(self) -> None:
        """connection refused 等の OSError も network error として正規化される。"""
        opener = mock.MagicMock(side_effect=OSError("Connection refused"))
        status, headers = send_webhook(
            "https://discord.invalid/webhooks/0/dummy",
            {"x": 1},
            opener=opener,
        )
        self.assertEqual(status, 0)
        self.assertIn("X-AgentOps-NetworkError", headers)

    def test_url_not_logged(self) -> None:
        """secret URL は戻り値以外で出さない。

        send_webhook は print しないので、stdout / stderr は空のはず。
        """
        opener = mock.MagicMock(return_value=_make_response(204))
        with mock.patch("sys.stdout") as out, mock.patch("sys.stderr") as err:
            send_webhook(
                "https://discord.invalid/webhooks/0/SECRET-XYZ",
                {"x": 1},
                opener=opener,
            )
        # write が呼ばれた場合に SECRET 文字列が含まれていないこと
        for call in (out.write.call_args_list + err.write.call_args_list):
            written = call.args[0] if call.args else ""
            self.assertNotIn("SECRET-XYZ", written)


if __name__ == "__main__":
    unittest.main()
