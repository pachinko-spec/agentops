# Codex グローバル設定雛形

このファイルは `~/.codex/AGENTS.md` に配置するための雛形です。
プロジェクト固有の `AGENTS.md`、`CLAUDE.md`、`.agentops/` がある場合は、それらを優先してください。

## 基本方針

- 応答、commit message、Issue/PR、レビューコメント、引き継ぎ文書は日本語で書く。
- 時刻、日付、ログ、run id、監視レポート、handoff、PR本文では、外部仕様でUTCが必須のときを除き `Asia/Tokyo` の日本時間を基準にする。
- コード、API名、CLI名、パッケージ名、UIラベルなど英語が自然なものは英語のままでよい。
- 作業前に必ず `git status --short --branch` で現在ブランチと未コミット差分を確認する。
- `main` / `master` / `develop` など保護対象ブランチでは直接作業しない。必要なら `codex/` プレフィックスの作業ブランチを作る。
- main への直 push は禁止する。作業ブランチ、commit、push、PR、レビュー、マージの順で扱う。
- 実装後は必ず検証する。テスト未実行または失敗状態では commit / push しない。
- 実装差分が README、docs、設定、prompt、skill、workflow に影響する場合はドキュメント更新を完了条件に含める。
- DbC の考え方を使い、前提条件、不変条件、完了条件、禁止事項、停止条件を明確にする。
- ライブラリ、ランタイム、CLI、API、モデルは AI の記憶だけで判断しない。公式 docs、GitHub、package registry、release notes、security advisory を優先する。

## 作業サイクル

1. ブランチと作業ツリーを確認する。
2. README、docs、プロジェクト固有設定を読む。
3. 影響範囲と完了条件を短く設計する。
4. 高リスクなら別モデルまたはサブエージェントで設計レビューを行う。
5. 実装する。
6. lint、型チェック、テスト、必要なら E2E / ブラウザ確認を行う。
7. ドキュメントを更新する。
8. 差分を確認して commit / push / PR へ進む。

## レビュー修正ループ

- レビュー指摘は P0 / P1 / P2 / P3 で分類する。
- P0 / P1 は必ず修正する。修正不能なら停止してユーザーに確認する。
- P2 は修正するか、理由つきで次セッションへ延期する。
- P3 だけで修正ループを続けない。
- レビュー修正は最大 2 周までにする。3 周目が必要なら統合判断を行い、ユーザー確認または次セッション分割を行う。

## クロスモデル委譲

- Claude Code へ委譲する場合は、原則として共通 CLI Wrapper を使う。
- 委譲依頼、進捗、stdout/stderr、結果は `.agentops/runs/` に残す。
- 委譲先の所見は参考情報であり、採否と統合判断はメインエージェントが持つ。

例:

```text
agentops delegate --to claude --role architect_frontier --model <claude-model-id> --effort xhigh --input .agentops/plans/current.md
```

## セッション引き継ぎ

1 セッションで終わらない場合は、次を `.agentops/handoffs/` または `.agentops/prompts/` に残す。

- 今回完了したこと
- 未完了のこと
- 現在のブランチ
- 変更ファイル
- 実行した検証
- 未解決リスク
- 次セッションに投入するプロンプト

## 参照優先順位

1. ユーザーの明示指示
2. プロジェクト固有の `AGENTS.md` / `CLAUDE.md` / docs / `.agentops/`
3. この `agentops` リポジトリの docs
4. 一般的なベストプラクティス
