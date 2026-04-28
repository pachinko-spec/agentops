# Next session プロンプト（2026-04-28 設計レビュー実装フェーズ）

parent_plan: 2026-04-28-design-review-p0-p1
status: pending implementation
created_at: 2026-04-28
timezone: Asia/Tokyo
entry_point: .agentops/tasks/01-p0-02-tool-stop-conditions.md

---

## 今回完了したこと（2026-04-28 計画立案セッション）

- PR #27（横断設計レビュー報告書）マージ済みを確認
- 報告書 §7 の P0=1 / P1=8 計 9 件を 1 plan で潰す実装計画を起票
  - `~/.claude/plans/2026-04-28-design-review-p0-p1.md`（Plan agent 詳細計画）
  - `.agentops/plans/current.md`（親 plan）
  - `.agentops/task-plans/current.md`（実装フェーズ雛形）
  - `.agentops/tasks/01-09-*.md`（9 task ファイル、DbC 完備）
- Codex (GPT-5.5 frontier) cross-review 委譲、所見 P1=4 / P2=4 / P3=3 を全件反映
  - `.agentops/reviews/plan.md`（所見と反映方針）
  - `.agentops/runs/20260428T181235+0900-codex-review_frontier/`
- PR #28 を `claude/design-review-2026-04-28` → `main` で作成済み

## 未完了のこと

- PR #28 のレビューとマージ（GitHub 上）
- マージ後、9 task の実装フェーズ（別ブランチ）
- 9 task すべてマージ後に plan を archive へ移動 + `archive/README.md` table への row 挿入

## 現在のブランチ

- 本セッションのブランチ: `claude/design-review-2026-04-28`（PR #28 開設済み）
- 実装フェーズ用ブランチ: `claude/design-review-impl-p0-p1`（PR #28 マージ後に main から切り直す）

## 変更ファイル

`.agentops/` 配下のみ。実装ファイル（docs / config / scripts / .github 等）には一切触れていない。

```
.agentops/plans/current.md
.agentops/task-plans/current.md
.agentops/tasks/01-p0-02-tool-stop-conditions.md
.agentops/tasks/02-p1-01-glossary.md
.agentops/tasks/03-p1-02-deprecation-marker.md
.agentops/tasks/04-p1-04-last-reviewed.md
.agentops/tasks/05-p1-05-dbc-consolidation.md
.agentops/tasks/06-p1-03-cross-reference.md
.agentops/tasks/07-p1-06-archive-auto-update.md
.agentops/tasks/08-p1-07-ci-and-gitignore.md
.agentops/tasks/09-p1-08-agents-md-unify.md
.agentops/reviews/plan.md
.agentops/prompts/next-session.md（このファイル）
```

## 実行したテスト

- `scripts/agentops doctor` → ok
- `scripts/agentops delegate --to codex --role review_frontier --effort high --input ...` → exit 0
- 観察事実裏取り（`.github/` 不在 / `.gitignore` secret 未列挙 / archive 構造 / CLAUDE.md・AGENTS.md 47 行）→ 全件報告書記述と一致

## 未解決リスク

- task 09 (P1-08): `@AGENTS.md` import が Claude Code / Codex 両方で確実に動作するか着手前に再確認必要（公式仕様変化が速い）
- task 07 (P1-06): pre-commit / post-commit / 手動 CLI のどれを発火タイミングにするか実装時に決定
- task 08 (P1-07): GitHub Actions が無料枠を超えないか着手時確認（public リポジトリなら問題なし）
- 監視 CLI 側で stop_conditions spec を読んで警告する実装は task 01 範囲外。次 plan の handoff 候補
- skills / workflows 側の逆参照列追加は task 06 範囲外。次 plan の handoff 候補

---

## 次セッション投入プロンプト（PR #28 マージ後にユーザーが貼って良い）

> agentops の `.agentops/tasks/01-p0-02-tool-stop-conditions.md` から実装フェーズを開始します。
>
> 起動手順:
>
> 1. PR #28 がマージ済みであることを確認し、`git checkout main && git pull --ff-only origin main` でローカル main を同期
> 2. `git checkout -b claude/design-review-impl-p0-p1` で実装ブランチを切る
> 3. `.agentops/tasks/01-p0-02-tool-stop-conditions.md` の DbC（前提・不変・実行内容・完了条件・検証・禁止・後処理・停止条件）を読み、内容に従って `docs/03-dbc-and-quality-gates.md` と `config/harness.yml` を編集
> 4. 編集後、`python3 -m compileall tools` と `scripts/agentops-watch check`（存在時）で検証
> 5. `scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/03-dbc-and-quality-gates.md` で Codex に cross-review 委譲。`config/harness.yml` も同様にもう一度委譲、もしくは diff を 1 ファイルにまとめて 1 回で投げる
> 6. Codex 所見を `.agentops/reviews/p0-02.md` に転記し、P0/P1 を反映（最大 2 周）
> 7. PR を作成（タイトル `P0-02: tool 実行層停止条件を docs/03 + harness.yml に追加`、本文に DbC + 検証コマンド + 未解決リスク）
> 8. main マージ後、本 task ファイルを `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/` へ移動（commit 前）
> 9. `prompts/next-session.md` を次番号 task（`02-p1-01-glossary.md`）に更新
> 10. ローカル main 同期確認（`git fetch && git status`）
>
> 制約:
>
> - 親 plan は `.agentops/plans/current.md`、task-plan は `.agentops/task-plans/current.md`、Plan agent 詳細は `~/.claude/plans/2026-04-28-design-review-p0-p1.md`
> - 1 task = 1 PR で完結。スコープ外リファクタ禁止
> - main 直 push 禁止、`claude/` プレフィックスブランチ必須
> - secret / 本番 / 課金 / 外部公開 / 破壊的操作が必要になったら停止して user 確認
> - レビュー修正は最大 2 周。3 周目が必要なら統合判断または user 確認
> - task 03 (P1-02) と task 07 (P1-06) は依存無しのため、別ブランチで並行 PR 化も可

## 関連ファイル

- 親 plan: `.agentops/plans/current.md`
- task-plan: `.agentops/task-plans/current.md`
- Plan agent 詳細: `~/.claude/plans/2026-04-28-design-review-p0-p1.md`（リポジトリ外）
- Codex cross-review 所見: `.agentops/reviews/plan.md`
- 報告書: `docs/reviews/2026-04-28-cross-repo-design-review.md`
- 規約: `docs/04-model-routing.md`, `docs/05-review-policy.md`, `CLAUDE.md`, `AGENTS.md`
