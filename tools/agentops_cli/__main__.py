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
    """外部エージェントへ渡す依頼文を、review_frontier では期待出力つきの Markdown に整形する。"""
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
    if args.role == "review_frontier":
        lines.extend(
            [
                "## Reviewer 出力期待値",
                "",
                "このレビュー run は agentops cross-review 用です。次の形式で `artifacts/review.md` を残してください (本ファイルに直接書き込んでも、stdout で同等内容を返してもよい):",
                "",
                "- 各指摘ごとに次のフィールドを含む",
                "  - `severity`: P0 / P1 / P2 / P3 (review-policy.md 準拠)",
                "  - `kind`: `mechanical` または `design`",
                "    - `mechanical` = patch / 行番号 / 具体書き換えで修正可能 (Claude が直接 git apply できる)",
                "    - `design` = 抽象指摘・判断要 (Claude が Codex coding_frontier に再委譲する)",
                "  - `file`: 対象ファイル相対パス",
                "  - `summary`: 1-2 行",
                "  - `details`: 必要に応じた本文",
                "- `kind: mechanical` の指摘には末尾に unified diff (`diff --git ...` 形式) を必ず添える",
                "- `kind: design` の指摘は patch 不要、抽象的な改善方針で OK",
                "- ループ防止のため、修正済みコードへの再指摘や P3 のみの細かい嗜好は避ける",
                "- 上記出力を `artifacts/review.md` に保存する (run_dir 配下、ファイル名固定)",
                "- 出力末尾に `kind` ラベル無しの自由記述を加える場合は、保守的に `design` 扱いとなる旨を Claude 側で読み替える",
                "",
            ]
        )
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


def find_archive_readme_separator(readme_path: Path, project: Path) -> int:
    """archive/README.md の table separator 行 index を返す。

    preflight で move より前に呼ぶことで、move 完了後に README 挿入だけが失敗する
    half-state を防ぐ（Codex round-2 review P1 指摘）。
    """
    if not readme_path.exists():
        raise AgentOpsError(
            f"archive README not found: {readme_path.relative_to(project)}"
        )
    text = readme_path.read_text(encoding="utf-8")
    for i, line in enumerate(text.splitlines()):
        if ARCHIVE_README_SEPARATOR_PATTERN.match(line):
            return i
    raise AgentOpsError(
        f"could not find table separator in "
        f"{readme_path.relative_to(project)}"
    )


def insert_archive_readme_row(
    readme_path: Path,
    *,
    new_row: str,
    project: Path,
) -> None:
    """archive/README.md の table 先頭（新しい順 = separator 行直後）に row を挿入する。

    既存 row には触れない。本関数は本番実行専用（dry-run はコンソール表示で完結する）。
    呼び出し前に `find_archive_readme_separator` で preflight 済み前提。
    """
    separator_idx = find_archive_readme_separator(readme_path, project)
    text = readme_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    lines.insert(separator_idx + 1, new_row)
    new_text = "\n".join(lines)
    if text.endswith("\n"):
        new_text += "\n"
    atomic_write_text(readme_path, new_text)


_COMPLETED_TASKS_INLINE_EMPTY_PATTERN = re.compile(
    r"^(completed_tasks):[ \t]*\[[ \t]*\][ \t]*$",
    re.MULTILINE,
)
_COMPLETED_TASKS_BLOCK_PATTERN = re.compile(
    r"(^completed_tasks:[ \t]*\n(?:[ \t]+-[^\n]*\n)*)",
    re.MULTILINE,
)
_UNSUPPORTED_COMPLETED_TASKS_NOTE = (
    "(skipped: unsupported completed_tasks format; "
    "expected block list or inline empty array)"
)


def _planned_entry_point(remaining: list[str]) -> str:
    """tasks/ 残ファイル名から、書き換え予定の entry_point 値を組み立てる。"""
    if remaining:
        return f".agentops/tasks/{remaining[0]}"
    return "(none — all tasks archived; consider removing this file)"


