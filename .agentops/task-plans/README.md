# task-plans

承認済みplanを、今回セッションで実行できる粒度へ分解した実行計画を置く場所です。

## 運用

- `current.md` は今回セッションまたは次回復帰用の実行計画です。
- 承認済みplanの継続でユーザー承認を省略できる場合でも、`current.md` 相当の小分け計画は必ず明示します。
- 前タスクの結果で後続タスクが変わる場合は、`tasks/*.md` とこのtask-planを更新します。
- 完了したtask-planは `.agentops/archive/<plan-id>/task-plans/` へ移します。
