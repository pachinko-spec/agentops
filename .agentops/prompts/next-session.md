# 次セッション用プロンプト

あなたは Codex として `/home/otaku/agentops` を作業する。

現時点で、このリポジトリの `.agentops/plans/current.md`、`.agentops/task-plans/current.md`、`.agentops/tasks/*.md` に未完了の入口は置かれていない。

新しい作業を始める場合は、まず次を読む:

- README.md
- decisions/README.md
- docs/15-reference-kit-structure.md
- docs/16-global-settings-application-checklist.md
- .agentops/archive/2026-04-27-agentops-reference-kit-refactor/plan.md

前回完了した作業:

- `2026-04-27-agentops-reference-kit-refactor` は完了済み。
- 完了済み plan、task-plan、task は `.agentops/archive/2026-04-27-agentops-reference-kit-refactor/` にある。
- `docs/15-reference-kit-structure.md` に、`rules/`、`skills/`、`workflows/` の移行候補、archive 方針、参照切れ確認方法がある。
- 参照キット本体の大規模移動や削除は行っていない。実移動する場合は、対象ファイル一覧、移動先、影響範囲、検証方法を提示してユーザー承認を得る。

新しい作業がある場合:

- `.agentops/plans/current.md` と `.agentops/task-plans/current.md` と `.agentops/tasks/*.md` を新しい目的に合わせて作る。
- 完了済み task や archive 済み task-plan を入口にしない。
- CLI 固有仕様を固定しすぎず、必要な場合は公式 docs と実環境を確認する。
- 変更後は `git diff --check` と `scripts/agentops-watch check --projects config/projects.yml` を実行する。

作業ルール:

- 日本語で応答する。
- 必ず作業ブランチを切る。
- 実装・ファイル編集前に、今回セッションの小分け計画を提示して承認を得る。
- 大きな削除や移動は、方針提示とユーザー承認なしに行わない。
- `rules/`、`skills/`、`workflows/` の構造整理は、`docs/15-reference-kit-structure.md` の分類案を入力として扱う。
- commit / push / PR 作成 / GitHub 上での merge / main 同期確認まで行う。
