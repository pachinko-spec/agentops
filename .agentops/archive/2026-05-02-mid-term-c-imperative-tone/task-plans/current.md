# Task Plan: 中期 C — Phase 0 着手 (本セッション)

- 親 plan: `.agentops/plans/current.md` (`2026-05-02-mid-term-c-imperative-tone`)
- セッション開始: 2026-05-02
- 担当 orchestrator: Claude
- 現在ブランチ: `claude/mid-term-c-imperative-tone`

## 本セッションの目標

Phase 0 (起票準備) → Phase 1 (対象選定) → Phase 1.5 (ownership lint) → Phase 2 (Codex cross-review) → Phase 3 (実装) → Phase 4 (4-α 同系列独立実装レビュー + 4-β cross-review) → Phase 4.5 (archive) → Phase 5 (PR / merge) を 1 セッション内で完遂を試みる。中期 plan の規模 (採用 ~9 件 + Phase 4 役割分離整合修正) は小〜中規模のため 1 セッション内完了が現実的。

## Phase 詳細表 (担当列必須)

| Phase | 内容 | 担当 (model / role) | 想定時間 |
| --- | --- | --- | --- |
| 0 | 起票準備 (本ファイル含む) | orchestrator (Claude) | 10 min |
| 1 | 対象選定基準確定 | research_fast (Explore agent) | 15 min |
| 1.5 | Phase ownership lint | docs_agent or Plan agent | 5 min |
| 2 | 設計レビュー (Codex cross-review) | review_frontier (Codex) | 20 min |
| 3 | 実装 (文末書き換え + Phase 4 役割分離) | coding_frontier (Codex) | 30 min |
| 4-α | 実装レビュー (Codex) | review_frontier (Codex) | 15 min |
| 4-β | 実装レビュー (Claude 内部) | review_frontier (Claude internal) | 10 min |
| 4.5 | archive + next-session 更新 | orchestrator (Claude) | 10 min |
| 5 | PR / CI / merge / 同期確認 | orchestrator (Claude) | 15 min |

## Phase 着手記録欄 (1 行宣言)

各 Phase 着手前、担当が以下に追記する:

- [x] Phase 0 — 担当: Claude (orchestrator_frontier) — 完了: 2026-05-02
- [x] Phase 1 — 担当: research_fast (Explore agent) — 完了: 2026-05-02
- [x] Phase 1.5 — 担当: docs_agent — 完了: 2026-05-02 (Phase ownership lint OK)
- [x] Phase 2 — 担当: Codex (review_frontier, effort high) — 完了: 2026-05-02 (P0=0, P1=3, P2=1、kind:design 軽微変更で orchestrator 反映、ループ 1 周目)
- [x] Phase 3 — 担当: Codex (coding_frontier, effort high) — 完了: 2026-05-02
- [x] Phase 4-α — 担当: Codex (review_frontier, effort high) — 完了: 2026-05-02 (P0=P1=P2=P3=0、指摘なし)
- [x] Phase 4-β — 担当: Claude (review_frontier internal, agentops-reviewer) — 完了: 2026-05-02 (P0=0/P1=0/P2=2/P3=2、merge 可能、P2-1 mechanical patch 反映済、ループ 1 周目)
- [ ] Phase 4.5 — 担当: orchestrator (Claude) (着手中)
- [ ] Phase 5 — 担当: (未着手)

## 親 task

- `.agentops/tasks/01-imperative-tone-unify.md`

## DbC (本セッション)

### 前提条件
- main branch が origin/main と同期済
- `claude/mid-term-c-imperative-tone` branch を作成済
- `.agentops/plans/current.md` が存在 (本ファイル含む)
- 本 plan の真ソース `~/.claude/plans/plan-c-cryptic-pixel.md` が user 承認済

### 不変条件
- 形式変更のみで rule の意味は変わらない (A-1 部分)
- Phase 4 役割分離記述は kind 分岐や他構造に踏み込まない (A-2 部分)
- agentops repo PR は単一 scope (採用リスト外の差分なし)
- secret 値が diff / commit / PR / log に出現しない
- archive task + archive plan は merge 前 commit に含まれる

### 完了条件
- Phase 1〜5 完了
- main にマージ済 + 同期確認済
- archive 完了

### 停止条件
- レビュー修正 2 周超
- 採用判断で意味変更を伴う候補が 3 件以上
- 中期 D 想定範囲との conflict
- secret / 本番 / 課金 / 外部公開 / 破壊的操作

## 採用 / 除外候補リスト (Phase 1 確定 + Codex Phase 2 review 反映済)

