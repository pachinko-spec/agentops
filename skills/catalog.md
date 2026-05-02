# skill catalog

AI エージェントが Claude Code / Codex 向けに Skill を生成するための候補一覧です。

Skill 名、description、tool 権限、supporting files は CLI ごとの公式 docs と実環境に合わせて調整します。特に description は自動起動の判断に使われるため、用途と発火条件を前に出します。

> 関連表: skill から代表 rule を辿る逆参照は本ファイルの「関連 rule（代表）」列、rule 起点で代表 skill / workflow / hook を辿る場合は [docs/17-cross-reference.md](../docs/17-cross-reference.md) を参照。
>
> **代表選定の非相互性**: 本ファイルの `skill → rule（代表）` と docs/17 の `rule → skill（代表）` は必ずしも相互一致しない（各方向で「最初に見るべき代表 1 件」を独立に選定）。網羅性が必要な場合は両表 + [rules/catalog.md](../rules/catalog.md) を併読する。

## design candidates

| 候補名 | 用途 | 発火条件 | 向き | 関連 rule（代表） |
| --- | --- | --- | --- | --- |
| requirements-review | 要件、非目的、完了条件、停止条件を確認する | 仕様策定、実装前計画 | global | [planning-approval](../rules/catalog.md) |
| architecture-boundary-review | 責務分離、依存方向、境界を確認する | 設計変更、リファクタ | global | [project-scope](../rules/catalog.md) |
| api-contract-review | API 互換性、入力出力、エラー契約を確認する | API追加、外部連携 | project | [design-policy](../rules/catalog.md) |
| data-model-review | データモデル、制約、migration 影響を確認する | DB変更、schema変更 | project | [design-policy](../rules/catalog.md) |
| security-design-review | 認証、認可、secret、攻撃面を確認する | auth/security 変更 | global | [secret-policy](../rules/catalog.md) |
| privacy-design-review | 個人情報、ログ、保持期間、第三者送信を確認する | PII、analytics、ログ変更 | global | [secret-policy](../rules/catalog.md) |
| reliability-design-review | 障害時挙動、retry、rollback、冪等性を確認する | 本番影響がある変更 | project | [destructive-operation-policy](../rules/catalog.md) |
| performance-design-review | latency、cache、N+1、bundle size を確認する | performance 懸念 | project | [design-policy](../rules/catalog.md) |
| accessibility-design-review | UI のアクセシビリティ要件を確認する | frontend UI 変更 | project | [design-policy](../rules/catalog.md) |
| profitability-review | 収益導線、課金、価格、運用コストを確認する | monetization 変更 | project | [design-policy](../rules/catalog.md) |

## implementation candidates

| 候補名 | 用途 | 発火条件 | 向き | 関連 rule（代表） |
| --- | --- | --- | --- | --- |
| web-frontend-implementation | Nuxt / Next.js などの frontend 実装観点を確認する | UI 実装 | project | [review-policy](../rules/catalog.md) |
| web-backend-implementation | API、validation、DB、domain logic の実装観点を確認する | backend 実装 | project | [review-policy](../rules/catalog.md) |
| deployment-adapter | Cloudflare、Xserver、GCP、ローカルの差分を確認する | deploy 設定変更 | project | [deployment-target-policy](../rules/catalog.md) |
| test-automation | unit、integration、E2E、fixture の追加方針を確認する | テスト追加、回帰確認 | global / project | [review-policy](../rules/catalog.md) |

## review candidates

| 候補名 | 用途 | 発火条件 | 向き | 関連 rule（代表） |
| --- | --- | --- | --- | --- |
| correctness-review | 仕様逸脱、境界値、例外、regression をレビューする | PR、差分レビュー | global | [review-policy](../rules/catalog.md) |
| security-review | 脆弱性、secret、権限、依存リスクをレビューする | security 影響 | global | [secret-policy](../rules/catalog.md) |
| testability-review | テスト不足、検証不能箇所、fixture をレビューする | PR、テスト設計 | global | [review-policy](../rules/catalog.md) |
| maintainability-review | 複雑化、重複、責務肥大をレビューする | リファクタ、PR | global | [review-policy](../rules/catalog.md) |
| performance-review | 性能劣化、無駄な I/O、bundle、query をレビューする | performance 懸念 | project | [review-policy](../rules/catalog.md) |
| dependency-supply-chain-review | 新規依存、license、supply chain をレビューする | dependency 追加 | global | [secret-policy](../rules/catalog.md) |
| cross-review | 主 orchestrator とは別 CLI / 別モデルファミリーの frontier reviewer で確認する | 高リスク変更、新機能、リファクタ、依存追加、API 契約変更、デプロイ影響、レビュー修正後 | global | [review-policy](../rules/catalog.md) |
| phase-ownership-lint | plan / task の Phase 詳細表に担当列と Phase 担当宣言欄があるかだけを軽量モデルで確認する。実 SKILL.md 配置は別 plan で扱う | plan 作成直後、plan 提示前 | global | [phase-owner-declaration](../rules/catalog.md) |
| release-readiness-review | release 前の検証、rollback、docs を確認する | release 前 | project | [git-and-branch-policy](../rules/catalog.md) |
| docs-review | README、API docs、runbook、handoff の更新漏れを確認する | docs 影響 | global | [language-policy](../rules/catalog.md) |

