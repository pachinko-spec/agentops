# rule catalog

AI エージェントがグローバル設定やプロジェクト設定へ取り込むか判断する rule 候補です。実際に置く文言、粒度、ファイル形式は対象 CLI の公式 docs と実設定を確認して調整します。

> 関連表: rule から代表 skill / workflow / hook を辿る場合は [docs/17-cross-reference.md](../docs/17-cross-reference.md) を参照。

| 候補名 | 用途 | 主な適用先 | 採用判断 | 関連 skill（代表） | 関連 workflow（代表） | 関連 hook（代表） |
| --- | --- | --- | --- | --- | --- | --- |
| language-policy | 応答、commit、PR、レビュー、handoff を日本語中心にする | global | 日本語話者の個人開発では global 候補 | docs-review | docs-update | — |
| planning-approval | 実装、削除、外部反映前に計画と承認を求める | global / project | 大きな変更が多い環境では global 候補 | requirements-review | plan-approval | — |
| git-and-branch-policy | 作業ブランチ、PR、merge、main 同期を統一する | global / project | GitHub 運用が前提なら global 候補 | release-readiness-review | feature-delivery | scripts/hooks/pre-commit |
| project-scope | 実作業対象、dotfiles 除外、プロジェクト固有設定優先を明確にする | global | 個人開発の境界として global 候補 | architecture-boundary-review | project-intake | — |
| project-integration-policy | 既存プロジェクトに残る Claude Code / Codex / Antigravity / Cursor / Gemini 等の旧設計痕跡と新グローバル設計との競合判定・統合戦略 (greenfield / inventory-rebuild / coexistence / freeze) を明確にする | global | 既存プロジェクトの onboarding やグローバル設計改訂後の見直しに採用。詳細は [docs/19-project-localization.md](../docs/19-project-localization.md) | project-localize-inventory | project-localize | — |
| freshness-policy | ライブラリ、CLI、API、モデルの最新性を公式情報で確認する | global | 変化の速い技術スタックでは global 候補 | freshness-audit | freshness-audit | — |
| documentation-policy | 実装差分に応じて README、docs、runbook、release notes を更新する | global / project | docs 更新漏れが課題なら global 候補 | docs-maintainer | docs-update | — |
| review-policy | correctness、security、regression、tests を優先してレビューする | global / project | レビュー品質を上げたい場合に採用 | correctness-review | code-review | — |
| design-policy | 前提条件、非目的、完了条件、停止条件を設計時に明確にする | global / project | 設計なし実装を避けたい場合に採用 | requirements-review | design-review | — |
| deployment-target-policy | Cloudflare、Xserver、GCP、ローカルの選定軸を確認する | project | デプロイ先が決まるプロジェクトで採用 | deployment-adapter | deployment-target-selection | — |
| secret-policy | secret を diff、ログ、PR、handoff に出さない | global | 原則 global 候補 | security-review | code-review | — |
| destructive-operation-policy | 削除、reset、外部公開、課金変更前に確認する | global | 原則 global 候補 | reliability-design-review | release-readiness | — |
| agentops-task-policy | `.agentops` の plan、task、archive を使い、完了済み task を未完了入口に残さない | project / global | 長い作業を分割する運用で採用 | session-handoff | session-handoff | — |
| auto-merge-permission | AI auto-merge 許諾条件 6 (全 AND) + 停止条件 + post-merge 1 PR scope 完結原則 + 「user 明示許可」3 要件例外条項 + 適用範囲 + 取消条件 | global | グローバル既定として全プロジェクト適用、durable instructions | release-readiness-review | feature-delivery | hooks/_common.py inspect_agentops |
| session-record-and-handoff | `.agentops/` 責務テーブル + 運用フロー + セッション分割条件 + マージ後報告 + prompts/next-session.md 同セッション内更新原則 (hook 整合) | global | 長い作業を分割する運用や agentops 運用標準として採用 | session-handoff | session-handoff | hooks/_common.py inspect_agentops |
| notification-policy | Discord webhook の channel 区分（DAILLY/WEEKLY/MONTHLY/ANT_TIME）と SECRET 管理、ANT_TIME 頻度上限、SessionStart/End と PermissionRequest 待ちの発火境界、cron 失敗時挙動を統一する | global | 通知運用がある場合に採用。詳細は [docs/18-notification-strategy.md](../docs/18-notification-strategy.md) | notification-digest-writer | notification-cron-setup | — |

## 生成時の注意

- Codex の `Rules` は sandbox 外コマンド許可の意味を持つため、このカタログの rule と混同しない。
- `AGENTS.md` / `CLAUDE.md` には安定した作業思想だけを置き、長い手順や観点別チェックは Skill、workflow、template へ分ける。
- 実プロジェクト固有の test、build、deploy、rollback、secret、remote URL は global ではなく project 側へ置く。
