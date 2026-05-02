# Task Plan: 担当列必須化 + Phase ownership lint rule 化 (本セッション実行計画)

plan-id: 2026-05-02-phase-ownership-rule
status: approved
created_at: 2026-05-02
timezone: Asia/Tokyo

## 今回の目的

本セッションで Phase 1〜5 (agentops repo PR merge まで) と Phase 6〜8 (グローバル反映 + `~/.claude/.agentops/` archive 整理 + next-session.md 整備) を完遂する。

## Phase 担当 (担当列必須化、Phase 着手記録欄)

| Phase | 担当 | 状況 | 着手宣言 (1 行記録) |
|---|---|---|---|
| 1 | Claude orchestrator_frontier | 完了 | "Phase 1 (設計 / 影響範囲調査) — 担当: Claude orchestrator_frontier (本セッション)" |
| 1.5 | agentops-research-fast (軽量) | 完了 (PASS) | "Phase 1.5 (Phase ownership lint) — 担当: agentops-research-fast (Sonnet 4.6 ベース subagent)" |
| 2 (1 周目) | Codex review_frontier | 完了 | run `20260502T130644+0900-codex-review_frontier` |
| 2 (2 周目) | Codex review_frontier | 完了 | run `20260502T131143+0900-codex-review_frontier` (P0/P1=0) |
| 3a | Claude orchestrator_frontier | **進行中** | "Phase 3a (agentops repo 主記録作成) — 担当: Claude orchestrator_frontier" |
| 3b | Codex coding_frontier | 未着手 | (Codex 側で着手時に発する: "Phase 3b (agentops repo 実装) — 担当: Codex coding_frontier (effort high)") |
| 4 | Codex review_frontier | 未着手 | run id 着手時記録 |
| 4.5 | Claude orchestrator_frontier | 未着手 | merge 前 archive (1 PR scope 完結原則) |
| 5 | Claude orchestrator_frontier | 未着手 | auto-merge or user 確認 |
| 6 | Claude orchestrator_frontier | 未着手 | グローバル反映 (user 承認必要) |
| 7 | Claude orchestrator_frontier | 未着手 | `~/.claude/.agentops/` archive 整理 (user 承認必要) |
| 8 | Claude orchestrator_frontier | 未着手 | `~/.claude/.agentops/prompts/next-session.md` 整備 |

## 実行順

1. Phase 1 (済): plan 設計 + Explore 3 体 + 影響範囲調査
2. Phase 1.5 (済): Phase ownership lint (agentops-research-fast、PASS)
3. Phase 2 (済): Codex cross-review 2 周 (P0/P1=0)
4. Phase 3a (進行中): `.agentops/plans/current.md`, `task-plans/current.md`, `tasks/01-*.md` 作成 (orchestrator 責務、Codex hook gate 解除)
5. Phase 3b (次): Codex coding_frontier に再委譲 (rules/, templates/, AGENTS.md, catalog 編集)
6. Phase 4: Codex review_frontier で実装レビュー
7. Phase 4.5: merge 前 archive (`scripts/agentops archive task --task-id 01-phase-ownership-rule-impl --dry-run` → 本番)
8. Phase 5: PR 作成 → auto-merge (許諾条件 6 全クリア時) or user 確認
9. Phase 6: agentops PR merge 後、`~/.claude/rules/model-routing.md` グローバル反映 (docs/16 遵守、user 承認必要)
10. Phase 7: `~/.claude/.agentops/` archive 整理 (mkdir / dry-run manifest / 直前 find / 段階実行 / 整理後記録、user 承認必要)
11. Phase 8: `~/.claude/.agentops/prompts/next-session.md` 整備

## 今回は行わないこと

- 中期 C (グローバル設定全面命令形化)
- 中期 D (review-policy.md 改訂 + 17 箇所同期)
- 中期 E (CLAUDE.md/AGENTS.md「軽微変更でも影響範囲必須調査」明記)
- 長期 hook 強化 (`~/.claude/hooks/pre_tool_use.py`)
- agentops repo `CLAUDE.md` の編集 (両 CLI 共通記述として AGENTS.md 単独完結)
- `rules/model-routing.md` 既存「Plan agent と cross-review の区別」節の変更

## 停止条件

- Codex cross-review / 実装レビューで P0/P1 残存 (3 周目 = user 確認)
- agentops repo CI fail / merge 失敗
- `~/.claude/.agentops/` 整理で進行中ファイル発見 (誤削除リスク)
- グローバル反映時 `diff` で手動編集差分発見
