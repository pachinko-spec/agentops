# Next session プロンプト（2026-04-28 設計レビュー実装フェーズ）

parent_plan: 2026-04-28-design-review-p0-p1
status: in progress (task 01 + 07 + 02 + 03 + 05 完了 / 残り 4 task)
created_at: 2026-04-28
updated_at: 2026-04-28
timezone: Asia/Tokyo
entry_point: .agentops/tasks/04-p1-04-last-reviewed.md
completed_tasks:
  - 01-p0-02-tool-stop-conditions (PR #30, archive 済)
  - 07-p1-06-archive-auto-update (PR #31 機能 + #32 ドッグフード archive + #33 round 3 記録 + #34 status 更新 + #35 本文書き直し)
  - 02-p1-01-glossary (PR #36 task-plan cleanup + #37 本体 + PR #38 archive ドッグフード)
  - 03-p1-02-deprecation-marker (PR #39 本体 + PR #40 archive ドッグフード)
  - 05-p1-05-dbc-consolidation

---

## 今回完了したこと（2026-04-28 task 05 P1-05 セッション）

ユーザー起動指示は task 04/05/06 から残 5 task の実装フェーズ継続。AskUserQuestion で **task 05 (DbC 集約)** を user が選択し、依存・順序制約ゼロかつ S(1h) の独立 task として着手。task 02 / 03 セッションで運用確立した Codex Round 1/2/3 + auto-merge 6 件確認フローを 2 PR 構成で実行:

実施内容:

- **PR #41** `P1-05: DbC 記述を docs/03 に集約 + 01/09/12 を参照のみに`
  - `docs/01-philosophy.md` §DbC: docs/03 への参照リンク追加
  - `docs/02-workflow.md` §標準サイクル 直前: 24 ステップ reference + docs/01 中核原則「単純で合成可能な workflow を優先」整合段落を追加
  - `docs/09-hooks-quality-gates.md` §DbC: 5 条件 prose 4 ブロック削除 → 関係文 + 1 段適用 prose に再構成（hooks 固有の前提・不変・完了・停止内容は保持しつつ、DbC 用語の見出し形式は廃止）
  - `docs/12-harness-engineering.md` §DbC 冒頭: 単一真ソース明示。DbC↔harness mapping table は docs/12 固有価値として保持
  - `.agentops/reviews/p1-05.md` 新規（Round 1/2/3 記録）
  - Codex cross-review:
    - **Round 1** (run_id `20260428T215000+0900-p1-05-r1`): P0=0 / **P1=0** / P2=1 advisory → **修正 0 周**
      - P2-1 advisory: 「差分外の docs/00, docs/10, docs/11 にも DbC prose があり、task md 検証 grep を厳密適用すると非ゼロ」→ task 05 スコープ外（触ってよい範囲は 01/02/03/09/12 限定）として PR 本文 + review 記録に明記する方針で対応
    - **Round 2** 確認用 (run_id `20260428T215800+0900-p1-05-r2`): P0/P1/P2/P3 = 0 — clean
    - **Round 3 確認専用** (run_id `20260428T220500+0900-p1-05-r3`): P0/P1/P2/P3 = 0 → **`no further P0/P1` 確認** ✅
  - AI auto-merge 許諾条件 6 件全 OK → `gh pr merge --squash --delete-branch`
  - **task 02 / 03 セッション運用との一貫性**: Round 1 で修正不要だったため修正 0 周、Round 2/3 はいずれも確認用 re-run。CLAUDE.md ループ防止ルール（最大 2 周）の範囲内
- **本 PR** post-merge ドッグフード: `scripts/agentops archive task --task-id 05-p1-05-dbc-consolidation` で task 05 を archive へ移し、`prompts/next-session.md` の本文を task 05 セッション内容で書き直し

## 未完了のこと

- 残 4 task の実装。次 task 選択は **user 確認** が必要:
  - **archive CLI 既定 entry_point**: `04-p1-04-last-reviewed`
  - **依存関係注意**: task 04 と task 06 はどちらを先に着手しても良いが、`06 → 04` 順だと task 04 で `docs/17` も同時に frontmatter 化できる（漏れ防止）。task 04 を先にする場合は task 06 のチェックリストに「frontmatter 追加」を含める必要（task 04 md L44 注記）
  - **依存順最短候補**: `04-p1-04-last-reviewed` / `06-p1-03-cross-reference` のどちらか（task 02 + 05 完了で残 task は依存解消、所要 1h–半日）→ `08-p1-07-ci-and-gitignore` (task 04 完了後) → `09-p1-08-agents-md-unify` (task 02 / 04 / 05 / 06 完了後)
- 4 task すべてマージ後、`scripts/agentops archive plan --plan-id 2026-04-28-design-review-p0-p1 --summary <text>` で plan 全体 archive + `archive/README.md` table への row 挿入

## 現在のブランチ

- 本 PR ブランチ: `claude/archive-task-p1-05-dogfood`
- 次セッション実装ブランチ: 各 task ごとに `claude/design-review-impl-<task-id>` を main から切り直す

## 変更ファイル（task 05 セッション全体）

```
PR #41: docs/01-philosophy.md (1 行 +/-), docs/02-workflow.md (+2), docs/09-hooks-quality-gates.md (-22 +6), docs/12-harness-engineering.md (1 行 +/-), .agentops/reviews/p1-05.md (新規, Round 1/2/3 記録)
本 PR: .agentops/{tasks/ → archive/.../tasks/}/05-p1-05-dbc-consolidation.md, .agentops/prompts/next-session.md (entry_point + completed_tasks 機械更新 + 本文手動書き直し)
```

## 実行したテスト

- `python3 -m compileall tools` 成功（Round 1 / Round 2 / Round 3 各時点で確認）
- `rg -c "^## (前提|不変|完了|禁止|停止)条件" docs/*.md` で docs/03 のみ 5 件、docs/00 §停止条件 (glossary entry) のみ 1 件、他 docs は 0 件
- `rg -n "前提条件:|不変条件:|完了条件:|停止条件:" docs/09-hooks-quality-gates.md` 0 件
- `rg -n "03-dbc-and-quality-gates" docs/{01,09,12}*.md` 各ファイル 1 件以上
- `rg -n "01-philosophy" docs/02-workflow.md` 1 件
- `python3 -m unittest discover -s tests` 12/12 pass (Codex Round 1/3 で実行)
- Codex cross-review 3 Round (Round 3 で `no further P0/P1` 確認)
- `scripts/agentops archive task --task-id 05-p1-05-dbc-consolidation --dry-run` → 衝突なし、preflight pass
- 本番実行で git mv + next-session.md 機械更新 (entry_point → 04 / completed_tasks += 05) 動作

## 次セッション投入プロンプト（task 04/06 着手用、user が貼って良い）

> agentops の `.agentops/tasks/` から残 4 task の実装フェーズを継続します。
>
> **次 task 選択（user 確認）**: 以下のいずれかを選んでください。
>
> - **task 04 (P1-04)** `.agentops/tasks/04-p1-04-last-reviewed.md` — `docs/01–16` 全件に `last-reviewed` frontmatter 追加。S（1h）。**archive CLI 既定 entry_point**。task 06 を後にする場合は task 06 チェックリストに frontmatter 追加を含める必要
> - **task 06 (P1-03)** `.agentops/tasks/06-p1-03-cross-reference.md` — rule ↔ skill ↔ workflow ↔ hook 逆参照テーブル。M（半日）。新規 `docs/17`。`06 → 04` 順だと task 04 で docs/17 も同時 frontmatter 化可能
>
> 起動手順:
>
> 1. `git status --short --branch` で main + clean 確認、`git fetch origin && git pull --ff-only origin main` で同期
> 2. `git checkout -b claude/design-review-impl-<task-id>` で実装ブランチを切る
> 3. 選択した task md の DbC（前提・不変・実行内容・完了条件・検証・禁止・後処理・停止条件）を読み実装
> 4. 検証: `python3 -m compileall tools` exit 0、task 固有の grep / 検証コマンドを task ファイル §検証 で実行
> 5. **Codex cross-review**: `scripts/agentops delegate --to codex --role review_frontier --effort high --input <該当ファイル>` で **Round 1**。所見を `.agentops/reviews/<task-id>.md` に転記、P0/P1 を反映。**修正したら Round 2 を回す**。**Round 3 は確認用レビューとして必ず実施し `no further P0/P1` を確認して終える**（task 02 / 03 / 05 セッションで運用確立）
> 6. PR 作成（タイトル `<task-id>: <短縮タイトル>`、本文に DbC + 検証コマンド + Codex 各 Round 結果）
> 7. AI auto-merge 許諾条件 6 件（CLAUDE.md §許諾条件）を独立評価。全件 OK なら `gh pr merge --squash --delete-branch`
> 8. main 同期: `git checkout main && git fetch origin && git pull --ff-only origin main && git status --short --branch`
> 9. **後処理**:
>    - `claude/archive-task-<task-id>-dogfood` ブランチを切り、`scripts/agentops archive task --task-id <basename> --dry-run` → 本番実行
>    - `git status` で `next-session.md` が unstaged であることを確認 → `git add .agentops/prompts/next-session.md`（CLI 既知問題、PR #32 で発覚、次 plan で hardening 候補）
>    - `next-session.md` 本文を **手動書き直し**（archive task CLI は本文を触らない設計）
>    - 別小 PR (`claude/archive-task-<task-id>-dogfood`) を作成 → self-merge → main 同期
>
> 制約:
>
> - 親 plan は `.agentops/plans/current.md`、task-plan は `.agentops/task-plans/current.md`、Plan agent 詳細は task ごとに `~/.claude/plans/<plan-name>.md` 新規作成（または task-plan で代替）
> - 1 task = 1 PR で完結。スコープ外リファクタ禁止
> - main 直 push 禁止、`claude/` プレフィックスブランチ必須
> - secret / 本番 / 課金 / 外部公開 / 破壊的操作が必要になったら停止して user 確認
> - **レビュー修正は最大 2 周。3 周目は確認専用。3 周目で修正必要なら統合判断 or user 確認**
> - **修正したら必ず再レビュー。最後はレビュー結果の確認で終える**（task 02 / 03 / 05 セッションで運用確立）
> - 並行 PR 化したい場合は user 確認の上で判断（task 05 完了で残 4 task は依存関係が緩いが、ブランチ衝突リスクあり）

## 関連ファイル

- 親 plan: `.agentops/plans/current.md`
- task-plan: `.agentops/task-plans/current.md`（task 02 セッション計画、task 04+ 着手前に書き直し or 流用判断）
- 残 task: `.agentops/tasks/{04-p1-04-last-reviewed,06-p1-03-cross-reference,08-p1-07-ci-and-gitignore,09-p1-08-agents-md-unify}.md`
- task 05 archive: `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/05-p1-05-dbc-consolidation.md`
- task 05 review (Round 1/2/3): `.agentops/reviews/p1-05.md`
- task 05 成果物: `docs/01-philosophy.md` §DbC リンク / `docs/02-workflow.md` §標準サイクル 24 step note / `docs/09-hooks-quality-gates.md` §DbC 関係文化 / `docs/12-harness-engineering.md` §DbC 冒頭強化
- 報告書: `docs/reviews/2026-04-28-cross-repo-design-review.md`
- archive CLI 仕様: `docs/11-monitoring-cli.md` §archive サブコマンド
- 規約: `CLAUDE.md` §許諾条件 / `AGENTS.md` §許諾条件 / `docs/04-model-routing.md` / `docs/05-review-policy.md`

## 未解決リスク（本 plan の他 task に影響しうるもの）

- **task 09 (P1-08)**: `@AGENTS.md` import が Claude Code / Codex 両方で確実に動作するか着手前に再確認必要（公式仕様変化が速い、AAIF 設立 2025-12-09 以降の仕様改訂に追従）
- **task 08 (P1-07)**: GitHub Actions が無料枠を超えないか着手時確認（public リポジトリなら問題なし）
- **task 04 / task 06 の順序依存**: task 04 を先にすると task 06 で新設される `docs/17` の frontmatter が漏れるため、task 06 のチェックリストに「frontmatter 追加」を含める運用が必要。`06 → 04` 順なら task 04 が docs/17 を含めてカバー（task 03 / 05 セッションで明文化）
- **task 05 で発覚した DbC prose 残存**: `docs/10-cli-wrapper.md` (4 件) と `docs/11-monitoring-cli.md` (8 件) にも `前提条件:` / `不変条件:` / `完了条件:` / `停止条件:` prose が残っている（CLI 仕様の DbC 適用節）。task 05 スコープ外として未着手。次 plan の handoff 候補として handoffs/ へ残すか、別 task として起票するか plan 全体完了時に判断
- **archive task CLI が next-session.md 本文を更新しない既知制約**: 責務分離のため意図的だが、結果として「本文の手動書き直し」が運用に必須。次 plan で運用ルール化 / CLI 拡張 / 別 session-log CLI 新設のいずれかを採用するか議論候補（task 07 から継続、task 02 / 03 / 05 でも踏襲）
- **archive task で git add 漏れ**: CLI は `git mv` で task md を staged にするが、`next-session.md` は通常 write のため unstaged のまま残る（PR #32 で発覚、task 02 / 03 / 05 で再現）。次 plan で CLI 側に `git add` を追加する hardening 候補
- **archive task CLI の P2 残課題**: `completed_tasks: []` がファイル末尾改行なしで終わる極端ケースで unsupported 扱い（task 07 Round 3 P2、実害は表示と実体の整合性が保たれているため軽微、次 plan で 1 行 regex hardening 候補）
- **task 03 で発覚した task md スコープ表現の曖昧さ**: 「`README.md` で archive を参照している箇所」が repo root README だけを指すか archive 配下 README も含むか task md 文面では曖昧で、Codex Round 1 P1 が補完した。次 plan で task md テンプレに「archive 配下 README 自体への注記要否」を明示する hardening 候補
- **glossary に追記すべき用語が新たに見つかった場合**: `docs/00-glossary.md` の `last_reviewed` frontmatter 更新で追記可能。次 plan の対象に入れる場合は handoffs/ へ
- **task 07 (P1-06) の発火タイミング選択**は本 task で完結（archive plan / archive task の手動 CLI 起動方式を採用、pre-commit / post-commit hook は不採用）
- **監視 CLI 側で stop_conditions spec を読んで警告する実装**は task 01 範囲外で次 plan の handoff 候補
- **skills / workflows 側の逆参照列追加**は task 06 範囲外で次 plan の handoff 候補
