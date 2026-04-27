# 次セッション用プロンプト

あなたは Codex として `/home/otaku/agentops` を作業する。

現時点で、このリポジトリの `.agentops/plans/current.md`、`.agentops/task-plans/current.md`、`.agentops/tasks/*.md` に未完了の入口は置かれていない。

新しい作業を始める場合は、まず次を読む:

- README.md
- decisions/README.md
- decisions/2026-04-27-reference-kit-catalog-pivot.md
- .agentops/archive/2026-04-28-cross-review-design/plan.md
- docs/15-reference-kit-structure.md
- docs/16-global-settings-application-checklist.md
- .agentops/archive/2026-04-27-reference-kit-catalog-pivot/plan.md

前回完了した作業:

- cross-review / cross-model review の設計思想を docs、catalog、config template に反映する。
- cross-review は特定 model id 固定ではなく、主エージェントとは別 CLI / 別モデルファミリーの frontier reviewer を検討する思想として整理する。
- 完了済み plan、task-plan、task、review は `.agentops/archive/2026-04-28-cross-review-design/` にある。
- `rules/`、`skills/`、`workflows/` を完成品集から候補カタログへ転換する。
- 旧実体を `archive/reference-kit-v1/` へ退避する。
- `templates/claude/`、`templates/codex/`、`templates/agentops/` を作る。
- README、docs、config の参照を新構造へ更新する。
- 完了済み plan、task-plan、task は `.agentops/archive/2026-04-27-reference-kit-catalog-pivot/` にある。

新しい作業がある場合:

- `.agentops/plans/current.md` と `.agentops/task-plans/current.md` と `.agentops/tasks/*.md` を新しい目的に合わせて作る。
- 完了済み task や archive 済み task-plan を入口にしない。
- CLI 固有仕様を固定しすぎず、必要な場合は公式 docs と実環境を確認する。
- 変更後は `git diff --check` と `scripts/agentops-watch check --projects config/projects.yml` を実行する。

作業ルール:

- 日本語で応答する。
- 必ず作業ブランチを切る。
- 実装・ファイル編集前に、今回セッションの小分け計画を提示して承認を得る。
- `rules/`、`skills/`、`workflows/` の現役入口は候補カタログにする。
- commit / push / PR 作成 / GitHub 上での merge / main 同期確認まで行う。
