# Plan: 担当列必須化 + Phase ownership lint の rule 化

plan-id: 2026-05-02-phase-ownership-rule
status: approved
created_at: 2026-05-02
approved_at: 2026-05-02T13:00:00+09:00
timezone: Asia/Tokyo

## 親 plan ファイル

本 plan の主文は orchestrator (Claude) plan workspace 側の `~/.claude/plans/plan-archive-2026-05-02-discord-notify-vivid-brooks.md` に保管されており、agentops repo 主記録としての本ファイルはエントリポイント + 進捗 + Phase 担当列を保持する。

cross-review run 記録:
- 1 周目: `.agentops/runs/20260502T130644+0900-codex-review_frontier/` (P1 2 件 + P2 2 件指摘)
- 2 周目: `.agentops/runs/20260502T131143+0900-codex-review_frontier/` (P0/P1=0、P2 mechanical 1 件残存 → orchestrator 直接 patch で解消)

## 背景

2026-05-02 セッションで 5 工程フロー違反 (Phase 2 実装を Codex coding_frontier に委譲せず orchestrator が直接実装) が発生。handoff `archive/2026-05-02-discord-notify-cleanup-and-sentrux-catalog/handoffs/2026-05-02-5-process-flow-violation-and-prevention.md` で 5 本立て中期再発防止策 (A-E) を文書化。本 plan は **A (担当列必須化) + B (Phase ownership lint 軽量専用 check) のみ切り出し** + `~/.claude/.agentops/` archive 整理を扱う。

## 目的

- `rules/model-routing.md` に新節 2 つ追加: 「実装着手前チェックポイント (Phase 担当宣言)」+「Phase ownership lint (記載漏れ専用 check)」
- `rules/catalog.md` / `skills/catalog.md` に新 entry 登録 (`phase-owner-declaration` rule + `phase-ownership-lint` skill)
- `templates/agentops/plans/current.md` / `templates/agentops/tasks/task.md` 雛形に担当列追加
- `AGENTS.md` に Phase ownership lint 節を 1-2 行追記 (cross-review 記述は変えない、両 CLI 共通記述として AGENTS.md 単独完結)

## 非目的

- 中期 C (グローバル設定全面命令形化)、D (review-policy.md 改訂 + 17 箇所同期)、E (CLAUDE.md/AGENTS.md「軽微変更でも影響範囲必須調査」明記)、長期 (hook 強化 `pre_tool_use.py`) は本 plan 対象外、別 plan で起票
- `CLAUDE.md` (agentops repo) の編集は **行わない** (CLAUDE.md:22 責務分離: 両 CLI 共通の更新は AGENTS.md 単独完結)
- 既存 `rules/model-routing.md` 「Plan agent と cross-review の区別」節は **変更しない** (cross-review は本来観点に専念)

## 影響範囲

### agentops repo 修正 (Phase 3 で Codex coding_frontier 担当)
- `rules/model-routing.md` (新節 2 追加)
- `rules/catalog.md` (新 entry)
- `skills/catalog.md` (新 entry)
- `templates/agentops/plans/current.md` (担当列追加)
- `templates/agentops/tasks/task.md` (Phase 列追加)
- `AGENTS.md` (1-2 行追記)
- `.agentops/plans/current.md` (本ファイル、Phase 3a で作成済)
- `.agentops/task-plans/current.md` (Phase 3a で作成済)
- `.agentops/tasks/01-phase-ownership-rule-impl.md` (Phase 3a で作成済)

### グローバル反映 (Phase 6 で Claude orchestrator が実施、user 承認必要)
- `~/.claude/rules/model-routing.md` (PR merge 後の同期)

### `~/.claude/.agentops/` archive 整理 (Phase 7 で Claude orchestrator が実施、user 承認必要)
- `~/.claude/.agentops/plans/current.md`, `task-plans/current.md`, `handoffs/*` を archive へ移動
- `.tmp/` 配下 backup / hook fixtures / event log を削除

## Phase 担当 (担当列必須化、Phase 着手前 1 行宣言)

| # | Phase | work area | 担当 | 状況 |
|---|---|---|---|---|
| 1 | 設計 / 影響範囲調査 / plan 作成 | 本 plan + Explore 3 体 | Claude orchestrator_frontier | 完了 |
| 1.5 | Phase ownership lint | 本 plan ファイル | 軽量モデル (agentops-research-fast) | 完了 (PASS) |
| 2 | 設計レビュー (cross-review) | 本 plan ファイル | Codex review_frontier (effort high) | 完了 (2 周、P0/P1=0) |
| 3a | agentops repo 主記録作成 | `.agentops/plans/`, `task-plans/`, `tasks/` | Claude orchestrator_frontier | **進行中** |
| 3b | agentops repo 実装 | rules/, templates/, AGENTS.md, catalog | Codex coding_frontier (effort high) | 未着手 |
| 4 | 実装レビュー | PR diff | Codex review_frontier (effort high) | 未着手 |
| 4.5 | merge 前 archive (1 PR scope 完結原則) | merge 前 commit に含める | Claude orchestrator_frontier | 未着手 |
| 5 | 最終判断 / auto-merge | agentops PR | Claude orchestrator_frontier | 未着手 |
| 6 | グローバル反映 | `~/.claude/rules/model-routing.md` | Claude orchestrator_frontier (user 承認必要) | 未着手 |
| 7 | `~/.claude/.agentops/` archive 整理 | plans / task-plans / handoffs / .tmp / runs | Claude orchestrator_frontier (user 承認必要) | 未着手 |
| 8 | next-session.md 整備 | `~/.claude/.agentops/prompts/` | Claude orchestrator_frontier | 未着手 |

各 Phase 着手前に「Phase X — 担当: <model> (役割)」の 1 行を発する。宣言なしで Edit/Write を呼ばない。

## 完了条件

- 上記 agentops repo 修正 8 ファイル (plans/task-plans/tasks 含む) が PR として merge される
- `python3 -m compileall tools` exit 0
- `AGENTS.md` 追記が既存「設計段階 cross-review」記述を変更しておらず、`CLAUDE.md` に差分なし
- `rules/model-routing.md` 既存「Plan agent と cross-review の区別」節が変更されていない
- グローバル反映 (Phase 6) の docs/16 チェックリスト遵守
- `~/.claude/.agentops/` archive 整理 (Phase 7) の dry-run manifest + mkdir + 直前 find 確認の 5 手順遂行

## 停止条件

- Codex cross-review (Phase 2 / 4) で P0/P1 残存 (3 周目 = user 確認)
- agentops repo PR merge 失敗、CI fail、観察事実食い違い
- `~/.claude/.agentops/` 整理時、進行中ファイル発見 (新規生成等)
- グローバル反映時 `diff` で手動編集差分発見
- 中期 C/D/E、長期 hook 強化に踏み込まない (本 plan scope 外)

## 検証方針

詳細は親 plan ファイル `~/.claude/plans/plan-archive-2026-05-02-discord-notify-vivid-brooks.md` の「## 検証」セクション参照。

- Phase 1.5 検証: 担当列・宣言欄の存在確認 (PASS 済)
- Phase 5 検証: `python3 -m compileall tools` / 雛形互換 / AGENTS.md・CLAUDE.md 整合 / catalog format / markdown lint
- Phase 6 検証: `claude --version` / 公式 docs / diff / `/memory` 確認 / 反映結果記録 (docs/16 遵守)
- Phase 7 検証: `~/.claude/.agentops/` 各ディレクトリの整理状態 + archive 配下移動済確認
