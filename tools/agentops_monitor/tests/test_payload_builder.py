"""payload builder (build_digest_embed / build_anttime_embed) と sanitize の検証。"""
from __future__ import annotations

import unittest
from datetime import datetime

from tools.agentops_monitor.__main__ import (
    JST,
    build_anttime_embed,
    build_digest_embed,
    sanitize_mention_text,
)


_NOW = datetime(2026, 4, 29, 9, 30, 0, tzinfo=JST)


class SanitizeMentionTextTests(unittest.TestCase):
    def test_everyone_is_neutralized(self) -> None:
        result = sanitize_mention_text("hello @everyone hi")
        self.assertNotIn("@everyone", result)
        self.assertIn("@​everyone", result)

    def test_here_is_neutralized(self) -> None:
        result = sanitize_mention_text("@here team")
        self.assertNotIn("@here", result)
        self.assertIn("@​here", result)

    def test_user_mention_is_neutralized(self) -> None:
        result = sanitize_mention_text("ping <@123456789012345678> please")
        self.assertNotIn("<@123456789012345678>", result)
        self.assertIn("<@​123456789012345678>", result)

    def test_role_mention_is_neutralized(self) -> None:
        result = sanitize_mention_text("role <@&999>")
        self.assertNotIn("<@&999>", result)
        self.assertIn("<@​&999>", result)

    def test_empty_returns_empty(self) -> None:
        self.assertEqual(sanitize_mention_text(""), "")
        self.assertEqual(sanitize_mention_text(None), None)  # type: ignore[arg-type]


class BuildDigestEmbedTests(unittest.TestCase):
    def _report(self) -> dict:
        return {
            "generated_at": _NOW.isoformat(timespec="seconds"),
            "projects": [
                {
                    "name": "ai-engine",
                    "path": "/home/otaku/dev/ai-engine",
                    "ok": True,
                    "warnings": [],
                    "errors": [],
                    "git": {"branch": "main", "dirty_files": 3},
                    "agentops": {
                        "runs": {"total": 2, "stuck": ["x"]},
                        "tasks": 1,
                        "handoffs": 2,
                        "next_session_md": True,
                    },
                }
            ],
        }

    def test_envelope_has_required_fields(self) -> None:
        payload = build_digest_embed("daily", self._report(), _NOW)
        self.assertEqual(payload["username"], "agentops-watch")
        self.assertEqual(payload["allowed_mentions"], {"parse": []})
        self.assertEqual(len(payload["embeds"]), 1)

    def test_daily_title_format(self) -> None:
        payload = build_digest_embed("daily", self._report(), _NOW)
        self.assertEqual(payload["embeds"][0]["title"], "daily digest — 2026-04-29")

    def test_weekly_title_format(self) -> None:
        payload = build_digest_embed("weekly", self._report(), _NOW)
        # 2026-04-29 (水) は 2026 W18
        self.assertRegex(payload["embeds"][0]["title"], r"^weekly digest — 2026-W\d{2}$")

    def test_monthly_title_format(self) -> None:
        payload = build_digest_embed("monthly", self._report(), _NOW)
        self.assertEqual(payload["embeds"][0]["title"], "monthly digest — 2026-04")

    def test_field_includes_required_keys(self) -> None:
        payload = build_digest_embed("daily", self._report(), _NOW)
        field_value = payload["embeds"][0]["fields"][0]["value"]
        self.assertIn("branch:", field_value)
        self.assertIn("open tasks:", field_value)
        self.assertIn("handoffs:", field_value)
        self.assertIn("next-session:", field_value)
        self.assertIn("dirty:", field_value)
        self.assertIn("stuck runs:", field_value)

    def test_sanitization_applied_to_branch(self) -> None:
        report = self._report()
        report["projects"][0]["git"]["branch"] = "feat/@everyone"
        payload = build_digest_embed("daily", report, _NOW)
        field_value = payload["embeds"][0]["fields"][0]["value"]
        self.assertNotIn("@everyone", field_value)

    def test_field_count_capped_at_25(self) -> None:
        report = self._report()
        report["projects"] = [report["projects"][0]] * 30
        payload = build_digest_embed("daily", report, _NOW)
        self.assertLessEqual(len(payload["embeds"][0]["fields"]), 25)

    def test_invalid_kind_raises(self) -> None:
        with self.assertRaises(ValueError):
            build_digest_embed("alert", self._report(), _NOW)


class BuildAnttimeEmbedTests(unittest.TestCase):
    def test_session_start_includes_project_branch(self) -> None:
        payload = build_anttime_embed(
            kind="session-start",
            project="/home/otaku/dev/ai-engine",
            message="",
            now_jst=_NOW,
            branch="main",
        )
        embed = payload["embeds"][0]
        self.assertEqual(embed["title"], "session-start: ai-engine")
        names = [f["name"] for f in embed["fields"]]
        self.assertIn("project", names)
        self.assertIn("branch", names)

    def test_alert_without_project_omits_fields(self) -> None:
        payload = build_anttime_embed(
            kind="alert",
            project="",
            message="something happened",
            now_jst=_NOW,
        )
        embed = payload["embeds"][0]
        names = [f["name"] for f in embed["fields"]]
        self.assertNotIn("project", names)
        self.assertNotIn("branch", names)
        self.assertEqual(embed["title"], "alert: something happened")

    def test_alert_long_message_added_as_field(self) -> None:
        long_msg = "x" * 200
        payload = build_anttime_embed(
            kind="alert",
            project="",
            message=long_msg,
            now_jst=_NOW,
        )
        names = [f["name"] for f in payload["embeds"][0]["fields"]]
        self.assertIn("message", names)

    def test_permission_wait_requires_message_in_title(self) -> None:
        payload = build_anttime_embed(
            kind="permission-wait",
            project="/p",
            message="Bash",
            now_jst=_NOW,
        )
        self.assertEqual(payload["embeds"][0]["title"], "permission-wait: Bash")

    def test_stop_failure_uses_dark_red(self) -> None:
        payload = build_anttime_embed(
            kind="stop-failure",
            project="/p",
            message="failed",
            now_jst=_NOW,
        )
        self.assertEqual(payload["embeds"][0]["color"], 10038562)

    def test_allowed_mentions_required(self) -> None:
        payload = build_anttime_embed("alert", "", "x", _NOW)
        self.assertEqual(payload["allowed_mentions"], {"parse": []})

    def test_message_sanitized(self) -> None:
        payload = build_anttime_embed("alert", "", "ping @everyone now", _NOW)
        title = payload["embeds"][0]["title"]
        self.assertNotIn("@everyone", title)

    def test_invalid_kind_raises(self) -> None:
        with self.assertRaises(ValueError):
            build_anttime_embed("daily", "/p", "", _NOW)


if __name__ == "__main__":
    unittest.main()
