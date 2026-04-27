# skill catalog

AI エージェントが Claude Code / Codex 向けに Skill を生成するための候補一覧です。

Skill 名、description、tool 権限、supporting files は CLI ごとの公式 docs と実環境に合わせて調整します。特に description は自動起動の判断に使われるため、用途と発火条件を前に出します。

## design candidates

| 候補名 | 用途 | 発火条件 | 向き |
| --- | --- | --- | --- |
| requirements-review | 要件、非目的、完了条件、停止条件を確認する | 仕様策定、実装前計画 | global |
| architecture-boundary-review | 責務分離、依存方向、境界を確認する | 設計変更、リファクタ | global |
| api-contract-review | API 互換性、入力出力、エラー契約を確認する | API追加、外部連携 | project |
| data-model-review | データモデル、制約、migration 影響を確認する | DB変更、schema変更 | project |
| security-design-review | 認証、認可、secret、攻撃面を確認する | auth/security 変更 | global |
| privacy-design-review | 個人情報、ログ、保持期間、第三者送信を確認する | PII、analytics、ログ変更 | global |
| reliability-design-review | 障害時挙動、retry、rollback、冪等性を確認する | 本番影響がある変更 | project |
| performance-design-review | latency、cache、N+1、bundle size を確認する | performance 懸念 | project |
| accessibility-design-review | UI のアクセシビリティ要件を確認する | frontend UI 変更 | project |
| profitability-review | 収益導線、課金、価格、運用コストを確認する | monetization 変更 | project |

## implementation candidates

| 候補名 | 用途 | 発火条件 | 向き |
| --- | --- | --- | --- |
| web-frontend-implementation | Nuxt / Next.js などの frontend 実装観点を確認する | UI 実装 | project |
| web-backend-implementation | API、validation、DB、domain logic の実装観点を確認する | backend 実装 | project |
| deployment-adapter | Cloudflare、Xserver、GCP、ローカルの差分を確認する | deploy 設定変更 | project |
| test-automation | unit、integration、E2E、fixture の追加方針を確認する | テスト追加、回帰確認 | global / project |

## review candidates

| 候補名 | 用途 | 発火条件 | 向き |
| --- | --- | --- | --- |
| correctness-review | 仕様逸脱、境界値、例外、regression をレビューする | PR、差分レビュー | global |
| security-review | 脆弱性、secret、権限、依存リスクをレビューする | security 影響 | global |
| testability-review | テスト不足、検証不能箇所、fixture をレビューする | PR、テスト設計 | global |
| maintainability-review | 複雑化、重複、責務肥大をレビューする | リファクタ、PR | global |
| performance-review | 性能劣化、無駄な I/O、bundle、query をレビューする | performance 懸念 | project |
| dependency-supply-chain-review | 新規依存、license、supply chain をレビューする | dependency 追加 | global |
| release-readiness-review | release 前の検証、rollback、docs を確認する | release 前 | project |
| docs-review | README、API docs、runbook、handoff の更新漏れを確認する | docs 影響 | global |

## docs / ops candidates

| 候補名 | 用途 | 発火条件 | 向き |
| --- | --- | --- | --- |
| docs-maintainer | 実装差分に合わせて docs 更新を支援する | docs更新、仕様変更 | global |
| decision-log-writer | ADR / decision log を書く | 設計判断が必要 | global |
| runbook-writer | 運用手順、障害対応、rollback を書く | production ops | project |
| changelog-release-notes | changelog / release notes を書く | release 準備 | project |
| session-handoff | 次セッションへ引き継ぐ情報を整理する | 長時間作業、context移行 | global |
| freshness-audit | 公式 docs、release notes、version を確認する | 最新性が必要 | global |
| cross-model-delegate | Claude / Codex / subagent へ分担する | 高リスクレビュー、広範囲調査 | global |
| review-loop-guard | レビュー修正ループを制御する | レビュー後修正 | global |

## 生成時の注意

- 1 Skill は 1 つの反復可能な仕事に絞る。
- description には「何をするか」と「いつ使うか」を入れる。
- Claude Code では `allowed-tools` や slash invocation の扱いを確認する。
- Codex では `name` / `description`、supporting files、implicit invocation、plugin 配布の扱いを確認する。
- scripts は deterministic な処理が必要な場合だけ付ける。
