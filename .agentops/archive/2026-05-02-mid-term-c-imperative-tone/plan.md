# Plan: 中期 C — グローバル設定全面命令形化 + 5 工程フロー Phase 4 役割分離

plan-id: 2026-05-02-mid-term-c-imperative-tone
status: approved
created_at: 2026-05-02
approved_at: 2026-05-02T14:53:00+09:00
timezone: Asia/Tokyo

- ID: `2026-05-02-mid-term-c-imperative-tone`
- 起票: 2026-05-02
- 起票者: Claude orchestrator
- 親 handoff: `~/.claude/.agentops/handoffs/2026-05-02-mid-term-cde-plan-followup.md` §中期 C
- 種別: 中期再発防止策 (5 工程フロー違反の根本対策の一部)
- リスク: 高 (durable instructions / catalog / AGENTS.md / global rules 改訂)
- ステータス: 進行中 (Phase 3 実装完了、Phase 4 review 待ち)
- user 承認: 2026-05-02 ExitPlanMode で承認済 (真ソース plan: `~/.claude/plans/plan-c-cryptic-pixel.md`)

## 全文

本 plan の全文は `~/.claude/plans/plan-c-cryptic-pixel.md` を真ソースとする。本ファイルは agentops repo 内での運用 entry として、要約と参照を提供する。

## scope

### A-1: 文末曖昧表現の命令形化 (採用候補 ~9 件)
- AGENTS.md / CLAUDE.md / docs/10 / docs/11 / docs/12 / docs/13 / docs/18 / templates/claude/CLAUDE.md / templates/codex/AGENTS.md

### A-2: Phase 4 役割分離 (4-α 同系列独立実装レビュー + 4-β cross-review 別系列) 整合修正
- rules/model-routing.md (5 工程フロー表 Phase 4 行)
- rules/auto-merge-permission.md (許諾条件 §2 4-α / 4-β 両者通過の明示)
- AGENTS.md § AI auto-merge 許諾
- CLAUDE.md § Claude 固有メモ
- docs/03-dbc-and-quality-gates.md / docs/04-model-routing.md / docs/05-review-policy.md (Phase 4 役割分離定義の寄せ先)

**注**: `agentops/rules/review-policy.md` は agentops repo に存在しないため対象外 (新規 rule 追加は非目的)。Phase 4 の役割分離定義は `docs/05-review-policy.md` に集約。4-α (cross-review **ではない** 独立検証) と 4-β (cross-review = 別系列) を明確に分離する。

### B (Phase 6 別作業 = 本 plan PR 完了条件外)
- `~/.claude/skills/` 配下 8 SKILL.md の日本語化 (cross-review / cross-model-delegate / freshness-audit / requirements-review / review-loop-guard / session-handoff / weekly-audit / monthly-audit)

## Phase 詳細表

| Phase | 内容 | 担当 (model / role) |
| --- | --- | --- |
| 0 | 起票準備 | orchestrator (Claude) |
| 1 | 対象選定基準確定 + 最終対象リスト | research_fast (Explore agent) |
| 1.5 | Phase ownership lint | docs_agent or Plan agent |
| 2 | 設計レビュー (Codex cross-review) | review_frontier (Codex, effort high) |
| 3 | 実装 | coding_frontier (Codex, effort high) |
| 4-α | 同系列独立実装レビュー (Codex 別 session、cross-review **ではない**) | review_frontier (Codex, effort high) |
| 4-β | cross-review (別系列、本来の cross 観点) | review_frontier (Claude, internal sub-agent) |
| 4.5 | archive task + archive plan + next-session.md (merge 前 commit) | orchestrator (Claude) + coding_fast |
| 5 | PR 作成 / CI / merge / 同期確認 | orchestrator (Claude) |
| 6 (別作業) | グローバル反映 (本 plan 完了条件外) | orchestrator (Claude) + research_fast + coding_frontier |

各 Phase 着手前、担当エージェントは以下の形で 1 行宣言する:

```text
Phase X — 担当: <model or CLI> (<role>)
```

宣言欄の記録先: `.agentops/task-plans/current.md` の Phase 着手記録欄。

## 親 task

- `.agentops/tasks/01-imperative-tone-unify.md` — Phase 1〜5 完結 task

## 完了条件 (要約)

- Phase 1〜5 完了 (Phase 4 は 4-α + 4-β の両レビュー通過)
- AI auto-merge 許諾条件 6 全 AND を満たして main にマージ済
- main 同期確認済
- archive task / archive plan が `.agentops/archive/2026-05-02-mid-term-c-imperative-tone/` 配下に存在
- `.agentops/prompts/next-session.md` が中期 D または「次タスクなし」を指す
- (Phase 6 別作業はこの plan の完了条件には含めない、user 提示するのみ)

## 共通教訓 (handoff §共通教訓、本 plan で再発させない)

1. **5 工程フロー違反**: 担当列必須化 + Phase ownership lint で対策済 → 本 plan で実践
2. **1 PR scope 完結原則違反**: archive task + archive plan を Phase 4.5 で両方 merge 前 commit に含める
3. **cross-review 過剰**: kind: mechanical は orchestrator 直接 patch で完結、再 cross-review 不要
4. **別 chore PR 起票時の user 明示許可 3 要件**: 暗黙承認解釈を禁止

## 参照

- 真ソース plan: `~/.claude/plans/plan-c-cryptic-pixel.md`
- 親 handoff: `~/.claude/.agentops/handoffs/2026-05-02-mid-term-cde-plan-followup.md`
- 関連 rule: `~/.claude/rules/model-routing.md` / `auto-merge-permission.md` / `review-policy.md`
- agentops 反映元: `agentops/rules/model-routing.md` / `auto-merge-permission.md` / `docs/05-review-policy.md`
