from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import string
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

ALLOWED_EFFORTS = ("low", "medium", "high", "xhigh", "max")
SUPPORTED_TEMPLATE_VARS = (
    "to",
    "role",
    "model",
    "model_arg",
    "effort",
    "request_file",
    "run_dir",
)


class AgentOpsError(Exception):
    """利用者へ簡潔に返す agentops wrapper の入力・運用エラー。"""


class CommandTemplateError(AgentOpsError):
    """外部 CLI command template の解決に失敗した。"""


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
    """role 名などを run_id に使いやすい ASCII の文字列へ整形する。"""
    safe = []
    for char in value.lower():
        if "a" <= char <= "z" or "0" <= char <= "9":
            safe.append(char)
        elif char in ("-", "_"):
            safe.append(char)
        elif char.isspace() or char == "/":
            safe.append("-")
    return "".join(safe).strip("-") or "run"


def validate_effort(effort: str) -> None:
    """wrapper が受け付ける reasoning effort を明示的に絞る。"""
    if effort not in ALLOWED_EFFORTS:
        allowed = ", ".join(ALLOWED_EFFORTS)
        raise AgentOpsError(f"invalid --effort {effort!r}; expected one of: {allowed}")


def sanitize_run_id(value: str) -> str:
    """明示 run_id を安全な slug に正規化する。"""
    run_id = slug(value)
    has_safe_char = any(
        "a" <= char.lower() <= "z" or "0" <= char <= "9" or char in ("-", "_") for char in value
    )
    if run_id == "run" and not has_safe_char:
        raise AgentOpsError("--run-id must contain an ASCII letter, digit, '-' or '_'")
    return run_id


def ensure_inside(base: Path, target: Path, label: str) -> None:
    """target が base 配下に解決されることを確認する。"""
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise AgentOpsError(f"{label} must stay inside {base}: {target}") from exc


def resolve_input_path(project: Path, raw_path: str) -> Path:
    """--input を project root 配下の実パスへ解決する。"""
    input_path = Path(raw_path)
    if not input_path.is_absolute():
        input_path = project / input_path
    resolved = input_path.resolve()
    ensure_inside(project, resolved, "--input")
    return resolved


def resolve_run_dir(runs_dir: Path, run_id: str) -> Path:
    """run_dir が .agentops/runs の外へ出ないことを確認して返す。"""
    base = runs_dir.resolve()
    run_dir = (runs_dir / run_id).resolve()
    ensure_inside(base, run_dir, "--run-id")
    return run_dir


def allocate_run_dir(runs_dir: Path, preferred_run_id: str, *, explicit: bool) -> tuple[str, Path]:
    """既存 run を上書きしない run_id と run_dir を選ぶ。"""
    run_dir = resolve_run_dir(runs_dir, preferred_run_id)
    if explicit:
        if run_dir.exists():
            raise AgentOpsError(f"--run-id already exists: {preferred_run_id}")
        return preferred_run_id, run_dir

    if not run_dir.exists():
        return preferred_run_id, run_dir

    for index in range(2, 100):
        candidate = f"{preferred_run_id}-{index}"
        candidate_dir = resolve_run_dir(runs_dir, candidate)
        if not candidate_dir.exists():
            return candidate, candidate_dir
    raise AgentOpsError(f"could not allocate a unique run_id for {preferred_run_id!r}")


