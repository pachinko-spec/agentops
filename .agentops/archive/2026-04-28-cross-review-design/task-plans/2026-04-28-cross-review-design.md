# Task Plan: cross-review design policy implementation

plan_id: 2026-04-28-cross-review-design
status: completed
created_at: 2026-04-28
completed_at: 2026-04-28
timezone: Asia/Tokyo

## 今回の目的

承認済み plan に沿って、cross-review / cross-model review の設計思想を agentops の現行 docs、catalog、config template へ反映した。

## 実行順

1. `main` から `codex/` prefix の作業ブランチを作成する。
2. `.agentops/plans/current.md`、`.agentops/task-plans/current.md`、`.agentops/tasks/001-cross-review-design.md` を作成する。
3. docs の cross-review / model routing / review policy を更新する。
4. skills / workflows catalog の cross-review 発火条件を更新する。
5. config / template 側の CLI 別雛形に、実設定ではなく生成方針として反映する。
6. `rg`、`git diff --check`、`scripts/agentops-watch check --projects config/projects.yml` を実行する。
7. diff 自己レビューを行う。
8. commit / push / PR / merge / main 同期まで行う。
9. 完了済み plan / task-plan / task / review を archive へ移す。

## 今回は行わないこと

- 実 model id の固定。
- `/home/otaku/.codex`、`/home/otaku/.claude`、shell profile、MCP 実設定の変更。
- cross-review を全変更で必須化すること。

## 完了状態

- PR #18 で設計思想反映を merge 済み。
- cleanup PR で `.agentops` の完了済み入口を archive へ移動する。

## 停止条件

- 実設定や dotfiles へ触る必要が出た。
- 未確認の model id を選ばないと文書が成立しない。
- レビュー修正またはテスト修正が2周を超えた。
- P0/P1 相当の未解決問題が残る。
