---
plan-id: 2026-04-29-notification-strategy-and-project-localization
created: 2026-04-29
status: in-progress
parent-handoff: ~/.claude/.agentops/handoffs/2026-04-28-agentops-followup-after-global-review.md (既消化済 / 反映不要、archive 移動は別機会)
last_reviewed: 2026-04-29
---

# Plan: 通知戦略 (PR-B) + プロジェクトローカライズ設計思想 (PR-C)

## Context

- ユーザー依頼の handoff `2026-04-28-agentops-followup-after-global-review.md` は既に agentops 側で消化済み (PR #25 + 後続)。設計思想反映は不要、archive 移動は本 plan のスコープ外。
- 新スコープ 2 件:
  - **PR-B**: Discord 通知体系の補完。既存 `agentops-watch notify` + `AGENTOPS_DISCORD_WEBHOOK_URL` 設計を 4 channel 仕様 (`DAILLY` / `WEEKLY` / `MONTHLY` / `ANT_TIME`) へ刷新。SessionStart/End / PermissionRequest 待ち / 任意アラートを `ANT_TIME` 専用 channel に分離。
  - **PR-C**: 既存プロジェクト (過去 Claude Code / Codex / Antigravity 痕跡あり) を新グローバル設計思想にどう統合するかを判定するローカライズ戦略 docs を新設。
- 既存環境変数: `DISCORD_WEBHOOK_URL_DAILLY` / `WEEKLY` / `MONTHLY` / `ANT_TIME` が `~/.bashrc` で export 済み。新規追加なし。
- 既存 cron (`crontab -l`): Discord 主目的 2 行 + 旧 dotfiles 残骸 audit 3 行 = 整理対象 5 行。サーバー状態通知 (`metrics-collect.sh` / `server-report.sh`) は触らない。

## 親 task 一覧

- [01-notification-strategy-docs](../tasks/01-notification-strategy-docs.md) — PR-B B-1: agentops 側 docs / catalog / templates 整備
- [02-project-localization-docs](../tasks/02-project-localization-docs.md) — PR-C: プロジェクトローカライズ戦略 docs 新設

## スコープ外 (別 plan)

- PR-A (handoff archive 移動) — 別グローバル設定作業時に処理
- PR-B B-2 (cron 実反映) — B-1 完了後の small confirmation を経て別 task / 別 plan
- `agentops-watch notify --kind` 実装、SessionStart/End hook 実体追加 — 別実装 plan
- `agentops localize` CLI 実装 — 別実装 plan
- 既存 `~/dev/` 5 プロジェクトの実マイグレーション — 各プロジェクト個別 plan

## 完了条件

- 各 task の DbC 完了条件をすべて満たす
- PR-B / PR-C ともに Codex `review_frontier --effort high` cross-review で P0/P1 0 件
- markdown-link-check pass
- 旧 envvar `AGENTOPS_DISCORD_WEBHOOK_URL` の参照に deprecated 注記が付いていること
- `~/.claude/CLAUDE.md` 行数増分 +5 行以内 / PR (合計 +10 行以内)

## 停止条件

- レビュー修正 2 周超過
- Webhook URL / SECRET 値が diff / commit / log / PR / handoff に混入
- 公式仕様確認が必要 (Claude Code SessionStart/SessionEnd hook 仕様、Discord plugin MCP transport 状態)
- `~/.claude/CLAUDE.md` 行数大幅増 (+50 行超)
- スコープ外への踏み込み (CLI 実装、cron 実反映、既存プロジェクト実マイグレーション)
- ANT_TIME 通知の頻度上限ガード未設計のまま実装 phase に進もうとした