### A-1 採用候補 (8 件確定)

| ファイル | 行 | 現状 | 提案 |
| --- | --- | --- | --- |
| AGENTS.md | 5 | 「両ファイルの章立ては本ファイルを基準にしてください」 | 「両ファイルの章立ては本ファイルを基準にする」 |
| CLAUDE.md | 5 | 「`AGENTS.md` を参照してください」 | 「`AGENTS.md` を参照する」 |
| docs/10-cli-wrapper.md | 101 | 「`{model_arg}` を推奨する」 | 規範強度ガード: 現状維持または「`{model_arg}` を採用する」(意味確認後 Phase 3 で確定) |
| docs/11-monitoring-cli.md | 220 | 「先に走らせて確認する運用を推奨する」 | 規範強度ガード: 「先に走らせて差分を確認する運用を採る」または現状維持 |
| docs/13-design-evaluation.md | 15 | 「設計を維持するのがよい」 | 「設計を維持する」(規範強度ガード適用、許可文脈) |
| docs/18-notification-strategy.md | 29 | 「グローバル設定で参照しても良い」 | 「グローバル設定で参照可能」または「グローバル設定から参照する」(許可文脈、Phase 3 で文脈確認) |
| templates/claude/CLAUDE.md | 3 | 「既存設定を確認してください」 | 「既存設定を確認する」 |
| templates/codex/AGENTS.md | 3 | 「既存設定を確認してください」 | 「既存設定を確認する」 |

### A-1 除外候補 (7 件確定)

| ファイル | 行 | 内容 | 除外理由 |
| --- | --- | --- | --- |
| docs/01-philosophy.md | 99 | 「単純な手順が強い場合がある」 | 除外 (c) (事実陳述) |
| docs/10-cli-wrapper.md | 22 | `--message "設計をレビューしてください"` | 除外 (a) (コマンド例文字列) |
| docs/10-cli-wrapper.md | 80 | 「動かない可能性があるため」 | 除外 (c) (事実陳述、Codex Phase 2 review 追加検出) |
| docs/10-cli-wrapper.md | 123 | 「failure または timeout することがある」 | 除外 (c) (事実陳述) |
| docs/12-harness-engineering.md | 90 | 「将来 `--harness` 引数を追加してもよい」 | 除外 (d) (規範強度変更不可、許可文脈) |
| skills/catalog.md | 73 | (description) 「4 戦略のうち 1 つを推奨する」 | 除外 (b) (description 機能説明) |
| templates/claude/skill/agentops-localize/SKILL.md | 3 | (description) 「1 つを推奨する」 | 除外 (b) (description 機能説明、Codex Phase 2 review 追加検出) |

### A-2 Phase 4 役割分離対象ファイル (Codex Phase 2 review 反映後、7 ファイル)

「Phase 4 担当 = Codex review_frontier 単独」記述を **「4-α: 同系列独立実装レビュー (cross-review ではない) + 4-β: cross-review (別系列、本来の cross 観点)」** の役割分離構造に修正する。

| ファイル | 触る範囲 |
| --- | --- |
| rules/model-routing.md | 5 工程フロー表 Phase 4 行 |
| rules/auto-merge-permission.md | 許諾条件 §2 (4-α / 4-β 両者通過の明示) |
| AGENTS.md | AI auto-merge 許諾節 / 設計段階 cross-review |
| CLAUDE.md | Claude 固有メモ (5 工程フロー言及部) |
| docs/03-dbc-and-quality-gates.md | マージ条件 (cross-review 記述部) |
| docs/04-model-routing.md | 5 工程フロー (Phase 4 役割分離) |
| docs/05-review-policy.md | cross-review (本来の意味 = 別系列のみを 4-β に適用、4-α は cross-review **ではない** 役割名で分離) |

**注**: `agentops/rules/review-policy.md` は agentops repo に **存在しない** (rules/ は auto-merge-permission.md / catalog.md / model-routing.md / session-record-and-handoff.md のみ)。新規 rule 追加は本 plan の非目的、Phase 4 の役割分離定義は `docs/05-review-policy.md` に集約する。

4-α / 4-β の役割名を使う。cross-review = 別系列レビュー (本来の定義) を 4-β のみに適用、4-α は同系列独立実装レビューとして別役割名で扱う。

## 参照

- 真ソース plan: `~/.claude/plans/plan-c-cryptic-pixel.md`
- 親 handoff: `~/.claude/.agentops/handoffs/2026-05-02-mid-term-cde-plan-followup.md`
