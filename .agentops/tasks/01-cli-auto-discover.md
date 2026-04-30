---
task-id: 01-cli-auto-discover
plan-id: 2026-04-30-discord-cron-3tier-redesign
status: in-progress
branch: claude/discord-cron-3tier-pr-a-auto-discover
pr-target: A
started: 2026-04-30T17:30:00+09:00
---

# PR-A: agentops-watch CLI auto-discovery 拡張

## 目的

`tools/agentops_monitor/__main__.py` に `--auto-discover` flag を追加し、ハードコードされた 4 root (`~/.claude` `~/.codex` `~/agentops` `~/dev/*`) から `.agentops/` を持つ project を自動列挙できるようにする。

これにより `docs/18-notification-strategy.md:78-84` の多プロジェクト走査ルール契約と CLI 実装の gap を埋める。

## 変更ファイル

- `tools/agentops_monitor/__main__.py:265-320` — `discover_projects()` / `iter_discovery_candidates()` / `is_agentops_project()` helper 追加、`load_projects()` 改修
- `tools/agentops_monitor/__main__.py:872-880` — `add_common()` に `--auto-discover` flag 追加
- `tools/agentops_monitor/tests/test_auto_discover.py` — 新規 test file

## DbC

### 前提条件
- `~/.claude` `~/.codex` `~/agentops` `~/dev` のうち少なくとも 1 つの root が読み取り可能
- 既存 `--projects config/projects.yml` 経路が動作している (regression base)

### 不変条件
- `--projects` 指定時の挙動 (`docs/18` DbC 「`--projects` YAML 読み込み失敗は invocation 停止」) を維持
- `Project` dataclass を新設しない (`dict[str, Any]` の戻り型を維持)
- secret 値 (webhook URL / API token) を log / stdout に出さない

### 完了条件
- `python3 -m unittest discover tools/agentops_monitor/tests` 全 test green
- `python3 -m compileall tools` exit 0
- 新規 `test_auto_discover.py` が以下を網羅:
  - 4 root mock で `discover_projects()` が `.agentops/` 持ち project のみ返す
  - 排他制約 (`--projects` と `--auto-discover` 同時指定で `ValueError`)
  - 0 件マッチ時に空 list を返す (空 embed 1 通送信を許す)
  - broken symlink / OSError は continue で skip
- `agentops-watch notify --kind daily --auto-discover --dry-run` で 4 root 由来 payload が出力される
- secret regex (`sk-` `xoxb-` `ghp_` `discord.com/api/webhooks`) が dry-run 出力に出ない
- 既存 `--projects config/projects.yml` 経路 regression なし

### 禁止事項
- `Project` dataclass 化
- `--auto-discover` を default ON (既存 cron / hook の後方互換性破壊)
- cwd fallback 挙動の変更
- `~/dev/*` glob max depth を 1 超に拡大 (panic safety)
- `~/.claude/runs/` `~/.codex/log/` 配下の free text を読む (secret 漏洩防止)

### 停止条件
- 既存 `--projects` 経路の regression 検出
- 4 root 全て read 不可で OSError 連発 (実行環境異常)
- tests 修正が 2 周を超える
- secret 値が log / stdout に出る経路を発見

## 設計詳細

### 新規 helper (`__main__.py:265` 付近)

```python
_DISCOVERY_ROOTS = (
    Path.home() / ".claude",
    Path.home() / ".codex",
    Path.home() / "agentops",
    # ~/dev/* は別 helper で 1 階層 glob 展開
)

def iter_discovery_candidates() -> Iterator[Path]:
    """4 root を walk し、.agentops 持ち候補 path を yield する。
    
    broken symlink / OSError は continue で skip。max depth は 1 (~/dev/foo まで)。
    """

def is_agentops_project(path: Path) -> bool:
    """path/.agentops が directory として存在することのみで True。
    
    空の .agentops/ も True (ユーザー方針: 対象を絞らず必ず scan)。
    """

def discover_projects() -> list[dict[str, Any]]:
    """auto-discovery 結果を load_projects() と同じスキーマで返す。
    
    重複 path を set で dedupe、戻り値は list[dict] で `name` / `path` を持つ。
    """
```

### `load_projects()` 改修 (`__main__.py:298-320`)

優先順位: `--projects > --auto-discover > --project > cwd fallback`

```python
def load_projects(args: argparse.Namespace) -> list[dict[str, Any]]:
    if getattr(args, "projects", None) and getattr(args, "auto_discover", False):
        raise ValueError("--projects and --auto-discover are mutually exclusive")
    if args.projects:
        # 既存ロジックそのまま
        ...
    if getattr(args, "auto_discover", False):
        return discover_projects()  # 0 件でも空 list を返す (CLI 停止しない)
    project = args.project or "."
    return [{"name": Path(project).resolve().name, "path": project}]
```

### `add_common()` 拡張 (`__main__.py:872-880`)

```python
target.add_argument(
    "--auto-discover",
    action="store_true",
    help="~/.claude/.agentops, ~/.codex/.agentops, ~/agentops/.agentops, ~/dev/*/.agentops を浅く走査して digest 対象を自動列挙する。--projects と排他。",
)
```

### tests (`tools/agentops_monitor/tests/test_auto_discover.py`)

既存 `test_cmd_notify.py` の patterns 踏襲:
- `tmp_path` fixture を `HOME` patch で root に
- 4 root 配下に `.agentops/` 有無 / broken symlink / 空 dir を作る
- `discover_projects()` 単体 test
- `load_projects()` 経由 test (排他 / 0 件 / fallback)
- `cmd_notify` 経由の dry-run test (4 root 由来 payload が embed の field に並ぶ)

## 検証手順

```bash
# 1. tests
cd /home/otaku/agentops
python3 -m unittest discover tools/agentops_monitor/tests

# 2. compileall
python3 -m compileall tools

# 3. dry-run (実 4 root を読む)
./scripts/agentops-watch notify --kind daily --auto-discover --dry-run

# 4. 既存 --projects 経路の regression
./scripts/agentops-watch notify --kind daily --projects config/projects.yml --dry-run

# 5. 排他チェック
./scripts/agentops-watch notify --kind daily --auto-discover --projects config/projects.yml --dry-run
# → exit 2 + ValueError メッセージ
```

## cross-review

- delegate 先: `scripts/agentops delegate --to codex --role review_frontier --effort high --input tools/agentops_monitor/__main__.py`
- レビュー観点: secret 漏洩、既存 `--projects` 経路 regression、4 root walk の panic safety、test coverage の十分性
- run 記録: `.agentops/runs/<ts>-pr-a-cli-auto-discover/`

## auto-merge 許諾条件

- DbC 完了 (上記)
- cross-review P0/P1 = 0
- CI green (`python3 -m unittest` + `python3 -m compileall`)
- secret 未混入
- scope 単一 (PR-A のみ、他 PR を混ぜない)

## ロールバック path

- `--auto-discover` flag を wrapper 側で渡さなければ behavior 変わらず (新 wrapper script は PR-C で導入)
- `--projects` 既存経路は触っていないので即時 fallback 可能
