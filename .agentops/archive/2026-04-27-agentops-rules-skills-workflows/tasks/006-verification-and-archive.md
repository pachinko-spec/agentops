# 006 検証とarchive

親plan: `.agentops/plans/current.md`
状態: done

## 実行内容

- 構文確認と配置確認を行う。
- 完了したtask、task-plan、planを `.agentops/archive/<plan-id>/` へ移す。

## 検証

- `node --check scripts/ua-bootstrap.mjs`
- `node --check scripts/ua-graph-controller.mjs`
- `git status --short`

## 停止条件

- 検証が失敗した場合はarchiveへ移さず、未完了taskを残す。
