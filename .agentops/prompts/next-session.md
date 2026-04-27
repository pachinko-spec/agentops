# 次セッション用プロンプト

あなたは Codex として `/home/otaku/agentops` を作業する。

まず次を読む:

- README.md
- decisions/README.md
- decisions/2026-04-27-agentops-reference-kit-refactor.md
- .agentops/plans/current.md
- .agentops/task-plans/current.md
- .agentops/tasks/003-structure-refactor-plan.md

今回の目的:

- `.agentops/tasks/003-structure-refactor-plan.md` から着手する。
- `rules/`、`skills/`、`workflows/` を残す、縮小する、移す、archive する方針を決める。
- `examples/`、`templates/`、`checklists/` への再編案を作る。
- 大量の見本がグローバル設定時のノイズにならない構成を設計する。
- 移動や削除はまだ実施せず、影響範囲と提案方針を文書化する。

作業ルール:

- 日本語で応答する。
- 必ず作業ブランチを切る。
- 実装・ファイル編集前に、今回セッションの小分け計画を提示して承認を得る。
- 大きな削除や移動はまだ行わない。
- `rules/`、`skills/`、`workflows/` の構造整理は、参照関係を確認してから分類案として扱う。
- 変更後は `git diff --check` と `scripts/agentops-watch check --projects config/projects.yml` を実行する。
- `003` が完了したら、完了済み task と今回の task-plan を `.agentops/archive/<plan-id>/` へ移す。
- 次に着手する task に合わせて `.agentops/task-plans/current.md` と `.agentops/prompts/next-session.md` を更新し、古い plan や完了済み task を入口にしない。
- commit / push / PR 作成 / GitHub 上での merge / main 同期確認まで行う。
