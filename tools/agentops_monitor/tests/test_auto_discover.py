"""auto-discover (4 root + ~/dev/*) と --auto-discover flag の挙動を検証する。

`HOME` を tempdir に patch することで、実ホームを汚染せずに 4 root を再現する。
"""
from __future__ import annotations

import argparse
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from tools.agentops_monitor import __main__ as monitor


def _make_args(**overrides: object) -> argparse.Namespace:
    """`load_projects` が触るフィールドを最小限揃えた Namespace を作る。"""
    base: dict[str, object] = {
        "projects": None,
        "project": None,
        "auto_discover": False,
        "freshness": None,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


class _HomePatchTestCase(unittest.TestCase):
    """`HOME` を tempdir に向け、4 root の配下を自由に組める基底クラス。"""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)
        # Path.home() は HOME envvar を参照する。
        self._env_patch = mock.patch.dict(os.environ, {"HOME": str(self.home)})
        self._env_patch.start()
        # _DISCOVERY_ROOTS / _DEV_GLOB_ROOT は import 時に評価済みなので、
        # 実値を tmp 配下のものに差し替える。
        self._roots_patch = mock.patch.object(
            monitor,
            "_DISCOVERY_ROOTS",
            (
                self.home / ".claude",
                self.home / ".codex",
                self.home / "agentops",
            ),
        )
        self._roots_patch.start()
        self._dev_patch = mock.patch.object(monitor, "_DEV_GLOB_ROOT", self.home / "dev")
        self._dev_patch.start()

    def tearDown(self) -> None:
        self._dev_patch.stop()
        self._roots_patch.stop()
        self._env_patch.stop()
        self._tmp.cleanup()

    def _make_agentops(self, base: Path) -> Path:
        """`base/.agentops/` を作って base を返す。"""
        (base / ".agentops").mkdir(parents=True, exist_ok=True)
        return base


class TestDiscoverProjects(_HomePatchTestCase):
    def test_finds_agentops_dirs_in_all_4_roots(self) -> None:
        # ~/.claude, ~/.codex, ~/agentops, ~/dev/foo にそれぞれ .agentops/ を作る。
        self._make_agentops(self.home / ".claude")
        self._make_agentops(self.home / ".codex")
        self._make_agentops(self.home / "agentops")
        self._make_agentops(self.home / "dev" / "foo")

        results = monitor.discover_projects()
        paths = [item["path"] for item in results]
        self.assertEqual(len(results), 4)
        # 結果は path 文字列でソートされた安定順序。
        self.assertEqual(paths, sorted(paths))
        # name は basename になる。
        names = {item["name"] for item in results}
        self.assertEqual(names, {".claude", ".codex", "agentops", "foo"})

    def test_empty_agentops_dir_still_matches(self) -> None:
        # 空の .agentops/ も対象 (ユーザー方針: 対象を絞らず必ず scan)。
        target = self._make_agentops(self.home / ".claude")
        # 内部にはなにも置かない。
        self.assertEqual(list((target / ".agentops").iterdir()), [])
        results = monitor.discover_projects()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], ".claude")

    def test_skips_paths_without_agentops(self) -> None:
        # ~/dev/bar には .agentops/ が無い → 候補から除外。
        (self.home / "dev" / "bar").mkdir(parents=True)
        self._make_agentops(self.home / "dev" / "foo")

        results = monitor.discover_projects()
        names = [item["name"] for item in results]
        self.assertEqual(names, ["foo"])

    def test_handles_broken_symlinks(self) -> None:
        # ~/dev に broken symlink を含むケースで OSError で落ちないこと。
        self.home.joinpath("dev").mkdir(parents=True)
        broken = self.home / "dev" / "broken-link"
        broken.symlink_to(self.home / "does-not-exist")
        # 正常な project も 1 つ作る。
        self._make_agentops(self.home / "dev" / "foo")

        results = monitor.discover_projects()
        names = [item["name"] for item in results]
        # broken symlink は skip され、foo だけ拾われる。
        self.assertIn("foo", names)
        self.assertNotIn("broken-link", names)

    def test_dedupe(self) -> None:
        # symlink で同一実体を指す 2 経路があっても dedupe される。
        real = self._make_agentops(self.home / "agentops")
        # ~/.claude を ~/agentops への symlink にする。
        link = self.home / ".claude"
        if link.exists():
            link.rmdir()
        link.symlink_to(real)

        results = monitor.discover_projects()
        # 同じ実体を指すので 1 件のみ。
        self.assertEqual(len(results), 1)

    def test_zero_match_returns_empty_list(self) -> None:
        # 4 root のいずれにも .agentops/ が無いケース。
        # root ディレクトリ自体は存在するが .agentops/ を作らない。
        (self.home / ".claude").mkdir()
        (self.home / "dev").mkdir()
        results = monitor.discover_projects()
        self.assertEqual(results, [])

    def test_dev_glob_max_depth_1(self) -> None:
        # ~/dev/foo/bar/.agentops は対象外 (depth 1 のみ)。
        nested = self.home / "dev" / "foo" / "bar"
        nested.mkdir(parents=True)
        (nested / ".agentops").mkdir()
        # ~/dev/foo 自体には .agentops/ 無し。
        results = monitor.discover_projects()
        self.assertEqual(results, [])

    def test_iter_discovery_candidates_yields_existing_roots_only(self) -> None:
        # ~/.claude のみ存在 / ~/dev に foo, bar (dir) と baz (file) がある場合の絞り込み。
        (self.home / ".claude").mkdir()
        (self.home / "dev" / "foo").mkdir(parents=True)
        (self.home / "dev" / "bar").mkdir()
        (self.home / "dev" / "baz").write_text("not a dir", encoding="utf-8")

        candidates = list(monitor.iter_discovery_candidates())
        names = sorted(c.name for c in candidates)
        # ~/.codex / ~/agentops は不在 → yield されない。
        # ~/dev/baz は file → yield されない。
        self.assertEqual(names, [".claude", "bar", "foo"])

    def test_is_agentops_project_true_only_for_directory(self) -> None:
        target = self.home / "claude-style"
        target.mkdir()
        self.assertFalse(monitor.is_agentops_project(target))
        # file ではなく dir を作る。
        (target / ".agentops").mkdir()
        self.assertTrue(monitor.is_agentops_project(target))

    def test_is_agentops_project_false_for_file(self) -> None:
        # `.agentops` が file の場合 (誤った設置) は False。
        target = self.home / "claude-style"
        target.mkdir()
        (target / ".agentops").write_text("oops", encoding="utf-8")
        self.assertFalse(monitor.is_agentops_project(target))


