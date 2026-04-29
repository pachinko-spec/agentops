@AGENTS.md

# agentops プロジェクト指示 — Claude Code 固有差分

本ファイルは `@AGENTS.md` で `AGENTS.md` 全文を Claude Code の context に展開した上で、Claude Code 固有のパス・確認コマンド・branch prefix のみを追記します。共通章（位置づけ / 記録先 / グローバル設定 / Git / 完了 / 停止 / AI auto-merge 許諾）は `AGENTS.md` を参照してください。

## Claude Code 固有のパスと確認方法

`AGENTS.md` §記録先 と §グローバル設定 (`~/.claude/` / `~/.codex/`) を触る作業 で並列記述している項目のうち、本セッションが Claude Code で動いている前提での値:

- 雛形 → 反映先: `config/claude/CLAUDE.md` → `~/.claude/CLAUDE.md`
- 関連実ファイル: `~/.claude/CLAUDE.md`、`~/.claude/settings.json`、`~/.claude/skills/`、`~/.claude/agents/`、`~/.claude/plugins/`、`~/.claude/` 配下の hooks、MCP 設定、permission
- 記録ディレクトリ: `~/.claude/.agentops/`、一時ファイル `~/.claude/.agentops/.tmp/`
- 確認コマンド: `claude --version`、`claude --help`、`/memory`、`/config`、`/mcp`
- 作業ブランチ prefix: `claude/`

## メモ

- `AGENTS.md` §AI auto-merge 許諾 の「主 orchestrator」は本セッションで使う Claude Code を指します。許諾条件・停止条件・後処理は `AGENTS.md` 記述のとおりです。
- `AGENTS.md` は両 CLI 共通の真ソースです。Claude Code 固有 / Codex 固有で記述が分かれる場合のみ、本ファイル（CLAUDE.md）または `config/codex/AGENTS.md`（Codex 固有グローバル雛形）を更新します。両 CLI 共通の更新は `AGENTS.md` 単独で完結させてください。
- `@AGENTS.md` 構文は Claude Code の memory file import 公式仕様（`code.claude.com/docs/en/memory` §AGENTS.md）に従っています。本 repo を初めて開いた Claude Code セッションでは初回 import 承認 dialog が出る場合があります（公式 docs 既知挙動）。
