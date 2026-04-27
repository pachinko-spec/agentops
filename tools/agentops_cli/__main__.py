from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any


# 実運用では、使用直前に公式 CLI docs を確認して環境変数で上書きする。
JST = ZoneInfo("Asia/Tokyo")


DEFAULT_TEMPLATES = {
    "codex": "codex exec {model_arg} -c model_reasoning_effort={effort} -",
    "claude": "claude {model_arg} --effort {effort} --print",
}


def jst_now() -> datetime:
    """日本時間の現在時刻を timezone-aware な datetime として返す。"""
    return datetime.now(JST)


def jst_timestamp() -> str:
    """run log に保存する日本時間の ISO 文字列を返す。"""
    return jst_now().isoformat(timespec="seconds")


def jst_run_id_stamp() -> str:
    """run_id に使う日本時間の短い時刻文字列を返す。"""
    return jst_now().strftime("%Y%m%dT%H%M%S+0900")


def slug(value: str) -> str:
    """role 名などを run_id に使いやすい ASCII 寄りの文字列へ整形する。"""
    safe = []
    for char in value.lower():
        if char.isalnum():
            safe.append(char)
        elif char in ("-", "_"):
            safe.append(char)
        elif char.isspace() or char == "/":
            safe.append("-")
    return "".join(safe).strip("-") or "run"


def write_json(path: Path, data: dict[str, Any]) -> None:
    """監視しやすいよう、UTF-8 かつ整形済み JSON で状態ファイルを書く。"""
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_input(args: argparse.Namespace, project: Path) -> str:
    """委譲依頼本文を --input、--message、stdin の順で集約する。

    --input の相対パスは呼び出し元ではなく対象プロジェクト基準で解釈する。
    """
    parts: list[str] = []
    if args.input:
        input_path = Path(args.input)
        if not input_path.is_absolute():
            # 相対入力は、呼び出し元 cwd ではなく委譲対象プロジェクトに属する。
            input_path = project / input_path
        parts.append(input_path.read_text(encoding="utf-8"))
    if args.message:
        parts.append(args.message)
    if not parts and not sys.stdin.isatty():
        stdin_text = sys.stdin.read()
        if stdin_text:
            parts.append(stdin_text)
    return "\n\n".join(part.strip() for part in parts if part.strip())


def build_request(args: argparse.Namespace, body: str) -> str:
    """外部エージェントへ渡す依頼文を、run log としても読める Markdown に整形する。"""
    lines = [
        "# AgentOps Delegate Request",
        "",
        f"- to: {args.to}",
        f"- role: {args.role}",
        f"- model: {args.model or '(adapter default)'}",
        f"- effort: {args.effort}",
        f"- created_at: {jst_timestamp()}",
        "",
        "## Task",
        "",
        body.strip() or "(no task body provided)",
        "",
    ]
    return "\n".join(lines)


def command_template(args: argparse.Namespace) -> str:
    """CLI 別のコマンドテンプレートを、明示引数、環境変数、既定値の順で解決する。"""
    if args.command_template:
        return args.command_template
    env_name = f"AGENTOPS_{args.to.upper()}_CMD"
    return os.environ.get(env_name, DEFAULT_TEMPLATES[args.to])


def expand_command(template: str, args: argparse.Namespace, request_file: Path, run_dir: Path) -> list[str]:
    """テンプレート変数を埋め込み、subprocess に渡せる argv 配列へ変換する。"""
    model_arg = f"--model {shlex.quote(args.model)}" if args.model else ""
    values = {
        "to": args.to,
        "role": args.role,
        "model": args.model,
        "model_arg": model_arg,
        "effort": args.effort,
        "request_file": str(request_file),
        "run_dir": str(run_dir),
    }
    return shlex.split(template.format(**values))


