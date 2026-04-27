# セッション引き継ぎworkflow

## 使う場面

作業が1セッションで終わらない場合、または次回復帰が必要な場合に使います。

## 手順

1. 完了したtaskをarchiveへ移す。
2. 未完了taskを `.agentops/tasks/` 直下に残す。
3. `.agentops/task-plans/current.md` の復帰ポイントを更新する。
4. `.agentops/handoffs/` または `.agentops/prompts/` に次セッション用情報を残す。
5. 未検証、未反映、未解決リスクを明記する。
