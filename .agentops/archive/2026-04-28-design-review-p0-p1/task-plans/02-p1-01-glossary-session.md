# task-plan: task 02 (P1-01) 用語統一表 docs/00-glossary.md 実装セッション

> 親 plan: `2026-04-28-design-review-p0-p1` (`.agentops/plans/current.md`)
> 対象 task: `.agentops/tasks/02-p1-01-glossary.md`
> 現在の状態: **PR A (cleanup) 進行中 → PR B (P1-01 本体) → PR C (archive dogfood)**
> 起票: 2026-04-28 (Asia/Tokyo)
> Plan agent 詳細: `~/.claude/plans/agentops-agentops-tasks-02-p1-01-glossar-linked-naur.md`

---

## 1. 今セッションのスコープ（2026-04-28）

PR を 3 本に分けて scope 単一性を担保する。

| PR | branch | 内容 | merge 方式 |
|---|---|---|---|
| A | `claude/cleanup-stale-task-plan-2026-04-28` | 残置した planning-phase 版 task-plan を archive へ退避 + 現セッション用 `current.md` を新規作成 | self-merge（Codex 省略可、`.agentops/` housekeeping） |
| B | `claude/design-review-impl-p1-01` | task 02 本体実装。docs/00-glossary.md 新規 + docs/01 双方向リンク + 用語ゆれを許容語付き 0 件化 | AI auto-merge（許諾 6 件 OK 時） |
| C | `claude/archive-task-02-dogfood` | task 02 を archive へ移動 + `prompts/next-session.md` 本文書き直し | self-merge（Codex 省略可、`.agentops/` housekeeping） |

各 PR は単独でマージ可能な完結状態。PR 間の依存は A → B → C 順序のみで、内容的には独立。

## 2. 起動手順（既に PR A 着手中、参考）

1. `git status --short --branch` で main + clean を確認、`git fetch origin && git pull --ff-only origin main` で同期。
2. `git checkout -b claude/cleanup-stale-task-plan-2026-04-28` で PR A ブランチを切る。
3. `git mv .agentops/task-plans/current.md .agentops/archive/2026-04-28-design-review-p0-p1/task-plans/initial-planning-phase.md`。
4. 本ファイル（task 02 セッション用 `task-plans/current.md`）を新規作成。
5. commit / push / PR 作成 / 許諾条件 6 件評価 / self-merge / main 同期確認。
6. PR B ブランチ `claude/design-review-impl-p1-01` を main から切り直し、task 02 本体実装。
7. PR B merge 後、PR C ブランチ `claude/archive-task-02-dogfood` で archive task CLI を回し、`next-session.md` 本文を書き直し。

## 3. PR B 実行内容（task 02 DbC ベース、Plan agent §Approach §PR B 参照）

1. `docs/00-glossary.md` 新規作成（19 用語 + 出典 + 許容語リスト）。報告書 Appendix B (`docs/reviews/2026-04-28-cross-repo-design-review.md` L451–) を出発点。
2. `docs/01-philosophy.md` 冒頭に glossary リンク + glossary 側に逆リンク（双方向）。
3. リポジトリ全体の `rg` で用語ゆれを統一（synonym 統一に限る、意味変更なし）。
   - `orchestrator` → 文脈が決定権者なら `主 orchestrator`、ロール名なら `orchestrator_frontier`。
   - `cross-review`（行為）と `cross-model-delegate`（CLI ラッパ）を使い分け。
   - `harness` / `harness spec` / `harness engineering` を docs/12 用語表（L43–48）に揃える。
4. **触らない**: `docs/reviews/`、`archive/`、`.agentops/archive/`、`.agentops/`、`tools/`、`scripts/`。
5. 検証コマンド（PR 本文に転記）:
   - `rg -n "orchestrator" docs/ config/ rules/ skills/ workflows/ CLAUDE.md AGENTS.md | rg -v "orchestrator_frontier|主 orchestrator|orchestrator role|orchestrators|docs/00-glossary.md"` が **0 件**。
   - `rg -n "cross-review|cross-model-delegate" docs/ config/ skills/ workflows/ CLAUDE.md AGENTS.md` が許容語と整合。
   - `rg -n "\bharness\b|harness spec|harness engineering" docs/12-harness-engineering.md docs/03-dbc-and-quality-gates.md` が docs/12 用語表と整合。
   - `python3 -m compileall tools` exit 0。

