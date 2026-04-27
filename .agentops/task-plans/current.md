# Task Plan: README and docs language cleanup

plan_id: 2026-04-27-agentops-reference-kit-refactor
status: pending
created_at: 2026-04-27
timezone: Asia/Tokyo

## 今回セッションの目的

`.agentops/tasks/002-readme-and-docs-language.md` から着手し、README と主要 docs に残る強すぎる語彙を整理する。

## 実行順

1. 作業ブランチを切る。
2. `.agentops/tasks/002-readme-and-docs-language.md` を読む。
3. `rg "正本|投影物|機械的" README.md docs rules workflows config` で残存箇所を確認する。
4. README と主要 docs の語彙を「参照資料」「判断材料」「反映候補」「採否を判断して反映」へ寄せる。
5. `rules/`、`skills/`、`workflows/` の表現は、構造整理に踏み込む場合は次タスクへ分ける。
6. `.agentops/tasks/002-readme-and-docs-language.md` の状態と残タスクを更新する。
7. `002` が完了した場合は、完了済み task と今回の `current.md` を `.agentops/archive/<plan-id>/` へ移す。
8. 次に着手する task に合わせて `.agentops/task-plans/current.md` と `.agentops/prompts/next-session.md` を更新する。
9. 差分を確認する。
10. `git diff --check` と `scripts/agentops-watch check --projects config/projects.yml` を実行する。
11. commit、push、PR作成、GitHub上でのmerge、main同期確認を行う。

## 今回は行わないこと

- `rules/`、`skills/`、`workflows/` の大規模な移動、削除、archive 化。
- Claude Code / Codex の実グローバル設定変更。
- `decisions/` を現役 docs として扱う変更。

## 停止条件

- 語彙変更だけでなく構造変更が必要になり、ユーザー判断が必要になる。
- 既存スクリプトや docs 参照と矛盾する。
- `rules/`、`skills/`、`workflows/` の扱いについて追加の設計判断が必要になる。