## tooling adoption candidates

agentops が提示する third-party tooling candidate (本 repo 内 Skill ではなく、外部 CLI / MCP / plugin の **採用候補**)。各 project の `skill project-localize-inventory` で候補を確認し、project 単位で採否を決定する。詳細は [docs/20-tooling-candidates.md](../docs/20-tooling-candidates.md)、雛形は `templates/projects/<tool>/` を参照。

| 候補名 | 用途 | 発火条件 | 向き | 採否方針 | 関連 docs / 雛形 |
| --- | --- | --- | --- | --- | --- |
| sentrux | Rust 製 CLI / MCP server。52 言語のコード構造解析、循環依存・モジュール性スコア化、CI / pre-commit gate で AI 生成コードの構造劣化を自動 block | 中規模以上 / 層境界が明示された project の onboarding 時 / 既存 project の品質強化時 | global (候補)、project (実適用) | 強制導入なし、project ごとに判断 | [docs/20-tooling-candidates.md §sentrux](../docs/20-tooling-candidates.md)、雛形 `templates/projects/sentrux/.sentrux/rules.toml.template` |

(Understand-Anything は 1 人 + AI 任せ運用との適合性が低いため暫定見送り。詳細は docs/20)

## docs / ops candidates

| 候補名 | 用途 | 発火条件 | 向き | 関連 rule（代表） |
| --- | --- | --- | --- | --- |
| docs-maintainer | 実装差分に合わせて docs 更新を支援する | docs更新、仕様変更 | global | [documentation-policy](../rules/catalog.md) |
| decision-log-writer | ADR / decision log を書く | 設計判断が必要 | global | [documentation-policy](../rules/catalog.md) |
| runbook-writer | 運用手順、障害対応、rollback を書く | production ops | project | [documentation-policy](../rules/catalog.md) |
| changelog-release-notes | changelog / release notes を書く | release 準備 | project | [documentation-policy](../rules/catalog.md) |
| session-handoff | 次セッションへ引き継ぐ情報を整理する | 長時間作業、context移行 | global | [agentops-task-policy](../rules/catalog.md) |
| freshness-audit | 公式 docs、release notes、version を確認する | 最新性が必要 | global | [freshness-policy](../rules/catalog.md) |
| cross-model-delegate | Claude / Codex / subagent へ分担する | cross-review、広範囲調査、別 CLI での独立確認 | global | [review-policy](../rules/catalog.md) |
| review-loop-guard | レビュー修正ループを制御する | レビュー後修正 | global | [review-policy](../rules/catalog.md) |
| notification-digest-writer | `.agentops/` の plans / tasks / handoffs / next-session.md / runs を集約して Discord embed payload (`--kind daily|weekly|monthly|alert|session-*` 等) を整形する | cron / hook / 手動アラート | global | [notification-policy](../rules/catalog.md) |
| project-localize-inventory | 既存プロジェクトの設計痕跡 (CLAUDE.md / AGENTS.md / .codex / .claude / .cursorrules 等) を inventory 化し、4 戦略 (greenfield / inventory-rebuild / coexistence / freeze) のうち 1 つを推奨する | 新規 onboarding、グローバル設計改訂後の見直し | global | [project-integration-policy](../rules/catalog.md) |

## 生成時の注意

- 1 Skill は 1 つの反復可能な仕事に絞る。
- description には「何をするか」と「いつ使うか」を入れる。
- Claude Code では `allowed-tools` や slash invocation の扱いを確認する。
- Codex では `name` / `description`、supporting files、implicit invocation、plugin 配布の扱いを確認する。
- scripts は deterministic な処理が必要な場合だけ付ける。
