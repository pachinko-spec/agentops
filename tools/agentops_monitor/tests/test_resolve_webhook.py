"""resolve_webhook_url の挙動を検証する。"""
from __future__ import annotations

import unittest

from tools.agentops_monitor.__main__ import (
    KIND_TO_ENVVAR,
    resolve_webhook_url,
)


class ResolveWebhookUrlTests(unittest.TestCase):
    def test_known_kinds_map_to_envvars(self) -> None:
        """8 種すべての kind が envvar に解決される。"""
        for kind in KIND_TO_ENVVAR:
            envvar, _url = resolve_webhook_url(kind, env={})
            self.assertEqual(envvar, KIND_TO_ENVVAR[kind])

    def test_returns_url_when_env_set(self) -> None:
        """環境変数に値があれば URL を返す。"""
        env = {"DISCORD_WEBHOOK_URL_DAILLY": "https://discord.invalid/webhooks/0/dummy"}
        envvar, url = resolve_webhook_url("daily", env=env)
        self.assertEqual(envvar, "DISCORD_WEBHOOK_URL_DAILLY")
        self.assertEqual(url, "https://discord.invalid/webhooks/0/dummy")

    def test_returns_none_when_env_missing(self) -> None:
        """環境変数が無ければ None を返す (例外ではない)。"""
        envvar, url = resolve_webhook_url("daily", env={})
        self.assertEqual(envvar, "DISCORD_WEBHOOK_URL_DAILLY")
        self.assertIsNone(url)

    def test_unknown_kind_raises(self) -> None:
        """未知の kind は ValueError。"""
        with self.assertRaises(ValueError):
            resolve_webhook_url("not-a-kind", env={})

    def test_anttime_kinds_share_env(self) -> None:
        """ANT_TIME 系 kind はすべて DISCORD_WEBHOOK_URL_ANT_TIME を引く。"""
        env = {"DISCORD_WEBHOOK_URL_ANT_TIME": "https://discord.invalid/webhooks/1/dummy"}
        for kind in ("session-start", "session-end", "permission-wait", "alert", "stop-failure"):
            envvar, url = resolve_webhook_url(kind, env=env)
            self.assertEqual(envvar, "DISCORD_WEBHOOK_URL_ANT_TIME")
            self.assertEqual(url, "https://discord.invalid/webhooks/1/dummy")


if __name__ == "__main__":
    unittest.main()
