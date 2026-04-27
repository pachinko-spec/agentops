# workflows

再利用可能な開発workflowを置く場所です。

`workflows/` は作業手順の正本です。常時適用する判断基準は `rules/`、特定観点の知識は `skills/`、背景や理由は `docs/` に置きます。

このディレクトリのworkflowは、agentops保守だけでなく、グローバル設定へ反映された後に `~/dev` 配下の実プロジェクトで使うテンプレートとして設計します。

## 実プロジェクト向け

- `project-intake.md`: 実プロジェクト作業開始時の対象、スタック、デプロイ先、検証条件確認。
- `feature-delivery.md`: 新機能、修正、UI/API変更を設計から検証、docs、リリース準備まで進める。
- `web-system-design.md`: Nuxt、Next.js、PHP、Go を中心にWebシステムを設計する。
- `deployment-target-selection.md`: Cloudflare Workers / Pages、Xserver、GCP、ローカルサーバーを比較する。
- `release-readiness.md`: 本番または外部公開前の検証、rollback、監視、docsを確認する。
- `production-operations.md`: 本番運用、障害対応、backup、cron、runbook整備。

## 共通品質

- `plan-approval.md`: 実装前の計画提示、承認、task-plan化。
- `design-review.md`: 設計レビュー。
- `code-review.md`: コードレビュー。
- `docs-update.md`: ドキュメント更新。
- `dependency-introduction.md`: 依存関係導入。
- `freshness-audit.md`: 最新性監査。
- `session-handoff.md`: セッション引き継ぎ。

## グローバル設定・補助ツール

- `understand-anything-bootstrap.md`: Understand-Anything導入確認。
- `understand-anything-graph-update.md`: Understand-Anything graph更新判断。
