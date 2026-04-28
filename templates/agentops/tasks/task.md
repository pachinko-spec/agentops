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

- **commit 前**に完了した task を `.agentops/archive/<parent_plan>/tasks/` へ移す。`plans/current.md` と `task-plans/current.md` も同タイミングで `archive/<parent_plan>/` へ移す。
- `archive/README.md` 時系列インデックスに当該 plan-id 行を追加する。
- 必要なら `.agentops/prompts/next-session.md` を更新するか削除する（動的判定: tasks 未完了→tasks ベース／なければ handoffs ベース／両方なければ削除）。

## 停止条件

- 停止または確認が必要な条件。
