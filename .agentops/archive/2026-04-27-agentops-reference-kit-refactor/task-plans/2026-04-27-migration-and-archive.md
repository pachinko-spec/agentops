# Task Plan: migration and archive

plan_id: 2026-04-27-agentops-reference-kit-refactor
status: completed
created_at: 2026-04-27
completed_at: 2026-04-27
timezone: Asia/Tokyo

## 次セッションの目的

`.agentops/tasks/005-migration-and-archive.md` から着手し、不要または過剰な見本群の扱い、archive 方針、参照切れ確認方法を整理する。

## 実行順

1. 作業ブランチを確認し、必要なら `codex/005-migration-and-archive` のような新しい作業ブランチを切る。
2. `.agentops/tasks/005-migration-and-archive.md` を読む。
3. `docs/15-reference-kit-structure.md` と `docs/16-global-settings-application-checklist.md` を確認する。
4. `rules/`、`skills/`、`workflows/` の移行候補、archive 候補、checklists / templates / examples 候補を再確認する。
5. README、docs、config、workflows、skills、scripts、`.agentops` からの参照を `rg` で確認する。
6. 大規模削除や移動に入る前に、移行方針と影響範囲をユーザーへ提示して承認を得る。
7. 承認範囲内で最小限の移動、参照更新、archive 方針の文書化を行う。
8. `005` が完了した場合は、完了済み task と今回の `current.md` を `.agentops/archive/<plan-id>/` へ移す。
9. 次に着手する task がなければ、`.agentops/prompts/next-session.md` に残タスクなし、または次の未完了作業を明記する。
10. `git diff --check` と `scripts/agentops-watch check --projects config/projects.yml` を実行する。
11. commit、push、PR作成、GitHub上でのmerge、main同期確認を行う。

## 今回は行わないこと

- ユーザー承認なしに大規模削除やディレクトリ移動を行うこと。
- CLI 固有仕様を公式 docs 未確認のまま固定すること。
- 実グローバル設定へ直接反映すること。

## 完了結果

- `docs/15-reference-kit-structure.md` に 005 の移行方針、archive 方針、参照切れ確認方法を追記した。
- `rules/`、`skills/`、`workflows/` 本体の大規模移動や削除は実施しなかった。
- 次に実移動を行う場合は、対象ファイル一覧、移動先、参照更新対象、検証方法を提示し、ユーザー承認を得る方針にした。
- 完了済み task、task-plan、plan は `.agentops/archive/2026-04-27-agentops-reference-kit-refactor/` へ移す。

## 停止条件

- 大量削除やディレクトリ移動が必要になったが、ユーザー承認がない。
- 参照切れや既存運用への影響が大きい。
- どのファイルを現役参照資料として残すか判断できない。
