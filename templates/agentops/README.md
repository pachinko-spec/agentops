# agentops templates

`.agentops` の plan、task-plan、task、next-session prompt を作るためのサンプルです。

## ファイル

- `plans/current.md`: 大きい承認済み plan。
- `task-plans/current.md`: 今回セッションの実行計画。
- `tasks/task.md`: 未完了または進行中の子 task。
- `prompts/next-session.md`: 次セッション入口。

## 方針

- 各 `tasks/*.md` は plan 内の作業単位（PR 単位）。新作業は次番号ファイル（例: `tasks-01-...`、`tasks-02-...`）に追記する。
- 完了済み task は `.agentops/tasks/` 直下に残さない。**commit 前**に対応する `.agentops/archive/<plan-id>/tasks/` へ移す。`plans/current.md` と `task-plans/current.md` も同タイミングで `archive/<plan-id>/` へ移す。
- 完了 handoff は `archive/<plan-id>/handoffs/` へ移し、`.agentops/handoffs/` 直下は進行中の引き継ぎだけにする。
- `prompts/next-session.md` は動的に決める: `tasks/` に未完了があれば tasks ベース、なければ `handoffs/` ベース、両方なければ生成しない（既存ファイルがあれば削除する）。
