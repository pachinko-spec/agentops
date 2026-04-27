# 002 ai撤去とUnderstand-Anything統合

親plan: `.agentops/plans/current.md`
状態: done

## 実行内容

- `/ai` を撤去する。
- 旧ai配下のUnderstand-Anything policy相当を `config/understand-anything-policy.json` に置く。
- `scripts/ua-bootstrap.mjs` と `scripts/ua-graph-controller.mjs` を維持する。

## 検証

- `/ai` が残っていないことを確認する。
- Node scriptの構文確認を行う。

## 停止条件

- `/ai` に未移行の正本が残っている場合は停止して移行先を決める。
