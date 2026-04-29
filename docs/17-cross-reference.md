---
last_reviewed: 2026-04-28
next_review_by: 2026-07-31
reviewer: pachinko-spec
language: ja
---

# rule ↔ skill ↔ workflow ↔ hook 逆参照表

> 上位文書: [docs/01-philosophy.md](./01-philosophy.md), [docs/03-dbc-and-quality-gates.md](./03-dbc-and-quality-gates.md)
> カタログ: [rules/catalog.md](../rules/catalog.md), [skills/catalog.md](../skills/catalog.md), [workflows/catalog.md](../workflows/catalog.md)

## 目的

`rules/`, `skills/`, `workflows/`, `scripts/hooks/` の 4 系統に分散している統制資産を **rule 起点で 1 件ずつ辿れる最小マッピング** に集約する。横断設計レビュー報告書 §7 提案 P1-03（ガバナンスの追跡性が低い）の最小対応であり、rule を変更したときに見直すべき skill / workflow / hook を機械的に列挙できる状態を作る。

## スコープ

本表は **rule 起点の最小マッピング** に限定する（rule 12 × skill 31 × workflow 15 を全て双方向化すると現プロジェクトの粒度では過剰）。

- **本表で扱うこと**: 各 rule に対して代表 skill / 代表 workflow / 代表 hook を 1 件ずつ。該当が無ければ `—`。
- **本表で扱わないこと**: skill / workflow から rule への逆引き、複数候補の網羅、優先順位付け。skill / workflow から rule への逆引きは [skills/catalog.md](../skills/catalog.md) / [workflows/catalog.md](../workflows/catalog.md) の `関連 rule（代表）` 列で扱う（plan `2026-04-29-handoff-followups` task 01 で追加済）。複数候補の網羅と優先順位付けは依然として handoff 候補。
- **代表選定の非相互性**: 本表の `rule → skill / workflow（代表）` と catalog 側 `skill / workflow → rule（代表）` は **必ずしも相互一致しない**（例: `design-policy → requirements-review` だが `requirements-review → planning-approval`）。各方向で独立に「最初に見るべき代表 1 件」を選んでいるため、双方向リンクの厳密一致は保証しない。網羅性が必要な場合は両表 + `rules/catalog.md` を併読する。
- **last-reviewed frontmatter**: 本ファイルは plan `2026-04-28-design-review-p0-p1` task 04（P1-04）で他 docs と同形式の YAML frontmatter を追加済（本ファイル冒頭の `---` 区切りブロック）。

## マッピング表

| rule_id | rule タイトル | 関連 skill（代表） | 関連 workflow（代表） | 関連 hook（代表） |
| --- | --- | --- | --- | --- |
| language-policy | 応答・commit・PR・レビュー・handoff を日本語中心にする | [docs-review](../skills/catalog.md) | [docs-update](../workflows/catalog.md) | — |
| planning-approval | 実装・削除・外部反映前に計画と承認を求める | [requirements-review](../skills/catalog.md) | [plan-approval](../workflows/catalog.md) | — |
| git-and-branch-policy | 作業ブランチ・PR・merge・main 同期を統一する | [release-readiness-review](../skills/catalog.md) | [feature-delivery](../workflows/catalog.md) | [scripts/hooks/pre-commit](../scripts/hooks/pre-commit)（[check-protected-branch](../scripts/check-protected-branch)） |
| project-scope | 実作業対象・dotfiles 除外・プロジェクト固有設定優先を明確にする | [architecture-boundary-review](../skills/catalog.md) | [project-intake](../workflows/catalog.md) | — |
| freshness-policy | ライブラリ・CLI・API・モデルの最新性を公式情報で確認する | [freshness-audit](../skills/catalog.md) | [freshness-audit](../workflows/catalog.md) | — |
| documentation-policy | 実装差分に応じて README・docs・runbook・release notes を更新する | [docs-maintainer](../skills/catalog.md) | [docs-update](../workflows/catalog.md) | — |
| review-policy | correctness・security・regression・tests を優先してレビューする | [correctness-review](../skills/catalog.md) | [code-review](../workflows/catalog.md) | — |
| design-policy | 前提条件・非目的・完了条件・停止条件を設計時に明確にする | [requirements-review](../skills/catalog.md) | [design-review](../workflows/catalog.md) | — |
| deployment-target-policy | Cloudflare・Xserver・GCP・ローカルの選定軸を確認する | [deployment-adapter](../skills/catalog.md) | [deployment-target-selection](../workflows/catalog.md) | — |
| secret-policy | secret を diff・ログ・PR・handoff に出さない | [security-review](../skills/catalog.md) | [code-review](../workflows/catalog.md) | — |
| destructive-operation-policy | 削除・reset・外部公開・課金変更前に確認する | [reliability-design-review](../skills/catalog.md) | [release-readiness](../workflows/catalog.md) | — |
| agentops-task-policy | `.agentops` の plan・task・archive を使い、完了済み task を未完了入口に残さない | [session-handoff](../skills/catalog.md) | [session-handoff](../workflows/catalog.md) | — |

