---
plan-id: 2026-04-30-applies-to-and-trinity
created: 2026-04-30
status: in-progress
parent-docs: docs/00-glossary.md, docs/18-notification-strategy.md, docs/11-monitoring-cli.md
last_reviewed: 2026-04-30
---

# Plan: applies-to frontmatter 導入 + 三役宣言 + Discord 通知 docs 改修

## Context

agentops repo は Claude Code / Codex のグローバル設定の **設計思想カタログ** として運用されているが、別 AI エージェントが docs を読んだとき以下の誤判定が発生する設計上の問題が前セッション (2026-04-30) で user により提起された:

1. docs を「これは agentops 内部運用専用」と誤読し、本来グローバル設定に反映すべき思想を反映しない
2. 実 host 全体で共有する Discord 通知 / hook 仕様 (CLI / 思想) と、agentops repo 自身の運用 docs が同じ `docs/` 配下に同列で並んで区別不能
3. 「Discord 通知は agentops repo の共有 CLI に集約 + 各層 (cron / hook / shell) から呼ぶ」という shared-cli-spec パターンが docs に明示されていない

意図する成果:

- 全 20 docs に **`applies-to`** frontmatter を機械可読で付与し、別 AI が分類可能にする (4 値: `global` / `shared-cli-spec` / `agentops-internal` / `template-source`)
- AGENTS.md / README.md トップで agentops の **三役** ((a) 設計思想カタログ / (b) 共有 CLI / ライブラリ / (c) 雛形配布元) を明示
- docs/18 / docs/11 に **shared-cli-spec パターン** (思想は global、実装は agentops 共有 CLI) を section として追加
- グローバル設定 (`~/.claude/` / `~/.codex/`) と dotfiles は本 plan で touch しない

## 親 task 一覧

- [01-applies-to-and-trinity](../tasks/01-applies-to-and-trinity.md) — 全 docs frontmatter 付与 + 三役宣言 + shared-cli-spec パターン明示

## スコープ外 (別 plan へ)

- `tools/agentops_cli/__main__.py` `doctor` の frontmatter lint 拡張 (user prompt で optional)
- `~/.claude/` / `~/.codex/` グローバル設定への反映
- dotfiles 編集
- B-rest (notify-pending-discord 修復)

## 完了条件

- task 01 の DbC 完了条件すべて
- Codex `review_frontier --effort high` cross-review で P0/P1 0 件 (or 反映済)
- 既存 frontmatter 4 フィールド (`last_reviewed` / `next_review_by` / `reviewer` / `language`) の値を変えていない
- 全 20 docs に `applies-to` frontmatter が付与され parse 可能
- AGENTS.md + README.md に三役宣言が追加済
- docs/18 + docs/11 に shared-cli-spec パターン明示済
- `python3 -m pytest tools/agentops_cli/tests tools/agentops_monitor/tests -q` 全 pass (regression なし)
- `markdown-link-check` 全 pass
- secret 未混入
- archive 移動 + commit + push + PR + auto-merge (許諾条件下) + main 同期確認

## 停止条件

- レビュー修正 2 周超過 → user 確認
- secret 値混入 → 即停止
- frontmatter parse 不能 (構文エラー)
- 既存テスト or markdown-link-check の regression
- 既存 docs に applies-to を付与しようとして本文の意味が変わる
- 別 AI 誤判定の余地が残ると判明 → 分類見直しを別 plan に escalate
- scope が `~/.claude/` / `~/.codex/` / dotfiles に広がる兆候
