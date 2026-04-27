# 次セッション用プロンプト

あなたは Codex として `/home/otaku/agentops` を作業する。

まず次を読む:

- README.md
- decisions/README.md
- decisions/2026-04-27-agentops-reference-kit-refactor.md
- .agentops/plans/current.md
- .agentops/task-plans/current.md
- .agentops/tasks/005-migration-and-archive.md
- docs/15-reference-kit-structure.md
- docs/16-global-settings-application-checklist.md

今回の目的:

- `.agentops/tasks/005-migration-and-archive.md` から着手する。
- 不要または過剰な見本群の扱いを決める。
- 削除を急がず、必要に応じて `examples/`、`templates/`、`checklists/`、archive へ寄せる方針を整理する。
- 移行時に README、docs、config、workflows、skills、script の参照切れを防ぐ。
- 大規模削除や移動に入る前に、移行方針と影響範囲を提示して承認を得る。

作業ルール:

- 日本語で応答する。
- 必ず作業ブランチを切る。
- 実装・ファイル編集前に、今回セッションの小分け計画を提示して承認を得る。
- 大きな削除や移動は、方針提示とユーザー承認なしに行わない。
- `rules/`、`skills/`、`workflows/` の構造整理は、`docs/15-reference-kit-structure.md` の分類案を入力として扱う。
- CLI 固有仕様を固定しすぎず、必要な場合は公式 docs と実環境を確認する。
- 変更後は `git diff --check` と `scripts/agentops-watch check --projects config/projects.yml` を実行する。
- `005` が完了したら、完了済み task と今回の task-plan を `.agentops/archive/<plan-id>/` へ移す。
- 次に着手する task があれば `.agentops/task-plans/current.md` と `.agentops/prompts/next-session.md` を更新し、古い plan や完了済み task を入口にしない。
- commit / push / PR 作成 / GitHub 上での merge / main 同期確認まで行う。
