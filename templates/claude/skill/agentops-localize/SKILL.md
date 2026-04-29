---
name: agentops-localize
description: 既存プロジェクトに残る Claude Code / Codex / Antigravity / Cursor / Gemini 等の設計痕跡を inventory 化し、4 戦略 (greenfield / inventory-rebuild / coexistence / freeze) のうち 1 つを推奨する。新規 onboarding やグローバル設計改訂後の既存プロジェクト見直しで起動する。
---

# agentops-localize

既存プロジェクトの設計痕跡と新グローバル設計の競合を判定し、適用戦略を決めるための skill。詳細仕様は [docs/19-project-localization.md](../../../../docs/19-project-localization.md) を参照する。

## Instructions

1. 対象 project path をユーザーに確認する。`~/dev/<name>` 配下を既定とする。dotfiles や `~/.claude` / `~/.codex` 配下は対象外。
2. 痕跡 inventory を取得する。検出対象は深さ 2 まで (詳細は [docs/19 §検出対象 inventory](../../../../docs/19-project-localization.md)):
   - Claude Code: `CLAUDE.md` (subproject 含む) / `.claude/` (dir) / `.claude` (0-byte file)
   - Codex: `AGENTS.md` (subproject 含む) / `.codex/` (dir) / `.codex` (0-byte file) / `AGENTS.override.md`
   - Gemini: `GEMINI.md` (root or subdir) / `.gemini/` / `.agent/`
   - 本人標準 / 共通: `.ai/` (contracts / decisions / gates / memory / reviews / tasks 等) / `.agentops/`
   - その他: `.cursorrules` / `.cursor/` / `.aider*` / `.windsurfrules` / `.antigravity/` / `.continue/` / `.copilot/`
   - 未列挙の `.<vendor>/` / `.<vendor>rules` / `<VENDOR>.md` を発見したら user 確認に escalate (docs/19 §検出網羅性)。ただし docs/19 §除外対象 dot dir / dot file (`.git/` / `.github/` / `.wrangler/` / `.playwright-mcp/` / `.tmp/` / `.cache/` / `.next/` 等) は AI 設計痕跡ではないため escalate 不要
   - 補助情報: `package.json` / `go.mod` / `composer.json` 等で技術スタック判定。`git log -1 --format=%cI -- CLAUDE.md AGENTS.md GEMINI.md` で痕跡の鮮度判定。
3. 競合判定マトリクスで「低 / 中 / 高」評価を出す。具体パターンは docs/19 の表を参照する。
4. 4 戦略の意思決定木 (docs/19) に当てはめ、1 戦略を選ぶ。複数戦略が該当する場合は user 確認に escalate (停止条件)。
5. inventory + 推奨戦略 + 戦略チェックリストの未完了項目を report し、`~/.claude/.agentops/runs/<run-id>/inventory.md` または対象 project の `.agentops/runs/` に書き出す。
6. ユーザー承認後、選んだ戦略の実マイグレーションは別 plan で扱う (本 skill は判定までで終える)。

## 使う tools

- Read / Glob / Grep / Bash (read-only) — 痕跡検出と git log
- 書き込みは inventory report のみ。既存 project ファイルを書き換えない。

## 停止条件

- project path が読めない、または `.git/` 配下のみに痕跡がある
- 4 戦略すべてが該当する判定軸の不足
- 痕跡ファイルから secret / 認証情報 / 個人データを inventory に書き写しそうになった
- ユーザー承認なしに既存ファイルを変更しようとした
- グローバル設計改訂と project の独自運用が衝突し統合判断を主 orchestrator から user に escalate すべき場合
- 上記検出対象に列挙されない `.<vendor>/` / `.<vendor>rules` / `<VENDOR>.md` を発見した場合は user 確認に escalate (docs/19 §検出網羅性)。docs/19 §除外対象 dot dir / dot file に該当する generic 痕跡 (`.git/` / `.github/` / `.wrangler/` / `.playwright-mcp/` / `.tmp/` / `.cache/` 等) は escalate 不要

## 出力

- inventory.md (痕跡一覧 + 鮮度 + 競合度)
- 推奨戦略 + 主な根拠
- 戦略のチェックリスト (移行物 / 廃棄物 / 残しもの / 検証 / archive 方針)
- 別 plan へのハンドオフ提案

## Notes

- agentops は **AI agent lifecycle hook (SessionStart / SessionEnd / PreToolUse / PostToolUse / PermissionRequest 等) の実体は持たない方針** (Git pre-commit / pre-push 等の VCS hook は別カテゴリで `scripts/hooks/` に存在)。本 skill が呼ぶ操作は read-only inventory + report 書き出しのみ。
- 将来 `agentops localize` CLI が追加されたら、本 skill から CLI 呼び出しに置き換えてよい (現時点では skill 内で Bash 経由で `find` / `git log` を実行)。
- description に「新規 onboarding」「グローバル設計改訂後の見直し」を明示しているのは、skill auto-trigger を確実にするため。
- `allowed-tools` frontmatter は本雛形では **未指定** とする。Claude Code の `allowed-tools` は active skill 中の **事前許可 (auto-approve allowlist)** であり、未列挙ツールも permission settings 次第で callable で、ツール利用そのものを制限する仕組みではない。読み取り限定を機械的に保証したい場合は `~/.claude/settings.json` の permission deny rules で別途制御する必要がある (本 skill のスコープ外)。
- 仮に `allowed-tools` を指定する場合は、Bash のような広い指定を避け、`Read` / `Glob` / `Grep` と、Bash は `Bash(find:*)` / `Bash(git log:*)` / `Bash(stat:*)` 等の最小パターンに絞る (read-only inventory 目的に対し `Bash` 一括は広すぎる)。`Write` / `Edit` は付けない (skill のスコープが read-only inventory + report 書き出しのみのため)。
- 本文「使う tools」の平文記述は仕様確定までの暫定指針であり、実機械的 enforcement ではない。実反映前に Claude Code 公式 skills 仕様 (`code.claude.com/docs/en/skills`) と permission settings 仕様を Context7 で確認する。
