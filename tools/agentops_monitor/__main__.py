from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import request
from zoneinfo import ZoneInfo


JST = ZoneInfo("Asia/Tokyo")


# kind と Webhook envvar の固定マッピング (docs/11 §kind→envvar マッピング表)。
# secret 値はここに書かない。値は実行時に os.environ から読む。
KIND_TO_ENVVAR: dict[str, str] = {
    "daily": "DISCORD_WEBHOOK_URL_DAILLY",
    "weekly": "DISCORD_WEBHOOK_URL_WEEKLY",
    "monthly": "DISCORD_WEBHOOK_URL_MONTHLY",
    "session-start": "DISCORD_WEBHOOK_URL_ANT_TIME",
    "session-end": "DISCORD_WEBHOOK_URL_ANT_TIME",
    "permission-wait": "DISCORD_WEBHOOK_URL_ANT_TIME",
    "alert": "DISCORD_WEBHOOK_URL_ANT_TIME",
    "stop-failure": "DISCORD_WEBHOOK_URL_ANT_TIME",
}

DIGEST_KINDS = frozenset({"daily", "weekly", "monthly"})
ANTTIME_KINDS = frozenset(KIND_TO_ENVVAR.keys()) - DIGEST_KINDS

LEGACY_ENVVAR = "AGENTOPS_DISCORD_WEBHOOK_URL"

# ユーザーをメンションする可能性のある記法。本 CLI は payload に
# `allowed_mentions: {"parse": []}` を必ず付け、追加で文字列レベルでも無害化する。
_USER_MENTION_RE = re.compile(r"<@([!&]?\d+)>")
_ZWSP = "​"

# Embed 1 個あたりの色 (Discord 視認性のため kind ごとに分ける)。
_EMBED_COLOR = {
    "digest": 3447003,        # blue
    "session-start": 3066993,  # green
    "session-end": 9807270,   # gray
    "permission-wait": 16776960,  # yellow
    "alert": 15158332,        # red
    "stop-failure": 10038562,  # dark red
}

# Discord embed の制約 (公式 docs)。
_EMBED_FIELDS_LIMIT = 25
_EMBED_FIELD_VALUE_LIMIT = 1024
_EMBED_TITLE_LIMIT = 256


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


def has_next_session_md(project: Path) -> bool:
    """`.agentops/prompts/next-session.md` の存在を真偽値で返す。"""
    return (project / ".agentops" / "prompts" / "next-session.md").exists()


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
        "next_session_md": has_next_session_md(project),
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
    """--projects 設定があれば複数プロジェクトを読み、なければ --project 単体を使う。

    --project が未指定 (None) の場合は cwd (".") にフォールバックする。
    notify では `--kind alert` で project optional を成立させたいので、引数定義側で
    default=None にし、ここで集約して fallback を担う。

    `--projects` を明示指定した場合は、ファイル不在や `projects:` エントリ欠如を
    silent fallback せず例外を上げる (docs/18 §DbC 停止条件: --projects YAML 読み込
    み失敗は invocation 停止)。呼び出し側 (cmd_check / cmd_notify / _legacy_notify)
    は FileNotFoundError / ValueError を捕捉して exit 2 に正規化する。
    """
    if args.projects:
        path = Path(args.projects)
        if not path.exists():
            raise FileNotFoundError(f"--projects file not found: {path}")
        config = load_simple_config(path)
        projects = config.get("projects", [])
        if not projects:
            raise ValueError(f"--projects file has no 'projects' entries: {path}")
        return projects
    project = args.project or "."
    return [{"name": Path(project).resolve().name, "path": project}]


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
    try:
        report = build_report(args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report), end="")
    has_error = any(project["errors"] for project in report["projects"])
    return 2 if has_error else 0


# -----------------------------------------------------------------------------
# notify ヘルパ群 (kind / webhook resolver / payload builder / rate-limit)
# -----------------------------------------------------------------------------


