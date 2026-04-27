# tasks

現在のplanに紐づく未完了、進行中、blockedの子タスクだけを置く場所です。

各プロジェクトでは、プロジェクトローカルの `.agentops/tasks/` を優先します。

## 監視CLIとの関係

`agentops-watch` は、`README.md` 以外の `.agentops/tasks/*.md` を未完了タスク数として数えます。

そのため、完了したtaskをこのディレクトリ直下に残してはいけません。完了、中止、置き換え済みのtaskは、対応する `.agentops/archive/<plan-id>/tasks/` へ移します。

## taskの必須項目

- 親plan。
- 現在状態。
- 実行内容。
- 検証。
- 停止条件。
- 次セッションへ残すこと。
