from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo
from typing import Any
from urllib import request


JST = ZoneInfo("Asia/Tokyo")


def jst_now() -> datetime:
    """日本時間の現在時刻を timezone-aware な datetime として返す。"""
    return datetime.now(JST)


def jst_today() -> date:
    """freshness 判定に使う日本時間の日付を返す。"""
    return jst_now().date()


def parse_scalar(value: str) -> Any:
    """浅い設定ファイル用に、文字列を bool / int / str へ最小限変換する。"""
    value = value.strip().strip('"').strip("'")
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        return value


def load_simple_config(path: Path) -> dict[str, Any]:
    """チェックイン済みの浅い YAML / JSON 設定を読む。

    監視 CLI を依存関係なしで動かすため、ここでは list-of-map 程度の YAML だけを扱う。
    """
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        return json.loads(text)

    data: dict[str, Any] = {}
    current_key: str | None = None
    current_item: dict[str, Any] | None = None

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current_key = line[:-1].strip()
            data[current_key] = []
            current_item = None
            continue
        stripped_line = line.strip()
        if stripped_line.startswith("- "):
            if current_key is None:
                continue
            current_item = {}
            data.setdefault(current_key, []).append(current_item)
            rest = stripped_line[2:].strip()
            if rest and ":" in rest:
                key, value = rest.split(":", 1)
                current_item[key.strip()] = parse_scalar(value)
            continue
        if current_item is not None and ":" in stripped_line:
            key, value = stripped_line.split(":", 1)
            current_item[key.strip()] = parse_scalar(value)

    return data


def run_git(project: Path, args: list[str]) -> tuple[int, str, str]:
    """対象プロジェクトで読み取り専用の git コマンドを実行する。"""
    completed = subprocess.run(
        ["git", *args],
        cwd=project,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def parse_git_status(output: str) -> dict[str, Any]:
    """porcelain branch 出力から、ブランチ要約と dirty file 数だけを取り出す。"""
    branch_line = ""
    dirty = 0
    for line in output.splitlines():
        if line.startswith("## "):
            branch_line = line[3:]
        elif line.strip():
            dirty += 1
    return {"branch_summary": branch_line, "dirty_files": dirty}


def parse_iso_datetime(value: str) -> datetime | None:
    """status.json の ISO 風時刻を日本時間の datetime に戻す。壊れた値は None にする。"""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=JST)
    return parsed.astimezone(JST)


