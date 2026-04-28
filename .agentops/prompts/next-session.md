# Next session プロンプト（2026-04-28 設計レビュー実装フェーズ）

parent_plan: 2026-04-28-design-review-p0-p1
status: in progress (task 01 + 07 + 02 完了 / 残り 6 task)
created_at: 2026-04-28
updated_at: 2026-04-28
timezone: Asia/Tokyo
entry_point: .agentops/tasks/03-p1-02-deprecation-marker.md
completed_tasks:
  - 01-p0-02-tool-stop-conditions (PR #30, archive 済)
  - 07-p1-06-archive-auto-update (PR #31 機能 + #32 ドッグフード archive + #33 round 3 記録 + #34 status 更新 + #35 本文書き直し)
  - 02-p1-01-glossary (PR #36 task-plan cleanup + #37 本体 + 本 PR archive ドッグフード)

---

## 今回完了したこと（2026-04-28 task 02 P1-01 セッション）

ユーザー起動指示は task 02 (P1-01 用語統一表) 着手。session 開始時に `task-plans/current.md` が **planning-phase snapshot のまま残置** されていた（CLAUDE.md `.agentops/ 運用フロー` 第 2 項が task 01/07 着手時にスキップされていた運用 bug、user が「許さない」と指摘）ため、3 PR 構成で対応:

実施内容:

- **PR #36** `chore(.agentops): archive planning-phase task-plan, refresh current.md for task 02 session`
  - planning-phase 版 `task-plans/current.md` を `archive/2026-04-28-design-review-p0-p1/task-plans/initial-planning-phase.md` へ退避
  - task 02 実装セッション用に `task-plans/current.md` を新規作成（PR A/B/C 3 本構成 / Codex Round 1/2/3 運用 / auto-merge 許諾 6 件）
  - self-merge（`.agentops/` 限定 housekeeping のため Codex 省略）
- **PR #37** `P1-01: 用語統一表 docs/00-glossary.md 追加 + 旧用語 0 件化`
  - 新規 `docs/00-glossary.md`（frontmatter + 19 用語 + 許容語リスト + 検証コマンド）。各エントリに公式出典 URL または内部参照（`docs/0X.md`）を 1 つ添付
  - `docs/01-philosophy.md` 冒頭に glossary 参照を追加、glossary 末尾「関連」節から逆リンクで双方向化
  - Codex cross-review:
    - **Round 1** (run_id `20260428T203719+0900-p1-01-r1`): P0=0 / **P1=2** / P2=1 → 全件反映
      - P1-1 AAIF 寄贈関係の誤り → Linux Foundation announcement に整合
      - P1-2 cross-model-delegate run_id 形式 → `<JST タイムスタンプ>-<to>-<role>` に修正
      - P2-1 orchestrator 固定 model id 鮮度リスク → `frontier reasoning model` に置換
    - **Round 2** (run_id `20260428T204132+0900-p1-01-r2`): P0=0 / **P1=3** / P2=1 → 全件反映
      - P1-1 MCP transport → 2025-06-18 spec (stdio + Streamable HTTP, 旧 HTTP+SSE deprecated) に修正
      - P1-2 Auto memory の 4 分類が公式 docs 未確認 → 公式 docs 整合表現 + 「本リポジトリの 4 分類は運用ルール」と明記
      - P1-3 review 記録の reviewer model id 未確認断定 → `adapter default / --model 未指定` に修正
      - P2-1 検証コマンドが orchestrator のみ → 「orchestrator 系の検証」と明記、cross-review / harness 系の確認 command 追加
    - **Round 3** (run_id `20260428T204619+0900-p1-01-r3`、**確認専用**): P0=0 / **P1=0** / P2=1（Round 3 セクション未記載のメタ指摘で本記録によって自己解消）
      - **`no further P0/P1` 確認** ✅
  - AI auto-merge 許諾条件 6 件全 OK → `gh pr merge --squash --delete-branch`
  - **改善点（前回 task 07 比）**: Round 3 を「確認専用レビュー」として正規ルーチン化し、最後はレビュー結果の確認で締めた（task 07 では Round 2 後にレビュー無し merge した違反を post-hoc Round 3 で穴埋めした反省を反映）
- **本 PR** post-merge ドッグフード: `scripts/agentops archive task --task-id 02-p1-01-glossary` で task 02 を archive へ移し、`prompts/next-session.md` の本文を task 02 セッション内容で書き直し

## 未完了のこと

- 残 6 task の実装。次 task 選択は **user 確認** が必要:
  - **依存順最短ルート**: `04-p1-04-last-reviewed` / `05-p1-05-dbc-consolidation` / `06-p1-03-cross-reference` のいずれか（task 02 完了で全件依存解消、所要 1h–半日）→ `08-p1-07-ci-and-gitignore` (task 04 完了後) → `09-p1-08-agents-md-unify` (task 02 / 04 / 05 / 06 完了後)
  - **並行 PR 候補**: `03-p1-02-deprecation-marker` は依存無し（archive CLI 機械更新の entry_point 既定値もこちら、所要 30m）
- 6 task すべてマージ後、`scripts/agentops archive plan --plan-id 2026-04-28-design-review-p0-p1 --summary <text>` で plan 全体 archive + `archive/README.md` table への row 挿入

## 現在のブランチ

- 本 PR ブランチ: `claude/archive-task-02-dogfood`
- 次セッション実装ブランチ: 各 task ごとに `claude/design-review-impl-<task-id>` を main から切り直す

## 変更ファイル（task 02 セッション全体）

```
PR #36: .agentops/task-plans/current.md (新内容), .agentops/archive/2026-04-28-design-review-p0-p1/task-plans/initial-planning-phase.md (退避)
PR #37: docs/00-glossary.md (新規), docs/01-philosophy.md (glossary リンク追加), .agentops/reviews/p1-01.md (Round 1/2/3 記録)
本 PR: .agentops/{tasks/ → archive/.../tasks/}/02-p1-01-glossary.md, .agentops/prompts/next-session.md (entry_point + completed_tasks 機械更新 + 本文手動書き直し)
```

## 実行したテスト

- `python3 -m compileall tools` 成功（Round 1 / Round 2 / Round 3 各時点で確認）
- `rg -n "orchestrator" docs/ config/ rules/ skills/ workflows/ CLAUDE.md AGENTS.md | rg -v "<許容語 + docs/reviews/>"` 0 件
- `rg -n "cross-review|cross-model-delegate" ...` 行為 / CLI ラッパで一貫使用
- `rg -n "\bharness\b|harness spec|harness engineering" docs/12 docs/03` 用語表 L43–48 と整合
- Codex cross-review 3 Round (Round 3 で `no further P0/P1` 確認)
- `scripts/agentops archive task --task-id 02-p1-01-glossary --dry-run` → 衝突なし、preflight pass
- 本番実行で git mv + next-session.md 機械更新 (entry_point / completed_tasks) 動作

## 次セッション投入プロンプト（task 03 or 04/05/06 着手用、user が貼って良い）

> agentops の `.agentops/tasks/` から残 6 task の実装フェーズを継続します。
>
> **次 task 選択（user 確認）**: 以下のいずれかを選んでください。
>
> - **task 03 (P1-02)** `.agentops/tasks/03-p1-02-deprecation-marker.md` — `archive/reference-kit-v1/{rules,skills,workflows}/README.md` 先頭に DEPRECATED 注記。S（30m）。依存なし、archive CLI 既定 entry_point。
> - **task 04 (P1-04)** `.agentops/tasks/04-p1-04-last-reviewed.md` — `docs/01–16` 全件に `last-reviewed` フロントマター追加。S（1h）。task 02 依存解消済。
> - **task 05 (P1-05)** `.agentops/tasks/05-p1-05-dbc-consolidation.md` — DbC 記述を `docs/03` に集約。S（1h）。task 02 依存解消済。
> - **task 06 (P1-03)** `.agentops/tasks/06-p1-03-cross-reference.md` — rule ↔ skill ↔ workflow ↔ hook 逆参照テーブル。M（半日）。task 02 依存解消済。
>
> 起動手順:
>
> 1. `git status --short --branch` で main + clean 確認、`git fetch origin && git pull --ff-only origin main` で同期
> 2. `git checkout -b claude/design-review-impl-<task-id>` で実装ブランチを切る
> 3. 選択した task md の DbC（前提・不変・実行内容・完了条件・検証・禁止・後処理・停止条件）を読み実装
> 4. 検証: `python3 -m compileall tools` exit 0、task 固有の grep / 検証コマンドを task ファイル §検証 で実行
> 5. **Codex cross-review**: `scripts/agentops delegate --to codex --role review_frontier --effort high --input <該当ファイル>` で **Round 1**。所見を `.agentops/reviews/<task-id>.md` に転記、P0/P1 を反映。**修正したら Round 2 を回す**。**Round 3 は確認用レビューとして必ず実施し `no further P0/P1` を確認して終える**（task 02 セッションで運用確立）
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
> - 親 plan は `.agentops/plans/current.md`、task-plan は `.agentops/task-plans/current.md`、Plan agent 詳細は `~/.claude/plans/agentops-agentops-tasks-02-p1-01-glossar-linked-naur.md`（task 02 用、task 03+ は新規作成 or task-plan で代替）
> - 1 task = 1 PR で完結。スコープ外リファクタ禁止
> - main 直 push 禁止、`claude/` プレフィックスブランチ必須
> - secret / 本番 / 課金 / 外部公開 / 破壊的操作が必要になったら停止して user 確認
> - **レビュー修正は最大 2 周。3 周目は確認専用。3 周目で修正必要なら統合判断 or user 確認**
> - **修正したら必ず再レビュー。最後はレビュー結果の確認で終える**（task 02 セッションで運用確立、task 07 違反を反省）
> - 並行 PR 化したい場合は task 03 + (04/05/06 のいずれか) が候補。user 確認の上で判断

## 関連ファイル

- 親 plan: `.agentops/plans/current.md`
- task-plan: `.agentops/task-plans/current.md`（task 02 セッション計画、task 03+ 着手前に書き直し or 流用判断）
- 残 task: `.agentops/tasks/{03-p1-02-deprecation-marker,04-p1-04-last-reviewed,05-p1-05-dbc-consolidation,06-p1-03-cross-reference,08-p1-07-ci-and-gitignore,09-p1-08-agents-md-unify}.md`
- task 02 archive: `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/02-p1-01-glossary.md`
- task 02 review (Round 1/2/3): `.agentops/reviews/p1-01.md`
- 用語集 (task 02 成果物): `docs/00-glossary.md`
- 報告書: `docs/reviews/2026-04-28-cross-repo-design-review.md`
- archive CLI 仕様: `docs/11-monitoring-cli.md` §archive サブコマンド
- 規約: `CLAUDE.md` §許諾条件 / `AGENTS.md` §許諾条件 / `docs/04-model-routing.md` / `docs/05-review-policy.md`

## 未解決リスク（本 plan の他 task に影響しうるもの）

- **task 09 (P1-08)**: `@AGENTS.md` import が Claude Code / Codex 両方で確実に動作するか着手前に再確認必要（公式仕様変化が速い、AAIF 設立 2025-12-09 以降の仕様改訂に追従）
- **task 08 (P1-07)**: GitHub Actions が無料枠を超えないか着手時確認（public リポジトリなら問題なし）
- **archive task CLI が next-session.md 本文を更新しない既知制約**: 責務分離のため意図的だが、結果として「本文の手動書き直し」が運用に必須。次 plan で運用ルール化 / CLI 拡張 / 別 session-log CLI 新設のいずれかを採用するか議論候補（task 07 から継続）
- **archive task で git add 漏れ**: CLI は `git mv` で task md を staged にするが、`next-session.md` は通常 write のため unstaged のまま残る（PR #32 で発覚）。次 plan で CLI 側に `git add` を追加する hardening 候補（task 07 から継続）
- **archive task CLI の P2 残課題**: `completed_tasks: []` がファイル末尾改行なしで終わる極端ケースで unsupported 扱い（task 07 Round 3 P2、実害は表示と実体の整合性が保たれているため軽微、次 plan で 1 行 regex hardening 候補）
- **glossary に追記すべき用語が新たに見つかった場合**: `docs/00-glossary.md` の `last_reviewed` フロントマター更新で追記可能。次 plan の対象に入れる場合は handoffs/ へ
- **task 07 (P1-06) の発火タイミング選択**は本 task で完結（archive plan / archive task の手動 CLI 起動方式を採用、pre-commit / post-commit hook は不採用）
- **監視 CLI 側で stop_conditions spec を読んで警告する実装**は task 01 範囲外で次 plan の handoff 候補
- **skills / workflows 側の逆参照列追加**は task 06 範囲外で次 plan の handoff 候補
