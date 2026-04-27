# <task id> <task title>

parent_plan: <yyyy-mm-dd-slug>
status: pending

## 実行内容

- 作業内容。

## 完了条件

- 完了と判断できる条件。

## 検証

- 検証方法。

## 完了時の後処理

- 完了した task は `.agentops/archive/<parent_plan>/tasks/` へ移す。
- 必要なら `.agentops/task-plans/current.md` と `.agentops/prompts/next-session.md` を更新する。

## 停止条件

- 停止または確認が必要な条件。
