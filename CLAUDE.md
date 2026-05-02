@AGENTS.md

# agentops プロジェクト指示 — Claude Code 固有差分

本ファイルは `@AGENTS.md` で `AGENTS.md` 全文を Claude Code の context に展開した上で、Claude Code 固有のパス・確認コマンド・branch prefix のみを追記します。共通章（位置づけ / 記録先 / グローバル設定 / Git / 完了 / 停止 / AI auto-merge 許諾）は `AGENTS.md` を参照する。

## Claude Code 固有のパスと確認方法

`AGENTS.md` §記録先 と §グローバル設定 (`~/.claude/` / `~/.codex/`) を触る作業 で並列記述している項目のうち、本セッションが Claude Code で動いている前提での値:

- 雛形 → 反映先: `config/claude/CLAUDE.md` → `~/.claude/CLAUDE.md`
- 関連実ファイル: `~/.claude/CLAUDE.md`、`~/.claude/settings.json`、`~/.claude/skills/`、`~/.claude/agents/`、`~/.claude/plugins/`、`~/.claude/` 配下の hooks、MCP 設定、permission
- 記録ディレクトリ: `~/.claude/.agentops/`、一時ファイル `~/.claude/.agentops/.tmp/`
- 確認コマンド: `claude --version`、`claude --help`、`/memory`、`/config`、`/mcp`
- 作業ブランチ prefix: `claude/`

## メモ

- `AGENTS.md` §AI auto-merge 許諾 の「主 orchestrator」は本セッションで使う Claude Code を指します。許諾条件・停止条件・後処理は `AGENTS.md` 記述のとおりです。
- `AGENTS.md` §AI auto-merge 許諾 の「設計段階 cross-review (高リスク plan で必須)」は、本セッション (主 Claude) では reviewer が **Codex** (`--to codex`) になります。実施は実装着手前、5 工程フロー (`rules/model-routing.md`) の工程 2 に相当し、工程 2 の `kind: design` 指摘は orchestrator が user 確認を再取得 (run A 未起動のため再委譲先がない)、`kind: mechanical` は parent plan ファイル直接 patch で反映します。
- `AGENTS.md` §AI auto-merge 許諾 の工程 4 は、4-α 同系列独立実装レビュー (Codex 別 session、cross-review ではない) と 4-β cross-review (実装担当 Codex と別系列の Claude review_frontier) を分けて扱う。
- `AGENTS.md` は両 CLI 共通の真ソースです。Claude Code 固有 project 差分は本ファイル（CLAUDE.md）に追記します。Codex 固有 project 差分は `AGENTS.md` 内の Codex 固有セクション、または agentops repo に意図的に導入する `AGENTS.override.md` に置きます（`config/codex/AGENTS.md` は `~/.codex/AGENTS.md` グローバル反映用の **雛形** であり、本 repo 内の project instruction ではないため使用しません）。両 CLI 共通の更新は `AGENTS.md` 単独で完結させてください。
- `@AGENTS.md` 構文は Claude Code の memory file import 公式仕様（`code.claude.com/docs/en/memory` §AGENTS.md）に従っています。本 repo を初めて開いた Claude Code セッションでは初回 import 承認 dialog が出る場合があります（公式 docs 既知挙動）。
