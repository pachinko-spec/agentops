# Next session プロンプト（2026-04-28 設計レビュー実装フェーズ）

parent_plan: 2026-04-28-design-review-p0-p1
status: in progress (task 01 + 07 + 02 + 03 + 05 + 06 完了 / 残り 3 task)
created_at: 2026-04-28
updated_at: 2026-04-28
timezone: Asia/Tokyo
entry_point: .agentops/tasks/04-p1-04-last-reviewed.md
completed_tasks:
  - 01-p0-02-tool-stop-conditions (PR #30, archive 済)
  - 07-p1-06-archive-auto-update (PR #31 機能 + #32 ドッグフード archive + #33 round 3 記録 + #34 status 更新 + #35 本文書き直し)
  - 02-p1-01-glossary (PR #36 task-plan cleanup + #37 本体 + PR #38 archive ドッグフード)
  - 03-p1-02-deprecation-marker (PR #39 本体 + PR #40 archive ドッグフード)
  - 05-p1-05-dbc-consolidation (PR #41 本体 + PR #42 archive ドッグフード + #43 docs/10/11 prose handoff)
  - 06-p1-03-cross-reference

---

## 今回完了したこと（2026-04-28 task 06 P1-03 セッション）

ユーザー起動指示は task 04/06 から残 4 task の実装フェーズ継続。AskUserQuestion で **task 06 (cross-reference) を先** を user が選択（task 04 DbC L44 が想定する `06 → 04` 順、漏れ防止）。task 02 / 03 / 05 セッションで運用確立した Codex Round 1/2/3 + auto-merge 6 件確認フローを 2 PR 構成で実行:

実施内容:

- **PR #44** `06-p1-03: rule ↔ skill ↔ workflow ↔ hook 逆参照テーブル`
  - `docs/17-cross-reference.md` 新規作成: rule 12 件 × {代表 skill / 代表 workflow / 代表 hook} の最小マッピング表 + 補完経路セクション
  - `rules/catalog.md`: 既存 12 行を維持、`関連 skill / 関連 workflow / 関連 hook` 列を末尾に追加、docs/17 への戻りリンク追加
  - `.agentops/reviews/p1-03.md` 新規（Round 1/2/3 記録）
  - Codex cross-review:
    - **Round 1** (run_id `20260428T222000+0900-p1-03-r1`): P0=0 / P1=0 / **P2=2** / P3=0 → 修正 1 周
      - P2-1: `destructive-operation-policy` の hook 列が `scripts/hooks/pre-push` (check-tests-before-push) になっていたが pre-push test gate は **品質 gate であり destructive 確認 gate ではない**。`—` に変更し、補完経路セクションで明示
      - P2-2: `agentops-task-policy` の hook 列が `scripts/agentops archive task` になっていたが post-merge **手動 CLI であり hook ではない**。`—` に変更し、補完経路セクションで明示。docs/17 hook 列定義を「commit / push 時点で機械的に拒否する gate」に絞り込み
    - **Round 2** (run_id `20260428T222600+0900-p1-03-r2`): P0/P1/P2/P3 = 0 — Round 1 P2 解消、本体 clean
    - **Round 3 確認専用** (run_id `20260428T223200+0900-p1-03-r3`): P0/P1=0、P2=1（レビュー記録の追記漏れのみ、本コミットで反映） → **`no further P0/P1` 確認** ✅
  - AI auto-merge 許諾条件 6 件全 OK → `gh pr merge --squash --delete-branch`
  - **task 02 / 03 / 05 セッション運用との一貫性**: 修正 1 周（Round 1 後）、Round 2 で clean、Round 3 で `no further P0/P1`。CLAUDE.md ループ防止ルール（最大 2 周）の範囲内
- **本 PR** post-merge ドッグフード: `scripts/agentops archive task --task-id 06-p1-03-cross-reference` で task 06 を archive へ移し、`prompts/next-session.md` の本文を task 06 セッション内容で書き直し、`handoffs/2026-04-28-cross-reference-skill-workflow-side.md` を新規追加（skill / workflow 側逆参照列追加を次 plan 申し送り）

## 未完了のこと

- 残 3 task の実装。次 task 選択は **user 確認** が必要:
  - **archive CLI 既定 entry_point**: `04-p1-04-last-reviewed`
  - **依存関係**: task 04 は task 02 完了後着手可（既に完了）。task 06 完了で `docs/17-cross-reference.md` 新規も対象に含まれた状態（task 04 §実行内容 L44 想定通り）→ `04 → 08` の順序になる。task 09 は task 02 / 04 / 05 / 06 完了後（task 04 完了で全依存解消）
  - **依存順最短候補**: `04-p1-04-last-reviewed` (S 1h) → `08-p1-07-ci-and-gitignore` (task 04 完了後、S–M 半日) → `09-p1-08-agents-md-unify` (M 半日)
- 3 task すべてマージ後、`scripts/agentops archive plan --plan-id 2026-04-28-design-review-p0-p1 --summary <text>` で plan 全体 archive + `archive/README.md` table への row 挿入

## 現在のブランチ

- 本 PR ブランチ: `claude/archive-task-06-p1-03-cross-reference-dogfood`
- 次セッション実装ブランチ: 各 task ごとに `claude/design-review-impl-<task-id>` を main から切り直す

## 変更ファイル（task 06 セッション全体）

```
PR #44: docs/17-cross-reference.md (新規, 61 行), rules/catalog.md (16 +/-, 14 -), .agentops/reviews/p1-03.md (新規, Round 1/2/3 記録)
本 PR: .agentops/{tasks/ → archive/.../tasks/}/06-p1-03-cross-reference.md, .agentops/prompts/next-session.md (entry_point + completed_tasks 機械更新 + 本文手動書き直し), .agentops/handoffs/2026-04-28-cross-reference-skill-workflow-side.md (新規)
```

## 実行したテスト

- `python3 -m compileall tools` 成功（Round 1 / Round 2 / Round 3 各時点で確認）
- `rg -n "^\| " rules/catalog.md` 14 行（header 1 + sep 1 + rule 12）
- `rg -n "^\| [a-z]" docs/17-cross-reference.md` 13 行（header 1 + rule 12 = 全 rule カバー）
- `rg -n "docs/17" rules/catalog.md` 1 件（戻りリンク）
- `python3 -m unittest discover -s tests` 12/12 pass
- Codex cross-review 3 Round (Round 3 で `no further P0/P1` 確認)
- `scripts/agentops archive task --task-id 06-p1-03-cross-reference --dry-run` → 衝突なし、preflight pass
- 本番実行で git mv + next-session.md 機械更新 (entry_point → 04 / completed_tasks += 06) 動作

## 次セッション投入プロンプト（task 04 着手用、user が貼って良い）

> agentops の `.agentops/tasks/` から残 3 task の実装フェーズを継続します。
>
> **次 task**: `04-p1-04-last-reviewed` (archive CLI 既定 entry_point)
>
> - `.agentops/tasks/04-p1-04-last-reviewed.md` — `docs/00, 01–16, 17` の **18 件** 全件に YAML frontmatter (`last_reviewed` / `next_review_by` / `reviewer` / `language`) 追加。S（1h）。形式選択根拠を `docs/06-freshness-and-monitoring.md` に記録。docs/00 のみ既存 YAML frontmatter（`scope: glossary`）があるため、task 04 形式に揃える（差分整理）
> - 完了後は `08-p1-07-ci-and-gitignore` (task 04 完了後、S–M 半日)、`09-p1-08-agents-md-unify` (M 半日) の順
>
> 起動手順:
>
> 1. `git status --short --branch` で main + clean 確認、`git fetch origin && git pull --ff-only origin main` で同期
> 2. `git checkout -b claude/design-review-impl-p1-04` で実装ブランチを切る
> 3. task 04 md の DbC（前提・不変・実行内容・完了条件・検証・禁止・後処理・停止条件）を読み実装
> 4. 検証: `python3 -m compileall tools` exit 0、`rg -L "^last_reviewed|^> last-reviewed" docs/[0-9]*.md` が空、`rg "^last_reviewed: 2026-04-28" docs/[0-9]*.md` の件数が 18 件（task 04 + 06 完了後の状態）
> 5. **Codex cross-review**: `scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/06-freshness-and-monitoring.md` で **Round 1**（task 04 検証指定）。所見を `.agentops/reviews/p1-04.md` に転記、P0/P1 を反映。**修正したら Round 2 を回す**。**Round 3 は確認用レビューとして必ず実施し `no further P0/P1` を確認して終える**（task 02 / 03 / 05 / 06 セッションで運用確立）
> 6. PR 作成（タイトル `04-p1-04: docs/01–16 + 00 + 17 に last-reviewed frontmatter 追加`、本文に DbC + 検証コマンド + Codex 各 Round 結果）
> 7. AI auto-merge 許諾条件 6 件（CLAUDE.md §許諾条件）を独立評価。全件 OK なら `gh pr merge --squash --delete-branch`
> 8. main 同期: `git checkout main && git fetch origin && git pull --ff-only origin main && git status --short --branch`
> 9. **後処理**:
>    - `claude/archive-task-04-p1-04-last-reviewed-dogfood` ブランチを切り、`scripts/agentops archive task --task-id 04-p1-04-last-reviewed --dry-run` → 本番実行
>    - `git status` で `next-session.md` が unstaged であることを確認 → `git add .agentops/prompts/next-session.md`（CLI 既知問題、PR #32 で発覚、次 plan で hardening 候補）
>    - `next-session.md` 本文を **手動書き直し**（archive task CLI は本文を触らない設計）
>    - 別小 PR (`claude/archive-task-04-p1-04-last-reviewed-dogfood`) を作成 → self-merge → main 同期
>
> 制約:
>
> - 親 plan は `.agentops/plans/current.md`、task-plan は `.agentops/task-plans/current.md`、Plan agent 詳細は task ごとに `~/.claude/plans/<plan-name>.md` 新規作成（または task-plan で代替）
> - 1 task = 1 PR で完結。スコープ外リファクタ禁止
> - main 直 push 禁止、`claude/` プレフィックスブランチ必須
> - secret / 本番 / 課金 / 外部公開 / 破壊的操作が必要になったら停止して user 確認
> - **レビュー修正は最大 2 周。3 周目は確認専用。3 周目で修正必要なら統合判断 or user 確認**
> - **修正したら必ず再レビュー。最後はレビュー結果の確認で終える**（task 02 / 03 / 05 / 06 セッションで運用確立）

## 関連ファイル

- 親 plan: `.agentops/plans/current.md`
- task-plan: `.agentops/task-plans/current.md`（過去セッション計画、task 04 着手前に書き直し or 流用判断）
- 残 task: `.agentops/tasks/{04-p1-04-last-reviewed,08-p1-07-ci-and-gitignore,09-p1-08-agents-md-unify}.md`
- task 06 archive: `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/06-p1-03-cross-reference.md`
- task 06 review (Round 1/2/3): `.agentops/reviews/p1-03.md`
- task 06 成果物: `docs/17-cross-reference.md` (新規) / `rules/catalog.md` 3 列追加
- task 06 から派生 handoff: `.agentops/handoffs/2026-04-28-cross-reference-skill-workflow-side.md`（skill / workflow 側逆参照列追加、次 plan 候補）
- 報告書: `docs/reviews/2026-04-28-cross-repo-design-review.md`
- archive CLI 仕様: `docs/11-monitoring-cli.md` §archive サブコマンド
- 規約: `CLAUDE.md` §許諾条件 / `AGENTS.md` §許諾条件 / `docs/04-model-routing.md` / `docs/05-review-policy.md`

## 未解決リスク（本 plan の他 task に影響しうるもの）

- **task 09 (P1-08)**: `@AGENTS.md` import が Claude Code / Codex 両方で確実に動作するか着手前に再確認必要（公式仕様変化が速い、AAIF 設立 2025-12-09 以降の仕様改訂に追従）
- **task 08 (P1-07)**: GitHub Actions が無料枠を超えないか着手時確認（public リポジトリなら問題なし）。task 04 完了後に着手（freshness-check job が task 04 frontmatter をパースする設計）
- **task 04 frontmatter 形式選択**: `docs/00-glossary.md` は task 02 で `last_reviewed: 2026-04-28 / scope: glossary` の最小 YAML 形式で作成済。task 04 推奨は `last_reviewed / next_review_by / reviewer / language` の 4 キー。docs/00 を task 04 形式に揃えるか、scope キーを保持するかは task 04 着手時に判断（task 04 §不変条件 L24「すべての docs で同一形式・同一順序・同一キー名」）
- **task 05 で発覚した DbC prose 残存（docs/10, docs/11）**: handoff として独立記録済み → `.agentops/handoffs/2026-04-28-dbc-prose-remnants-docs-10-11.md`。本 plan 完了後の新 plan で task 化を判断
- **task 06 から派生: skill / workflow 側逆参照列追加**: handoff として独立記録 → `.agentops/handoffs/2026-04-28-cross-reference-skill-workflow-side.md`。skill → rule、workflow → rule の双方向参照を次 plan で検討
- **archive task CLI が next-session.md 本文を更新しない既知制約**: 責務分離のため意図的だが、結果として「本文の手動書き直し」が運用に必須。次 plan で運用ルール化 / CLI 拡張 / 別 session-log CLI 新設のいずれかを採用するか議論候補（task 02 / 03 / 05 / 06 で踏襲）
- **archive task で git add 漏れ**: CLI は `git mv` で task md を staged にするが、`next-session.md` は通常 write のため unstaged のまま残る（PR #32 で発覚、task 02 / 03 / 05 / 06 で再現）。次 plan で CLI 側に `git add` を追加する hardening 候補
- **archive task CLI の P2 残課題**: `completed_tasks: []` がファイル末尾改行なしで終わる極端ケースで unsupported 扱い（task 07 Round 3 P2、実害は表示と実体の整合性が保たれているため軽微、次 plan で 1 行 regex hardening 候補）
- **task 03 で発覚した task md スコープ表現の曖昧さ**: 「`README.md` で archive を参照している箇所」が repo root README だけを指すか archive 配下 README も含むか task md 文面では曖昧で、Codex Round 1 P1 が補完した。次 plan で task md テンプレに「archive 配下 README 自体への注記要否」を明示する hardening 候補
- **glossary に追記すべき用語が新たに見つかった場合**: `docs/00-glossary.md` の `last_reviewed` frontmatter 更新で追記可能。次 plan の対象に入れる場合は handoffs/ へ
- **task 07 (P1-06) の発火タイミング選択**は task 07 で完結（archive plan / archive task の手動 CLI 起動方式を採用、pre-commit / post-commit hook は不採用）
- **監視 CLI 側で stop_conditions spec を読んで警告する実装**は task 01 範囲外で次 plan の handoff 候補