class TestLoadProjectsWithAutoDiscover(_HomePatchTestCase):
    def test_projects_and_auto_discover_mutually_exclusive(self) -> None:
        # `--projects` と `--auto-discover` 同時指定 → ValueError。
        args = _make_args(projects="config/projects.yml", auto_discover=True)
        with self.assertRaises(ValueError) as ctx:
            monitor.load_projects(args)
        self.assertIn("排他", str(ctx.exception))

    def test_auto_discover_returns_discover_projects_result(self) -> None:
        self._make_agentops(self.home / ".claude")
        self._make_agentops(self.home / "dev" / "foo")
        args = _make_args(auto_discover=True)

        result = monitor.load_projects(args)
        names = sorted(item["name"] for item in result)
        self.assertEqual(names, [".claude", "foo"])

    def test_auto_discover_zero_match_returns_empty_list(self) -> None:
        # 0 件でも例外を上げず空 list を返す (空 embed 1 通送信を許す)。
        args = _make_args(auto_discover=True)
        result = monitor.load_projects(args)
        self.assertEqual(result, [])

    def test_project_fallback_when_neither_projects_nor_auto_discover(self) -> None:
        # `--projects` も `--auto-discover` も無く、`--project` 指定 → 単体 list を返す。
        args = _make_args(project=str(self.home))
        result = monitor.load_projects(args)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["path"], str(self.home))

    def test_cwd_fallback_when_no_arg_provided(self) -> None:
        # 何も指定が無ければ cwd (".") にフォールバック。
        args = _make_args()
        result = monitor.load_projects(args)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["path"], ".")

    def test_projects_explicit_still_works(self) -> None:
        # `--projects` 単独経路の regression 確認。
        yaml_path = self.home / "projects.yml"
        yaml_path.write_text(
            "projects:\n"
            "  - name: dummy\n"
            "    path: .\n",
            encoding="utf-8",
        )
        args = _make_args(projects=str(yaml_path))
        result = monitor.load_projects(args)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "dummy")


