# Next session プロンプト（2026-04-28 設計レビュー実装フェーズ）

parent_plan: 2026-04-28-design-review-p0-p1
status: in progress (task 01 + 07 + 02 + 03 + 05 + 06 + 04 完了 / 残り 2 task)
created_at: 2026-04-28
updated_at: 2026-04-28
timezone: Asia/Tokyo
entry_point: .agentops/tasks/08-p1-07-ci-and-gitignore.md
completed_tasks:
  - 01-p0-02-tool-stop-conditions (PR #30, archive 済)
  - 07-p1-06-archive-auto-update (PR #31 機能 + #32 ドッグフード archive + #33 round 3 記録 + #34 status 更新 + #35 本文書き直し)
  - 02-p1-01-glossary (PR #36 task-plan cleanup + #37 本体 + PR #38 archive ドッグフード)
  - 03-p1-02-deprecation-marker (PR #39 本体 + PR #40 archive ドッグフード)
  - 05-p1-05-dbc-consolidation (PR #41 本体 + PR #42 archive ドッグフード + #43 docs/10/11 prose handoff)
  - 06-p1-03-cross-reference (PR #44 本体 + PR #45 archive ドッグフード)
  - 04-p1-04-last-reviewed (PR #47 本体 + 本 PR archive ドッグフード)

---

## 今回完了したこと（2026-04-28 task 04 P1-04 セッション）

ユーザー起動指示は task 04/06 残 4 task の依存順最短候補に沿って task 04 (last-reviewed frontmatter 追加) を実行。task 02 / 03 / 05 / 06 セッションで運用確立した Codex Round 1/2/3 + auto-merge 6 件確認フローを 2 PR 構成で実行:

実施内容:

- **PR #47** `P1-04: docs/00–17 全 18 件に last_reviewed frontmatter 追加`
  - `docs/01–17` (17 件): 既存 frontmatter なし → YAML 4 共通キー (`last_reviewed` / `next_review_by` / `reviewer` / `language`) 追加 (各 +7 行)
  - `docs/00-glossary.md`: 既存 2 キー (`last_reviewed` / `scope: glossary`) → 共通 4 キー + `scope: glossary` の 5 キー構成 (user 確認済み例外、+3 行)
  - `docs/06-freshness-and-monitoring.md`: `## last_reviewed フロントマター形式` セクション新設 (YAML 採用理由 / blockquote 不採用理由 / scope 例外 / ISO 8601 / GitHub user / BCP 47、+11 行)
  - `.agentops/reviews/p1-04.md` 新規（Round 1/2/3 記録 + 不変条件解釈ノート、167 行）
  - `.agentops/task-plans/current.md` 新規（task 04 セッション計画、76 行）
  - Codex cross-review:
    - **Round 1** (run_id `20260428t2253270900-p1-04-r1`): P0=0 / **P1=1** / P2=0 / P3=1 → 修正 1 周
      - **P1**: docs/00 5 キー例外と task 04 §不変条件 L24「同一キー名」の解釈整合性。auto-merge「DbC 完了」評価で説明が割れる懸念 → **採用**: review 記録 (`p1-04.md`) に「不変条件の解釈ノート」追加し、共通 4 キー同順 + docs/00 5 キー目例外を許容と明示。docs/00–17 本体差分は変更なし。
      - **P3**: task 04 §検証 L58 の `rg -L "^last_reviewed|^> last-reviewed"` は ripgrep 15.1.0 で `-L = --follow` であり「未一致ファイル列挙」は `--files-without-match` が正 → **task 08 申し送り**（後述未解決リスク）
    - **Round 2** (run_id `20260428t2257230900-p1-04-r2`): P0/P1/P2/P3 = 0 — Round 1 P1 完全解消、本体 clean
    - **Round 3 確認専用** (run_id `20260428t2259480900-p1-04-r3`): P0/P1/P2/P3 = 0 → **`no further P0/P1` 確認** ✅
  - AI auto-merge 許諾条件 6 件全 OK → `gh pr merge --squash --delete-branch`
  - **task 02 / 03 / 05 / 06 セッション運用との一貫性**: 修正 1 周（Round 1 後の review 記録のみ）、Round 2 で本体 clean、Round 3 で `no further P0/P1`。CLAUDE.md ループ防止ルール（最大 2 周）の範囲内
- **本 PR** post-merge ドッグフード: `scripts/agentops archive task --task-id 04-p1-04-last-reviewed` で task 04 を archive へ移し、`prompts/next-session.md` の本文を task 04 セッション内容で書き直し

## 未完了のこと

- 残 2 task の実装。**依存順**: `08-p1-07-ci-and-gitignore` (S–M 半日) → `09-p1-08-agents-md-unify` (M 半日)
  - **archive CLI 既定 entry_point**: `08-p1-07-ci-and-gitignore`
  - **依存関係**: task 08 は task 04 完了後着手可（既に完了）。task 09 は task 02 / 04 / 05 / 06 完了後（task 04 完了で全依存解消、08 後でも 09 単独でも可）
- 2 task すべてマージ後、`scripts/agentops archive plan --plan-id 2026-04-28-design-review-p0-p1 --summary <text>` で plan 全体 archive + `archive/README.md` table への row 挿入

## 現在のブランチ

- 本 PR ブランチ: `claude/archive-task-04-p1-04-last-reviewed-dogfood`
- 次セッション実装ブランチ: 各 task ごとに `claude/design-review-impl-<task-id>` を main から切り直す

## 変更ファイル（task 04 セッション全体）

```
PR #47:
  docs/00-glossary.md (+3 行: scope 維持で 5 キー化)
  docs/01-philosophy.md ..16-global-settings-application-checklist.md (各 +7 行: YAML frontmatter 追加)
  docs/06-freshness-and-monitoring.md (+11 行: frontmatter + ## last_reviewed フロントマター形式 セクション)
  docs/17-cross-reference.md (+7 行)
  .agentops/reviews/p1-04.md (新規, 167 行, Round 1/2/3 + 不変条件解釈ノート)
  .agentops/task-plans/current.md (新規, 76 行, task 04 セッション計画)
本 PR:
  .agentops/{tasks/ → archive/.../tasks/}/04-p1-04-last-reviewed.md (git mv)
  .agentops/prompts/next-session.md (entry_point + completed_tasks 機械更新 + 本文手動書き直し)
```

## 実行したテスト

- `python3 -m compileall tools` 成功（Round 1 / Round 2 / Round 3 各時点で確認）
- `rg --files-without-match "^last_reviewed|^> last-reviewed" docs/[0-9]*.md` 空（task 04 §検証 L58 の `rg -L` を正しい flag に補正）
- `rg "^last_reviewed: 2026-04-28" docs/[0-9]*.md` 18 件
- `rg "^scope: glossary" docs/[0-9]*.md` 1 件（docs/00 のみ）
- `rg "^## last_reviewed" docs/06-freshness-and-monitoring.md` 1 件
- `python3 -m unittest discover -s tests` 12/12 pass
- `git diff --check -- docs` clean
- Codex cross-review 3 Round (Round 3 で `no further P0/P1` 確認)
- `scripts/agentops archive task --task-id 04-p1-04-last-reviewed --dry-run` → 衝突なし、preflight pass
- 本番実行で git mv + next-session.md 機械更新 (entry_point → 08 / completed_tasks += 04) 動作

## 次セッション投入プロンプト（task 08 着手用、user が貼って良い）

> agentops の `.agentops/tasks/` から残 2 task の実装フェーズを継続します。
>
> **次 task**: `08-p1-07-ci-and-gitignore` (archive CLI 既定 entry_point)
>
> - `.agentops/tasks/08-p1-07-ci-and-gitignore.md` — 最小 CI（`actionlint` / `yamllint` / `markdown-link-check` を fail 系、`freshness-check` を warn のみ）+ `.gitignore` に secret 拡張子追加。S–M（半日）。task 04 で追加した YAML frontmatter (`last_reviewed` / `next_review_by`) を freshness-check job がパースする設計。
> - 完了後は `09-p1-08-agents-md-unify` (M 半日) で plan 完了
>
> 起動手順:
>
> 1. `git status --short --branch` で main + clean 確認、`git fetch origin && git pull --ff-only origin main` で同期
> 2. `git checkout -b claude/design-review-impl-p1-07` で実装ブランチを切る
> 3. task 08 md の DbC（前提・不変・実行内容・完了条件・検証・禁止・後処理・停止条件）を読み実装
> 4. **重要 (task 04 Round 1 P3 申し送り)**: freshness-check job の grep 表現は **YAML frontmatter 専用** (`^last_reviewed:` / `^next_review_by:`) に絞ること。`^last_reviewed|^> last-reviewed` の OR は旧 blockquote 形式を許容してしまう。また ripgrep 15.1.0 で `rg -L` は `--follow` のため「未一致ファイル列挙」は `rg --files-without-match` を使う。
> 5. 検証: `python3 -m compileall tools` exit 0、`actionlint .github/workflows/*.yml` exit 0、`yamllint -d relaxed .github/workflows/`、`markdown-link-check docs/*.md`、freshness-check job が docs/00–17 (18 件) の `last_reviewed` をパースし `next_review_by` 期限を warn 表示
> 6. **Codex cross-review**: `scripts/agentops delegate --to codex --role review_frontier --effort high --input .github/workflows/ci.yml` で **Round 1**。所見を `.agentops/reviews/p1-07.md` に転記、P0/P1 を反映。**修正したら Round 2 を回す**。**Round 3 は確認用レビューとして必ず実施し `no further P0/P1` を確認して終える**（task 02 / 03 / 04 / 05 / 06 セッションで運用確立）
> 7. PR 作成（タイトル `P1-07: 最小 CI + .gitignore secret 拡張子追加`、本文に DbC + 検証コマンド + Codex 各 Round 結果 + auto-merge 6 件評価）
> 8. AI auto-merge 許諾条件 6 件（CLAUDE.md §許諾条件）を独立評価。全件 OK なら `gh pr merge --squash --delete-branch`
> 9. main 同期: `git checkout main && git fetch origin && git pull --ff-only origin main && git status --short --branch`
> 10. **後処理**:
>    - `claude/archive-task-08-p1-07-ci-and-gitignore-dogfood` ブランチを切り、`scripts/agentops archive task --task-id 08-p1-07-ci-and-gitignore --dry-run` → 本番実行
>    - `git status` で `next-session.md` が unstaged であることを確認 → `git add .agentops/prompts/next-session.md`（CLI 既知問題、PR #32 で発覚、次 plan で hardening 候補）
>    - `next-session.md` 本文を **手動書き直し**（archive task CLI は本文を触らない設計）
>    - 別小 PR を作成 → self-merge → main 同期
>
> 制約:
>
> - 親 plan は `.agentops/plans/current.md`、task-plan は `.agentops/task-plans/current.md`、Plan agent 詳細は task ごとに `~/.claude/plans/<plan-name>.md` 新規作成（または task-plan で代替）
> - 1 task = 1 PR で完結。スコープ外リファクタ禁止
> - main 直 push 禁止、`claude/` プレフィックスブランチ必須
> - secret / 本番 / 課金 / 外部公開 / 破壊的操作が必要になったら停止して user 確認
> - **レビュー修正は最大 2 周。3 周目は確認専用。3 周目で修正必要なら統合判断 or user 確認**
> - **修正したら必ず再レビュー。最後はレビュー結果の確認で終える**（task 02 / 03 / 04 / 05 / 06 セッションで運用確立）

## 関連ファイル

- 親 plan: `.agentops/plans/current.md`
- task-plan: `.agentops/task-plans/current.md`（過去セッション計画、task 08 着手前に書き直し or 流用判断）
- 残 task: `.agentops/tasks/{08-p1-07-ci-and-gitignore,09-p1-08-agents-md-unify}.md`
- task 04 archive: `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/04-p1-04-last-reviewed.md`
- task 04 review (Round 1/2/3): `.agentops/reviews/p1-04.md`
- task 04 成果物: `docs/00-17` (18 件 frontmatter) / `docs/06 §## last_reviewed フロントマター形式`
- 報告書: `docs/reviews/2026-04-28-cross-repo-design-review.md`
- archive CLI 仕様: `docs/11-monitoring-cli.md` §archive サブコマンド
- 規約: `CLAUDE.md` §許諾条件 / `AGENTS.md` §許諾条件 / `docs/04-model-routing.md` / `docs/05-review-policy.md` / `docs/06-freshness-and-monitoring.md` §last_reviewed フロントマター形式

## 未解決リスク（本 plan の他 task に影響しうるもの）

- **task 04 Round 1 P3 申し送り (task 08 で必須対応)**: 検証コマンド `^last_reviewed|^> last-reviewed` の OR を CI freshness-check で単独採用すると旧 blockquote 形式 `> last-reviewed: ...` だけのファイルも通ってしまう。task 08 では **YAML frontmatter 専用 (`^last_reviewed:` / `^next_review_by:`)** に絞る。さらに ripgrep 15.1.0 で `rg -L` は `--follow` のため、「未一致ファイル列挙」目的では `rg --files-without-match` を使う（task 04 §検証 L58 表記の補正）
- **task 09 (P1-08)**: `@AGENTS.md` import が Claude Code / Codex 両方で確実に動作するか着手前に再確認必要（公式仕様変化が速い、AAIF 設立 2025-12-09 以降の仕様改訂に追従）
- **task 08 (P1-07)**: GitHub Actions が無料枠を超えないか着手時確認（public リポジトリなら問題なし）。task 04 完了で freshness-check job が docs/00–17 (18 件) の `last_reviewed` / `next_review_by` をパースする設計の前提が整った
- **task 05 で発覚した DbC prose 残存（docs/10, docs/11）**: handoff として独立記録済み → `.agentops/handoffs/2026-04-28-dbc-prose-remnants-docs-10-11.md`。本 plan 完了後の新 plan で task 化を判断
- **task 06 から派生: skill / workflow 側逆参照列追加**: handoff として独立記録 → `.agentops/handoffs/2026-04-28-cross-reference-skill-workflow-side.md`。skill → rule、workflow → rule の双方向参照を次 plan で検討
- **archive task CLI が next-session.md 本文を更新しない既知制約**: 責務分離のため意図的だが、結果として「本文の手動書き直し」が運用に必須。次 plan で運用ルール化 / CLI 拡張 / 別 session-log CLI 新設のいずれかを採用するか議論候補（task 02 / 03 / 04 / 05 / 06 で踏襲）
- **archive task で git add 漏れ**: CLI は `git mv` で task md を staged にするが、`next-session.md` は通常 write のため unstaged のまま残る（PR #32 で発覚、task 02 / 03 / 04 / 05 / 06 で再現）。次 plan で CLI 側に `git add` を追加する hardening 候補
- **archive task CLI の P2 残課題**: `completed_tasks: []` がファイル末尾改行なしで終わる極端ケースで unsupported 扱い（task 07 Round 3 P2、実害は表示と実体の整合性が保たれているため軽微、次 plan で 1 行 regex hardening 候補）
- **task 03 で発覚した task md スコープ表現の曖昧さ**: 「`README.md` で archive を参照している箇所」が repo root README だけを指すか archive 配下 README も含むか task md 文面では曖昧で、Codex Round 1 P1 が補完した。次 plan で task md テンプレに「archive 配下 README 自体への注記要否」を明示する hardening 候補
- **glossary に追記すべき用語が新たに見つかった場合**: `docs/00-glossary.md` の `last_reviewed` frontmatter 更新で追記可能。次 plan の対象に入れる場合は handoffs/ へ
- **task 07 (P1-06) の発火タイミング選択**は task 07 で完結（archive plan / archive task の手動 CLI 起動方式を採用、pre-commit / post-commit hook は不採用）
- **監視 CLI 側で stop_conditions spec を読んで警告する実装**は task 01 範囲外で次 plan の handoff 候補