## 4. クロスレビュー運用（PR B のみ、task 共通）

- **Round 1**: `scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/00-glossary.md`。所見を `.agentops/reviews/p1-01.md` に Round 1 として転記、P0/P1/P2/P3 分類。run 記録は `.agentops/runs/<ISO8601>-p1-01/`。
- **Round 2**: P0/P1 反映後に再委譲、`.agentops/reviews/p1-01.md` に Round 2 として追記。
- **Round 3**（**必須・確認用**）: 修正がなくても確認専用で実行し、no further P0/P1 を確認して `.agentops/reviews/p1-01.md` に Round 3 として追記。**前回 task 07 セッションで Round 2 後にレビュー無し merge した違反を再発させない**。
- レビュー修正は最大 2 周。3 周目は確認のみ。3 周目で修正必要なら統合判断 or user 確認。

## 5. AI auto-merge 許諾条件（PR B、CLAUDE.md L51 §許諾条件 6 件）

1. **DbC 完了**: task 02 ファイルの完了条件節すべて満たす（許容語付き 0 件、双方向リンク、Codex 反映、PR マージ）。
2. **Codex cross-review 通過**: Round 3 で P0/P1 = 0、run 記録 `.agentops/runs/<ISO8601>-p1-01/` あり。
3. **CI green**: `.github/` 不在のため `python3 -m compileall tools` exit 0 で代替（task 08 完了前の暫定運用）。
4. **観察事実食い違いなし**: Appendix B / docs/12 用語表との整合確認。
5. **PR スコープ単一**: docs / config / rules / skills / workflows / catalog.md / CLAUDE.md / AGENTS.md / templates/ のみ。`.agentops/` には触れない（PR A/C で別途）。
6. **secret 未混入**: diff 目視確認。

PR A / C は `.agentops/` 限定 housekeeping のため、本許諾条件 §2 の対象（task DbC 直接 PR）外として Codex cross-review 省略可。

## 6. 共通停止条件

- task 02 ファイル §停止条件（公式 docs と用語食い違い、置換対象想定 3 倍超え、レビュー修正 2 周超え）に該当 → 即停止 user 確認。
- Codex Round 1 で P0 が出た場合 → 反映後 Round 2、それでも P0/P1 残るなら user 確認。
- archive task CLI が想定外エラー（dry-run で検出）→ task 07 review p1-06.md P2 残課題（`completed_tasks: []` 末尾改行なし極端ケース）に該当しないか確認、該当時は手動編集。
- secret / 本番 / 課金 / 外部公開 / 破壊的操作（git reset --hard、force push、main 直 push）が必要 → 停止。
- AI auto-merge 許諾条件 6 件のいずれかが NG → 停止 user 確認。
- レビュー修正 3 周目に入りそうな場合 → 統合判断 or user 確認。

## 7. 後処理（PR C 完了後、CLAUDE.md auto-merge 後の必須手順）

1. `git checkout main && git fetch origin && git pull --ff-only origin main && git status --short --branch` で main 同期確認。
2. `prompts/next-session.md` の本文を task 02 セッション内容で書き直し済みか再確認（PR C 内で実施）。
3. plan 全体完了でないため、`scripts/agentops archive plan` は **不実行**（task 03–06, 08, 09 が残）。

## 8. 関連ファイル

- 親 plan: `.agentops/plans/current.md`
- 着手 task: `.agentops/tasks/02-p1-01-glossary.md`
- 報告書 Appendix B: `docs/reviews/2026-04-28-cross-repo-design-review.md` L451–
- 用語表ソース: `docs/12-harness-engineering.md` L43–48
- 前 task 07 review（Round 3 運用例）: `.agentops/reviews/p1-06.md`
- archive CLI 仕様: `docs/11-monitoring-cli.md` §archive サブコマンド
- Plan agent 詳細: `~/.claude/plans/agentops-agentops-tasks-02-p1-01-glossar-linked-naur.md`（リポジトリ外）
- planning-phase 版（archive 済み）: `.agentops/archive/2026-04-28-design-review-p0-p1/task-plans/initial-planning-phase.md`