class TestNotifyCmdWithAutoDiscover(_HomePatchTestCase):
    """`agentops-watch notify --auto-discover --dry-run` の E2E 動作確認。

    secret 値 (webhook URL) を env から外し、dry-run のみで stdout payload を検証する。
    """

    def setUp(self) -> None:
        super().setUp()
        # env を最小限に: secret webhook を空に、cache は tmpdir に。
        self._cache_dir = tempfile.TemporaryDirectory()
        self._env_patch2 = mock.patch.dict(
            os.environ,
            {
                "DISCORD_WEBHOOK_URL_DAILLY": "",
                "DISCORD_WEBHOOK_URL_WEEKLY": "",
                "DISCORD_WEBHOOK_URL_MONTHLY": "",
                "DISCORD_WEBHOOK_URL_ANT_TIME": "",
                "AGENTOPS_DISCORD_WEBHOOK_URL": "",
                "XDG_CACHE_HOME": self._cache_dir.name,
            },
            clear=False,
        )
        self._env_patch2.start()

    def tearDown(self) -> None:
        self._env_patch2.stop()
        self._cache_dir.cleanup()
        super().tearDown()

    def _run(self, argv: list[str]) -> tuple[int, str, str]:
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = monitor.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_dry_run_with_auto_discover_shows_4_root_projects(self) -> None:
        # 4 root に .agentops/ を作り、各 project に signal を持たせる
        # (open tasks 1 件) ことで signal フィルタを通過させ、4 project すべて
        # description (markdown ## ヘッダー) に出ることを確認する。
        for sub in (".claude", ".codex", "agentops", "dev/foo"):
            base = self.home / sub
            self._make_agentops(base)
            (base / ".agentops" / "tasks").mkdir(exist_ok=True)
            (base / ".agentops" / "tasks" / "01.md").write_text("# task\n", encoding="utf-8")

        rc, out, _ = self._run(
            ["notify", "--kind", "daily", "--auto-discover", "--dry-run"]
        )
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertEqual(len(payload["embeds"]), 1)
        description = payload["embeds"][0]["description"]
        # 4 project すべて ## ヘッダーで出る
        self.assertEqual(description.count("\n## "), 3)  # 先頭 ## + 改行つき ##×3
        self.assertTrue(description.startswith("## "))
        for expected in (".claude", ".codex", "agentops", "foo"):
            self.assertIn(expected, description)

    def test_auto_discover_collects_agentops_state_in_non_git_dirs(self) -> None:
        # 非 git の ~/.claude/.agentops/tasks/01.md があれば open tasks: 1 が
        # description 内に出る (Codex P1 指摘の回帰テスト)。
        claude_root = self.home / ".claude"
        self._make_agentops(claude_root)
        (claude_root / ".agentops" / "tasks").mkdir(exist_ok=True)
        (claude_root / ".agentops" / "handoffs").mkdir(exist_ok=True)
        (claude_root / ".agentops" / "tasks" / "01-some-task.md").write_text(
            "# task\n", encoding="utf-8"
        )
        (claude_root / ".agentops" / "handoffs" / "h1.md").write_text(
            "# handoff\n", encoding="utf-8"
        )

        rc, out, _ = self._run(
            ["notify", "--kind", "daily", "--auto-discover", "--dry-run"]
        )
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        description = payload["embeds"][0]["description"]
        # description 内に .claude project section が出る
        self.assertIn(".claude", description)
        # 集計値 + 絵文字 prefix も含まれる
        self.assertIn("open tasks: **1**", description)
        self.assertIn("handoffs: **1**", description)
        self.assertIn("📋", description)

    def test_dry_run_with_auto_discover_zero_match_emits_empty_embed(self) -> None:
        # 0 件マッチでも payload は生成される。description に "no projects discovered"
        # 行のみが出て、fields は空。title は kind 別 emoji 付き daily digest。
        rc, out, _ = self._run(
            ["notify", "--kind", "daily", "--auto-discover", "--dry-run"]
        )
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertEqual(len(payload["embeds"]), 1)
        embed = payload["embeds"][0]
        self.assertEqual(embed["fields"], [])
        self.assertIn("no projects discovered", embed["description"])
        self.assertIn("daily digest", embed["title"])

    def test_dry_run_with_projects_and_auto_discover_exits_2(self) -> None:
        # 排他指定は exit 2 + 排他エラーメッセージ。
        yaml_path = self.home / "projects.yml"
        yaml_path.write_text("projects:\n  - name: x\n    path: .\n", encoding="utf-8")
        rc, _, err = self._run(
            [
                "notify", "--kind", "daily",
                "--auto-discover",
                "--projects", str(yaml_path),
                "--dry-run",
            ]
        )
        self.assertEqual(rc, 2)
        self.assertIn("排他", err)


if __name__ == "__main__":
    unittest.main()
