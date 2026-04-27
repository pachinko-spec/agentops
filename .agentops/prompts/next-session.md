# 次セッション用プロンプト

あなたは Codex として `/home/otaku/agentops` を作業する。

まず次を読む:

- README.md
- decisions/README.md
- decisions/2026-04-27-agentops-reference-kit-refactor.md
- .agentops/plans/current.md
- .agentops/task-plans/current.md
- .agentops/tasks/002-readme-and-docs-language.md

今回の目的:

- `.agentops/tasks/002-readme-and-docs-language.md` から着手する。
- README と主要 docs の語彙を見直す。
- 「正本」「投影物」「機械的に反映」という印象を弱める。
- 「参照資料」「判断材料」「反映候補」「各 CLI エージェントが採否を判断する」という表現へ寄せる。
- `docs/` は現役参照資料、`decisions/` は判断履歴として分ける。

作業ルール:

- 日本語で応答する。
- 必ず作業ブランチを切る。
- 実装・ファイル編集前に、今回セッションの小分け計画を提示して承認を得る。
- 大きな削除や移動はまだ行わない。
- `rules/`、`skills/`、`workflows/` の構造整理に踏み込む場合は次タスクへ分ける。
- 変更後は `git diff --check` と `scripts/agentops-watch check --projects config/projects.yml` を実行する。
- `002` が完了したら、完了済み task と今回の task-plan を `.agentops/archive/<plan-id>/` へ移す。
- 次に着手する task に合わせて `.agentops/task-plans/current.md` と `.agentops/prompts/next-session.md` を更新し、古い plan や完了済み task を入口にしない。
- commit / push / PR 作成 / GitHub 上での merge / main 同期確認まで行う。
