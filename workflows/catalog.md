# workflow catalog

AI エージェントが Claude Code / Codex の仕様と対象プロジェクトに合わせて生成する workflow 候補です。

> 関連表: workflow から代表 rule を辿る逆参照は本ファイルの「関連 rule（代表）」列、rule 起点で代表 skill / workflow / hook を辿る場合は [docs/17-cross-reference.md](../docs/17-cross-reference.md) を参照。
>
> **代表選定の非相互性**: 本ファイルの `workflow → rule（代表）` と docs/17 の `rule → workflow（代表）` は必ずしも相互一致しない（各方向で「最初に見るべき代表 1 件」を独立に選定）。網羅性が必要な場合は両表 + [rules/catalog.md](../rules/catalog.md) を併読する。

| 候補名 | 用途 | 発火条件 | 主な出力先 | 関連 rule（代表） |
| --- | --- | --- | --- | --- |
| project-intake | 対象パス、スタック、デプロイ先、検証コマンド、制約を確認する | 新規プロジェクト着手 | `.agentops/plans/current.md` | [project-scope](../rules/catalog.md) |
| plan-approval | 目的、非目的、影響範囲、完了条件、停止条件を整理し承認を得る | 実装前、削除前、外部反映前 | `.agentops/plans/current.md` | [planning-approval](../rules/catalog.md) |
| feature-delivery | 実装、検証、docs、レビュー、PR までの流れを組む | 新機能、修正 | `.agentops/task-plans/current.md` | [git-and-branch-policy](../rules/catalog.md) |
| web-system-design | Web システム設計の要件、境界、データ、運用を整理する | Web 設計 | docs / `.agentops/tasks/` | [design-policy](../rules/catalog.md) |
| deployment-target-selection | Cloudflare、Xserver、GCP、ローカルの選定軸を確認する | deploy 先検討 | docs / project config | [deployment-target-policy](../rules/catalog.md) |
| code-review | correctness、security、tests、regression をレビューする | PR、差分確認 | review comment / `.agentops/reviews/` | [review-policy](../rules/catalog.md) |
| design-review | 要件、境界、データ、運用、セキュリティをレビューする | 設計レビュー | review comment / docs | [design-policy](../rules/catalog.md) |
| cross-review | 主 orchestrator とは別 CLI / 別モデルファミリーの frontier reviewer に確認を依頼し、採否を主 orchestrator が判断する | 高リスク変更、新機能、リファクタ、依存追加、API 契約変更、デプロイ影響、レビュー修正後 | `.agentops/reviews/` / `.agentops/runs/` | [review-policy](../rules/catalog.md) |
| docs-update | README、docs、runbook、release notes の更新漏れを確認する | docs 影響あり | docs | [documentation-policy](../rules/catalog.md) |
| dependency-introduction | 新規依存の必要性、license、security、代替を確認する | dependency 追加 | plan / review | [secret-policy](../rules/catalog.md) |
| freshness-audit | 公式 docs、release notes、version を確認する | 最新性が必要 | docs / plan | [freshness-policy](../rules/catalog.md) |
| release-readiness | release 前検証、rollback、monitoring、docs を確認する | release 前 | checklist / PR | [git-and-branch-policy](../rules/catalog.md) |
| production-operations | 本番運用変更の手順、監視、rollback を整理する | production ops | runbook | [destructive-operation-policy](../rules/catalog.md) |
| session-handoff | 次セッションの入口、未完了、検証、リスクをまとめる | context 移行 | `.agentops/prompts/next-session.md` | [agentops-task-policy](../rules/catalog.md) |
| reference-kit-migration | カタログ、テンプレート、archive の参照切れを防ぎながら移行する | agentops 構造整理 | `.agentops/tasks/` | [agentops-task-policy](../rules/catalog.md) |

## 生成時の注意

- workflow は対象 CLI の native skill、slash command、prompt、subagent のどれで表すかを実環境で判断する。
- `.agentops` は作業計画と履歴のサンプルとして使い、完了済み task を未完了入口に残さない。
- 実プロジェクト固有コマンドは global workflow に固定せず、project 側へ置く。
