from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import shlex
import sys
import tempfile
import unittest

from tools.agentops_cli import __main__ as cli


def make_args(**overrides: object) -> argparse.Namespace:
    values = {
        "to": "codex",
        "role": "review role",
        "model": "model with space",
        "effort": "xhigh",
        "input": None,
        "message": "Return exactly: OK",
        "project": ".",
        "run_id": "safe-run",
        "dry_run": True,
        "command_template": "codex exec {model_arg} -c model_reasoning_effort={effort} -",
        "timeout": 0,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def run_cli(argv: list[str]) -> int:
    """CLI の標準出力をテストログへ流さず main() を実行する。"""
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        return cli.main(argv)


class ExpandCommandTests(unittest.TestCase):
    def test_expand_command_quotes_template_values_as_single_argv_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            args = make_args(role="role with space", model="model with space")

            command = cli.expand_command(
                "runner --role {role} --effort {effort} {model_arg} --request {request_file}",
                args,
                base / "request file.md",
                base / "run dir",
            )

        self.assertEqual(
            command,
            [
                "runner",
                "--role",
                "role with space",
                "--effort",
                "xhigh",
                "--model",
                "model with space",
                "--request",
                str(base / "request file.md"),
            ],
        )

    def test_expand_command_rejects_unknown_template_variable(self) -> None:
        args = make_args()
        with self.assertRaisesRegex(cli.CommandTemplateError, "unknown command template variable"):
            cli.expand_command("runner {unknown}", args, Path("request.md"), Path("run"))


class DelegateDryRunTests(unittest.TestCase):
    def test_delegate_dry_run_writes_status_and_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".agentops" / "runs").mkdir(parents=True)
            rc = run_cli(
                [
                    "delegate",
                    "--to",
                    "codex",
                    "--role",
                    "smoke",
                    "--effort",
                    "xhigh",
                    "--message",
                    "Return exactly: OK",
                    "--project",
                    str(project),
                    "--run-id",
                    "Dry Run/Smoke",
                    "--dry-run",
                    "--command-template",
                    "codex exec {model_arg} -c model_reasoning_effort={effort} -",
                ]
            )

            self.assertEqual(rc, 0)
            run_dir = project / ".agentops" / "runs" / "dry-run-smoke"
            status = json.loads((run_dir / "status.json").read_text(encoding="utf-8"))
            self.assertEqual(status["state"], "dry_run")
            self.assertEqual(status["run_id"], "dry-run-smoke")
            self.assertEqual(status["command"], ["codex", "exec", "-c", "model_reasoning_effort=xhigh", "-"])
            self.assertIn("Return exactly: OK", (run_dir / "request.md").read_text(encoding="utf-8"))

    def test_run_id_path_traversal_is_sanitized_inside_runs_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".agentops" / "runs").mkdir(parents=True)
            rc = run_cli(
                [
                    "delegate",
                    "--to",
                    "codex",
                    "--role",
                    "smoke",
                    "--effort",
                    "high",
                    "--message",
                    "OK",
                    "--project",
                    str(project),
                    "--run-id",
                    "../outside",
                    "--dry-run",
                    "--command-template",
                    "runner {effort}",
                ]
            )

            self.assertEqual(rc, 0)
            self.assertTrue((project / ".agentops" / "runs" / "outside" / "status.json").exists())
            self.assertFalse((project / ".agentops" / "outside").exists())

    def test_explicit_run_id_does_not_overwrite_existing_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            existing = project / ".agentops" / "runs" / "existing"
            existing.mkdir(parents=True)
            (existing / "status.json").write_text('{"state": "old"}\n', encoding="utf-8")

            rc = run_cli(
                [
                    "delegate",
                    "--to",
                    "codex",
                    "--role",
                    "smoke",
                    "--effort",
                    "high",
                    "--message",
                    "OK",
                    "--project",
                    str(project),
                    "--run-id",
                    "existing",
                    "--dry-run",
                    "--command-template",
                    "runner {effort}",
                ]
            )

            self.assertEqual(rc, 2)
            status = json.loads((existing / "status.json").read_text(encoding="utf-8"))
            self.assertEqual(status["state"], "old")

    def test_input_path_must_stay_inside_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            outside = Path(tmp) / "outside.txt"
            outside.write_text("outside local data", encoding="utf-8")

            rc = run_cli(
                [
                    "delegate",
                    "--to",
                    "codex",
                    "--role",
                    "smoke",
                    "--effort",
                    "high",
                    "--input",
                    str(outside),
                    "--project",
                    str(project),
                    "--run-id",
                    "outside-input",
                    "--dry-run",
                    "--command-template",
                    "runner {effort}",
                ]
            )

            self.assertEqual(rc, 2)
            self.assertFalse((project / ".agentops" / "runs" / "outside-input").exists())

    def test_invalid_effort_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    cli.main(
                        [
                            "delegate",
                            "--to",
                            "codex",
                            "--role",
                            "smoke",
                            "--effort",
                            "xhigh --extra",
                            "--message",
                            "OK",
                            "--project",
                            str(project),
                            "--dry-run",
                        ]
                    )

            self.assertNotEqual(raised.exception.code, 0)

    def test_missing_external_command_marks_run_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".agentops" / "runs").mkdir(parents=True)

            rc = run_cli(
                [
                    "delegate",
                    "--to",
                    "codex",
                    "--role",
                    "smoke",
                    "--effort",
                    "high",
                    "--message",
                    "OK",
                    "--project",
                    str(project),
                    "--run-id",
                    "missing-command",
                    "--command-template",
                    "agentops-cli-missing-command-for-test",
                ]
            )

            self.assertEqual(rc, 127)
            status_file = project / ".agentops" / "runs" / "missing-command" / "status.json"
            status = json.loads(status_file.read_text(encoding="utf-8"))
            self.assertEqual(status["state"], "failed")
            self.assertEqual(status["exit_code"], 127)
            self.assertIn("command was not found", status["error"])

    def test_unknown_template_variable_marks_run_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".agentops" / "runs").mkdir(parents=True)

            rc = run_cli(
                [
                    "delegate",
                    "--to",
                    "codex",
                    "--role",
                    "smoke",
                    "--effort",
                    "high",
                    "--message",
                    "OK",
                    "--project",
                    str(project),
                    "--run-id",
                    "bad-template",
                    "--dry-run",
                    "--command-template",
                    "runner {unknown}",
                ]
            )

            self.assertEqual(rc, 2)
            status_file = project / ".agentops" / "runs" / "bad-template" / "status.json"
            status = json.loads(status_file.read_text(encoding="utf-8"))
            self.assertEqual(status["state"], "failed")
            self.assertIn("unknown command template variable", status["error"])