def resolve_webhook_url(kind: str, env: dict[str, str] | None = None) -> tuple[str, str | None]:
    """kind から envvar 名を引き、対応する Webhook URL を返す。

    secret 値そのものは戻り値経由でしか扱わない (log / stdout には出さない)。
    """
    if kind not in KIND_TO_ENVVAR:
        raise ValueError(f"unknown kind: {kind}")
    envvar = KIND_TO_ENVVAR[kind]
    env_source = env if env is not None else os.environ
    return envvar, env_source.get(envvar)


def sanitize_mention_text(text: str) -> str:
    """`@everyone` / `@here` / `<@id>` 系を ZWSP 挿入で無害化する。

    payload の `allowed_mentions: {"parse": []}` で Discord 側はメンションを無効化するが、
    自由テキスト中の文字列が誤解されないよう文字列レベルでも保険をかける。
    """
    if not text:
        return text
    sanitized = text.replace("@everyone", f"@{_ZWSP}everyone").replace("@here", f"@{_ZWSP}here")
    sanitized = _USER_MENTION_RE.sub(lambda m: f"<@{_ZWSP}{m.group(1)}>", sanitized)
    return sanitized


def _truncate(value: str, limit: int) -> str:
    """Discord embed の長さ制約に合わせて末尾を省略する。"""
    if len(value) <= limit:
        return value
    if limit <= 1:
        return value[:limit]
    return value[: limit - 1] + "…"


def _embed_envelope(embed: dict[str, Any]) -> dict[str, Any]:
    """Discord webhook へ送る共通封筒 (allowed_mentions 必須)。"""
    return {
        "username": "agentops-watch",
        "allowed_mentions": {"parse": []},
        "embeds": [embed],
    }


def build_digest_embed(
    kind: str,
    report: dict[str, Any],
    now_jst: datetime,
    message: str | None = None,
) -> dict[str, Any]:
    """daily / weekly / monthly digest 用 embed payload を構築する。

    `message` を渡すと embed の fields 末尾に `audit log` field として追加する。
    audit-*.sh など外部 cron スクリプトが log の要約を embed に乗せるための拡張点。
    Discord embed の field 上限 (25) と value 上限 (1024) は尊重する。message 指定時は
    audit log field の枠を確保するため project field 数を最大 24 件に制限する。
    """
    if kind == "daily":
        title = f"daily digest — {now_jst.strftime('%Y-%m-%d')}"
    elif kind == "weekly":
        iso_year, iso_week, _ = now_jst.isocalendar()
        title = f"weekly digest — {iso_year}-W{iso_week:02d}"
    elif kind == "monthly":
        title = f"monthly digest — {now_jst.strftime('%Y-%m')}"
    else:
        raise ValueError(f"build_digest_embed: not a digest kind: {kind}")

    fields: list[dict[str, Any]] = []
    for project in report.get("projects", []):
        name_raw = str(project.get("name", ""))
        git = project.get("git", {}) or {}
        ag = project.get("agentops", {}) or {}
        branch_raw = str(git.get("branch", "") or git.get("branch_summary", ""))
        dirty = int(git.get("dirty_files", 0) or 0)
        open_tasks = int(ag.get("tasks", 0) or 0)
        handoffs = int(ag.get("handoffs", 0) or 0)
        next_session = bool(ag.get("next_session_md", False))
        stuck_count = len(ag.get("runs", {}).get("stuck", []) or [])

        value_lines = [
            f"branch: {sanitize_mention_text(branch_raw) or '(unknown)'}",
            f"open tasks: {open_tasks}",
            f"handoffs: {handoffs}",
            f"next-session: {'yes' if next_session else 'no'}",
        ]
        if dirty:
            value_lines.append(f"dirty: {dirty}")
        if stuck_count:
            value_lines.append(f"stuck runs: {stuck_count}")

        fields.append(
            {
                "name": _truncate(f"project: {sanitize_mention_text(name_raw)}", _EMBED_TITLE_LIMIT),
                "value": _truncate("\n".join(value_lines), _EMBED_FIELD_VALUE_LIMIT),
                "inline": False,
            }
        )

    # message があれば audit log field を末尾に追加する。
    audit_log_field: dict[str, Any] | None = None
    if message:
        sanitized_message = sanitize_mention_text(message)
        audit_log_field = {
            "name": "audit log",
            "value": _truncate(sanitized_message, _EMBED_FIELD_VALUE_LIMIT),
            "inline": False,
        }

    if audit_log_field is not None:
        # audit log field の枠を確保するため project fields は (上限 - 1) まで。
        capped_fields = fields[: _EMBED_FIELDS_LIMIT - 1]
        capped_fields.append(audit_log_field)
    else:
        capped_fields = fields[:_EMBED_FIELDS_LIMIT]

    embed: dict[str, Any] = {
        "title": _truncate(title, _EMBED_TITLE_LIMIT),
        "color": _EMBED_COLOR["digest"],
        "fields": capped_fields,
        "footer": {"text": f"agentops-watch / {now_jst.isoformat(timespec='seconds')}"},
    }
    return _embed_envelope(embed)