def write_json(path: Path, data: dict[str, Any]) -> None:
    """監視しやすいよう、UTF-8 かつ整形済み JSON で状態ファイルを書く。"""
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_input(args: argparse.Namespace, project: Path) -> str:
    """委譲依頼本文を --input、--message、stdin の順で集約する。

    --input の相対パスは呼び出し元ではなく対象プロジェクト基準で解釈する。
    """
    parts: list[str] = []
    if args.input:
        input_path = resolve_input_path(project, args.input)
        try:
            parts.append(input_path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise AgentOpsError(f"failed to read --input {args.input!r}: {exc}") from exc
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


def template_values(args: argparse.Namespace, request_file: Path, run_dir: Path) -> dict[str, str]:
    """template 展開値を shlex 用に quote した文字列として用意する。"""
    model_arg = f"--model {shlex.quote(args.model)}" if args.model else ""
    raw_values = {
        "to": args.to,
        "role": args.role,
        "model": args.model,
        "effort": args.effort,
        "request_file": str(request_file),
        "run_dir": str(run_dir),
    }
    values = {key: shlex.quote(str(value)) for key, value in raw_values.items()}
    values["model_arg"] = model_arg
    return values


def validate_template_fields(template: str) -> None:
    """未知の template 変数や format 修飾を分かりやすいエラーにする。"""
    allowed = ", ".join(f"{{{name}}}" for name in SUPPORTED_TEMPLATE_VARS)
    try:
        parsed = list(string.Formatter().parse(template))
    except ValueError as exc:
        raise CommandTemplateError(f"invalid command template: {exc}") from exc

    for _, field_name, format_spec, conversion in parsed:
        if field_name is None:
            continue
        if field_name not in SUPPORTED_TEMPLATE_VARS:
            raise CommandTemplateError(
                f"unknown command template variable {{{field_name}}}; supported variables: {allowed}"
            )
        if format_spec or conversion:
            raise CommandTemplateError(
                f"command template variable {{{field_name}}} does not support format modifiers; "
                f"supported variables: {allowed}"
            )


def expand_command(template: str, args: argparse.Namespace, request_file: Path, run_dir: Path) -> list[str]:
    """テンプレート変数を埋め込み、subprocess に渡せる argv 配列へ変換する。"""
    validate_template_fields(template)
    try:
        formatted = template.format(**template_values(args, request_file, run_dir))
    except KeyError as exc:
        allowed = ", ".join(f"{{{name}}}" for name in SUPPORTED_TEMPLATE_VARS)
        raise CommandTemplateError(
            f"unknown command template variable {{{exc.args[0]}}}; supported variables: {allowed}"
        ) from exc
    command = shlex.split(formatted)
    if not command:
        raise CommandTemplateError("command template expanded to an empty command")
    return command


def subprocess_output_text(value: str | bytes | None) -> str:
    """TimeoutExpired の stdout/stderr を write_text できる文字列へ揃える。"""
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def markdown_code_block(content: str, info: str = "text") -> str:
    """content 内の backtick fence と衝突しない Markdown code block を返す。"""
    longest_backtick_run = 0
    current_run = 0
    for char in content:
        if char == "`":
            current_run += 1
            longest_backtick_run = max(longest_backtick_run, current_run)
        else:
            current_run = 0

    fence = "`" * max(3, longest_backtick_run + 1)
    closing_newline = "\n" if content and not content.endswith("\n") else ""
    return f"{fence}{info}\n{content}{closing_newline}{fence}\n"


def mark_failed_run(
    *,
    status_file: Path,
    status: dict[str, Any],
    stderr_file: Path,
    result_file: Path,
    message: str,
    exit_code: int,
) -> int:
    """実行中 run を failed に確定させ、可能な限り記録を残す。"""
    try:
        stderr_file.write_text(message + "\n", encoding="utf-8")
        result_file.write_text(f"# Delegate Failed\n\n{message}\n", encoding="utf-8")
    except OSError:
        # status の確定を優先する。ログ書き込み失敗は status.error に残す。
        pass
    status["state"] = "failed"
    status["exit_code"] = exit_code
    status["completed_at"] = jst_timestamp()
    status["error"] = message
    write_json(status_file, status)
    return exit_code


def os_error_exit_code(exc: OSError) -> int:
    """POSIX に寄せた外部コマンド起動失敗の exit code を返す。"""
    if isinstance(exc, FileNotFoundError):
        return 127
    if isinstance(exc, PermissionError):
        return 126
    return 1


def base_status(
    *,
    args: argparse.Namespace,
    run_id: str,
    project: Path,
    request_file: Path,
    command: list[str],
    state: str,
    started_at: str,
) -> dict[str, Any]:
    """status.json の共通フィールドを組み立てる。"""
    return {
        "run_id": run_id,
        "state": state,
        "to": args.to,
        "role": args.role,
        "model": args.model,
        "effort": args.effort,
        "project": str(project),
        "request_file": str(request_file),
        "command": command,
        "started_at": started_at,
    }


def delegate(args: argparse.Namespace) -> int:
    """委譲 run を作成し、必要なら外部 CLI を実行する。

    request/status/stdout/stderr/result を同じ run_dir に保存し、dry-run、失敗、timeout も
    後から監視 CLI や人間が追跡できる形で残す。
    """
    validate_effort(args.effort)
    project = Path(args.project).resolve()
    runs_dir = project / ".agentops" / "runs"
    explicit_run_id = args.run_id is not None
    preferred_run_id = (
        sanitize_run_id(args.run_id) if explicit_run_id else f"{jst_run_id_stamp()}-{args.to}-{slug(args.role)}"
    )
    run_id, run_dir = allocate_run_dir(runs_dir, preferred_run_id, explicit=explicit_run_id)

    body = read_input(args, project)

    request_text = build_request(args, body)
    request_file = run_dir / "request.md"
    stdout_file = run_dir / "stdout.log"
    stderr_file = run_dir / "stderr.log"
    result_file = run_dir / "result.md"
    status_file = run_dir / "status.json"
    artifacts_dir = run_dir / "artifacts"
    # ドライランや起動失敗も調査できるよう、実行前に run ディレクトリ全体を作る。
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    request_file.write_text(request_text, encoding="utf-8")
    stdout_file.write_text("", encoding="utf-8")
    stderr_file.write_text("", encoding="utf-8")

    template = command_template(args)
    started_at = jst_timestamp()
    status = base_status(
        args=args,
        run_id=run_id,
        project=project,
        request_file=request_file,
        command=[],
        state="failed",
        started_at=started_at,
    )
    try:
        command = expand_command(template, args, request_file, run_dir)
    except CommandTemplateError as exc:
        exit_code = mark_failed_run(
            status_file=status_file,
            status=status,
            stderr_file=stderr_file,
            result_file=result_file,
            message=str(exc),
            exit_code=2,
        )
        print(f"delegate command template error: {exc}", file=sys.stderr)
        return exit_code

    status = base_status(
        args=args,
        run_id=run_id,
        project=project,
        request_file=request_file,
        command=command,
        state="dry_run" if args.dry_run else "running",
        started_at=started_at,
    )
    # 外部 CLI 起動前に status を書くことで、途中停止した run も stuck として検知できる。
    write_json(status_file, status)

    if args.dry_run:
        result_file.write_text(
            "# Dry Run\n\n"
            "External agent command was not executed.\n\n"
            "## Command\n\n"
            f"{markdown_code_block(shlex.join(command))}",
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
            f"{markdown_code_block(completed.stdout)}\n"
            "## Stderr\n\n"
            f"{markdown_code_block(completed.stderr)}",
            encoding="utf-8",
        )
        status["state"] = "succeeded" if completed.returncode == 0 else "failed"
        status["exit_code"] = completed.returncode
        status["completed_at"] = jst_timestamp()
        write_json(status_file, status)
        print(f"delegate run finished with exit code {completed.returncode}: {run_dir}")
        return completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout_file.write_text(subprocess_output_text(exc.stdout), encoding="utf-8")
        stderr_file.write_text(subprocess_output_text(exc.stderr), encoding="utf-8")
        result_file.write_text(f"# Delegate Timeout\n\nTimed out after {args.timeout} seconds.\n", encoding="utf-8")
        status["state"] = "timeout"
        status["exit_code"] = 124
        status["completed_at"] = jst_timestamp()
        write_json(status_file, status)
        print(f"delegate run timed out: {run_dir}", file=sys.stderr)
        return 124
    except OSError as exc:
        # 端末出力だけで終わらせず、失敗した run として記録を残す。
        if isinstance(exc, FileNotFoundError):
            message = (
                "The external agent command was not found. Configure AGENTOPS_CODEX_CMD, "
                f"AGENTOPS_CLAUDE_CMD, or pass --command-template. ({exc})"
            )
            print(f"delegate command not found: {exc}", file=sys.stderr)
        else:
            message = f"delegate command failed before completion: {exc}"
            print(message, file=sys.stderr)
        return mark_failed_run(
            status_file=status_file,
            status=status,
            stderr_file=stderr_file,
            result_file=result_file,
            message=message,
            exit_code=os_error_exit_code(exc),
        )
    except KeyboardInterrupt:
        message = "delegate run interrupted"
        print(message, file=sys.stderr)
        return mark_failed_run(
            status_file=status_file,
            status=status,
            stderr_file=stderr_file,
            result_file=result_file,
            message=message,
            exit_code=130,
        )


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


# ----- archive サブコマンド -----
#
# `.agentops/` 運用ルール (CLAUDE.md / AGENTS.md durable instructions §auto-merge 後の必須手順)
# を CLI で機械強制するためのコマンド群。
#   - archive plan : plan 全体（plans / task-plans / tasks / reviews）を archive へ
#   - archive task : 個別 task ファイルを archive へ + next-session.md を自動更新
# 詳細は docs/11-monitoring-cli.md に記述。

# ``> plan-id: `<id>` `` 形式（または素のキー記述）に対応した簡易 parser。
# パストラバーサル防止のため `/` を許可せず、`.` も連続させない値だけを取り出す。
PLAN_ID_PATTERN = re.compile(
    r"^>?\s*plan-id\s*:\s*`?([A-Za-z0-9][A-Za-z0-9_.-]*)`?\s*$",
    re.MULTILINE,
)

# 安全な plan-id / task-id (パストラバーサル防止)。
# `-` `.` `_` を許可するが `..` のような連続ピリオド、先頭非英数は弾く。
SAFE_PLAN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
SAFE_TASK_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# archive README の table separator 行（列数 3 の Markdown table）。
ARCHIVE_README_SEPARATOR_PATTERN = re.compile(
    r"^\|[\s\-:]+\|[\s\-:]+\|[\s\-:]+\|\s*$"
)


def detect_active_plan_id(project: Path) -> str:
    """.agentops/plans/current.md からアクティブな plan-id を取り出す。

    フロントマター風の ``> plan-id: `<id>` `` 行を期待する。検出失敗または
    `_validate_plan_id` での安全性チェック失敗は AgentOpsError。
    """
    plans_current = project / ".agentops" / "plans" / "current.md"
    if not plans_current.exists():
        raise AgentOpsError(
            "active plan not found: "
            f"{plans_current.relative_to(project)} does not exist"
        )
    text = plans_current.read_text(encoding="utf-8")
    match = PLAN_ID_PATTERN.search(text)
    if not match:
        raise AgentOpsError(
            f"could not detect plan-id in {plans_current.relative_to(project)}; "
            "expected a line like '> plan-id: `<id>`'"
        )
    plan_id = match.group(1).strip()
    # 抽出値も CLI 引数と同じ DbC で検証する（regex 改変や frontmatter 攻撃への二重防御）。
    _validate_plan_id(plan_id)
    return plan_id


def is_git_repo(project: Path) -> bool:
    """project が git worktree 配下にあるかの軽量判定。"""
    return (project / ".git").exists()


def git_tracked(path: Path, project: Path) -> bool:
    """path が git の管理下にあるかを `git ls-files` で確認する。"""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path.relative_to(project))],
            cwd=project,
            check=False,
            capture_output=True,
        )
    except (FileNotFoundError, OSError):
        return False
    return result.returncode == 0


