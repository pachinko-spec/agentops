# Task Plan: agentops reference kit refactor

plan_id: 2026-04-27-agentops-reference-kit-refactor
status: completed
created_at: 2026-04-27
timezone: Asia/Tokyo

## 今回セッションの目的

設計思想の大きな方向転換に入る前に、`.agentops` の計画、task-plan、tasks と、`decisions/` の設計判断ログ置き場を作る。

## 実行順

1. 作業ブランチを切る。
2. `decisions/README.md` を作成する。
3. `decisions/2026-04-27-agentops-reference-kit-refactor.md` を作成する。
4. `.agentops/plans/current.md` を作成する。
5. `.agentops/task-plans/current.md` を作成する。
6. `.agentops/tasks/001-positioning-and-decision-log.md` を作成する。
7. `.agentops/tasks/002-readme-and-docs-language.md` を作成する。
8. `.agentops/tasks/003-structure-refactor-plan.md` を作成する。
9. `.agentops/tasks/004-cli-template-focus.md` を作成する。
10. `.agentops/tasks/005-migration-and-archive.md` を作成する。
11. 差分を確認する。
12. `git diff --check` と `scripts/agentops-watch check --projects config/projects.yml` を実行する。
13. commit、push、PR作成、GitHub上でのmerge、main同期確認を行う。

## 今回は行わないこと

- README や docs の本格リファクタ。
- `rules/`、`skills/`、`workflows/` の移動、削除、archive 化。
- Claude Code / Codex の実グローバル設定変更。

## 停止条件

- `.agentops` の既存運用と矛盾するファイル配置が必要になった。
- decisions の置き場所について再判断が必要になった。
- 作成予定ファイルの内容が、承認済み方針から外れる。