## 表の読み方

- **rule_id**: [rules/catalog.md](../rules/catalog.md) の候補名と一致する。
- **関連 skill / workflow（代表）**: [skills/catalog.md](../skills/catalog.md) / [workflows/catalog.md](../workflows/catalog.md) から、当該 rule を実務適用するときに最初に確認したい代表を 1 件選んだもの。複数候補がある rule でも、初動として参照すべきものに絞る。
- **関連 hook（代表）**: `scripts/hooks/{pre-commit,pre-push}` から、当該 rule の違反を **commit / push 時点で機械的に拒否** する gate を選んだもの。違反検知が hook では成立しない rule（手動のみ、または別経路の CLI で支援する rule）は `—`。

## hook 列が `—` の rule に対する補完経路

hook 列が `—` でも、別経路で rule を機械的・半機械的に支援する場合は以下を参照する。これらは hook の代替ではなく、別レイヤの gate として扱う。

- **destructive-operation-policy**: `scripts/hooks/pre-push`（[check-tests-before-push](../scripts/check-tests-before-push)）は push 前のテスト品質 gate であり、削除・reset・外部公開・課金変更そのものを検知する gate ではない。本 rule は **plan-approval / requirements-review / レビュー時の確認** に依存する。
- **agentops-task-policy**: post-merge の手動 CLI `scripts/agentops archive task`（[docs/11-monitoring-cli.md](./11-monitoring-cli.md) §archive サブコマンド）が完了済み task の archive 移動と `prompts/next-session.md` 更新を支援する。pre-commit / pre-push では起動しない。

## 残課題（次 plan へ handoff）

- **複数候補の網羅**: 1 rule に対して関連 skill / workflow が複数あるケース（例: secret-policy → security-review + dependency-supply-chain-review）の二次候補列追加は依然として handoff 候補。
- **代表選定の相互一致**: 本表と catalog 側で代表選定が非相互になっている。相互一致に寄せるか、現状の「各方向で最も近い 1 件」を維持するかは運用観察で判断（handoff 候補）。
- **catalog 側 frontmatter 追加**: skills/catalog.md / workflows/catalog.md / rules/catalog.md は frontmatter なしで運用中。docs と同形式の YAML frontmatter 追加は handoff 候補。

## 関連リンク

- 設計思想: [docs/01-philosophy.md](./01-philosophy.md), [docs/03-dbc-and-quality-gates.md](./03-dbc-and-quality-gates.md)
- review 運用: [docs/05-review-policy.md](./05-review-policy.md)
- hook 運用: [docs/09-hooks-quality-gates.md](./09-hooks-quality-gates.md)
- archive CLI: [docs/11-monitoring-cli.md](./11-monitoring-cli.md)
- カタログ: [rules/catalog.md](../rules/catalog.md), [skills/catalog.md](../skills/catalog.md), [workflows/catalog.md](../workflows/catalog.md)
- 出典: 横断設計レビュー報告書 [docs/reviews/2026-04-28-cross-repo-design-review.md](./reviews/2026-04-28-cross-repo-design-review.md) §7 P1-03