class ResultMarkdownTests(unittest.TestCase):
    def test_markdown_code_block_uses_fence_longer_than_backtick_runs(self) -> None:
        block = cli.markdown_code_block("outer ```\ninner ````\n")

        self.assertTrue(block.startswith("`````text\n"))
        self.assertTrue(block.endswith("`````\n"))

    def test_markdown_code_block_keeps_empty_content_compact(self) -> None:
        self.assertEqual(cli.markdown_code_block(""), "```text\n```\n")

    def test_delegate_result_preserves_output_and_avoids_fence_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".agentops" / "runs").mkdir(parents=True)
            script = project / "emit_fences.py"
            script.write_text(
                "import sys\n"
                "sys.stdout.write('stdout has ``` inside\\n')\n"
                "sys.stderr.write('stderr has ```` inside\\n')\n",
                encoding="utf-8",
            )

            rc = run_cli(
                [
                    "delegate",
                    "--to",
                    "codex",
                    "--role",
                    "fence",
                    "--effort",
                    "high",
                    "--message",
                    "emit fences",
                    "--project",
                    str(project),
                    "--run-id",
                    "fence-output",
                    "--command-template",
                    f"{shlex.quote(sys.executable)} {shlex.quote(str(script))}",
                ]
            )

            self.assertEqual(rc, 0)
            run_dir = project / ".agentops" / "runs" / "fence-output"
            self.assertEqual((run_dir / "stdout.log").read_text(encoding="utf-8"), "stdout has ``` inside\n")
            self.assertEqual((run_dir / "stderr.log").read_text(encoding="utf-8"), "stderr has ```` inside\n")

            result = (run_dir / "result.md").read_text(encoding="utf-8")
            self.assertIn("````text\nstdout has ``` inside\n````\n", result)
            self.assertIn("`````text\nstderr has ```` inside\n`````\n", result)


if __name__ == "__main__":
    unittest.main()
