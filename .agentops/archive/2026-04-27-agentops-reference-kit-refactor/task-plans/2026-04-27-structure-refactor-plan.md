# Task Plan: structure refactor plan

plan_id: 2026-04-27-agentops-reference-kit-refactor
status: completed
created_at: 2026-04-27
timezone: Asia/Tokyo

## 今回セッションの目的

`.agentops/tasks/003-structure-refactor-plan.md` から着手し、`rules/`、`skills/`、`workflows/` を残す、縮小する、移す、archive する方針を設計する。

## 実行順

1. 作業ブランチを切る。
2. `.agentops/tasks/003-structure-refactor-plan.md` を読む。
3. `rules/`、`skills/`、`workflows/` のファイル一覧と README、docs、config からの参照関係を `rg` で確認する。
4. 現役参照資料として残すもの、最小見本として `examples/` に移すもの、CLI 用テンプレートとして `templates/` に移すもの、チェックリストとして `checklists/` に移すもの、archive 候補に分類する。
5. 移動や削除は実施せず、影響範囲と提案方針を文書化する。
6. `.agentops/tasks/003-structure-refactor-plan.md` の状態と残タスクを更新する。
7. `003` が完了した場合は、完了済み task と今回の `current.md` を `.agentops/archive/<plan-id>/` へ移す。
8. 次に着手する task に合わせて `.agentops/task-plans/current.md` と `.agentops/prompts/next-session.md` を更新する。
9. 差分を確認する。
10. `git diff --check` と `scripts/agentops-watch check --projects config/projects.yml` を実行する。
11. commit、push、PR作成、GitHub上でのmerge、main同期確認を行う。

## 今回は行わないこと

- `rules/`、`skills/`、`workflows/` の大規模な移動、削除、archive 化。
- Claude Code / Codex の実グローバル設定変更。
- `decisions/` を現役 docs として扱う変更。

## 停止条件

- 移動先ディレクトリ構成に合意がない。
- 既存の `skills/` や `workflows/` を削ると、ユーザーが期待する参照資料が失われる。
- 参照関係が広く、分類だけでは安全な次アクションを決められない。

## 完了メモ

- `rules/`、`skills/`、`workflows/` の全ファイルと参照関係を棚卸しした。
- 分類案と影響範囲を `docs/15-reference-kit-structure.md` に文書化した。
- 003 task を archive に移した。
- 次の current task-plan は 004 cli template focus に切り替える。
