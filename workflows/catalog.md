# workflow catalog

AI エージェントが Claude Code / Codex の仕様と対象プロジェクトに合わせて生成する workflow 候補です。

| 候補名 | 用途 | 発火条件 | 主な出力先 |
| --- | --- | --- | --- |
| project-intake | 対象パス、スタック、デプロイ先、検証コマンド、制約を確認する | 新規プロジェクト着手 | `.agentops/plans/current.md` |
| plan-approval | 目的、非目的、影響範囲、完了条件、停止条件を整理し承認を得る | 実装前、削除前、外部反映前 | `.agentops/plans/current.md` |
| feature-delivery | 実装、検証、docs、レビュー、PR までの流れを組む | 新機能、修正 | `.agentops/task-plans/current.md` |
| web-system-design | Web システム設計の要件、境界、データ、運用を整理する | Web 設計 | docs / `.agentops/tasks/` |
| deployment-target-selection | Cloudflare、Xserver、GCP、ローカルの選定軸を確認する | deploy 先検討 | docs / project config |
| code-review | correctness、security、tests、regression をレビューする | PR、差分確認 | review comment / `.agentops/reviews/` |
| design-review | 要件、境界、データ、運用、セキュリティをレビューする | 設計レビュー | review comment / docs |
| docs-update | README、docs、runbook、release notes の更新漏れを確認する | docs 影響あり | docs |
| dependency-introduction | 新規依存の必要性、license、security、代替を確認する | dependency 追加 | plan / review |
| freshness-audit | 公式 docs、release notes、version を確認する | 最新性が必要 | docs / plan |
| release-readiness | release 前検証、rollback、monitoring、docs を確認する | release 前 | checklist / PR |
| production-operations | 本番運用変更の手順、監視、rollback を整理する | production ops | runbook |
| session-handoff | 次セッションの入口、未完了、検証、リスクをまとめる | context 移行 | `.agentops/prompts/next-session.md` |
| reference-kit-migration | カタログ、テンプレート、archive の参照切れを防ぎながら移行する | agentops 構造整理 | `.agentops/tasks/` |

## 生成時の注意

- workflow は対象 CLI の native skill、slash command、prompt、subagent のどれで表すかを実環境で判断する。
- `.agentops` は作業計画と履歴のサンプルとして使い、完了済み task を未完了入口に残さない。
- 実プロジェクト固有コマンドは global workflow に固定せず、project 側へ置く。
