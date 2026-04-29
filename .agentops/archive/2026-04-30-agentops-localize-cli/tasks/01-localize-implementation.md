---
task-id: 01-localize-implementation
parent-plan: ../plans/current.md
created: 2026-04-30
status: in-progress
pr-target: PR (agentops localize CLI 実装)
branch: claude/agentops-localize-cli-2026-04-30
---

# Task 01: agentops localize CLI 実装

## 前提条件

- `docs/19-project-localization.md` (PR #59 merge 済) を仕様の真ソースとする
- `docs/10-cli-wrapper.md` の `localize` spec に整合
- 既存 `tools/agentops_cli/__main__.py` の `delegate` / `runs` / `doctor` / `archive` は破壊しない
- Python 3.11+ 標準ライブラリのみ (subprocess / pathlib / json / argparse / datetime / zoneinfo / shutil / fnmatch)
- 高リスク領域該当なし (主に read-only 監視) だが、誤って既存 project ファイル書き換えのリスク → 不変条件で対策

## 不変条件

- **既存 project ファイルを書き換えない** (`--dry-run` モードのみ。本 plan では `--apply` 未実装)
- secret / 認証情報 / Webhook URL の値 / 個人 data を inventory / log / stdout に書かない
- 痕跡内容の長文をそのまま転載しない (パス・存在・サイズ・鮮度のみ。docs/19 §不変条件)
- グローバル run log は `~/.claude/.agentops/runs/<run-id>/inventory.md` または対象 project の `.agentops/runs/` に保存
- 検出対象に列挙されていない `.<vendor>/` / `.<vendor>rules` / `<VENDOR>.md` は **未列挙痕跡として report に escalate** (docs/19 §検出網羅性)

## 完了条件

- `tools/agentops_cli/__main__.py` に `localize` サブコマンド追加:
  - 引数: `--project <path>` (default `.`)、`--strategy {auto,greenfield,inventory-rebuild,coexistence,freeze}` (default `auto`)、`--dry-run` (default true、明示 flag は no-op で互換)、`--run-id`
  - 出力: stdout に Markdown report + `~/.claude/.agentops/runs/<run-id>/inventory.md` に同内容を保存
- 痕跡検出 (depth-2):
  - **Claude**: `CLAUDE.md` (root + subdir)、`.claude/` (dir)、`.claude` (0-byte file)
  - **Codex**: `AGENTS.md` (root + subdir)、`.codex/`、`.codex` (0-byte)、`AGENTS.override.md`
  - **Gemini**: `GEMINI.md` (root + subdir)、`.gemini/`、`.agent/`
  - **Other**: `.antigravity/`、`.cursorrules`、`.cursor/`、`.aider*`、`.windsurfrules`、`.continue/`、`.copilot/`
  - **Personal**: `.ai/`、`.agentops/`
- 除外対象 (docs/19 §除外対象):
  - VCS: `.git/`、`.github/`、`.gitlab/`、`.gitignore`、`.gitattributes`
  - runtime/cache: `.tmp/`、`.cache/`、`.next/`、`.nuxt/`、`.svelte-kit/`、`.vite/`、`.turbo/`、`.parcel-cache/`、`node_modules/.cache/`
  - deploy: `.wrangler/`、`.vercel/`、`.netlify/`、`.firebase/`、`.gcloud/`
  - IDE: `.vscode/`、`.idea/`、`.zed/`、`.fleet/`
  - env: `.venv/`、`.python-version`、`.tool-versions`、`.nvmrc`
  - test: `.playwright-mcp/`、`.playwright/`
- 鮮度判定:
  - 各痕跡の `stat().st_mtime` を Asia/Tokyo で日付化
  - bucket: `≤30d`, `31-180d`, `180+d`, `unknown`
  - 補助: `git log -1 --format=%cI -- <path>` で最終 commit 鮮度
- 技術スタック推定:
  - `package.json` → Node (deps から `nuxt` / `next` / `react` / `vue` を抽出)
  - `go.mod` → Go
  - `composer.json` → PHP
  - `Cargo.toml` → Rust
  - `Gemfile` → Ruby
  - `pyproject.toml` / `requirements.txt` → Python
- git activity:
  - last commit (any file): `git log -1 --format=%cI`
  - 30 日内 commit 数: `git rev-list --count HEAD --since="30 days ago"`
- 4 戦略意思決定 (docs/19 §4 戦略の意思決定木):
  - 痕跡なし or AGENTS.md のみ最小 → `greenfield`
  - 痕跡 180 日以上前 + 休止 (30 日内 commit 0) → `freeze`
  - 痕跡 ≤30d OR (31-180d + substantial `.agent/.ai/.claude` 構造) + 30 日内 commit 1 件以上 + 競合度中〜高 → `inventory-rebuild`
  - 競合度低〜中 + 短命/プロト判定 → `coexistence`
  - 上記いずれにも該当しない → user 確認 escalate (`strategy: needs-user-confirmation`)
- 競合度判定 (docs/19 §競合判定マトリクス を簡易評価):
  - `.claude/plans/` あり + `.agentops/` なし → 高
  - `.claude/hooks/` の独自 hook → 中〜高 (hooks dir 内ファイル数で判定)
  - `.cursorrules` のみ → 低
  - `.ai/` フル構造 + `.agentops/` なし → 高
  - default: 中
- report 出力:
  - 必須セクション: project / generated_at / run_id / strategy / inventory / tech stack / git activity / freshness summary / conflict assessment / recommended strategy / reasoning / checklist / unlisted traces
  - sanitize: SECRET / Webhook URL の文字列が報告対象 file path や args に紛れた場合は ZWSP 挿入で無害化 (agentops_monitor の `sanitize_mention_text` を再利用しないが、相当の対処を localize 内で実施)
- run log 保存:
  - グローバル: `~/.claude/.agentops/runs/<run-id>/inventory.md` (`XDG_DATA_HOME` を尊重しない、`~/.claude/` 既定)
  - run-id 命名: `<JST timestamp>-<sanitized-project-name>-localize`
- 単体テスト追加 (`tools/agentops_cli/tests/`):
  - tests dir 新設 (`__init__.py` + `test_localize.py`)
  - tempdir で fixture project 作成 → 各カテゴリ痕跡検出
  - 除外対象 (`.git/` 等) が検出されない
  - 戦略判定 4 戦略 + escalate
  - 競合度判定の主要パターン
  - run log 保存先が tempdir に閉じる (テスト中に host `~/.claude/` を汚染しない)
- docs 更新:
  - `docs/10-cli-wrapper.md`: 実装ステータス注記を `localize` 実装済に更新
  - `docs/19-project-localization.md`: §CLI 仕様 を「実装済」表記に更新
- 検証:
  - `python3 -m compileall tools/` exit 0
  - `python3 -m unittest discover tools/agentops_cli/tests` 既存維持 + 新規テスト pass
  - 既存 monitor tests 76 件も regression なし
  - dry-run smoke: `scripts/agentops localize --project /home/otaku/agentops --dry-run` で agentops 自身を inventory
  - secret (実 webhook URL) 混入なし
- Codex `review_frontier --effort high` cross-review で P0/P1 0 件 (1〜2 round 想定)
- archive 移動 + commit + push + PR + auto-merge (許諾条件下)

## 禁止事項

- 既存 project ファイルを書き換える / delete / move
- 既存 `delegate` / `archive` 実装の挙動を変更
- 痕跡内の SECRET / 認証情報 / 個人 data を inventory に転載
- skill `templates/claude/skill/agentops-localize/SKILL.md` の実体を変更 (本 plan は skill 雛形だけ参照)
- `--apply` モードや本反映機能を実装 (将来仕様、本 plan のスコープ外)
- 5 主要プロジェクト以外で勝手に dry-run を広げる (docs/19 §禁止事項)

## 停止条件

- レビュー修正が 2 周を超える → user 確認
- secret 値が誤って報告に混入 → 即停止
- docs/19 仕様と実装の乖離が plan 中に判明 → docs/19 を真ソースに合わせる、必要なら user 確認
- 4 戦略どれにも該当しない判定不能ケースで auto 推奨を強制しようとする → user 確認 escalate に切り替え
- mock なしで実 host `~/.claude/.agentops/runs/` を汚染しそう → 設計変更してテスト独立性を確保

## 検証手順

1. `python3 -m compileall tools/`
2. `python3 -m unittest discover tools/agentops_cli/tests -v`
3. `python3 -m unittest discover tools/agentops_monitor/tests` (既存 76 件 regression なし)
4. `scripts/agentops localize --project /home/otaku/agentops --dry-run` → strategy + inventory が stdout
5. `scripts/agentops localize --project /home/otaku/dev/ai-engine --dry-run` → docs/19 表と整合 (inventory-rebuild 推奨想定)
6. `ls ~/.claude/.agentops/runs/` で run log が増えている
7. `grep -rn 'discord.com/api/webhooks/[0-9]' tools/ docs/ scripts/` → 0 件
8. agentops-reviewer subagent で独立レビュー
9. `scripts/agentops delegate --to codex --role review_frontier --effort high --input tools/agentops_cli/__main__.py`
10. P0/P1 反映後、reviewer 再走で 0 件
11. archive + commit + push + PR + auto-merge

## DbC

- **適用前提**: docs/19 / docs/10 仕様が変更されていない、Python 3.11+ 標準ライブラリのみ、`delegate` / `archive` 既存挙動を破壊しない
- **適用不変**: 既存 project 書き換えなし、SECRET 値非露出、痕跡内容長文転載なし
- **適用完了**: 上記「完了条件」全項目
- **適用禁止**: 上記「禁止事項」記載
- **適用停止**: 上記「停止条件」のいずれか発生
