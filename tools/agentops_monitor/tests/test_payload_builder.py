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
        # title に kind 別 emoji prefix を付ける (📊 daily / 📈 weekly / 🗓️ monthly)
        self.assertEqual(payload["embeds"][0]["title"], "📊 daily digest — 2026-04-29")

    def test_weekly_title_format(self) -> None:
        payload = build_digest_embed("weekly", self._report(), _NOW)
        # 2026-04-29 (水) は 2026 W18
        self.assertRegex(payload["embeds"][0]["title"], r"^📈 weekly digest — 2026-W\d{2}$")

    def test_monthly_title_format(self) -> None:
        payload = build_digest_embed("monthly", self._report(), _NOW)
        self.assertEqual(payload["embeds"][0]["title"], "🗓️ monthly digest — 2026-04")

    def test_description_includes_required_keys(self) -> None:
        # signal を含む project は embed.description に markdown ## ヘッダー + bullet
        # 形式で出力される (field 構造ではなく description ベース、見出し感を出す)。
        payload = build_digest_embed("daily", self._report(), _NOW)
        description = payload["embeds"][0]["description"]
        self.assertIn("## ", description)  # h2 ヘッダー
        self.assertIn("branch:", description)
        self.assertIn("open tasks:", description)
        self.assertIn("handoffs:", description)
        self.assertIn("dirty:", description)
        self.assertIn("stuck runs:", description)
        # next-session.md の存在は signal にも description にも含めない設計
        self.assertNotIn("next-session", description)

    def test_sanitization_applied_to_branch(self) -> None:
        report = self._report()
        report["projects"][0]["git"]["branch"] = "feat/@everyone"
        payload = build_digest_embed("daily", report, _NOW)
        # branch sanitize は description (project section) に反映される
        self.assertNotIn("@everyone", payload["embeds"][0]["description"])

    def test_description_truncated_to_4096(self) -> None:
        # Discord embed.description は 4096 文字上限。30 project でも超過しないこと。
        report = self._report()
        report["projects"] = [report["projects"][0]] * 30
        payload = build_digest_embed("daily", report, _NOW)
        self.assertLessEqual(len(payload["embeds"][0]["description"]), 4096)

    def test_invalid_kind_raises(self) -> None:
        with self.assertRaises(ValueError):
            build_digest_embed("alert", self._report(), _NOW)

    # --- --message 拡張のテスト (PR-C で追加) ---

    def test_message_added_to_embed_fields(self) -> None:
        """--message は description とは独立した "📜 audit log" field として保持される。

        project section は description (markdown ##) に集約、audit log のみ field に
        分離することで、tail 50 が見出し階層を崩さない設計。
        """
        payload = build_digest_embed("daily", self._report(), _NOW, message="[smoke] OK")
        embed = payload["embeds"][0]
        fields = embed["fields"]
        self.assertEqual(fields[-1]["name"], "📜 audit log")
        self.assertEqual(fields[-1]["value"], "[smoke] OK")
        # project section は description 側に維持される
        self.assertIn("## ", embed["description"])

    def test_message_sanitized_in_digest(self) -> None:
        """--message に含まれる @everyone / <@id> 等が無害化される。"""
        payload = build_digest_embed(
            "weekly", self._report(), _NOW, message="ping @everyone <@123456> now"
        )
        audit_field = payload["embeds"][0]["fields"][-1]
        self.assertEqual(audit_field["name"], "📜 audit log")
        self.assertNotIn("@everyone", audit_field["value"])
        self.assertNotIn("<@123456>", audit_field["value"])

    def test_message_truncated_to_1024(self) -> None:
        """1024 文字を超える message は末尾が省略される。"""
        long_msg = "x" * 2000
        payload = build_digest_embed("monthly", self._report(), _NOW, message=long_msg)
        audit_field = payload["embeds"][0]["fields"][-1]
        self.assertLessEqual(len(audit_field["value"]), 1024)
        # truncate 表記 "…" が末尾に付く
        self.assertTrue(audit_field["value"].endswith("…"))

    def test_no_message_preserves_existing_shape(self) -> None:
        """message 無しは "📜 audit log" field を含めない (regression test)。"""
        payload = build_digest_embed("daily", self._report(), _NOW)
        embed = payload["embeds"][0]
        names = [f["name"] for f in embed["fields"]]
        self.assertNotIn("📜 audit log", names)
        # signal を持つ project は description に出る
        self.assertIn("## ", embed["description"])

    def test_empty_message_treated_as_no_message(self) -> None:
        """空文字 message も "📜 audit log" field を作らない。"""
        payload = build_digest_embed("daily", self._report(), _NOW, message="")
        names = [f["name"] for f in payload["embeds"][0]["fields"]]
        self.assertNotIn("📜 audit log", names)

    def test_message_reserves_slot_when_at_field_limit(self) -> None:
        """既存 project が 25 件あっても message 指定時は 24 + audit log = 25 になる。"""
        report = self._report()
        # 30 個の同一 project で fields 上限超過状態にする
        report["projects"] = [report["projects"][0]] * 30
        payload = build_digest_embed("daily", report, _NOW, message="[smoke] cap")
        fields = payload["embeds"][0]["fields"]
        self.assertLessEqual(len(fields), 25)
        self.assertEqual(fields[-1]["name"], "📜 audit log")


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