def check_runs(project: Path, stuck_run_hours: int) -> dict[str, Any]:
    """`.agentops/runs/` の状態ファイルから stuck run を検出する。

    実プロセスへは触らず、永続化済み status だけを見るのでセッションをまたいだ監視に使える。
    """
    runs_dir = project / ".agentops" / "runs"
    stuck: list[str] = []
    total = 0
    now = jst_now()
    if runs_dir.exists():
        for status_file in runs_dir.glob("*/status.json"):
            total += 1
            try:
                status = json.loads(status_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                stuck.append(f"{status_file.parent.name}: invalid status")
                continue
            state = status.get("state")
            started_at = parse_iso_datetime(status.get("started_at", ""))
            if state in {"running", "started"} and started_at:
                age_hours = (now - started_at).total_seconds() / 3600
                if age_hours >= stuck_run_hours:
                    stuck.append(f"{status_file.parent.name}: {age_hours:.1f}h")
    return {"total": total, "stuck": stuck}


def count_markdown_items(path: Path) -> int:
    """README 以外の Markdown を、未完了タスクや handoff の件数として数える。"""
    if not path.exists():
        return 0
    return sum(1 for item in path.glob("*.md") if item.name.lower() != "readme.md")


def check_project(project_config: dict[str, Any]) -> dict[str, Any]:
    """単一プロジェクトの Git と `.agentops/` 状態を確認する。

    監視 CLI は警告とエラーを分ける。dirty worktree など運用上の注意は warning、
    パス不在や Git 失敗のように監視不能な状態は error として返す。
    """
    project = Path(str(project_config.get("path", "."))).expanduser().resolve()
    default_branch = str(project_config.get("default_branch", "main"))
    stuck_run_hours = int(project_config.get("stuck_run_hours", 2))
    max_ahead = int(project_config.get("max_ahead_commits", 50))
    max_behind = int(project_config.get("max_behind_commits", 10))

    result: dict[str, Any] = {
        "name": project_config.get("name", project.name),
        "path": str(project),
        "default_branch": default_branch,
        "ok": True,
        "warnings": [],
        "errors": [],
    }

    if not project.exists():
        result["ok"] = False
        result["errors"].append("project path does not exist")
        return result

    code, status_out, status_err = run_git(project, ["status", "--porcelain=v1", "--branch"])
    if code != 0:
        result["ok"] = False
        result["errors"].append(status_err or "not a git repository")
        return result

    git_status = parse_git_status(status_out)
    result["git"] = git_status
    if git_status["dirty_files"] > 0:
        result["warnings"].append(f"dirty worktree: {git_status['dirty_files']} files")

    code, branch, _ = run_git(project, ["branch", "--show-current"])
    result["git"]["branch"] = branch if code == 0 else ""
    if branch == default_branch:
        result["warnings"].append(f"currently on default branch: {default_branch}")

    # ローカル検証では remote がないこともあるため、divergence 不明は致命扱いしない。
    code, divergence, _ = run_git(project, ["rev-list", "--left-right", "--count", f"origin/{default_branch}...HEAD"])
    if code == 0 and divergence:
        behind_text, ahead_text = divergence.split()
        behind = int(behind_text)
        ahead = int(ahead_text)
        result["git"]["behind"] = behind
        result["git"]["ahead"] = ahead
        if behind > max_behind:
            result["warnings"].append(f"behind origin/{default_branch}: {behind} commits")
        if ahead > max_ahead:
            result["warnings"].append(f"ahead of origin/{default_branch}: {ahead} commits")

    result["agentops"] = {
        "runs": check_runs(project, stuck_run_hours),
        "tasks": count_markdown_items(project / ".agentops" / "tasks"),
        "handoffs": count_markdown_items(project / ".agentops" / "handoffs"),
    }
    if result["agentops"]["runs"]["stuck"]:
        result["warnings"].append(f"stuck runs: {len(result['agentops']['runs']['stuck'])}")

    return result


def check_freshness(path: Path) -> list[dict[str, Any]]:
    """freshness-sources の最終確認日から、陳腐化している情報源を判定する。

    いまは日付ベースのみとし、URL 取得や registry 照会は後続の network-aware check に分ける。
    """
    config = load_simple_config(path)
    sources = config.get("sources", [])
    today = jst_today()
    results: list[dict[str, Any]] = []
    for source in sources:
        last_checked_raw = str(source.get("last_checked", ""))
        max_age_days = int(source.get("max_age_days", 30))
        try:
            last_checked = date.fromisoformat(last_checked_raw)
            age_days = (today - last_checked).days
            stale = age_days > max_age_days
        except ValueError:
            age_days = None
            stale = True
        results.append(
            {
                "name": source.get("name"),
                "kind": source.get("kind"),
                "url": source.get("url"),
                "last_checked": last_checked_raw,
                "max_age_days": max_age_days,
                "age_days": age_days,
                "stale": stale,
            }
        )
    return results


def load_projects(args: argparse.Namespace) -> list[dict[str, Any]]:
    """--projects 設定があれば複数プロジェクトを読み、なければ --project 単体を使う。"""
    if args.projects:
        config = load_simple_config(Path(args.projects))
        projects = config.get("projects", [])
        if projects:
            return projects
    return [{"name": Path(args.project).resolve().name, "path": args.project}]


def render_text(report: dict[str, Any]) -> str:
    """人間向け、cron 通知向けの短い Markdown レポートを作る。"""
    lines = ["# agentops-watch report", ""]
    for project in report["projects"]:
        mark = "OK" if project["ok"] and not project["warnings"] else "WARN"
        if project["errors"]:
            mark = "ERROR"
        lines.append(f"## {project['name']} [{mark}]")
        lines.append(f"- path: {project['path']}")
        git = project.get("git", {})
        if git:
            lines.append(f"- branch: {git.get('branch', '') or git.get('branch_summary', '')}")
            lines.append(f"- dirty_files: {git.get('dirty_files', 0)}")
            if "ahead" in git or "behind" in git:
                lines.append(f"- divergence: ahead={git.get('ahead', 0)} behind={git.get('behind', 0)}")
        agentops = project.get("agentops", {})
        if agentops:
            lines.append(f"- runs: {agentops['runs']['total']} total, {len(agentops['runs']['stuck'])} stuck")
            lines.append(f"- tasks: {agentops['tasks']}")
            lines.append(f"- handoffs: {agentops['handoffs']}")
        for warning in project["warnings"]:
            lines.append(f"- warning: {warning}")
        for error in project["errors"]:
            lines.append(f"- error: {error}")
        lines.append("")

    if report.get("freshness"):
        lines.append("## freshness")
        for source in report["freshness"]:
            status = "stale" if source["stale"] else "ok"
            lines.append(f"- {source['name']}: {status} (last_checked={source['last_checked']})")
    return "\n".join(lines).rstrip() + "\n"


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    """プロジェクト状態と freshness 結果を 1 つの report 辞書へまとめる。"""
    projects = [check_project(project) for project in load_projects(args)]
    report: dict[str, Any] = {
        "generated_at": jst_now().isoformat(timespec="seconds"),
        "projects": projects,
    }
    if args.freshness:
        report["freshness"] = check_freshness(Path(args.freshness))
    return report


def cmd_check(args: argparse.Namespace) -> int:
    """check サブコマンドを実行し、text または JSON で report を出力する。"""
    report = build_report(args)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report), end="")
    has_error = any(project["errors"] for project in report["projects"])
    return 2 if has_error else 0


