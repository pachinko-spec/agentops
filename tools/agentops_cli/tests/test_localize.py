"""agentops localize の痕跡検出 / 戦略判定 / report 出力を検証する。"""
from __future__ import annotations

import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tools.agentops_cli import __main__ as cli


def _git_init(path: Path) -> None:
    """tempdir に最小限の git init を施す (鮮度判定用)。"""
    subprocess.run(
        ["git", "init", "-q"],
        cwd=path, check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.invalid"],
        cwd=path, check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "test"],
        cwd=path, check=True, capture_output=True,
    )


def _git_commit_dummy(path: Path) -> None:
    """git activity を作るためダミー commit を 1 件入れる。"""
    (path / "README.md").write_text("test\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=path, check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init", "-q"],
        cwd=path, check=True, capture_output=True,
        env={**os.environ, "GIT_AUTHOR_DATE": "2026-04-29T12:00:00+09:00", "GIT_COMMITTER_DATE": "2026-04-29T12:00:00+09:00"},
    )


class LocalizeTraceScanTests(unittest.TestCase):
    """痕跡検出 (depth-2、各カテゴリ、除外対象)。"""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_no_traces_returns_empty(self) -> None:
        """空 dir では痕跡が 0 件。"""
        traces = cli._localize_scan_traces(self.proj)
        self.assertEqual(traces, [])

    def test_claude_md_detected(self) -> None:
        (self.proj / "CLAUDE.md").write_text("# test\n", encoding="utf-8")
        traces = cli._localize_scan_traces(self.proj)
        names = [t["name"] for t in traces]
        self.assertIn("CLAUDE.md", names)

    def test_claude_dir_detected_with_children(self) -> None:
        d = self.proj / ".claude"
        d.mkdir()
        (d / "settings.json").write_text("{}", encoding="utf-8")
        (d / "agents").mkdir()
        traces = cli._localize_scan_traces(self.proj)
        cl = next(t for t in traces if t["name"] == ".claude")
        self.assertEqual(cl["kind"], "dir")
        self.assertIn("settings.json", cl["children"])
        self.assertIn("agents", cl["children"])

    def test_codex_zero_byte_marker(self) -> None:
        """0-byte の .codex は marker フラグが立つ。"""
        (self.proj / ".codex").touch()
        traces = cli._localize_scan_traces(self.proj)
        codex = next(t for t in traces if t["name"] == ".codex")
        self.assertEqual(codex["kind"], "file")
        self.assertEqual(codex["size_bytes"], 0)
        self.assertTrue(codex.get("zero_byte_marker"))

    def test_gemini_md_and_agent_dir(self) -> None:
        (self.proj / "GEMINI.md").write_text("# gemini\n", encoding="utf-8")
        (self.proj / ".agent").mkdir()
        (self.proj / ".agent" / "memory").mkdir()
        traces = cli._localize_scan_traces(self.proj)
        cats = {t["name"]: t["category"] for t in traces}
        self.assertEqual(cats["GEMINI.md"], "gemini")
        self.assertEqual(cats[".agent"], "gemini")

    def test_excluded_dirs_not_detected(self) -> None:
        """`.git/` `.vscode/` `node_modules/` などは検出されない。"""
        (self.proj / ".git").mkdir()
        (self.proj / ".vscode").mkdir()
        (self.proj / "node_modules").mkdir()
        (self.proj / ".cache").mkdir()
        traces = cli._localize_scan_traces(self.proj)
        names = [t["name"] for t in traces]
        for excluded in (".git", ".vscode", "node_modules", ".cache"):
            self.assertNotIn(excluded, names)

    def test_subdir_claude_md_detected_at_depth_2(self) -> None:
        """subproject の `engine/CLAUDE.md` も depth-2 で検出される。"""
        sub = self.proj / "engine"
        sub.mkdir()
        (sub / "CLAUDE.md").write_text("# sub\n", encoding="utf-8")
        traces = cli._localize_scan_traces(self.proj)
        paths = [t["path"] for t in traces]
        self.assertIn("engine/CLAUDE.md", paths)

    def test_aider_files_detected(self) -> None:
        (self.proj / ".aider.conf.yml").write_text("model: gpt\n", encoding="utf-8")
        (self.proj / ".aider.chat.history.md").write_text("history\n", encoding="utf-8")
        traces = cli._localize_scan_traces(self.proj)
        names = [t["name"] for t in traces]
        self.assertIn(".aider.conf.yml", names)
        self.assertIn(".aider.chat.history.md", names)
        for t in traces:
            if t["name"].startswith(".aider"):
                self.assertEqual(t["category"], "other")

    def test_cursorrules_low_conflict(self) -> None:
        """`.cursorrules` のみは low conflict として扱われる。"""
        (self.proj / ".cursorrules").write_text("rules\n", encoding="utf-8")
        traces = cli._localize_scan_traces(self.proj)
        level, _ = cli._localize_assess_conflict(traces)
        self.assertEqual(level, "低")


class LocalizeStackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_node_with_nuxt(self) -> None:
        (self.proj / "package.json").write_text(
            json.dumps({"dependencies": {"nuxt": "^3.0"}}), encoding="utf-8"
        )
        stack = cli._localize_detect_stack(self.proj)
        self.assertEqual(stack["detected"], ["Node"])
        self.assertEqual(stack["details"].get("framework"), "nuxt")

    def test_go(self) -> None:
        (self.proj / "go.mod").write_text("module x\n", encoding="utf-8")
        stack = cli._localize_detect_stack(self.proj)
        self.assertEqual(stack["detected"], ["Go"])

    def test_no_stack(self) -> None:
        stack = cli._localize_detect_stack(self.proj)
        self.assertEqual(stack["detected"], [])

    def test_python_via_pyproject(self) -> None:
        (self.proj / "pyproject.toml").write_text("[build-system]\n", encoding="utf-8")
        stack = cli._localize_detect_stack(self.proj)
        self.assertEqual(stack["detected"], ["Python"])


class LocalizeStrategyTests(unittest.TestCase):
    def test_greenfield_no_traces(self) -> None:
        strategy, conf, _ = cli._localize_classify_strategy([], {"is_git_repo": False})
        self.assertEqual(strategy, "greenfield")
        self.assertEqual(conf, "high")

    def test_greenfield_only_minimal_agents_md(self) -> None:
        traces = [
            {"category": "codex", "name": "AGENTS.md", "depth": 1, "kind": "file",
             "size_bytes": 80, "mtime_days": 0, "freshness": "≤30d"}
        ]
        strategy, _, _ = cli._localize_classify_strategy(traces, {"commits_last_30d": 1})
        self.assertEqual(strategy, "greenfield")

    def test_inventory_rebuild_recent_active_high_conflict(self) -> None:
        traces = [
            {"category": "claude", "name": "CLAUDE.md", "depth": 1, "kind": "file",
             "size_bytes": 5000, "mtime_days": 5, "freshness": "≤30d"},
            {"category": "claude", "name": ".claude", "depth": 1, "kind": "dir",
             "size_bytes": None, "mtime_days": 5, "freshness": "≤30d",
             "children": ["plans", "agents", "hooks", "settings.json"]},
        ]
        strategy, _, reasoning = cli._localize_classify_strategy(
            traces, {"commits_last_30d": 10}
        )
        self.assertEqual(strategy, "inventory-rebuild")
        self.assertTrue(any(".claude/plans/" in r for r in reasoning))

    def test_freeze_old_idle(self) -> None:
        traces = [
            {"category": "claude", "name": "CLAUDE.md", "depth": 1, "kind": "file",
             "size_bytes": 5000, "mtime_days": 250, "freshness": "180+d"},
        ]
        strategy, _, _ = cli._localize_classify_strategy(
            traces, {"commits_last_30d": 0}
        )
        self.assertEqual(strategy, "freeze")

    def test_coexistence_low_conflict_short(self) -> None:
        traces = [
            {"category": "other", "name": ".cursorrules", "depth": 1, "kind": "file",
             "size_bytes": 100, "mtime_days": 5, "freshness": "≤30d"}
        ]
        strategy, _, _ = cli._localize_classify_strategy(
            traces, {"commits_last_30d": 5}
        )
        self.assertEqual(strategy, "coexistence")

    def test_forced_strategy_overrides(self) -> None:
        traces = [
            {"category": "claude", "name": "CLAUDE.md", "depth": 1, "kind": "file",
             "size_bytes": 5000, "mtime_days": 5, "freshness": "≤30d"}
        ]
        strategy, _, reasoning = cli._localize_classify_strategy(
            traces, {"commits_last_30d": 10}, forced="freeze"
        )
        self.assertEqual(strategy, "freeze")
        self.assertIn("--strategy freeze で強制指定", reasoning[0])

    def test_needs_user_confirmation_when_uncertain(self) -> None:
        """大量痕跡 + 低 conflict のような曖昧ケースは escalate。"""
        traces = [
            {"category": "claude", "name": "CLAUDE.md", "depth": 1, "kind": "file",
             "size_bytes": 1000, "mtime_days": 5, "freshness": "≤30d"},
            {"category": "codex", "name": "AGENTS.md", "depth": 1, "kind": "file",
             "size_bytes": 1000, "mtime_days": 5, "freshness": "≤30d"},
            {"category": "claude", "name": ".claude", "depth": 1, "kind": "dir",
             "size_bytes": None, "mtime_days": 5, "freshness": "≤30d", "children": ["x"]},
            {"category": "codex", "name": ".codex", "depth": 1, "kind": "dir",
             "size_bytes": None, "mtime_days": 5, "freshness": "≤30d", "children": ["x"]},
            {"category": "personal", "name": ".agentops", "depth": 1, "kind": "dir",
             "size_bytes": None, "mtime_days": 5, "freshness": "≤30d", "children": ["plans"]},
        ]
        strategy, _, _ = cli._localize_classify_strategy(
            traces, {"commits_last_30d": 50}
        )
        self.assertEqual(strategy, "needs-user-confirmation")


