# agentops templates

`.agentops` の plan、task-plan、task、next-session prompt を作るためのサンプルです。

## ファイル

- `plans/current.md`: 大きい承認済み plan。
- `task-plans/current.md`: 今回セッションの実行計画。
- `tasks/task.md`: 未完了または進行中の子 task。
- `prompts/next-session.md`: 次セッション入口。

## 方針

- 完了済み task は `.agentops/tasks/` 直下に残さない。
- 完了済み plan、task-plan、task は `.agentops/archive/<plan-id>/` へ移す。
- 次セッション prompt は完了済み task を入口にしない。
