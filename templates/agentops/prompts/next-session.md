# 次セッション用プロンプト（雛形）

`next-session.md` の参照先は動的に決まる。実体側で生成する前に次を確認する。

1. `.agentops/tasks/*.md` に未完了 task があれば、**tasks ベース**で書く（次番号 task をエントリポイントとして指す）
2. tasks が空で `.agentops/handoffs/` に進行中の引き継ぎがあれば、**handoffs ベース**で書く
3. 両方なければ、`next-session.md` を **生成しない**（既存ファイルは削除する）

以下は tasks ベースで生成する場合の雛形。handoffs ベースの場合は読み込み対象とプロンプト本文を差し替える。

---

あなたは Codex または Claude Code として `<repo path>` を作業する。

まず次を読む:

- README.md
- .agentops/plans/current.md
- .agentops/task-plans/current.md
- .agentops/tasks/<次に着手する task ファイル>.md

今回の目的:

- 次に着手すること。

作業ルール:

- 日本語で応答する。
- 作業ブランチを切る。
- 実装着手前に `.agentops/plans/current.md`、`.agentops/task-plans/current.md`、`.agentops/tasks/*.md` を最新化する。
- 変更後は指定の検証を実行する。
- commit 前に完了 task と plan 類を `.agentops/archive/<plan-id>/` へ移動する。