class LocalizeFreshnessBucketTests(unittest.TestCase):
    def test_bucket_boundaries(self) -> None:
        self.assertEqual(cli._localize_freshness_bucket(0), "≤30d")
        self.assertEqual(cli._localize_freshness_bucket(30), "≤30d")
        self.assertEqual(cli._localize_freshness_bucket(31), "31-180d")
        self.assertEqual(cli._localize_freshness_bucket(180), "31-180d")
        self.assertEqual(cli._localize_freshness_bucket(181), "180+d")
        self.assertEqual(cli._localize_freshness_bucket(None), "unknown")


class LocalizeCmdTests(unittest.TestCase):
    """end-to-end (cmd_localize) を tempdir + tempdir runs-root で検証。"""

    def setUp(self) -> None:
        self.tmp_proj = tempfile.TemporaryDirectory()
        self.tmp_runs = tempfile.TemporaryDirectory()
        self.proj = Path(self.tmp_proj.name)
        self.runs_root = Path(self.tmp_runs.name)

    def tearDown(self) -> None:
        self.tmp_proj.cleanup()
        self.tmp_runs.cleanup()

    def _run(self, *extra: str) -> tuple[int, str, str]:
        out = io.StringIO()
        err = io.StringIO()
        argv = [
            "localize",
            "--project", str(self.proj),
            "--runs-root", str(self.runs_root),
            *extra,
        ]
        with redirect_stdout(out), redirect_stderr(err):
            rc = cli.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_dry_run_writes_inventory_md(self) -> None:
        (self.proj / "CLAUDE.md").write_text("test\n", encoding="utf-8")
        rc, out, _ = self._run("--dry-run")
        self.assertEqual(rc, 0)
        self.assertIn("# project-localize report", out)
        # run log file が tempdir runs-root 配下に作られる
        runs = list(self.runs_root.iterdir())
        self.assertEqual(len(runs), 1)
        self.assertTrue((runs[0] / "inventory.md").exists())

    def test_does_not_write_to_project(self) -> None:
        """dry-run は project 配下に何も書き込まない。"""
        (self.proj / "CLAUDE.md").write_text("test\n", encoding="utf-8")
        files_before = sorted(self.proj.iterdir())
        self._run("--dry-run")
        files_after = sorted(self.proj.iterdir())
        self.assertEqual(files_before, files_after)

    def test_explicit_run_id(self) -> None:
        (self.proj / "CLAUDE.md").write_text("test\n", encoding="utf-8")
        rc, _, _ = self._run("--run-id", "my-test-run")
        self.assertEqual(rc, 0)
        self.assertTrue((self.runs_root / "my-test-run" / "inventory.md").exists())

    def test_unlisted_dot_dir_triggers_user_confirmation(self) -> None:
        """`.unknownai/` のような未列挙 dot-dir → needs-user-confirmation (P1-1 fix)."""
        (self.proj / ".unknownai").mkdir()
        (self.proj / ".unknownai" / "config.yaml").write_text("x", encoding="utf-8")
        rc, out, _ = self._run("--dry-run")
        self.assertEqual(rc, 0)
        self.assertIn("needs-user-confirmation", out)
        self.assertIn(".unknownai", out)
        self.assertIn("Unlisted traces", out)

    def test_unlisted_uppercase_md_triggers_escalate(self) -> None:
        """`MYAGENT.md` のような未列挙 UPPER.md → needs-user-confirmation (P1-1 fix)."""
        (self.proj / "MYAGENT.md").write_text("# x\n", encoding="utf-8")
        rc, out, _ = self._run("--dry-run")
        self.assertEqual(rc, 0)
        self.assertIn("needs-user-confirmation", out)
        self.assertIn("MYAGENT.md", out)

    def test_unlisted_vendor_rules_triggers_escalate(self) -> None:
        """`.unknownairules` のような未列挙 vendor-rules → escalate (P1-1 fix)."""
        (self.proj / ".unknownairules").write_text("rules\n", encoding="utf-8")
        rc, out, _ = self._run("--dry-run")
        self.assertEqual(rc, 0)
        self.assertIn("needs-user-confirmation", out)
        self.assertIn(".unknownairules", out)

    def test_excluded_tooling_dirs_not_unlisted(self) -> None:
        """`.husky/` `.devcontainer/` 等の一般 tooling は unlisted にならない。"""
        (self.proj / ".husky").mkdir()
        (self.proj / ".devcontainer").mkdir()
        rc, out, _ = self._run("--dry-run")
        self.assertEqual(rc, 0)
        # tooling が unlisted セクションに含まれない
        self.assertNotIn("`.husky`", out)
        self.assertNotIn("`.devcontainer`", out)

    def test_known_traces_not_in_unlisted(self) -> None:
        """既知 AI 痕跡 (CLAUDE.md / .claude / .ai 等) は unlisted に重複しない。"""
        (self.proj / "CLAUDE.md").write_text("test\n", encoding="utf-8")
        (self.proj / ".claude").mkdir()
        rc, out, _ = self._run("--dry-run")
        self.assertEqual(rc, 0)
        # CLAUDE.md は Inventory セクションに 1 度だけ出る (Unlisted には出ない)
        unlisted_section = out.split("## Unlisted traces")[1] if "## Unlisted traces" in out else ""
        self.assertNotIn("CLAUDE.md", unlisted_section)
        self.assertNotIn("`.claude`", unlisted_section)

    def test_high_conflict_when_both_agentops_and_claude_plans(self) -> None:
        """`.claude/plans/` 既存 + `.agentops/` 既存 → 競合度 高 (P1-2 fix)."""
        cl = self.proj / ".claude"
        cl.mkdir()
        (cl / "plans").mkdir()
        ag = self.proj / ".agentops"
        ag.mkdir()
        (ag / "plans").mkdir()
        rc, out, _ = self._run("--dry-run")
        self.assertEqual(rc, 0)
        self.assertIn("conflict level: **高**", out)

    def test_readme_md_not_flagged_as_unlisted(self) -> None:
        """`README.md` は UPPER.md だが標準 project docs なので escalate しない (Round 2 P1)。"""
        (self.proj / "README.md").write_text("# project\n", encoding="utf-8")
        rc, out, _ = self._run("--dry-run")
        self.assertEqual(rc, 0)
        # greenfield (no AI traces, no unlisted) になることを期待
        self.assertNotIn("needs-user-confirmation", out)
        # README.md は Unlisted セクションに出ない
        unlisted_section = out.split("## Unlisted traces")[1] if "## Unlisted traces" in out else ""
        self.assertNotIn("README.md", unlisted_section)

    def test_changelog_md_not_flagged_as_unlisted(self) -> None:
        (self.proj / "CHANGELOG.md").write_text("# changelog\n", encoding="utf-8")
        rc, out, _ = self._run("--dry-run")
        self.assertEqual(rc, 0)
        self.assertNotIn("needs-user-confirmation", out)

    def test_contributing_and_license_md_not_flagged(self) -> None:
        (self.proj / "CONTRIBUTING.md").write_text("# contributing\n", encoding="utf-8")
        (self.proj / "LICENSE.md").write_text("# license\n", encoding="utf-8")
        (self.proj / "CODE_OF_CONDUCT.md").write_text("# coc\n", encoding="utf-8")
        rc, out, _ = self._run("--dry-run")
        self.assertEqual(rc, 0)
        self.assertNotIn("needs-user-confirmation", out)

    def test_high_conflict_when_both_agentops_and_ai_full_structure(self) -> None:
        """`.ai/` フル構造 + `.agentops/` 既存 → 競合度 高 (P1-2 fix)."""
        ai = self.proj / ".ai"
        ai.mkdir()
        for sub in ("contracts", "decisions", "tasks"):
            (ai / sub).mkdir()
        ag = self.proj / ".agentops"
        ag.mkdir()
        rc, out, _ = self._run("--dry-run")
        self.assertEqual(rc, 0)
        self.assertIn("conflict level: **高**", out)

    def test_missing_project_errors(self) -> None:
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = cli.main(
                [
                    "localize",
                    "--project", str(self.proj / "no-such-subdir"),
                    "--runs-root", str(self.runs_root),
                ]
            )
        self.assertNotEqual(rc, 0)
        self.assertIn("does not exist", err.getvalue())


if __name__ == "__main__":
    unittest.main()
