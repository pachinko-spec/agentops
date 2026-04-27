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

## 完了時の後処理

- 完了した task は `.agentops/tasks/` 直下に残さず、対応する `.agentops/archive/<parent_plan>/tasks/` へ移す。
- 完了した `.agentops/task-plans/current.md` は `.agentops/archive/<parent_plan>/task-plans/` へ移し、次に着手する task に合わせて新しい `current.md` を作る。
- `.agentops/prompts/next-session.md` は、次に読むべき `current.md` と task を指す内容へ更新し、古い plan や完了済み task を入口にしない。
- `scripts/agentops-watch check --projects config/projects.yml` で、完了済み task が未完了件数に残っていないことを確認する。

## 停止条件

- 大量削除やディレクトリ移動が必要になったが、ユーザー承認がない。
- 参照切れや既存運用への影響が大きい。
