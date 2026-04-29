# Next session プロンプト（2026-04-29 handoff フォローアップ plan）

parent_plan: 2026-04-29-handoff-followups
status: in progress (task 01 完了 / 残り 1 task)
created_at: 2026-04-29
updated_at: 2026-04-29
timezone: Asia/Tokyo
entry_point: .agentops/tasks/02-dbc-prose-cleanup-docs-10-11.md
completed_tasks:
  - 01-cross-reference-bidirectional (PR #54 本体 + 本 PR archive ドッグフード + 旧 handoff 1 archive)

---

## 今回完了したこと（2026-04-29 task 01 セッション）

前 plan `2026-04-28-design-review-p0-p1` (PR #30-53、9 task 全完了) の handoffs/ 配下 2 件のうち 1 件目を消化。user 判断 (A: 実装する) を受けて新 plan `2026-04-29-handoff-followups` を起票、2 task 構成で実行中。

実施内容:

- **PR #54** `01: cross-reference skill / workflow → rule 逆参照列追加`
  - `skills/catalog.md`: 4 セクション (design 10 / impl 4 / review 9 / docs/ops 8 = 31 skill) に「関連 rule（代表）」列追加
  - `workflows/catalog.md`: 単一 table (15 workflow) に「関連 rule（代表）」列追加
  - `docs/17-cross-reference.md` §スコープ §残課題: 「逆引きは catalog 側で扱う」「代表選定の非相互性」「複数候補の網羅と catalog frontmatter は引き続き handoff 候補」を整合化
  - `.agentops/plans/current.md` 新規（`2026-04-29-handoff-followups`）、`.agentops/tasks/01-..., 02-...` 新規、`.agentops/task-plans/current.md` 新規、`.agentops/reviews/01-cross-reference-bidirectional.md` 新規
  - Codex cross-review:
    - **Round 1** (run_id `20260429t1527080900-01-cross-reference-bidirectional-r1`): P0=0 / **P1=1** / P2=2 / P3=1 → 修正 1 周
      - **P1 採用**: docs/17 §22-23 §57 矛盾、§22 を新方針 (catalog 側で逆引き) に更新、§残課題 整合化
      - **P2 採用**: 代表選定の非相互性が未明記 → docs/17 / catalog 両方に注記追加
      - **P2 採用**: .agentops 記録が PR 現況とずれ → tasks/01 を「進行中」、Phase 1 を ✅ に更新
      - **P3 採用**: tasks/01 §31 と plans/current.md §64 の「複数なら `/` 区切り」削除
    - **Round 2** (run_id `20260429t1534060900-01-cross-reference-bidirectional-r2`): P0=0 / P1=0 (Round 1 P1 完全解消) / P2=0 / **P3=1** → 修正 1 周
      - **P3 採用**: tasks/01 §31 で Round 1 P3 採用の取りこぼし → 「最も近い rule のみ採用」に統一
    - **Round 3 確認専用** (run_id `20260429t1537450900-01-cross-reference-bidirectional-r3`): P0/P1/P2/P3 = 0 → **`no further P0/P1` 確認** ✅
  - AI auto-merge 許諾条件 6 件全 OK → `gh pr merge 54 --squash --delete-branch`
  - **CLAUDE.md ループ防止ルール**: Round 1 後 1 周 + Round 2 後 1 周 = 2 周修正、ループ防止上限 (2 周) 内で完結
- **本 PR** post-merge ドッグフード:
  - `scripts/agentops archive task --task-id 01-cross-reference-bidirectional` で task 01 を archive へ移動
  - 旧 handoff `2026-04-28-cross-reference-skill-workflow-side.md` を `archive/2026-04-28-design-review-p0-p1/handoffs/` へ移動 (本 task で実装完了したため、前 plan に紐づく handoff として archive 化)
  - 本 `next-session.md` を新規作成 (前 plan archive 時に削除済、新 plan 用)

## 未完了のこと

- 残 1 task の実装。**task 02 = `02-dbc-prose-cleanup-docs-10-11`** (S 1h 想定) で plan 完了
  - **archive CLI 既定 entry_point**: `02-dbc-prose-cleanup-docs-10-11`
  - **依存関係**: なし（前 plan task 05 で docs/03 canonical 化、docs/09 で再構成パターン確立済）
- task 02 マージ後、`scripts/agentops archive plan --plan-id 2026-04-29-handoff-followups --summary <text>` で plan 全体 archive

## 現在のブランチ

- 本 PR ブランチ: `claude/archive-task-01-cross-reference-bidirectional-dogfood`
- 次セッション実装ブランチ: `claude/handoff-followup-impl-02-dbc-prose-cleanup-docs-10-11` を main から切り直す

## 変更ファイル（task 01 セッション全体）

```
PR #54:
  skills/catalog.md (+45 行: 4 セクションに関連 rule 列追加 + 非相互性注記)
  workflows/catalog.md (+18 行: 関連 rule 列追加 + 非相互性注記)
  docs/17-cross-reference.md (Round 1 P1 反映: §スコープ整合化 + §残課題 更新)
  .agentops/plans/current.md (新規, 78 行)
  .agentops/tasks/01-cross-reference-bidirectional.md (新規, 83 行)
  .agentops/tasks/02-dbc-prose-cleanup-docs-10-11.md (新規, 79 行)
  .agentops/task-plans/current.md (新規, 106 行)
  .agentops/reviews/01-cross-reference-bidirectional.md (新規, 230+ 行: マッピング根拠 31+15 件 + Round 1/2/3)
本 PR:
  .agentops/{tasks/ → archive/2026-04-29-handoff-followups/tasks/}/01-...md (git mv)
  .agentops/{handoffs/ → archive/2026-04-28-design-review-p0-p1/handoffs/}/2026-04-28-cross-reference-skill-workflow-side.md (git mv)
  .agentops/prompts/next-session.md (新規)
```

## 実行したテスト

- `python3 -m compileall tools` exit 0
- `python3 -m unittest discover -s tests` 12/12 pass
- rule id 整合性: skill 31 + workflow 15 = 46 件、すべて rules/catalog.md の 12 rule id と整合 (Python 検証で invalid 0 件)
- markdown 標準 table 7 フィールド統一 (`|` 分割)
- **CI (PR #54)**: Actions runs 25094190520 (初回) / 25094418982 (R1 修正後) / 25094542381 (R2 修正後) / 25094660439 (R3 後) 全て 4 job 全 pass
- Codex cross-review 3 Round (Round 3 で `no further P0/P1` 確認)
- `scripts/agentops archive task --task-id 01-cross-reference-bidirectional --dry-run` → 衝突なし
- 本番実行で git mv 動作 (next-session.md は前 plan archive 時に削除済のため CLI が skip → 本 PR で新規作成)

## 次セッション投入プロンプト（task 02 着手用、user が貼って良い）

> agentops の `.agentops/tasks/` から残 1 task の実装フェーズを継続します。
>
> **次 task**: `02-dbc-prose-cleanup-docs-10-11` (archive CLI 既定 entry_point)
>
> - `.agentops/tasks/02-dbc-prose-cleanup-docs-10-11.md` — docs/10-cli-wrapper.md と docs/11-monitoring-cli.md の DbC prose 12 箇所を docs/03 参照化。S(1h) 想定。前 plan task 05 で確立した docs/09 再構成パターンを再適用。
> - 完了後は `scripts/agentops archive plan --plan-id 2026-04-29-handoff-followups --summary <text>` で plan 全体 archive
>
> 起動手順:
>
> 1. `git status --short --branch` で main + clean 確認、`git fetch origin && git pull --ff-only origin main` で同期
> 2. `git checkout -b claude/handoff-followup-impl-02-dbc-prose-cleanup-docs-10-11` で実装ブランチを切る
> 3. task 02 md の DbC（前提・不変・実行内容・完了条件・検証・禁止・後処理・停止条件）を読み実装
> 4. **重要 (前 plan task 05 で確立したパターン参照)**: docs/09-hooks-quality-gates.md §DbC を先行パターン例として読み、docs/10, 11 の DbC prose を「関係文 + docs/03 参照リンク + 1 段適用 prose」形式に再構成
> 5. 検証: `python3 -m compileall tools` exit 0、`rg -nE "^前提条件:|^不変条件:|^完了条件:|^停止条件:" docs/10-cli-wrapper.md docs/11-monitoring-cli.md` が 0 件、CI 4 job 全 pass
> 6. **Codex cross-review**: `scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/10-cli-wrapper.md --run-id <ts>+0900-02-dbc-prose-cleanup-docs-10-11-r1` で **Round 1**。所見を `.agentops/reviews/02-dbc-prose-cleanup-docs-10-11.md` に転記、P0/P1 を反映。Round 2 で clean 確認、Round 3 で `no further P0/P1` 確認
> 7. PR 作成（タイトル `02: docs/10, 11 の DbC prose を docs/03 参照化`、本文に DbC + 検証コマンド + Codex 各 Round 結果 + auto-merge 6 件評価）
> 8. AI auto-merge 許諾条件 6 件（CLAUDE.md / AGENTS.md §許諾条件）を独立評価。全件 OK なら `gh pr merge --squash --delete-branch`
> 9. main 同期: `git checkout main && git fetch origin && git pull --ff-only origin main && git status --short --branch`
> 10. **後処理**:
>    - `claude/archive-task-02-dbc-prose-cleanup-docs-10-11-dogfood` ブランチを切り、`scripts/agentops archive task --task-id 02-dbc-prose-cleanup-docs-10-11 --dry-run` → 本番実行
>    - 旧 handoff 2 (`2026-04-28-dbc-prose-remnants-docs-10-11.md`) を `archive/2026-04-28-design-review-p0-p1/handoffs/` へ git mv
>    - **plan 全体完了** → `scripts/agentops archive plan --plan-id 2026-04-29-handoff-followups --summary <text>` で plan archive、`prompts/next-session.md` を削除（CLAUDE.md グローバル方針）
>    - 別小 PR を作成 → self-merge → main 同期
>
> 制約:
>
> - 親 plan は `.agentops/plans/current.md`、task-plan は `.agentops/task-plans/current.md`
> - 1 task = 1 PR で完結。スコープ外リファクタ禁止
> - main 直 push 禁止、`claude/` プレフィックスブランチ必須
> - secret / 本番 / 課金 / 外部公開 / 破壊的操作が必要になったら停止して user 確認
> - **レビュー修正は最大 2 周。3 周目は確認専用**
> - **修正したら必ず再レビュー。最後はレビュー結果の確認で終える**

## 関連ファイル

- 親 plan: `.agentops/plans/current.md`
- task-plan: `.agentops/task-plans/current.md`（task 02 着手前に書き直し or 流用判断）
- 残 task: `.agentops/tasks/02-dbc-prose-cleanup-docs-10-11.md`
- task 01 archive: `.agentops/archive/2026-04-29-handoff-followups/tasks/01-cross-reference-bidirectional.md`
- task 01 review: `.agentops/reviews/01-cross-reference-bidirectional.md`
- task 01 成果物: `skills/catalog.md`, `workflows/catalog.md`（関連 rule 列追加）
- 旧 handoff 1 (archive 済): `.agentops/archive/2026-04-28-design-review-p0-p1/handoffs/2026-04-28-cross-reference-skill-workflow-side.md`
- 旧 handoff 2 (本 plan task 02 で消化予定): `.agentops/handoffs/2026-04-28-dbc-prose-remnants-docs-10-11.md`
- 規約: `CLAUDE.md` / `AGENTS.md` §AI auto-merge 許諾、`docs/03-dbc-and-quality-gates.md`、`docs/05-review-policy.md`

## 未解決リスク

- task 02 (docs/10, 11 DbC prose 整理): docs/09 で確立した再構成パターンの再適用、低リスク。CLI 仕様が prose 形式必須と判明した場合のみ user 確認
- 本 plan で発生した P3 レベル handoff (task 01 §残課題: 代表選定の相互一致、catalog 側 frontmatter 追加) は plan 全体 archive 時に判断。task 02 完了後の plan archive で次 plan 候補として残置する想定
- 前 plan の P2/P3 延期分（actionlint binary checksum、`.env.example` 例外、config/ 雛形の同戦略適用、AGENTS.override.md override 挙動、archive task CLI hardening、監視 CLI で stop_conditions 警告）は次 plan 候補として残置