def build_anttime_embed(
    kind: str,
    project: str,
    message: str,
    now_jst: datetime,
    branch: str = "",
) -> dict[str, Any]:
    """ANT_TIME 系 (session-start/end / permission-wait / alert / stop-failure) embed payload を構築する。"""
    project_safe = sanitize_mention_text(project) if project else ""
    branch_safe = sanitize_mention_text(branch) if branch else ""
    message_safe = sanitize_mention_text(message) if message else ""

    # session title に出る project basename は文字列レベルでも sanitize する
    # (allowed_mentions と二重防御、docs/18 §SECRET 管理 / payload 雛形 と整合)。
    project_short = sanitize_mention_text(Path(project).name) if project else ""

    if kind == "session-start":
        title = f"session-start: {project_short or 'unknown'}"
    elif kind == "session-end":
        title = f"session-end: {project_short or 'unknown'}"
    elif kind == "permission-wait":
        title = f"permission-wait: {message_safe or 'unknown'}"
    elif kind == "alert":
        snippet = message_safe if message_safe else "alert"
        title = f"alert: {snippet}"
    elif kind == "stop-failure":
        snippet = message_safe if message_safe else "stop-failure"
        title = f"stop-failure: {snippet}"
    else:
        raise ValueError(f"build_anttime_embed: not an ANT_TIME kind: {kind}")

    color = _EMBED_COLOR.get(kind, _EMBED_COLOR["digest"])

    fields: list[dict[str, Any]] = []
    if project_safe:
        fields.append({"name": "project", "value": _truncate(project_safe, _EMBED_FIELD_VALUE_LIMIT), "inline": True})
    if branch_safe:
        fields.append({"name": "branch", "value": _truncate(branch_safe, _EMBED_FIELD_VALUE_LIMIT), "inline": True})

    if message_safe:
        # alert は title に短い見出しを入れているので、長い本文は fields に追加。
        if kind == "alert" and len(message_safe) <= 80:
            pass
        else:
            fields.append(
                {
                    "name": "message",
                    "value": _truncate(message_safe, _EMBED_FIELD_VALUE_LIMIT),
                    "inline": False,
                }
            )

    embed: dict[str, Any] = {
        "title": _truncate(title, _EMBED_TITLE_LIMIT),
        "color": color,
        "fields": fields[:_EMBED_FIELDS_LIMIT],
        "footer": {"text": f"agentops-watch / {now_jst.isoformat(timespec='seconds')}"},
    }
    return _embed_envelope(embed)


def anttime_state_path() -> Path:
    """ANT_TIME rate-limit state の保存先を返す。XDG_CACHE_HOME を尊重する。"""
    cache_root = os.environ.get("XDG_CACHE_HOME", "")
    base = Path(cache_root) if cache_root else Path.home() / ".cache"
    return base / "agentops-watch" / "anttime-rate.json"


