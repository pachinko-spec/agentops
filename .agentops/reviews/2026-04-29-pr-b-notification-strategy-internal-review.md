---
review-id: 2026-04-29-pr-b-notification-strategy-internal-review
date: 2026-04-29
reviewer: claude-code (independent subagent)
target-pr: PR-B
target-branch: claude/notification-strategy-2026-04-29
target-task: .agentops/tasks/01-notification-strategy-docs.md
review-axes: correctness / security / tests / docs / maintainability
verdict: minor fixes
---

# PR-B independent internal review (summary)

P0: 0 / P1: 2 / P2: 3 / P3: 3. 詳細所見は本セッションの assistant 応答テキストに記載。
parent agent (orchestrator) は本ファイルではなくレビュアー応答本文を主たる入力として扱う。

## 主要 P1

1. scripts/README.md:21 の notify usage 例が docs/11 の --kind 必須仕様と乖離。
2. rules/catalog.md:21 の hook 列 (em dash) と docs/17:42 の hook 列 (stub.md) が同方向で不一致。

## 主要 P2

- docs/18:141 vs :150 の rate-limit 文言の二義性
- docs/18:86 が tools/agentops_monitor/notifiers/ 未存在のまま将来形で参照
- docs/18:147 の DbC 適用前提が --projects 必須範囲を限定していない

## 残リスク (read-only)

- tools/agentops_monitor 実装本体との整合は別 plan で再検証必要
- markdown-link-check 未再走
- 公式 hooks docs 仕様未再確認