def delegate(args: argparse.Namespace) -> int:
    """委譲 run を作成し、必要なら外部 CLI を実行する。

    request/status/stdout/stderr/result を同じ run_dir に保存し、dry-run、失敗、timeout も
    後から監視 CLI や人間が追跡できる形で残す。
    """
    project = Path(args.project).resolve()
    runs_dir = project / ".agentops" / "runs"
    run_id = args.run_id or f"{jst_run_id_stamp()}-{args.to}-{slug(args.role)}"
    run_dir = runs_dir / run_id
    artifacts_dir = run_dir / "artifacts"
    # ドライランや起動失敗も調査できるよう、実行前に run ディレクトリ全体を作る。
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    body = read_input(args, project)
    request_text = build_request(args, body)
    request_file = run_dir / "request.md"
    stdout_file = run_dir / "stdout.log"
    stderr_file = run_dir / "stderr.log"
    result_file = run_dir / "result.md"
    status_file = run_dir / "status.json"

    request_file.write_text(request_text, encoding="utf-8")
    stdout_file.write_text("", encoding="utf-8")
    stderr_file.write_text("", encoding="utf-8")

    template = command_template(args)
    command = expand_command(template, args, request_file, run_dir)
    started_at = jst_timestamp()

    status: dict[str, Any] = {
        "run_id": run_id,
        "state": "dry_run" if args.dry_run else "running",
        "to": args.to,
        "role": args.role,
        "model": args.model,
        "effort": args.effort,
        "project": str(project),
        "request_file": str(request_file),
        "command": command,
        "started_at": started_at,
    }
    # 外部 CLI 起動前に status を書くことで、途中停止した run も stuck として検知できる。
    write_json(status_file, status)

    if args.dry_run:
        result_file.write_text(
            "# Dry Run\n\n"
            "External agent command was not executed.\n\n"
            "## Command\n\n"
            f"```text\n{shlex.join(command)}\n```\n",
            encoding="utf-8",
        )
        status["completed_at"] = jst_timestamp()
        status["exit_code"] = 0
        write_json(status_file, status)
        print(f"created dry-run delegate record: {run_dir}")
        return 0

    try:
        completed = subprocess.run(
            command,
            input=request_text,
            text=True,
            cwd=project,
            capture_output=True,
            timeout=args.timeout if args.timeout > 0 else None,
            check=False,
        )
        stdout_file.write_text(completed.stdout, encoding="utf-8")
        stderr_file.write_text(completed.stderr, encoding="utf-8")
        result_file.write_text(
            "# Delegate Result\n\n"
            f"- exit_code: {completed.returncode}\n"
            f"- completed_at: {jst_timestamp()}\n\n"
            "## Stdout\n\n"
            f"```text\n{completed.stdout}\n```\n\n"
            "## Stderr\n\n"
            f"```text\n{completed.stderr}\n```\n",
            encoding="utf-8",
        )
        status["state"] = "succeeded" if completed.returncode == 0 else "failed"
        status["exit_code"] = completed.returncode
        status["completed_at"] = jst_timestamp()
        write_json(status_file, status)
        print(f"delegate run finished with exit code {completed.returncode}: {run_dir}")
        return completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout_file.write_text(exc.stdout or "", encoding="utf-8")
        stderr_file.write_text(exc.stderr or "", encoding="utf-8")
        result_file.write_text(f"# Delegate Timeout\n\nTimed out after {args.timeout} seconds.\n", encoding="utf-8")
        status["state"] = "timeout"
        status["exit_code"] = 124
        status["completed_at"] = jst_timestamp()
        write_json(status_file, status)
        print(f"delegate run timed out: {run_dir}", file=sys.stderr)
        return 124
    except FileNotFoundError as exc:
        # 端末出力だけで終わらせず、失敗した run として記録を残す。
        stderr_file.write_text(str(exc) + "\n", encoding="utf-8")
        result_file.write_text(
            "# Delegate Failed\n\n"
            "The external agent command was not found. Configure AGENTOPS_CODEX_CMD, "
            "AGENTOPS_CLAUDE_CMD, or pass --command-template.\n",
            encoding="utf-8",
        )
        status["state"] = "failed"
        status["exit_code"] = 127
        status["completed_at"] = jst_timestamp()
        status["error"] = str(exc)
        write_json(status_file, status)
        print(f"delegate command not found: {exc}", file=sys.stderr)
        return 127


def list_runs(args: argparse.Namespace) -> int:
    """保存済みの委譲 run を新しい順に表示する。"""
    runs_dir = Path(args.project).resolve() / ".agentops" / "runs"
    if not runs_dir.exists():
        print("no runs directory")
        return 0

    rows: list[dict[str, Any]] = []
    for status_file in sorted(runs_dir.glob("*/status.json"), reverse=True):
        try:
            rows.append(json.loads(status_file.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            rows.append({"run_id": status_file.parent.name, "state": "invalid_status"})

    for row in rows[: args.limit]:
        print(
            f"{row.get('run_id', '-')}\t"
            f"{row.get('state', '-')}\t"
            f"{row.get('to', '-')}\t"
            f"{row.get('role', '-')}"
        )
    return 0


def doctor(args: argparse.Namespace) -> int:
    """wrapper を使う前提条件が揃っているかを簡易確認する。"""
    project = Path(args.project).resolve()
    checks = {
        "project_exists": project.exists(),
        "agentops_runs_dir": (project / ".agentops" / "runs").exists(),
        "git_repo": (project / ".git").exists(),
        "codex_template": bool(os.environ.get("AGENTOPS_CODEX_CMD") or DEFAULT_TEMPLATES.get("codex")),
        "claude_template": bool(os.environ.get("AGENTOPS_CLAUDE_CMD") or DEFAULT_TEMPLATES.get("claude")),
    }
    if args.json:
        print(json.dumps(checks, ensure_ascii=False, indent=2))
    else:
        for name, ok in checks.items():
            print(f"{name}: {'ok' if ok else 'missing'}")
    return 0 if all(checks.values()) else 1


def build_parser() -> argparse.ArgumentParser:
    """agentops CLI のサブコマンドと引数を定義する。"""
    parser = argparse.ArgumentParser(prog="agentops", description="AgentOps CLI wrapper")
    sub = parser.add_subparsers(dest="command", required=True)

    delegate_parser = sub.add_parser("delegate", help="delegate a task to Claude Code or Codex")
    delegate_parser.add_argument("--to", choices=("codex", "claude"), required=True)
    delegate_parser.add_argument("--role", required=True)
    delegate_parser.add_argument("--model", default="")
    delegate_parser.add_argument("--effort", default="high")
    delegate_parser.add_argument("--input")
    delegate_parser.add_argument("--message")
    delegate_parser.add_argument("--project", default=".")
    delegate_parser.add_argument("--run-id")
    delegate_parser.add_argument("--dry-run", action="store_true")
    delegate_parser.add_argument("--command-template")
    delegate_parser.add_argument("--timeout", type=int, default=0)
    delegate_parser.set_defaults(func=delegate)

    runs_parser = sub.add_parser("runs", help="list delegate runs")
    runs_parser.add_argument("--project", default=".")
    runs_parser.add_argument("--limit", type=int, default=20)
    runs_parser.set_defaults(func=list_runs)

    doctor_parser = sub.add_parser("doctor", help="check wrapper prerequisites")
    doctor_parser.add_argument("--project", default=".")
    doctor_parser.add_argument("--json", action="store_true")
    doctor_parser.set_defaults(func=doctor)

    return parser


def main(argv: list[str] | None = None) -> int:
    """コマンドライン引数を解析し、選ばれたサブコマンドへ処理を渡す。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