def update_next_session(
    project: Path,
    archived_task_id: str,
    *,
    dry_run: bool,
) -> dict[str, str]:
    """next-session.md の `entry_point` / `updated_at` を更新し `completed_tasks` に行を足す。

    本文（マニュアル記述部分）は触らない。dry_run 時は予定値だけ返してファイルは触らない。
    `completed_tasks` が block 形式でも inline 空配列でもない場合は配列追記をスキップし、
    呼び出し元の log でも `(skipped: unsupported ...)` を返す（dry-run と本番で表示が一致）。
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

    planned_entry_point = _planned_entry_point(remaining)

    if not next_session_path.exists():
        return {
            "entry_point": planned_entry_point,
            "completed_added": "(skipped: next-session.md does not exist)",
        }

    text = next_session_path.read_text(encoding="utf-8")

    # 形式判定: 実ファイルを inline 空配列正規化したうえで block 形式の存在を確認する。
    # dry-run と本番で同じ判定を共有することで、preview と実体の差異 (Codex round-2 P2) を防ぐ。
    normalized_for_check = _COMPLETED_TASKS_INLINE_EMPTY_PATTERN.sub(
        r"\1:", text, count=1
    )
    has_block = _COMPLETED_TASKS_BLOCK_PATTERN.search(
        normalized_for_check
    ) is not None
    if has_block:
        completed_status = archived_task_id
    else:
        completed_status = _UNSUPPORTED_COMPLETED_TASKS_NOTE

    if dry_run:
        return {
            "entry_point": planned_entry_point,
            "completed_added": completed_status,
        }

    replacement_entry = f"entry_point: {planned_entry_point}"
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

    text = _COMPLETED_TASKS_INLINE_EMPTY_PATTERN.sub(r"\1:", text, count=1)
    if has_block:
        new_completed_line = f"  - {archived_task_id}"
        match = _COMPLETED_TASKS_BLOCK_PATTERN.search(text)
        if match:
            block = match.group(1)
            already_listed = re.search(
                rf"^[ \t]+-[ \t]+{re.escape(archived_task_id)}(\s|$)",
                block,
                re.MULTILINE,
            )
            if not already_listed:
                new_block = (
                    block.rstrip("\n") + "\n" + new_completed_line + "\n"
                )
                text = text[: match.start()] + new_block + text[match.end():]

    atomic_write_text(next_session_path, text)

    return {
        "entry_point": planned_entry_point,
        "completed_added": completed_status,
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
    # README 存在 + separator 行存在 を move 前に検証する（half-state 防止）。
    find_archive_readme_separator(readme_path, project)
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
    completed_added = next_session_preview["completed_added"]
    if completed_added.startswith("(skipped"):
        # 実ファイル形式が非対応 / 不在で配列追記しないケース。`+=` と書くと誤解の元なので
        # ステータス文字列として表示する（dry-run / 本番で表示が一致する）。
        print(f"  next-session completed_tasks: {completed_added}")
    else:
        print(f"  next-session completed_tasks += {completed_added}")

    if dry_run:
        return 0

    use_git = is_git_repo(project)
    move_path(src, dst, project=project, use_git=use_git)
    update_next_session(project, task_id, dry_run=False)
    return 0


# =============================================================================
# localize subcommand (PR-D)
# 既存プロジェクトの設計痕跡を inventory + 4 戦略意思決定木で推奨戦略を出す。
# 仕様: docs/19-project-localization.md / docs/10-cli-wrapper.md
# 不変条件: 既存 project ファイルを書き換えない (--dry-run 既定)。SECRET 値を
# inventory / log / docs に書かない。痕跡内容の長文は転載しない (パス・存在・
# サイズ・鮮度のみ)。
# =============================================================================

# 検出対象痕跡 (depth-2 まで)。docs/19 §検出対象 inventory に列挙したもの。
LOCALIZE_TRACE_PATTERNS: dict[str, list[tuple[str, str]]] = {
    "claude": [
        ("CLAUDE.md", "file"),
        (".claude", "dir-or-file"),
    ],
    "codex": [
        ("AGENTS.md", "file"),
        ("AGENTS.override.md", "file"),
        (".codex", "dir-or-file"),
    ],
    "gemini": [
        ("GEMINI.md", "file"),
        (".gemini", "dir"),
        (".agent", "dir"),
    ],
    "other": [
        (".antigravity", "dir"),
        (".cursorrules", "file"),
        (".cursor", "dir"),
        (".aider.conf.yml", "file"),
        (".aider.chat.history.md", "file"),
        (".aider.input.history", "file"),
        (".windsurfrules", "file"),
        (".continue", "dir"),
        (".copilot", "dir"),
    ],
    "personal": [
        (".ai", "dir"),
        (".agentops", "dir"),
    ],
}

# 除外対象 (docs/19 §除外対象 dot dir / dot file)。ここにマッチした path は
# 痕跡対象外として skip し、再帰探索でも入らない。
LOCALIZE_EXCLUDE_NAMES: frozenset[str] = frozenset(
    {
        # VCS / CI
        ".git", ".github", ".gitlab",
        ".gitignore", ".gitattributes",
        # runtime / build / cache
        ".tmp", ".cache", ".next", ".nuxt", ".svelte-kit", ".vite", ".turbo", ".parcel-cache",
        "node_modules",
        # deploy
        ".wrangler", ".vercel", ".netlify", ".firebase", ".gcloud",
        # IDE / editor
        ".vscode", ".idea", ".zed", ".fleet",
        # 環境 / Python
        ".venv", ".python-version", ".tool-versions", ".nvmrc",
        # テスト / MCP
        ".playwright-mcp", ".playwright",
    }
)

# 一般的な project tooling dot-dir / dot-file (docs/19 §除外対象に列挙されていないが
# AI 痕跡ではない)。未列挙 AI 痕跡検出の false positive を抑えるため除外する。
LOCALIZE_EXCLUDE_NAMES_TOOLING: frozenset[str] = frozenset(
    {
        ".husky", ".devcontainer", ".dependabot", ".changeset", ".cspell",
        ".config", ".local",
        ".editorconfig",
        ".npmrc", ".yarnrc", ".yarnrc.yml", ".npmignore", ".yarnignore",
        ".env", ".env.example", ".env.local", ".env.production", ".env.development", ".env.test",
        ".dockerignore", ".dockerfile",
        ".browserslistrc", ".node-version",
        ".prettierrc", ".prettierrc.js", ".prettierrc.json", ".prettierrc.yml", ".prettierrc.yaml",
        ".prettierignore",
        ".eslintrc", ".eslintrc.js", ".eslintrc.json", ".eslintrc.yml",
        ".eslintignore",
        ".stylelintrc", ".babelrc",
        ".ruff_cache", ".mypy_cache", ".pytest_cache", ".tox",
        ".coverage",
        ".storybook",
        ".commitlintrc", ".lintstagedrc", ".releaserc",
        ".markdownlint.json", ".markdownlintignore",
    }
)


def _localize_is_excluded(name: str) -> bool:
    """docs/19 §除外対象 + 一般 project tooling 除外を一元判定する。"""
    return name in LOCALIZE_EXCLUDE_NAMES or name in LOCALIZE_EXCLUDE_NAMES_TOOLING


# 標準 project docs (UPPERCASE.md だが AI 痕跡ではない) の denylist。
# 未列挙 AI 痕跡候補検出 (`<VENDOR>.md` ヒューリスティック) で false positive を防ぐ。
LOCALIZE_PROJECT_DOC_NAMES: frozenset[str] = frozenset(
    {
        "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
        "LICENSE.md", "LICENCE.md", "COPYING.md", "NOTICE.md",
        "SECURITY.md", "GOVERNANCE.md", "MAINTAINERS.md", "AUTHORS.md", "OWNERS.md",
        "TODO.md", "FAQ.md", "USAGE.md", "INSTALL.md", "ROADMAP.md",
        "HISTORY.md", "RELEASE.md", "RELEASES.md",
        "SUPPORT.md", "STYLE.md", "STYLEGUIDE.md", "MIGRATION.md", "UPGRADING.md",
        "ISSUE_TEMPLATE.md", "PULL_REQUEST_TEMPLATE.md",
        "BUG_REPORT.md", "FEATURE_REQUEST.md", "DISCUSSION.md",
    }
)

# 補助情報 (技術スタック判定)
LOCALIZE_STACK_FILES: dict[str, str] = {
    "package.json": "Node",
    "go.mod": "Go",
    "composer.json": "PHP",
    "Cargo.toml": "Rust",
    "Gemfile": "Ruby",
    "pyproject.toml": "Python",
    "requirements.txt": "Python",
}

LOCALIZE_STRATEGIES = (
    "greenfield",
    "inventory-rebuild",
    "coexistence",
    "freeze",
    "needs-user-confirmation",
)


def _localize_freshness_bucket(days: int | None) -> str:
    """鮮度を docs/19 の判定軸 4 (≤30 / 31-180 / 180+ / 不明) に対応させる。"""
    if days is None:
        return "unknown"
    if days <= 30:
        return "≤30d"
    if days <= 180:
        return "31-180d"
    return "180+d"


def _localize_match_pattern(name: str) -> tuple[str, str] | None:
    """ファイル / dir 名が検出対象パターンに一致するなら (category, kind) を返す。"""
    for cat, patterns in LOCALIZE_TRACE_PATTERNS.items():
        for pname, kind in patterns:
            if name == pname:
                return cat, kind
    if name.startswith(".aider"):
        return "other", "file"
    return None


def _localize_record_trace(
    base: Path,
    entry: Path,
    depth: int,
    *,
    now_ts: float,
) -> dict[str, Any] | None:
    """痕跡 entry に対する 1 件分の inventory record を作る。"""
    matched = _localize_match_pattern(entry.name)
    if matched is None:
        return None
    cat, _expected_kind = matched
    try:
        st = entry.stat()
    except OSError:
        return None
    is_dir = entry.is_dir()
    actual_kind = "dir" if is_dir else "file"
    size = None if is_dir else st.st_size
    mtime_days = max(0, int((now_ts - st.st_mtime) // 86400))
    record: dict[str, Any] = {
        "category": cat,
        "name": entry.name,
        "path": str(entry.relative_to(base)),
        "kind": actual_kind,
        "size_bytes": size,
        "mtime_days": mtime_days,
        "freshness": _localize_freshness_bucket(mtime_days),
        "depth": depth,
    }
    if not is_dir and size == 0 and entry.name in (".claude", ".codex"):
        record["zero_byte_marker"] = True
    if is_dir:
        try:
            children = sorted(
                c.name for c in entry.iterdir() if c.name not in LOCALIZE_EXCLUDE_NAMES
            )
        except (PermissionError, OSError):
            children = []
        record["children"] = children[:30]
    return record


def _localize_scan_traces(project: Path, max_depth: int = 2) -> list[dict[str, Any]]:
    """痕跡を depth-2 まで scan して inventory list を返す。

    検出対象は LOCALIZE_TRACE_PATTERNS、除外は LOCALIZE_EXCLUDE_NAMES。
    """
    found: list[dict[str, Any]] = []
    now_ts = jst_now().timestamp()

    def _walk(cur: Path, depth: int) -> None:
        if depth > max_depth:
            return
        try:
            entries = sorted(cur.iterdir(), key=lambda p: p.name)
        except (PermissionError, OSError):
            return
        for entry in entries:
            name = entry.name
            if _localize_is_excluded(name):
                continue
            record = _localize_record_trace(project, entry, depth, now_ts=now_ts)
            if record is not None:
                found.append(record)
                continue
            if entry.is_dir() and depth < max_depth:
                _walk(entry, depth + 1)

    _walk(project, depth=1)
    return found


def _localize_is_known_pattern_name(name: str) -> bool:
    """検出対象に列挙されたパターン名 (LOCALIZE_TRACE_PATTERNS + .aider*) を判定する。"""
    for patterns in LOCALIZE_TRACE_PATTERNS.values():
        for pname, _kind in patterns:
            if name == pname:
                return True
    if name.startswith(".aider"):
        return True
    return False


def _localize_detect_unlisted(project: Path, max_depth: int = 2) -> list[dict[str, Any]]:
    """docs/19 §検出網羅性: 未列挙 AI 痕跡候補 (`.<vendor>/` / `.<vendor>rules` /
    `<VENDOR>.md`) を検出する。検出されたら `needs-user-confirmation` で escalate する。

    false positive を抑えるため `_localize_is_excluded` (docs/19 除外 + 一般 tooling)
    を経由する。
    """
    now_ts = jst_now().timestamp()
    unlisted: list[dict[str, Any]] = []
    seen: set[str] = set()

    def _walk(cur: Path, depth: int) -> None:
        if depth > max_depth:
            return
        try:
            entries = sorted(cur.iterdir(), key=lambda p: p.name)
        except (PermissionError, OSError):
            return
        for entry in entries:
            name = entry.name
            if _localize_is_excluded(name):
                continue
            if _localize_is_known_pattern_name(name):
                # 既知 AI 痕跡は本検出器の対象外 (上位 _localize_scan_traces が拾う)。
                # ただし内部 dir は再帰しない (既知 dir 配下は子も既知配下として扱う)。
                continue

            is_dot_dir = name.startswith(".") and entry.is_dir()
            # 標準 project docs (README.md / CHANGELOG.md 等) は AI 痕跡ではないので除外。
            is_upper_md = (
                not entry.is_dir()
                and name.endswith(".md")
                and len(name) > 3
                and name[:-3].isupper()
                and name not in LOCALIZE_PROJECT_DOC_NAMES
            )
            is_vendor_rules = (
                not entry.is_dir() and name.startswith(".") and name.endswith("rules")
            )

            if is_dot_dir or is_upper_md or is_vendor_rules:
                rel = str(entry.relative_to(project))
                if rel in seen:
                    continue
                seen.add(rel)
                try:
                    st = entry.stat()
                except OSError:
                    continue
                trigger = (
                    "dot-dir" if is_dot_dir
                    else ("UPPERCASE.md" if is_upper_md else "vendor-rules")
                )
                unlisted.append(
                    {
                        "path": rel,
                        "name": name,
                        "kind": "dir" if entry.is_dir() else "file",
                        "size_bytes": None if entry.is_dir() else st.st_size,
                        "mtime_days": max(0, int((now_ts - st.st_mtime) // 86400)),
                        "depth": depth,
                        "trigger": trigger,
                    }
                )

            # subdir も再帰 (除外 / 既知パターンに該当しない一般 dir のみ)
            if entry.is_dir() and depth < max_depth:
                _walk(entry, depth + 1)

    _walk(project, depth=1)
    return unlisted


def _localize_detect_stack(project: Path) -> dict[str, Any]:
    """補助 file (`package.json` 等) から技術スタックを推定する。"""
    detected: list[str] = []
    details: dict[str, str] = {}
    for fname, stack in LOCALIZE_STACK_FILES.items():
        path = project / fname
        if not path.exists():
            continue
        if stack not in detected:
            detected.append(stack)
        details[fname] = stack
        if fname == "package.json":
            try:
                pkg = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(pkg, dict):
                continue
            deps: dict[str, Any] = {}
            for key in ("dependencies", "devDependencies", "peerDependencies"):
                section = pkg.get(key)
                if isinstance(section, dict):
                    deps.update(section)
            for marker in ("nuxt", "next", "react", "vue", "svelte"):
                if marker in deps:
                    details["framework"] = marker
                    break
    return {"detected": detected, "details": details}


def _localize_git_activity(project: Path) -> dict[str, Any]:
    """git の last commit / 30 日内 commit 数を取得する。"""
    if not (project / ".git").exists():
        return {"is_git_repo": False}
    info: dict[str, Any] = {"is_git_repo": True}
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI"],
            cwd=project, capture_output=True, text=True, check=False, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            iso = result.stdout.strip()
            info["last_commit_iso"] = iso
            try:
                commit_dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
                if commit_dt.tzinfo is None:
                    commit_dt = commit_dt.replace(tzinfo=JST)
                days = (jst_now() - commit_dt.astimezone(JST)).days
                info["last_commit_days_ago"] = max(0, days)
            except ValueError:
                pass
    except (subprocess.SubprocessError, OSError):
        pass
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD", "--since=30 days ago"],
            cwd=project, capture_output=True, text=True, check=False, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip().isdigit():
            info["commits_last_30d"] = int(result.stdout.strip())
    except (subprocess.SubprocessError, OSError):
        pass
    return info


def _localize_assess_conflict(traces: list[dict[str, Any]]) -> tuple[str, list[str]]:
    """痕跡から競合度を低 / 中 / 高 で推定する (docs/19 §競合判定マトリクス簡易版)。

    `.claude/plans/` / `.ai/` フル構造 / `.agent/` substantial は **`.agentops/` の有無に
    関わらず高〜中の競合**として扱う (二重運用は単独存在より厳しい衝突)。docs/19 §競合
    判定マトリクス line 76-78 と整合。
    """
    by_name: dict[str, dict[str, Any]] = {t["name"]: t for t in traces if t["depth"] == 1}
    reasons: list[str] = []
    score = 1
    has_agentops = ".agentops" in by_name
    has_ai = ".ai" in by_name and by_name[".ai"]["kind"] == "dir"
    has_agent = ".agent" in by_name and by_name[".agent"]["kind"] == "dir"
    has_claude_dir = ".claude" in by_name and by_name[".claude"]["kind"] == "dir"
    has_codex_dir = ".codex" in by_name and by_name[".codex"]["kind"] == "dir"
    if has_claude_dir:
        children = by_name[".claude"].get("children", []) or []
        if "plans" in children:
            score = max(score, 3)
            if has_agentops:
                reasons.append(".claude/plans/ + .agentops/ 既存 → plan 二重運用 (docs/19 §競合判定マトリクス 高)")
            else:
                reasons.append(".claude/plans/ + .agentops/ なし → plan 単一真ソース原則と衝突")
        if "hooks" in children:
            score = max(score, 2)
            reasons.append(".claude/hooks/ あり → グローバル hook と event 競合候補")
    if has_codex_dir:
        children = by_name[".codex"].get("children", []) or []
        if any(c in children for c in ("agents", "subagents", "hooks")):
            score = max(score, 2)
            reasons.append(".codex/ に subagent / hook あり → グローバル Codex 設定と責務重複")
    if has_ai:
        ai_children = by_name[".ai"].get("children", []) or []
        if any(c in ai_children for c in ("contracts", "decisions", "gates", "memory", "reviews", "tasks")):
            score = max(score, 3)
            if has_agentops:
                reasons.append(".ai/ フル構造 + .agentops/ 既存 → 責務重複 (docs/19 §競合判定マトリクス 高)")
            else:
                reasons.append(".ai/ フル構造 + .agentops/ なし → 責務重複候補")
    if has_agent:
        agent_children = by_name[".agent"].get("children", []) or []
        substantial = sum(1 for c in agent_children if c not in ("README.md", ".gitkeep"))
        if substantial >= 3:
            score = max(score, 2)
            reasons.append(".agent/ に複数 subdir → Gemini 系運用残存の可能性")
    only_cursorrules = (
        len([t for t in traces if t["depth"] == 1]) == 1
        and ".cursorrules" in by_name
    )
    if only_cursorrules:
        score = 1
    level = {1: "低", 2: "中", 3: "高"}[score]
    return level, reasons


def _localize_classify_strategy(
    traces: list[dict[str, Any]],
    git_activity: dict[str, Any],
    forced: str | None = None,
) -> tuple[str, str, list[str]]:
    """4 戦略 + escalate を意思決定木で判定する (docs/19 §4 戦略の意思決定木)。"""
    if forced:
        return forced, "high", [f"--strategy {forced} で強制指定"]
    reasons: list[str] = []
    substantive = [t for t in traces if not (t["category"] == "personal" and t["name"] == ".agentops")]
    if not substantive:
        return "greenfield", "high", ["痕跡なし → greenfield"]
    if (
        len(substantive) == 1
        and substantive[0]["name"] == "AGENTS.md"
        and (substantive[0].get("size_bytes") or 0) < 200
    ):
        return "greenfield", "high", ["AGENTS.md のみ最小 → greenfield"]
    days_list = [t["mtime_days"] for t in substantive if t.get("mtime_days") is not None]
    newest_days = min(days_list) if days_list else None
    commits_30d = git_activity.get("commits_last_30d")
    is_idle = commits_30d == 0
    is_active = commits_30d is not None and commits_30d >= 1
    conflict_level, conflict_reasons = _localize_assess_conflict(traces)
    if newest_days is not None and newest_days >= 180 and is_idle:
        reasons.append(f"newest trace {newest_days} 日前 + 30 日内 commit なし → 休止")
        reasons.extend(conflict_reasons)
        return "freeze", "high", reasons
    has_substantial_dir = any(
        t.get("kind") == "dir"
        and t.get("category") in {"claude", "gemini", "personal"}
        and len(t.get("children", []) or []) >= 3
        for t in traces
    )
    if newest_days is not None and (
        newest_days <= 30 or (newest_days <= 180 and has_substantial_dir)
    ):
        if is_active and conflict_level in {"中", "高"}:
            reasons.append(
                f"newest trace {newest_days} 日前 + 30 日内 commit {commits_30d} 件 + "
                f"競合度 {conflict_level} → inventory-rebuild"
            )
            reasons.extend(conflict_reasons)
            return "inventory-rebuild", "high", reasons
    if conflict_level in {"低", "中"} and len(substantive) <= 3:
        reasons.append(
            f"競合度 {conflict_level} + 痕跡 {len(substantive)} 件 → coexistence (短命/プロト想定)"
        )
        reasons.extend(conflict_reasons)
        return "coexistence", "medium", reasons
    reasons.append("4 戦略どれにも明確に該当しない → user 確認 escalate")
    reasons.extend(conflict_reasons)
    return "needs-user-confirmation", "low", reasons


_LOCALIZE_CHECKLISTS: dict[str, list[str]] = {
    "greenfield": [
        "グローバル `~/.claude/CLAUDE.md` / `~/.codex/AGENTS.md` を import する `CLAUDE.md` / `AGENTS.md` を作成",
        "`.agentops/{plans,task-plans,tasks,handoffs,reviews,runs,archive,prompts}/` 構造を生成",
        "`.agentops/archive/README.md` の table header を初期化",
        "技術スタック固有の lint / test / build / deploy コマンドを project 側 docs に明記",
        "AI auto-merge 許諾を project でも適用するか拒否するか CLAUDE.md / AGENTS.md に記載",
    ],
    "inventory-rebuild": [
        "旧設計痕跡の inventory を `~/.claude/.agentops/runs/<run-id>/inventory.md` または対象 project の `.agentops/runs/` に書き出す",
        "各要素を「移行」「廃棄」「温存」「保留」のいずれかに分類",
        "移行: 新方針へ組み替え + diff レビュー",
        "廃棄: 削除または `archive/` へ退避",
        "温存: 新グローバルと共存できる根拠を docs に書く",
        "保留: 次セッションへ handoff",
        "グローバル設計改訂後の追従可能性を確保 (project 固有差分は `AGENTS.override.md` 等に集約)",
    ],
    "coexistence": [
        "`.agentops/` 構造のみ追加 (旧 CLAUDE.md / AGENTS.md / GEMINI.md / `.codex` / `.claude/` / `.agent/` / `.ai/` / `.cursorrules` / `.cursor/` 等には触れない)",
        "`.agentops/plans/current.md` の Context に「既存設計と共存しており、見直しは inventory-rebuild に切り替える時に再評価」と記載",
        "グローバル設計改訂時の追従が薄くなる旨を CLAUDE.md / AGENTS.md に注記",
    ],
    "freeze": [
        "既存ファイルに override notice (1-3 行) のみ追記:「本プロジェクトは凍結状態。グローバル設計改訂を反映する場合は本プロジェクトを `inventory-rebuild` で再起動する」",
        "`.agentops/` は **追加しない** (休止プロジェクトに新規 dir を生やすと管理対象が増える)",
        "次回再起動時に本 docs を再評価する旨を `~/.claude/.agentops/handoffs/` に残すかは ad-hoc 判断",
    ],
    "needs-user-confirmation": [
        "本 report の判定軸 (痕跡有無 / 鮮度 / git activity / 競合度) を user が確認",
        "user が 4 戦略のいずれかを `--strategy <name>` で強制指定するか、追加情報を加味して再判定",
    ],
}


def _localize_render_report(
    project: Path,
    traces: list[dict[str, Any]],
    stack: dict[str, Any],
    git_activity: dict[str, Any],
    strategy: str,
    confidence: str,
    reasoning: list[str],
    run_id: str,
    generated_at: str,
    unlisted: list[dict[str, Any]] | None = None,
) -> str:
    """Markdown report (人間 + 機械可読) を生成する。"""
    lines: list[str] = []
    lines.append("# project-localize report")
    lines.append("")
    lines.append(f"- project: `{project}`")
    lines.append(f"- generated_at: {generated_at}")
    lines.append(f"- run_id: `{run_id}`")
    lines.append(f"- strategy: **{strategy}**")
    lines.append(f"- confidence: {confidence}")
    lines.append("")
    lines.append("## Inventory")
    lines.append("")
    if not traces:
        lines.append("- (痕跡なし)")
        lines.append("")
    else:
        by_cat: dict[str, list[dict[str, Any]]] = {}
        for t in traces:
            by_cat.setdefault(t["category"], []).append(t)
        cat_titles = {
            "claude": "Claude Code 系",
            "codex": "Codex 系",
            "gemini": "Gemini / 汎用 AI 系",
            "other": "その他 (Cursor / Aider / Antigravity / Windsurf / Continue / Copilot 等)",
            "personal": "本人標準 / agentops",
        }
        for cat in ("claude", "codex", "gemini", "other", "personal"):
            entries = by_cat.get(cat)
            if not entries:
                continue
            lines.append(f"### {cat_titles.get(cat, cat)}")
            lines.append("")
            for t in entries:
                marker = " (0-byte marker)" if t.get("zero_byte_marker") else ""
                size_str = f", {t['size_bytes']} bytes" if t.get("size_bytes") is not None else ""
                age = f"{t['mtime_days']} 日前" if t.get("mtime_days") is not None else "鮮度不明"
                lines.append(f"- `{t['path']}` ({t['kind']}{size_str}, {age}{marker})")
                if t["kind"] == "dir" and t.get("children"):
                    children_preview = ", ".join(t["children"][:10])
                    if len(t["children"]) > 10:
                        children_preview += ", ..."
                    lines.append(f"  - children: {children_preview}")
            lines.append("")
    lines.append("## Tech stack")
    lines.append("")
    if stack["detected"]:
        lines.append(f"- detected: {', '.join(stack['detected'])}")
        for fname, val in stack["details"].items():
            lines.append(f"  - `{fname}` → {val}")
    else:
        lines.append("- (技術スタック判定材料なし)")
    lines.append("")
    lines.append("## Git activity")
    lines.append("")
    if git_activity.get("is_git_repo"):
        last = git_activity.get("last_commit_iso", "(unknown)")
        last_days = git_activity.get("last_commit_days_ago")
        last_str = f"{last} ({last_days} 日前)" if last_days is not None else last
        lines.append(f"- last commit: {last_str}")
        c30 = git_activity.get("commits_last_30d")
        if c30 is not None:
            lines.append(f"- commits in last 30 days: {c30}")
    else:
        lines.append("- (git repo ではない)")
    lines.append("")
    lines.append("## Freshness summary")
    lines.append("")
    days_list = [t["mtime_days"] for t in traces if t.get("mtime_days") is not None]
    if days_list:
        lines.append(f"- newest trace: {min(days_list)} 日前")
        lines.append(f"- oldest trace: {max(days_list)} 日前")
        bucket_counts: dict[str, int] = {}
        for t in traces:
            b = t.get("freshness", "unknown")
            bucket_counts[b] = bucket_counts.get(b, 0) + 1
        for b in ("≤30d", "31-180d", "180+d", "unknown"):
            if b in bucket_counts:
                lines.append(f"  - {b}: {bucket_counts[b]} 件")
    else:
        lines.append("- (鮮度判定可能な痕跡なし)")
    lines.append("")
    conflict_level, conflict_reasons = _localize_assess_conflict(traces)
    lines.append("## Conflict assessment")
    lines.append("")
    lines.append(f"- conflict level: **{conflict_level}**")
    if conflict_reasons:
        for r in conflict_reasons:
            lines.append(f"  - {r}")
    else:
        lines.append("  - (顕著な衝突なし)")
    lines.append("")
    lines.append(f"## Recommended strategy: {strategy}")
    lines.append("")
    lines.append("### Reasoning")
    for r in reasoning:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("### Checklist")
    for item in _LOCALIZE_CHECKLISTS.get(strategy, []):
        lines.append(f"- [ ] {item}")
    lines.append("")
    lines.append("## Unlisted traces (docs/19 §検出網羅性)")
    lines.append("")
    if unlisted:
        lines.append(
            "未列挙の dot-dir / `<UPPERCASE>.md` / `.<vendor>rules` 候補を検出。"
            "user 確認の上、AI 痕跡なら docs/19 §検出対象 inventory に追加してください。"
        )
        lines.append("")
        for u in unlisted:
            size_str = f", {u['size_bytes']} bytes" if u.get("size_bytes") is not None else ""
            age = f"{u['mtime_days']} 日前" if u.get("mtime_days") is not None else "鮮度不明"
            trigger = u.get("trigger", "?")
            lines.append(f"- `{u['path']}` ({u['kind']}{size_str}, {age}, trigger: {trigger})")
    else:
        lines.append("- (未列挙 AI 痕跡候補は検出されず)")
    return "\n".join(lines) + "\n"


def localize(args: argparse.Namespace) -> int:
    """agentops localize: 既存 project の AI 設計痕跡を inventory + 戦略推奨 (dry-run only)。"""
    project = Path(args.project).expanduser().resolve()
    if not project.exists():
        raise AgentOpsError(f"--project path does not exist: {project}")
    if not project.is_dir():
        raise AgentOpsError(f"--project path is not a directory: {project}")

    forced_strategy: str | None
    if args.strategy and args.strategy != "auto":
        forced_strategy = args.strategy
    else:
        forced_strategy = None

    traces = _localize_scan_traces(project)
    unlisted = _localize_detect_unlisted(project)
    stack = _localize_detect_stack(project)
    git_activity = _localize_git_activity(project)
    strategy, confidence, reasoning = _localize_classify_strategy(
        traces, git_activity, forced=forced_strategy
    )

    # 未列挙 AI 痕跡候補があれば user 確認 escalate (docs/19 §検出網羅性)。
    # `--strategy <name>` で強制指定された場合は escalate を上書きしない。
    if unlisted and forced_strategy is None:
        strategy = "needs-user-confirmation"
        confidence = "low"
        reasoning.insert(
            0,
            f"未列挙 AI 痕跡候補 {len(unlisted)} 件を検出 → user 確認 escalate "
            "(docs/19 §検出網羅性)",
        )

    generated_at = jst_timestamp()
    project_slug = slug(project.name) or "project"
    timestamp = jst_run_id_stamp()
    run_id = sanitize_run_id(args.run_id) if args.run_id else f"{timestamp}-{project_slug}-localize"

    report = _localize_render_report(
        project=project,
        traces=traces,
        stack=stack,
        git_activity=git_activity,
        strategy=strategy,
        confidence=confidence,
        reasoning=reasoning,
        run_id=run_id,
        generated_at=generated_at,
        unlisted=unlisted,
    )

    runs_root = (
        Path(args.runs_root).expanduser()
        if args.runs_root
        else (Path.home() / ".claude" / ".agentops" / "runs")
    )
    run_dir = (runs_root / run_id).resolve()
    try:
        ensure_inside(runs_root.resolve(), run_dir, "--run-id")
    except AgentOpsError:
        raise
    try:
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "inventory.md").write_text(report, encoding="utf-8")
    except OSError as exc:
        raise AgentOpsError(f"failed to write run log to {run_dir}: {exc}") from exc

    print(report, end="")
    print(f"\n[localize] run log saved: {run_dir / 'inventory.md'}", file=sys.stderr)
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

    localize_parser = sub.add_parser(
        "localize",
        help="inventory existing project AI traces and recommend a localization strategy (dry-run)",
    )
    localize_parser.add_argument(
        "--project", default=".", help="target project path (default: cwd)"
    )
    localize_parser.add_argument(
        "--strategy",
        choices=("auto", *LOCALIZE_STRATEGIES),
        default="auto",
        help="recommended strategy; 'auto' (default) uses the docs/19 decision tree",
    )
    localize_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="dry-run mode (default and only mode for now; --apply is future scope)",
    )
    localize_parser.add_argument(
        "--run-id", help="explicit run id (default: <JST timestamp>-<project>-localize)"
    )
    localize_parser.add_argument(
        "--runs-root",
        default=None,
        help="run log root (default: ~/.claude/.agentops/runs/); used by tests",
    )
    localize_parser.set_defaults(func=localize)

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