def cmd_notify(args: argparse.Namespace) -> int:
    """Discord webhook へ監視ダイジェストを送る。

    dry-run では送信せず payload だけ表示する。実送信時の webhook URL は環境変数から読み、
    secret をリポジトリへ置かない。
    """
    report = build_report(args)
    # 通知本文は Discord の content 上限に余裕を残し、webhook 側の整形差分を吸収する。
    payload = {"content": render_text(report)[:1900]}
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    webhook = os.environ.get("AGENTOPS_DISCORD_WEBHOOK_URL")
    if not webhook:
        print("AGENTOPS_DISCORD_WEBHOOK_URL is not set", file=sys.stderr)
        return 2

    data = json.dumps(payload).encode("utf-8")
    req = request.Request(webhook, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=args.timeout) as response:
        print(f"discord notification sent: HTTP {response.status}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """agentops-watch CLI のサブコマンドと共通引数を定義する。"""
    parser = argparse.ArgumentParser(prog="agentops-watch", description="AgentOps local monitoring CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(target: argparse.ArgumentParser) -> None:
        """check / notify で共有する監視対象指定の引数を追加する。"""
        target.add_argument("--project", default=".")
        target.add_argument("--projects")
        target.add_argument("--freshness", default="config/freshness-sources.yml")

    check = sub.add_parser("check", help="check local project state")
    add_common(check)
    check.add_argument("--json", action="store_true")
    check.set_defaults(func=cmd_check)

    notify = sub.add_parser("notify", help="send or preview a Discord digest")
    add_common(notify)
    notify.add_argument("--dry-run", action="store_true")
    notify.add_argument("--timeout", type=int, default=10)
    notify.set_defaults(func=cmd_notify)

    return parser


def main(argv: list[str] | None = None) -> int:
    """コマンドライン引数を解析し、選ばれたサブコマンドへ処理を渡す。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