def move_path(src: Path, dst: Path, *, project: Path, use_git: bool) -> None:
    """git 管理ファイルは `git mv`、そうでなければ shutil.move で移動する。

    `OSError` は AgentOpsError で包んでメイン処理側でクリーンに止められるようにする。
    """
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise AgentOpsError(
            f"could not create parent directory for {dst}: {exc}"
        ) from exc

    if use_git and git_tracked(src, project):
        rel_src = src.relative_to(project)
        rel_dst = dst.relative_to(project)
        result = subprocess.run(
            ["git", "mv", str(rel_src), str(rel_dst)],
            cwd=project,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise AgentOpsError(
                f"git mv failed for {rel_src} -> {rel_dst}: "
                f"{result.stderr.strip() or result.stdout.strip()}"
            )
        return

    try:
        shutil.move(str(src), str(dst))
    except OSError as exc:
        raise AgentOpsError(f"failed to move {src} -> {dst}: {exc}") from exc


def archive_display_name(plan_id: str) -> str:
    """`YYYY-MM-DD-foo-bar` から `foo-bar` を取り出す。日付プレフィックスがなければそのまま。"""
    match = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", plan_id)
    return match.group(1) if match else plan_id


def atomic_write_text(path: Path, content: str) -> None:
    """同ディレクトリの一時ファイルへ書き出してから rename する。"""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def build_archive_readme_row(plan_id: str, summary: str, date: str) -> str:
    """archive README へ挿入する Markdown table row を組み立てる。

    `summary` 内の `|` は table を壊さないよう `\\|` に escape する。改行は
    呼び出し側 (`archive_plan`) で事前に検証済み前提。
    """
    display_name = archive_display_name(plan_id)
    safe_summary = summary.replace("|", r"\|")
    return f"| {date} | [{display_name}]({plan_id}/plan.md) | {safe_summary} |"


def insert_archive_readme_row(
    readme_path: Path,
    *,
    new_row: str,
    project: Path,
) -> None:
    """archive/README.md の table 先頭（新しい順 = separator 行直後）に row を挿入する。

    既存 row には触れない。本関数は本番実行専用（dry-run はコンソール表示で完結する）。
    """
    if not readme_path.exists():
        raise AgentOpsError(
            f"archive README not found: {readme_path.relative_to(project)}"
        )

    text = readme_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    separator_idx: int | None = None
    for i, line in enumerate(lines):
        if ARCHIVE_README_SEPARATOR_PATTERN.match(line):
            separator_idx = i
            break
    if separator_idx is None:
        raise AgentOpsError(
            f"could not find table separator in "
            f"{readme_path.relative_to(project)}"
        )

    lines.insert(separator_idx + 1, new_row)
    new_text = "\n".join(lines)
    if text.endswith("\n"):
        new_text += "\n"
    atomic_write_text(readme_path, new_text)


def update_next_session(
    project: Path,
    archived_task_id: str,
    *,
    dry_run: bool,
) -> dict[str, str]:
    """next-session.md の `entry_point` / `updated_at` を更新し `completed_tasks` に行を足す。

    本文（マニュアル記述部分）は触らない。dry_run 時は予定値だけ返してファイルは触らない。
    """
    next_session_path = project / ".agentops" / "prompts" / "next-session.md"

    tasks_dir = project / ".agentops" / "tasks"
    remaining: list[str] = []
    if tasks_dir.exists():
        for task_file in sorted(tasks_dir.glob("*.md")):
            if task_file.name == "README.md":
                continue
            if task_file.stem == archived_task_id:
                continue
            remaining.append(task_file.name)

    new_entry_point_value = f".agentops/tasks/{remaining[0]}" if remaining else ""

    if not next_session_path.exists():
        return {
            "entry_point": new_entry_point_value or "(none)",
            "completed_added": archived_task_id,
            "note": "skipped: next-session.md does not exist",
        }

    if dry_run:
        return {
            "entry_point": new_entry_point_value or "(none — all tasks archived)",
            "completed_added": archived_task_id,
        }

    text = next_session_path.read_text(encoding="utf-8")

    if new_entry_point_value:
        replacement_entry = f"entry_point: {new_entry_point_value}"
    else:
        replacement_entry = (
            "entry_point: (none — all tasks archived; "
            "consider removing this file)"
        )
    text, entry_subs = re.subn(
        r"^entry_point:.*$",
        lambda _m: replacement_entry,
        text,
        count=1,
        flags=re.MULTILINE,
    )

    today = jst_now().strftime("%Y-%m-%d")
    text, _updated_subs = re.subn(
        r"^updated_at:.*$",
        lambda _m: f"updated_at: {today}",
        text,
        count=1,
        flags=re.MULTILINE,
    )

    # `completed_tasks: []` のような inline 空配列はブロック形式へ正規化する。
    # ブロック形式しかパースしないと「追記成功」とログに出しつつファイルが変わらない
    # 不整合になるため (Codex review P2 指摘)。`\s*` は改行を含み貪欲消費するので
    # `[ \t]*` だけに絞り、行末の改行は触らない。
    text = re.sub(
        r"^(completed_tasks):[ \t]*\[[ \t]*\][ \t]*$",
        r"\1:",
        text,
        count=1,
        flags=re.MULTILINE,
    )

    new_completed_line = f"  - {archived_task_id}"
    completed_pattern = re.compile(
        r"(^completed_tasks:[ \t]*\n(?:[ \t]+-[^\n]*\n)*)",
        re.MULTILINE,
    )
    match = completed_pattern.search(text)
    if match:
        block = match.group(1)
        if not re.search(
            rf"^[ \t]+-[ \t]+{re.escape(archived_task_id)}(\s|$)",
            block,
            re.MULTILINE,
        ):
            new_block = block.rstrip("\n") + "\n" + new_completed_line + "\n"
            text = text[: match.start()] + new_block + text[match.end():]
    else:
        # block 形式でも inline 空配列でもなく、`completed_tasks:` が見当たらない、
        # または別の形式（未対応）。run log には残るが追記しない。
        pass

    atomic_write_text(next_session_path, text)

    return {
        "entry_point": new_entry_point_value or "(none — all tasks archived)",
        "completed_added": archived_task_id,
        "entry_replaced": "yes" if entry_subs else "no",
    }


def _validate_plan_id(plan_id: str) -> None:
    """パストラバーサル防止と慣行（英数 + ハイフン）の確認。"""
    if not SAFE_PLAN_ID_PATTERN.match(plan_id):
        raise AgentOpsError(
            f"invalid --plan-id {plan_id!r}; "
            "only [A-Za-z0-9_.-] allowed and must start with [A-Za-z0-9]"
        )
    if ".." in plan_id:
        raise AgentOpsError(
            f"--plan-id may not contain '..': {plan_id!r}"
        )


def _validate_task_id(task_id: str) -> None:
    if not SAFE_TASK_ID_PATTERN.match(task_id):
        raise AgentOpsError(
            f"invalid --task-id {task_id!r}; "
            "only [A-Za-z0-9_.-] allowed and must start with [A-Za-z0-9]"
        )
    if ".." in task_id:
        raise AgentOpsError(
            f"--task-id may not contain '..': {task_id!r}"
        )


def _validate_summary(summary: str) -> None:
    """archive README の table を壊し得る改行を弾く。`|` は build 時に escape する。"""
    if "\n" in summary or "\r" in summary:
        raise AgentOpsError(
            "--summary must not contain newline characters"
        )


def _validate_date(date: str) -> None:
    """`--date` が `YYYY-MM-DD` 形式かを確認する。空文字は呼び出し前に既定値で埋める。"""
    if not DATE_PATTERN.match(date):
        raise AgentOpsError(
            f"invalid --date {date!r}; expected YYYY-MM-DD"
        )


def archive_plan(args: argparse.Namespace) -> int:
    """plan 全体を `.agentops/archive/<plan-id>/` へ移動し README table へ row を挿入する。

    既定では `.agentops/runs/` は移動しない（runs は plan-id と直接紐づかない場合があるため）。
    `--include-runs` を指定したときのみ runs/* を全件移動する。

    実行順は preflight (dst 衝突確認) → 計画表示 → dry-run なら return → move → README 挿入
    の順。途中で停止しても README / next-session を半端に書き換えない。
    """
    project = Path(args.project).resolve()
    plan_id = args.plan_id
    summary = args.summary
    date = args.date or jst_now().strftime("%Y-%m-%d")
    dry_run = args.dry_run

    _validate_plan_id(plan_id)
    _validate_summary(summary)
    _validate_date(date)

    archive_root = project / ".agentops" / "archive" / plan_id
    operations: list[tuple[Path, Path]] = []

    plans_current = project / ".agentops" / "plans" / "current.md"
    if plans_current.exists():
        operations.append((plans_current, archive_root / "plan.md"))

    task_plan_current = project / ".agentops" / "task-plans" / "current.md"
    if task_plan_current.exists():
        operations.append(
            (task_plan_current, archive_root / "task-plans" / "current.md")
        )

    tasks_dir = project / ".agentops" / "tasks"
    if tasks_dir.exists():
        for task_file in sorted(tasks_dir.glob("*.md")):
            if task_file.name == "README.md":
                continue
            operations.append(
                (task_file, archive_root / "tasks" / task_file.name)
            )

    reviews_dir = project / ".agentops" / "reviews"
    if reviews_dir.exists():
        for review_entry in sorted(reviews_dir.iterdir()):
            if review_entry.name == "README.md":
                continue
            operations.append(
                (review_entry, archive_root / "reviews" / review_entry.name)
            )

    if args.include_runs:
        runs_dir = project / ".agentops" / "runs"
        if runs_dir.exists():
            for run_entry in sorted(runs_dir.iterdir()):
                operations.append(
                    (run_entry, archive_root / "runs" / run_entry.name)
                )

    # PREFLIGHT: 移動先の衝突を事前検知する。途中まで move → 失敗 で半端な状態を残さない。
    for _src, dst in operations:
        if dst.exists():
            raise AgentOpsError(
                f"archive destination already exists: "
                f"{dst.relative_to(project)}"
            )

    readme_path = project / ".agentops" / "archive" / "README.md"
    if not readme_path.exists():
        raise AgentOpsError(
            f"archive README not found: {readme_path.relative_to(project)}"
        )
    new_row = build_archive_readme_row(plan_id, summary, date)

    print(f"{'[dry-run] ' if dry_run else ''}archive plan: {plan_id}")
    if not operations:
        print("  (no plans / task-plans / tasks / reviews to move)")
    for src, dst in operations:
        print(
            f"  move: {src.relative_to(project)} -> {dst.relative_to(project)}"
        )
    print(
        f"  insert row to {readme_path.relative_to(project)}: {new_row}"
    )

    if dry_run:
        return 0

    use_git = is_git_repo(project)
    for src, dst in operations:
        move_path(src, dst, project=project, use_git=use_git)
    insert_archive_readme_row(readme_path, new_row=new_row, project=project)
    return 0


def archive_task(args: argparse.Namespace) -> int:
    """個別 task md を archive へ移動し、next-session.md の entry_point / completed_tasks を更新する。

    実行順は preflight (dst 衝突確認) → 計画表示 → dry-run なら return → move →
    next-session.md 更新。途中で停止しても next-session.md を半端に書き換えない。
    """
    project = Path(args.project).resolve()
    task_id = args.task_id
    dry_run = args.dry_run

    _validate_task_id(task_id)
    plan_id = detect_active_plan_id(project)

    src = project / ".agentops" / "tasks" / f"{task_id}.md"
    if not src.exists():
        raise AgentOpsError(
            f"task file not found: {src.relative_to(project)}"
        )
    dst = (
        project / ".agentops" / "archive" / plan_id / "tasks" / f"{task_id}.md"
    )
    if dst.exists():
        raise AgentOpsError(
            f"archive destination already exists: "
            f"{dst.relative_to(project)}"
        )

    # dry-run プレビューを生成（実ファイルには触れない）。
    next_session_preview = update_next_session(
        project, task_id, dry_run=True
    )

    print(
        f"{'[dry-run] ' if dry_run else ''}archive task: {task_id} "
        f"(active plan: {plan_id})"
    )
    print(f"  move: {src.relative_to(project)} -> {dst.relative_to(project)}")
    print(
        f"  next-session entry_point -> {next_session_preview['entry_point']}"
    )
    print(
        f"  next-session completed_tasks += "
        f"{next_session_preview['completed_added']}"
    )
    if "note" in next_session_preview:
        print(f"  note: {next_session_preview['note']}")

    if dry_run:
        return 0

    use_git = is_git_repo(project)
    move_path(src, dst, project=project, use_git=use_git)
    update_next_session(project, task_id, dry_run=False)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """agentops CLI のサブコマンドと引数を定義する。"""
    parser = argparse.ArgumentParser(prog="agentops", description="AgentOps CLI wrapper")
    sub = parser.add_subparsers(dest="command", required=True)

    delegate_parser = sub.add_parser("delegate", help="delegate a task to Claude Code or Codex")
    delegate_parser.add_argument("--to", choices=("codex", "claude"), required=True)
    delegate_parser.add_argument("--role", required=True)
    delegate_parser.add_argument("--model", default="")
    delegate_parser.add_argument("--effort", choices=ALLOWED_EFFORTS, default="high")
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

    archive_parser = sub.add_parser(
        "archive",
        help="archive a completed plan or task into .agentops/archive/<plan-id>/",
    )
    archive_sub = archive_parser.add_subparsers(
        dest="archive_command", required=True
    )

    archive_plan_parser = archive_sub.add_parser(
        "plan",
        help=(
            "move plans/current.md, task-plans/current.md, tasks/*, reviews/* "
            "into .agentops/archive/<plan-id>/ and add a row to archive/README.md"
        ),
    )
    archive_plan_parser.add_argument("--plan-id", required=True)
    archive_plan_parser.add_argument("--summary", required=True)
    archive_plan_parser.add_argument(
        "--date",
        default="",
        help="completion date (default: today in Asia/Tokyo, YYYY-MM-DD)",
    )
    archive_plan_parser.add_argument(
        "--include-runs",
        action="store_true",
        help=(
            "also move .agentops/runs/* into the archive "
            "(default: keep runs in place because they are not always plan-scoped)"
        ),
    )
    archive_plan_parser.add_argument("--dry-run", action="store_true")
    archive_plan_parser.add_argument("--project", default=".")
    archive_plan_parser.set_defaults(func=archive_plan)

    archive_task_parser = archive_sub.add_parser(
        "task",
        help=(
            "move .agentops/tasks/<task-id>.md into the active plan's archive "
            "and update .agentops/prompts/next-session.md"
        ),
    )
    archive_task_parser.add_argument(
        "--task-id",
        required=True,
        help="basename of the task file (without .md), e.g. 02-p1-01-glossary",
    )
    archive_task_parser.add_argument("--dry-run", action="store_true")
    archive_task_parser.add_argument("--project", default=".")
    archive_task_parser.set_defaults(func=archive_task)

    return parser


def main(argv: list[str] | None = None) -> int:
    """コマンドライン引数を解析し、選ばれたサブコマンドへ処理を渡す。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except AgentOpsError as exc:
        print(f"agentops: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
