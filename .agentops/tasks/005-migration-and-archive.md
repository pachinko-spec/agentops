# 005 migration and archive

parent_plan: 2026-04-27-agentops-reference-kit-refactor
status: pending

## 実行内容

- 不要または過剰な見本群の扱いを決める。
- 削除を急がず、必要に応じて `examples/`、`archive/`、`.agentops/archive/` へ移す。
- 移行時に README、docs、config、script の参照切れを防ぐ。

## 完了条件

- 移行候補一覧がある。
- archive 方針がある。
- 参照切れ確認方法がある。
- ユーザー承認なしに大規模削除へ進まないことが明記されている。

## 検証

- `rg` で移動対象への参照を確認する。
- `git diff --check`
- `scripts/agentops-watch check --projects config/projects.yml`

## 停止条件

- 大量削除やディレクトリ移動が必要になったが、ユーザー承認がない。
- 参照切れや既存運用への影響が大きい。
