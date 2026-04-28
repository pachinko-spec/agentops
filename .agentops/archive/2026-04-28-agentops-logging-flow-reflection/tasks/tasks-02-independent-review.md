# tasks-02: 独立レビューと修正

親 plan: 2026-04-28-agentops-logging-flow-reflection
状態: pending（tasks-01 完了後着手）
作業ブランチ: claude/agentops-logging-rule-reflection

## 実行内容

1. `agentops-reviewer` subagent を起動し、tasks-01 で更新した 10 ファイル（雛形整合 P1-3 で +2 ファイル含む）を独立レビュー
2. 指摘を P0 / P1 / P2 / P3 に分類
3. P0 / P1 は必ず修正。P2 は採否判断、P3 は記録のみで修正ループ継続しない
4. 修正後は再レビュー。最終再レビューで P0 / P1 残存ゼロを確認して終える
5. レビュー結果と修正経過を `.agentops/archive/<plan-id>/reviews/` に格納（commit 前移動の一部）

## 検証

- レビュー報告に P0 / P1 残存ゼロ
- 最終 git diff が意図差分のみ
- レビュー修正は最大 2 周以内

## 停止条件

- レビュー修正が 2 周を超えそう → 統合判断またはユーザー確認