class AnttimeRateGuard:
    """ANT_TIME channel の頻度上限ガード。

    1 分 5 件 / 1 時間 60 件を保守値として、超過時は payload を skip させる。
    HTTP 429 を受けた場合の Retry-After もここで保存する。
    本クラスは単一プロセス前提 (lock を持たない)。
    """

    def __init__(
        self,
        state_path: Path,
        per_minute: int = 5,
        per_hour: int = 60,
    ) -> None:
        self.state_path = state_path
        self.per_minute = per_minute
        self.per_hour = per_hour

    def _load(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"events": [], "retry_after_until": 0}
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"events": [], "retry_after_until": 0}
        if not isinstance(data, dict):
            return {"events": [], "retry_after_until": 0}
        data.setdefault("events", [])
        data.setdefault("retry_after_until", 0)
        return data

    def _save(self, state: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        # 1 時間より古いイベントは保存しない (不要なファイル肥大化を避ける)。
        now_ts = jst_now().timestamp()
        cutoff = now_ts - 3600
        state["events"] = sorted(t for t in state.get("events", []) if t > cutoff)
        self.state_path.write_text(json.dumps(state), encoding="utf-8")

    def is_blocked_by_retry_after(self, now: datetime | None = None) -> tuple[bool, float]:
        """直前 invocation で 429 を受けた場合、Retry-After 残り秒数を返す。"""
        now = now or jst_now()
        state = self._load()
        until = float(state.get("retry_after_until", 0) or 0)
        now_ts = now.timestamp()
        if until > now_ts:
            return True, until - now_ts
        return False, 0.0

    def check_and_record(self, now: datetime | None = None) -> tuple[bool, str]:
        """1 分 / 1 時間の窓内のイベント数で許可判定し、許可時は記録する。"""
        now = now or jst_now()
        state = self._load()
        events = list(state.get("events", []))
        now_ts = now.timestamp()

        last_minute = sum(1 for t in events if now_ts - 60 <= t <= now_ts)
        last_hour = sum(1 for t in events if now_ts - 3600 <= t <= now_ts)

        if last_minute >= self.per_minute:
            return False, f"rate-limit: {last_minute} events in last 60s (limit {self.per_minute})"
        if last_hour >= self.per_hour:
            return False, f"rate-limit: {last_hour} events in last 3600s (limit {self.per_hour})"

        events.append(now_ts)
        state["events"] = events
        self._save(state)
        return True, "ok"

    def record_retry_after(self, retry_after_seconds: float, now: datetime | None = None) -> None:
        """HTTP 429 応答時の Retry-After を保存し、次回 invocation の skip 判定に使う。"""
        now = now or jst_now()
        state = self._load()
        state["retry_after_until"] = now.timestamp() + max(0.0, float(retry_after_seconds))
        self._save(state)


def send_webhook(
    url: str,
    payload: dict[str, Any],
    timeout: int = 10,
    opener: Any = None,
) -> tuple[int, dict[str, str]]:
    """Webhook へ POST し、HTTP status と response headers を返す。

    HTTPError 経由の 429 / 5xx は status code として上位に渡す (HTTPError は HTTP
    レスポンスとして読める)。URLError 経由の DNS / connect timeout / connection
    refused 等のネットワークエラーは status=0 を返し、上位 (`cmd_notify`) が exit 2
    に正規化する (docs/18 §DbC 停止条件: connect timeout は当該 invocation を停止)。
    エラー詳細は headers の擬似 key `X-AgentOps-NetworkError` に格納する。
    secret URL は引数経由でしか扱わず、log / stdout に出さない。
    """
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    open_func = opener or request.urlopen
    try:
        with open_func(req, timeout=timeout) as response:
            return int(response.status), {k: v for k, v in response.headers.items()}
    except urllib_error.HTTPError as exc:
        headers = {k: v for k, v in (exc.headers.items() if exc.headers else [])}
        return int(exc.code), headers
    except urllib_error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        return 0, {"X-AgentOps-NetworkError": str(reason)}
    except (TimeoutError, OSError) as exc:
        # urllib より下位 (socket) で発生する例外も網羅的に捕捉する。
        return 0, {"X-AgentOps-NetworkError": str(exc)}


def _get_branch(project_path: Path) -> str:
    """notify ANT_TIME 系で branch を表示するため、git から軽量に取得する。"""
    if not project_path.exists():
        return ""
    code, branch, _ = run_git(project_path, ["branch", "--show-current"])
    return branch if code == 0 else ""


def _legacy_notify(args: argparse.Namespace) -> int:
    """旧 envvar AGENTOPS_DISCORD_WEBHOOK_URL を使う後方互換 path。

    `--kind` 未指定で呼ばれた場合に限り動作する。stderr へ deprecation 警告を出す。
    payload には `allowed_mentions: {"parse": []}` を必須付与し、content も sanitize する
    (docs/18 §SECRET 管理 / payload 雛形 と整合)。
    """
    print(
        "warning: --kind 未指定の notify は deprecated です。"
        " --kind {daily|weekly|monthly|session-start|session-end|permission-wait|alert|stop-failure}"
        " を指定してください。旧 envvar "
        f"{LEGACY_ENVVAR} は将来撤去されます。",
        file=sys.stderr,
    )
    try:
        report = build_report(args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    content = sanitize_mention_text(render_text(report))[:1900]
    payload = {"content": content, "allowed_mentions": {"parse": []}}
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    webhook = os.environ.get(LEGACY_ENVVAR)
    if not webhook:
        print(f"{LEGACY_ENVVAR} is not set", file=sys.stderr)
        return 2

    status, _ = send_webhook(webhook, payload, timeout=args.timeout)
    if status in (200, 204):
        print(f"discord notification sent: HTTP {status}")
        return 0
    print(f"error: discord webhook returned HTTP {status}", file=sys.stderr)
    return 2


def _validate_anttime_args(kind: str, args: argparse.Namespace) -> str | None:
    """ANT_TIME 系 kind の必須引数を検査する。エラーメッセージを返す (OK は None)。

    `--bypass-rate-limit` は docs/18 §ANT_TIME 頻度上限ガードで「緊急 alert
    (`--kind alert --priority high`)」のみ bypass 選択肢を残す契約。それ以外の
    kind / priority で bypass 指定された場合はエラーにする。
    """
    if kind in {"session-start", "session-end", "permission-wait", "stop-failure"}:
        if not args.project:
            return f"--kind {kind} requires --project <path>"
    if kind in {"permission-wait", "alert", "stop-failure"}:
        if not args.message:
            return f"--kind {kind} requires --message <text>"
    if args.bypass_rate_limit and kind in ANTTIME_KINDS:
        if not (kind == "alert" and args.priority == "high"):
            return "--bypass-rate-limit requires --kind alert --priority high"
    return None


def cmd_notify(args: argparse.Namespace) -> int:
    """Discord webhook へ kind 別 digest / alert を送る。

    --kind 指定が新 path、未指定が旧 envvar 後方互換 path (deprecation 警告つき)。
    secret 値 (Webhook URL) は env 経由でしか扱わず、stdout / log に出さない。
    """
    if not args.kind:
        return _legacy_notify(args)

    kind = args.kind
    now = jst_now()

    # ANT_TIME 系 kind の必須引数検査。
    validation = _validate_anttime_args(kind, args)
    if validation:
        print(f"error: {validation}", file=sys.stderr)
        return 2

    # 送信モード (非 dry-run) では webhook envvar 未設定を rate-guard より前に検出する。
    # 後で検出すると rate-guard で skip した時の exit 0 に「未設定 = exit 2」が隠れる
    # (docs/18 §DbC: webhook URL 未設定で実送信を求められた場合は CLI 全体を停止)。
    webhook_url: str | None = None
    if not args.dry_run:
        envvar, webhook_url = resolve_webhook_url(kind)
        if not webhook_url:
            print(f"error: {envvar} is not set", file=sys.stderr)
            return 2

    # ANT_TIME channel に乗る kind は rate-limit guard 対象。
    # dry-run では state を変更しない (preview の副作用回避)。
    # Retry-After block は bypass 不可 (Discord 側 rate-limit は常に尊重)。
    # `--bypass-rate-limit` は自前の 1 分 / 1 時間窓ガードにのみ作用する。
    rate_guard: AnttimeRateGuard | None = None
    if kind in ANTTIME_KINDS and not args.dry_run:
        rate_guard = AnttimeRateGuard(anttime_state_path())
        blocked, remaining = rate_guard.is_blocked_by_retry_after(now)
        if blocked:
            print(
                f"warning: blocked by Retry-After for {remaining:.0f}s, skipping",
                file=sys.stderr,
            )
            return 0
        if not args.bypass_rate_limit:
            allowed, reason = rate_guard.check_and_record(now)
            if not allowed:
                print(f"warning: {reason}, skipping", file=sys.stderr)
                return 0
        else:
            # bypass する場合でも記録だけは進める (連続送信時の上限カウントとして機能)。
            rate_guard.check_and_record(now)

    # payload 構築。
    payload: dict[str, Any]
    if kind in DIGEST_KINDS:
        try:
            report = build_report(args)
        except (FileNotFoundError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        # digest kind では --message を任意 audit log として embed に乗せる
        # (audit-*.sh 等の cron スクリプトが log 要約を渡す経路)。
        payload = build_digest_embed(kind, report, now, message=args.message)
    else:
        project = ""
        branch = ""
        if args.project:
            project_path = Path(args.project).expanduser().resolve()
            project = str(project_path)
            branch = _get_branch(project_path)
        payload = build_anttime_embed(
            kind=kind,
            project=project,
            message=args.message or "",
            now_jst=now,
            branch=branch,
        )

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    # webhook_url は dry-run でない時だけ設定済 (上で None なら exit 2 済み)。
    assert webhook_url is not None
    status, headers = send_webhook(webhook_url, payload, timeout=args.timeout)
    if status in (200, 204):
        print(f"discord notification sent: HTTP {status}")
        return 0

    # status=0 はネットワークエラー (DNS / connect timeout / connection refused)。
    # docs/18 §DbC 停止条件と整合する exit 2 に正規化する。
    if status == 0:
        reason = headers.get("X-AgentOps-NetworkError", "unknown")
        print(f"error: discord webhook network error: {reason}", file=sys.stderr)
        return 2

    # 429 / 5xx: CLI 全体を停止する。Retry-After は HTTP 429 のときだけ state に記録する
    # (docs/18 §DbC: HTTP 429 を受けた場合に Retry-After を記録、5xx では記録しない)。
    retry_seconds = 0.0
    retry_header = headers.get("Retry-After") or headers.get("retry-after")
    if retry_header:
        try:
            retry_seconds = float(retry_header)
        except ValueError:
            retry_seconds = 0.0
    if status == 429 and rate_guard is not None and retry_seconds > 0:
        rate_guard.record_retry_after(retry_seconds, now)
    print(
        f"error: discord webhook returned HTTP {status} (retry_after={retry_seconds}s)",
        file=sys.stderr,
    )
    return 2


def build_parser() -> argparse.ArgumentParser:
    """agentops-watch CLI のサブコマンドと共通引数を定義する。"""
    parser = argparse.ArgumentParser(prog="agentops-watch", description="AgentOps local monitoring CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(target: argparse.ArgumentParser) -> None:
        """check / notify で共有する監視対象指定の引数を追加する。

        --project default は None。load_projects 側で cwd (".") にフォールバックする。
        notify の `--kind alert` で project を optional にする要件と整合させるため。
        """
        target.add_argument("--project", default=None)
        target.add_argument("--projects")
        target.add_argument("--freshness", default="config/freshness-sources.yml")

    check = sub.add_parser("check", help="check local project state")
    add_common(check)
    check.add_argument("--json", action="store_true")
    check.set_defaults(func=cmd_check)

    notify = sub.add_parser("notify", help="send or preview a Discord digest")
    add_common(notify)
    notify.add_argument(
        "--kind",
        choices=sorted(KIND_TO_ENVVAR.keys()),
        default=None,
        help="通知 kind。未指定は deprecated な旧 envvar path。",
    )
    notify.add_argument("--message", default=None, help="permission-wait / alert / stop-failure の本文")
    notify.add_argument(
        "--priority",
        choices=["low", "high"],
        default="low",
        help="alert 用優先度 (現状は表示には使わない、将来の bypass 判定用)",
    )
    notify.add_argument(
        "--bypass-rate-limit",
        action="store_true",
        help="ANT_TIME rate-limit を bypass する (緊急 alert 用、Discord 側 rate-limit は依然尊重)",
    )
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
