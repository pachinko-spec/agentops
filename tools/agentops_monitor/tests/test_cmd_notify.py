"""cmd_notify の dry-run / kind dispatch / 旧 envvar 後方互換 path を検証する。"""
from __future__ import annotations

import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from tools.agentops_monitor import __main__ as monitor


class CmdNotifyDryRunTests(unittest.TestCase):
    def setUp(self) -> None:
        # 各テストでホスト env を汚染しない。
        self._env_patcher = mock.patch.dict(
            os.environ,
            {
                "DISCORD_WEBHOOK_URL_DAILLY": "",
                "DISCORD_WEBHOOK_URL_WEEKLY": "",
                "DISCORD_WEBHOOK_URL_MONTHLY": "",
                "DISCORD_WEBHOOK_URL_ANT_TIME": "",
                "AGENTOPS_DISCORD_WEBHOOK_URL": "",
            },
            clear=False,
        )
        self._env_patcher.start()
        # rate-limit state file は tempdir に置く。
        self.tmp = tempfile.TemporaryDirectory()
        self._cache_patcher = mock.patch.dict(
            os.environ,
            {"XDG_CACHE_HOME": self.tmp.name},
        )
        self._cache_patcher.start()

    def tearDown(self) -> None:
        self._env_patcher.stop()
        self._cache_patcher.stop()
        self.tmp.cleanup()

    def _run(self, argv: list[str]) -> tuple[int, str, str]:
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = monitor.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_dry_run_alert_no_project(self) -> None:
        rc, out, err = self._run(["notify", "--kind", "alert", "--message", "test", "--dry-run"])
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertEqual(payload["embeds"][0]["title"], "alert: test")
        names = [f["name"] for f in payload["embeds"][0]["fields"]]
        self.assertNotIn("project", names)

    def test_dry_run_session_start(self) -> None:
        rc, out, _ = self._run(
            ["notify", "--kind", "session-start", "--project", "/home/otaku/agentops", "--dry-run"]
        )
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertTrue(payload["embeds"][0]["title"].startswith("session-start:"))

    def test_session_start_missing_project_errors(self) -> None:
        rc, _, err = self._run(["notify", "--kind", "session-start", "--dry-run"])
        self.assertEqual(rc, 2)
        self.assertIn("requires --project", err)

    def test_permission_wait_missing_message_errors(self) -> None:
        rc, _, err = self._run(
            ["notify", "--kind", "permission-wait", "--project", "/tmp", "--dry-run"]
        )
        self.assertEqual(rc, 2)
        self.assertIn("requires --message", err)

    def test_alert_missing_message_errors(self) -> None:
        rc, _, err = self._run(["notify", "--kind", "alert", "--dry-run"])
        self.assertEqual(rc, 2)
        self.assertIn("requires --message", err)

    def test_legacy_path_emits_deprecation_warning(self) -> None:
        rc, out, err = self._run(
            ["notify", "--project", "/home/otaku/agentops", "--dry-run"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("deprecated", err)
        # 旧 path は content payload (embed ではない)
        payload = json.loads(out)
        self.assertIn("content", payload)
        self.assertNotIn("embeds", payload)

    def test_dry_run_does_not_send(self) -> None:
        """dry-run では urlopen が呼ばれない。"""
        with mock.patch("tools.agentops_monitor.__main__.request.urlopen") as urlopen:
            rc, _, _ = self._run(
                ["notify", "--kind", "alert", "--message", "no-send", "--dry-run"]
            )
            self.assertEqual(rc, 0)
            urlopen.assert_not_called()

    def test_dry_run_does_not_modify_rate_state(self) -> None:
        """dry-run は ANT_TIME rate-limit state を更新しない (preview の副作用回避)。"""
        state_path = Path(self.tmp.name) / "agentops-watch" / "anttime-rate.json"
        # 何回 dry-run を回しても state file が作られない
        for _ in range(7):
            rc, _, _ = self._run(
                ["notify", "--kind", "alert", "--message", "x", "--dry-run"]
            )
            self.assertEqual(rc, 0)
        self.assertFalse(state_path.exists())

    def test_legacy_payload_includes_allowed_mentions(self) -> None:
        """旧 path の payload にも allowed_mentions: parse [] が必須。"""
        rc, out, _ = self._run(
            ["notify", "--project", "/home/otaku/agentops", "--dry-run"]
        )
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertEqual(payload.get("allowed_mentions"), {"parse": []})

    def test_legacy_content_sanitized_with_mention_in_path(self) -> None:
        """旧 path の content sanitize を E2E で確認する。

        `@everyone` を含むディレクトリ名で git repo を作り、その project を notify
        する。生成された content に mention 文字列がそのまま残らないことを確認する。
        """
        with tempfile.TemporaryDirectory() as proj_root:
            mention_proj = Path(proj_root) / "project-with-@everyone-name"
            mention_proj.mkdir()
            # 最小限の git init で報告対象として有効にする。
            try:
                subprocess.run(
                    ["git", "init", "-q"],
                    cwd=mention_proj,
                    check=True,
                    capture_output=True,
                )
            except (FileNotFoundError, subprocess.CalledProcessError) as exc:
                self.skipTest(f"git init unavailable: {exc}")

            rc, out, _ = self._run(
                ["notify", "--project", str(mention_proj), "--dry-run"]
            )
            self.assertEqual(rc, 0)
            payload = json.loads(out)
            content = payload.get("content", "")
            # path / project name は content に出るが、@everyone リテラルとしては
            # sanitize 後に存在してはならない。
            self.assertNotIn("@everyone", content)
            self.assertEqual(payload.get("allowed_mentions"), {"parse": []})


class CmdNotifySendTests(unittest.TestCase):
    """実送信 (mock) のテスト。env と rate-limit state を tmpdir に閉じる。"""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        env_patch = {
            "DISCORD_WEBHOOK_URL_ANT_TIME": "https://discord.invalid/webhooks/0/dummy",
            "DISCORD_WEBHOOK_URL_DAILLY": "https://discord.invalid/webhooks/1/dummy",
            "XDG_CACHE_HOME": self.tmp.name,
        }
        self._patcher = mock.patch.dict(os.environ, env_patch)
        self._patcher.start()

    def tearDown(self) -> None:
        self._patcher.stop()
        self.tmp.cleanup()

    def _run(self, argv: list[str]) -> tuple[int, str, str]:
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = monitor.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def _ok_response(self, status: int = 204):
        cm = mock.MagicMock()
        cm.__enter__.return_value.status = status
        cm.__enter__.return_value.headers = {}
        cm.__exit__.return_value = False
        return cm

    def test_alert_sends_to_anttime(self) -> None:
        with mock.patch(
            "tools.agentops_monitor.__main__.request.urlopen",
            return_value=self._ok_response(204),
        ) as urlopen:
            rc, _, _ = self._run(["notify", "--kind", "alert", "--message", "ok"])
            self.assertEqual(rc, 0)
            urlopen.assert_called_once()
            req = urlopen.call_args.args[0]
            self.assertEqual(req.full_url, "https://discord.invalid/webhooks/0/dummy")

    def test_rate_limit_skips_after_5_per_minute(self) -> None:
        with mock.patch(
            "tools.agentops_monitor.__main__.request.urlopen",
            return_value=self._ok_response(204),
        ) as urlopen:
            for _ in range(5):
                rc, _, _ = self._run(["notify", "--kind", "alert", "--message", "x"])
                self.assertEqual(rc, 0)
            # 6 件目は skip
            rc, _, err = self._run(["notify", "--kind", "alert", "--message", "x"])
            self.assertEqual(rc, 0)
            self.assertIn("rate-limit", err)
            self.assertIn("skipping", err)
            # urlopen は 5 回しか呼ばれない
            self.assertEqual(urlopen.call_count, 5)

    def test_429_records_retry_after(self) -> None:
        from email.message import Message
        from urllib import error as urllib_error

        msg = Message()
        msg["Retry-After"] = "120"
        err = urllib_error.HTTPError(
            url="https://discord.invalid/webhooks/0/dummy",
            code=429,
            msg="Too Many Requests",
            hdrs=msg,  # type: ignore[arg-type]
            fp=io.BytesIO(b""),
        )
        with mock.patch(
            "tools.agentops_monitor.__main__.request.urlopen",
            side_effect=err,
        ):
            rc, _, stderr = self._run(["notify", "--kind", "alert", "--message", "x"])
            self.assertEqual(rc, 2)
            self.assertIn("HTTP 429", stderr)
        # state file に retry_after_until が書き込まれていること
        state_path = Path(self.tmp.name) / "agentops-watch" / "anttime-rate.json"
        self.assertTrue(state_path.exists())
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertGreater(state.get("retry_after_until", 0), 0)

    def test_subsequent_call_blocked_by_retry_after(self) -> None:
        from email.message import Message
        from urllib import error as urllib_error

        msg = Message()
        msg["Retry-After"] = "120"
        err = urllib_error.HTTPError(
            url="https://discord.invalid/webhooks/0/dummy",
            code=429,
            msg="Too Many Requests",
            hdrs=msg,  # type: ignore[arg-type]
            fp=io.BytesIO(b""),
        )
        # 1 回目: 429 で停止
        with mock.patch(
            "tools.agentops_monitor.__main__.request.urlopen",
            side_effect=err,
        ):
            self._run(["notify", "--kind", "alert", "--message", "x"])
        # 2 回目: Retry-After 内なので skip (送信されない)
        with mock.patch(
            "tools.agentops_monitor.__main__.request.urlopen",
        ) as urlopen2:
            rc, _, stderr = self._run(["notify", "--kind", "alert", "--message", "y"])
            self.assertEqual(rc, 0)
            self.assertIn("Retry-After", stderr)
            urlopen2.assert_not_called()

    def test_5xx_does_not_record_retry_after(self) -> None:
        from email.message import Message
        from urllib import error as urllib_error

        msg = Message()
        err = urllib_error.HTTPError(
            url="https://discord.invalid/webhooks/0/dummy",
            code=503,
            msg="Service Unavailable",
            hdrs=msg,  # type: ignore[arg-type]
            fp=io.BytesIO(b""),
        )
        with mock.patch(
            "tools.agentops_monitor.__main__.request.urlopen",
            side_effect=err,
        ):
            rc, _, stderr = self._run(["notify", "--kind", "alert", "--message", "x"])
            self.assertEqual(rc, 2)
            self.assertIn("HTTP 503", stderr)

    def test_5xx_with_retry_after_header_does_not_record(self) -> None:
        """5xx + Retry-After ヘッダがあっても state に記録しない (記録対象は 429 のみ)。"""
        from email.message import Message
        from urllib import error as urllib_error

        msg = Message()
        msg["Retry-After"] = "30"
        err = urllib_error.HTTPError(
            url="https://discord.invalid/webhooks/0/dummy",
            code=503,
            msg="Service Unavailable",
            hdrs=msg,  # type: ignore[arg-type]
            fp=io.BytesIO(b""),
        )
        with mock.patch(
            "tools.agentops_monitor.__main__.request.urlopen",
            side_effect=err,
        ):
            rc, _, stderr = self._run(["notify", "--kind", "alert", "--message", "x"])
            self.assertEqual(rc, 2)
            self.assertIn("HTTP 503", stderr)
        state_path = Path(self.tmp.name) / "agentops-watch" / "anttime-rate.json"
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            # 5xx では記録しないので 0 (または key なし) のままであるべき。
            self.assertEqual(state.get("retry_after_until", 0), 0)

    def test_bypass_does_not_override_retry_after(self) -> None:
        """`--bypass-rate-limit` は Discord 側 Retry-After block には作用しない。"""
        from email.message import Message
        from urllib import error as urllib_error

        # 1 回目: 429 を受けて Retry-After を保存させる。
        msg = Message()
        msg["Retry-After"] = "120"
        err429 = urllib_error.HTTPError(
            url="https://discord.invalid/webhooks/0/dummy",
            code=429,
            msg="Too Many Requests",
            hdrs=msg,  # type: ignore[arg-type]
            fp=io.BytesIO(b""),
        )
        with mock.patch(
            "tools.agentops_monitor.__main__.request.urlopen",
            side_effect=err429,
        ):
            self._run(["notify", "--kind", "alert", "--message", "x"])

        # 2 回目: --bypass-rate-limit でも Retry-After 中なので skip され、urlopen は呼ばれない。
        # bypass は alert + priority=high のみ許可 (docs/18 §ANT_TIME 頻度上限ガード)。
        with mock.patch(
            "tools.agentops_monitor.__main__.request.urlopen",
        ) as urlopen2:
            rc, _, stderr = self._run(
                [
                    "notify", "--kind", "alert", "--message", "y",
                    "--priority", "high", "--bypass-rate-limit",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertIn("Retry-After", stderr)
            urlopen2.assert_not_called()

    def test_missing_env_exits_2_without_recording_state(self) -> None:
        """Webhook envvar 未設定では exit 2、ANT_TIME state は更新しない。

        Round 2 P1 の回帰テスト。env 未設定での exit 2 が rate-limit skip に隠れて
        exit 0 になる挙動を防ぐ。
        """
        # 親 setUp で env を有効化したので一旦消す。
        with mock.patch.dict(os.environ, {"DISCORD_WEBHOOK_URL_ANT_TIME": ""}):
            for _ in range(7):
                rc, _, stderr = self._run(["notify", "--kind", "alert", "--message", "x"])
                self.assertEqual(rc, 2)
                self.assertIn("DISCORD_WEBHOOK_URL_ANT_TIME is not set", stderr)
        # state file は一切作られない。
        state_path = Path(self.tmp.name) / "agentops-watch" / "anttime-rate.json"
        self.assertFalse(state_path.exists())

    def test_missing_projects_yaml_exits_2(self) -> None:
        """--projects が存在しないパスを指せば silent fallback せず exit 2。

        Round 4 P1 の回帰テスト。docs/18 §DbC 停止条件: --projects YAML 読み込み
        失敗は invocation 停止。
        """
        rc, _, stderr = self._run(
            [
                "notify", "--kind", "daily",
                "--projects", "/tmp/agentops-no-such-projects-2026-04-30.yml",
                "--dry-run",
            ]
        )
        self.assertEqual(rc, 2)
        self.assertIn("--projects file not found", stderr)

    def test_empty_projects_yaml_exits_2(self) -> None:
        """--projects YAML に projects: エントリがなければ exit 2。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False, encoding="utf-8"
        ) as f:
            f.write("# empty projects file\n")
            empty_path = f.name
        try:
            rc, _, stderr = self._run(
                ["notify", "--kind", "weekly", "--projects", empty_path, "--dry-run"]
            )
            self.assertEqual(rc, 2)
            self.assertIn("no 'projects' entries", stderr)
        finally:
            os.unlink(empty_path)

    def test_network_error_exits_2(self) -> None:
        """URLError (DNS / connect timeout) は exit 2 に正規化される。

        Round 3 P1 の回帰テスト。docs/18 §DbC 停止条件: connect timeout は当該
        invocation を停止し DbC 停止条件として扱う。
        """
        from urllib import error as urllib_error

        with mock.patch(
            "tools.agentops_monitor.__main__.request.urlopen",
            side_effect=urllib_error.URLError("Name or service not known"),
        ):
            rc, _, stderr = self._run(["notify", "--kind", "alert", "--message", "x"])
            self.assertEqual(rc, 2)
            self.assertIn("network error", stderr)

    def test_bypass_requires_alert_priority_high(self) -> None:
        """--bypass-rate-limit は alert + priority=high 限定 (docs/18 §ANT_TIME)。"""
        # session-start で bypass はエラー
        rc, _, stderr = self._run(
            [
                "notify", "--kind", "session-start", "--project", "/home/otaku/agentops",
                "--bypass-rate-limit",
            ]
        )
        self.assertEqual(rc, 2)
        self.assertIn("--bypass-rate-limit requires --kind alert --priority high", stderr)
        # alert + priority=low (default) でも bypass はエラー
        rc, _, stderr = self._run(
            ["notify", "--kind", "alert", "--message", "x", "--bypass-rate-limit"]
        )
        self.assertEqual(rc, 2)
        self.assertIn("--bypass-rate-limit requires --kind alert --priority high", stderr)

    def test_bypass_with_alert_priority_high_allowed(self) -> None:
        """alert + priority=high + bypass-rate-limit は窓ガードを抜けて送信される。"""
        with mock.patch(
            "tools.agentops_monitor.__main__.request.urlopen",
            return_value=self._ok_response(204),
        ) as urlopen:
            # まず通常の rate guard が窓を埋め切るまで送信
            for _ in range(5):
                self._run(["notify", "--kind", "alert", "--message", "x"])
            # 6 回目: bypass で窓を抜ける (alert + priority=high)
            rc, _, _ = self._run(
                [
                    "notify", "--kind", "alert", "--message", "high-prio",
                    "--priority", "high", "--bypass-rate-limit",
                ]
            )
            self.assertEqual(rc, 0)
            # 6 回呼ばれている (5 通常 + 1 bypass)
            self.assertEqual(urlopen.call_count, 6)

    def test_session_title_sanitized_with_mention(self) -> None:
        """session-start title の project basename も sanitize される。"""
        with tempfile.TemporaryDirectory() as proj_root:
            # @everyone を含むディレクトリ名 (mention の悪用シナリオ)
            mention_proj = Path(proj_root) / "@everyone-test"
            mention_proj.mkdir()
            with mock.patch(
                "tools.agentops_monitor.__main__.request.urlopen",
                return_value=self._ok_response(204),
            ) as urlopen:
                rc, _, _ = self._run(
                    ["notify", "--kind", "session-start", "--project", str(mention_proj)]
                )
                self.assertEqual(rc, 0)
                req = urlopen.call_args.args[0]
                body = json.loads(req.data.decode("utf-8"))
                title = body["embeds"][0]["title"]
                self.assertNotIn("@everyone", title)


if __name__ == "__main__":
    unittest.main()
