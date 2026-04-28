# task-plan: agentops 運用ルール反映

親 plan: 2026-04-28-agentops-logging-flow-reflection
作業ブランチ: claude/agentops-logging-rule-reflection
作成: 2026-04-28

## フェーズと予想時間

| フェーズ | 内容 | 予想 |
|---|---|---|
| 1 | tasks-01: docs/02-workflow.md 強化（責務テーブル化、ハンドオフ節追記、サイクル微調整） | 15 分 |
| 2 | tasks-01: archive/README.md 時系列インデックス化（11 件） | 15 分 |
| 3 | tasks-01: 4 README 整備（plans / task-plans / tasks / handoffs）+ prompts/README.md 新規作成 | 10 分 |
| 4 | tasks-01: next-session.md 削除 + 雛形同期（templates/agentops/prompts/next-session.md, docs/15 L34） | 10 分 |
| 5 | tasks-01 自己レビュー: git diff 目視、相互参照整合、既存 docs 非矛盾 | 10 分 |
| 6 | tasks-02: agentops-reviewer subagent 独立レビュー実施 | 10 分 |
| 7 | tasks-02: P0/P1 指摘修正（あれば、最大 2 周） | 0-30 分 |
| 8 | commit 前 archive 移動（plans/current.md, task-plans/current.md, 完了 task） | 5 分 |
| 9 | archive/README.md インデックスに今回 plan-id 行追加 | 3 分 |
| 10 | commit / push / PR 作成 / マージ / main 同期確認 | 10 分 |

合計: 約 90-120 分

## 停止条件（再掲）

- 既存 docs と大きな矛盾
- レビュー修正 2 周超過
- 機密値・破壊的操作・スコープ大幅拡張
- archive 既存 5 件サマリ推定不能

## 完了条件

- 反映対象 10 ファイル更新完了
- agentops-reviewer P0/P1 ゼロ
- PR 作成、レビュー、マージ、main 同期確認まで完了
