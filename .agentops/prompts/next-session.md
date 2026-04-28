# Next session プロンプト（2026-04-28 設計レビュー実装フェーズ）

parent_plan: 2026-04-28-design-review-p0-p1
status: in progress (task 01 + 07 完了 / 残り 7 task)
created_at: 2026-04-28
updated_at: 2026-04-28
timezone: Asia/Tokyo
entry_point: .agentops/tasks/02-p1-01-glossary.md
completed_tasks:
  - 01-p0-02-tool-stop-conditions (PR #30, archive 済)
  - 07-p1-06-archive-auto-update (PR #31 機能 + #32 ドッグフード archive + #33 round 3 記録 + #34 status 更新 + 本 PR で本文書き直し)

---

## 今回完了したこと（2026-04-28 task 07 P1-06 セッション）

ユーザー起動指示は task 01 だったが、リポジトリ実状で **task 01 (P0-02) は前回マージ済み** (PR #30) と確認。さらに user 追加要望「`.agentops/tasks/` 配下完了 md / `task-plan/current.md` archive / `next-session.md` 更新の人手忘れに対し強制力を上げたい、早ければ早いほど後続 task の役に立つ」を受け、本来 task 02 の予定だったセッションを **task 07 (P1-06: archive 自動更新 hook) 先行着手** に切り替えた。

実施内容:

- **PR #31** `P1-06: archive 自動更新 hook + 個別 task archive CLI`
  - `tools/agentops_cli/__main__.py` に `archive plan` / `archive task` サブコマンドを追加 (argparse nested subparser)
  - パストラバーサル防御 (二重) / preflight (dst 衝突 + README separator 検証) / atomic write / `--date` (YYYY-MM-DD) / `--summary` (改行禁止 + `|` escape) / inline 空配列正規化 / completed_tasks 非対応形式の skipped 表示
  - `CLAUDE.md` / `AGENTS.md` の auto-merge 後の必須手順を CLI 必須化に書き換え（章立て対称維持、`diff` で完全一致確認）
  - `docs/11-monitoring-cli.md` に archive サブコマンド仕様 / DbC / ロールバック手順を追加
  - Codex cross-review: Round 1 (P1=2 / P2=2 / P3=2) → Round 2 (P1=1 / P2=1) → 全件反映
- **PR #32** post-merge ドッグフード: 新コマンドで task 07 自身を `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/` へ移動
- **PR #33** post-hoc Round 3 cross-review 記録 (P0/P1=0、P2 1 件は次 plan 候補に延期)
  - **反省**: Round 2 修正後にレビュー無しで PR / merge / ドッグフードまで進めた。user グローバル CLAUDE.md「修正したら必ず再レビュー、最後はレビュー結果の確認で終える」に違反。指摘を受けて post-hoc で Round 3 を回し記録に残した。次セッションは Round 1 → 修正 → Round 2 → 修正 → Round 3 (確認のみ) で締める運用を厳守する
- **PR #34** `next-session.md` の `status:` ヘッダーを `task 01 + 07 完了 / 残り 7 task` に手動更新
- **本 PR** `next-session.md` 本文を task 07 完了 → task 02 着手用に全面書き直し
  - 反省: archive task CLI は entry_point と completed_tasks の機械更新は行うが、本文 (`## 今回完了したこと` / `## 次セッション投入プロンプト`) は触らない設計にしていた。これは責務分離としては正しいが、運用上は次セッションが起動時に古い投入プロンプトを見るため **手動更新が必須** になるべきだった。本 PR で書き直し + 次 plan で「本文更新も運用ルール化」を検討する

## 未完了のこと

- 残 7 task の実装 (依存順): `02-p1-01-glossary` → `04-p1-04-last-reviewed` / `05-p1-05-dbc-consolidation` / `06-p1-03-cross-reference` (いずれも task 02 完了後着手可) → `08-p1-07-ci-and-gitignore` (task 04 完了後) → `09-p1-08-agents-md-unify` (task 02/04/05/06 完了後)
- 並行 PR 候補: `03-p1-02-deprecation-marker` は依存無し (task 02 と並行可、ただし用語ゆれ二重発生防止のため task 02 マージ後を推奨)
- 7 task すべてマージ後、`scripts/agentops archive plan --plan-id 2026-04-28-design-review-p0-p1 --summary <text>` で plan 全体 archive + `archive/README.md` table への row 挿入

## 現在のブランチ

- 本 PR ブランチ: `claude/rewrite-next-session-md`
- 次セッション実装ブランチ: 各 task ごとに `claude/design-review-impl-<task-id>` を main から切り直す

## 変更ファイル（task 07 セッション全体）

```
PR #31: tools/agentops_cli/__main__.py, CLAUDE.md, AGENTS.md, docs/11-monitoring-cli.md, .agentops/reviews/p1-06.md (round 1, 2)
PR #32: .agentops/{tasks/ → archive/.../tasks/}/07-p1-06-archive-auto-update.md, .agentops/prompts/next-session.md (completed_tasks 追記)
PR #33: .agentops/reviews/p1-06.md (round 3 追記)
PR #34: .agentops/prompts/next-session.md (status 行)
本 PR: .agentops/prompts/next-session.md (本文全面書き直し)
```

## 実行したテスト

- `python3 -m compileall tools` 成功
- `scripts/agentops archive --help` / `archive plan --help` / `archive task --help` 表示確認
- 仮 fixture `.agentops/.tmp/smoke-{v2,v3,attack,preflight,r2}/` で T1–T9 全件期待動作:
  - T1: 通常 archive task / T2: inline `completed_tasks: []` 正規化 + 空行保持 / T3: traversal 攻撃 (slash, leading dot, double-dot) reject / T4: 不正 `--date` reject / T5: `--summary` 改行 reject / T6: `--summary` `|` escape / T7: preflight 衝突で副作用ゼロ / T8: 非対応形式の skipped 表示 / T9: README separator 欠落で preflight 失敗 + move ゼロ
- 実リポジトリで archive task / archive plan dry-run 想定通り
- 本番実行 (PR #32) で git mv 経路 + next-session.md 更新の動作実証

## 次セッション投入プロンプト（task 02 着手用、user が貼って良い）

> agentops の `.agentops/tasks/02-p1-01-glossary.md` から実装フェーズを継続します。
>
> 起動手順:
>
> 1. `git status --short --branch` で main + clean を確認、`git fetch origin && git pull --ff-only origin main` で同期
> 2. `git checkout -b claude/design-review-impl-p1-01` で実装ブランチを切る
> 3. `.agentops/tasks/02-p1-01-glossary.md` の DbC（前提・不変・実行内容・完了条件・検証・禁止・後処理・停止条件）を読み、内容に従って `docs/00-glossary.md` を新規作成し、報告書 Appendix B + task 01 で確定した停止条件用語を取り込んで 19 用語を 1 行ずつ定義
> 4. リポジトリ全体を `rg` で grep し、用語ゆれ（orchestrator / cross-review vs cross-model-delegate / harness / harness spec / harness engineering）を統一。許容語リストを glossary 冒頭に明記
> 5. `docs/01-philosophy.md` 冒頭に glossary への参照リンクを追加（双方向リンク）
> 6. 検証: `rg -n "orchestrator" docs/ config/ rules/ skills/ workflows/ CLAUDE.md AGENTS.md | rg -v "<許容語>"` で 0 件、`python3 -m compileall tools` exit 0
> 7. **Codex cross-review**: `scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/00-glossary.md` で **Round 1**。所見を `.agentops/reviews/p1-01.md` に転記、P0/P1 を反映。**修正したら必ず Round 2** を回す。修正があれば最大 2 周まで。**Round 3 は確認用レビューとして必ず実施し、`no further P0/P1` を確認して終える** (本セッションの反省点)
> 8. PR を作成（タイトル `P1-01: 用語統一表 docs/00-glossary.md 追加 + 旧用語 0 件化`、本文に DbC + 検証コマンド + Codex 各 Round 結果 + 未解決リスク）
> 9. AI auto-merge 許諾条件 6 件 (CLAUDE.md durable instructions §許諾条件) を独立評価。全件 OK なら `gh pr merge --squash --delete-branch`
> 10. main 同期: `git checkout main && git fetch origin && git pull --ff-only origin main && git status --short --branch`
> 11. **後処理 (CLAUDE.md auto-merge 後の必須手順)**:
>     - `claude/archive-task-02-dogfood` ブランチを切り、`scripts/agentops archive task --task-id 02-p1-01-glossary --dry-run` → 本番実行
>     - 本番実行後 `git status` で next-session.md の差分を確認し、`git add .agentops/prompts/next-session.md` を **忘れずに**（CLI が通常 write で書き換えるため unstaged のまま残る既知問題、PR #32 で発覚）
>     - `next-session.md` の **本文 (`## 今回完了したこと` / `## 未完了のこと` / `## 変更ファイル` / `## 実行したテスト` / `## 次セッション投入プロンプト` / `## 関連ファイル`) を task 02 セッションの内容に手動で書き直す**（archive task CLI は本文を触らない設計のため）
>     - 別小 PR (`claude/archive-task-02-dogfood`) を作成 → self-merge → main 同期
>
> 制約:
>
> - 親 plan は `.agentops/plans/current.md`、task-plan は `.agentops/task-plans/current.md`、Plan agent 詳細は `~/.claude/plans/2026-04-28-design-review-p0-p1.md` (リポジトリ外)
> - 1 task = 1 PR で完結。スコープ外リファクタ禁止
> - main 直 push 禁止、`claude/` プレフィックスブランチ必須
> - secret / 本番 / 課金 / 外部公開 / 破壊的操作が必要になったら停止して user 確認
> - **レビュー修正は最大 2 周。3 周目は確認のみ。3 周目で修正必要なら統合判断または user 確認**
> - **修正したら必ず再レビュー。最後はレビュー結果の確認で終える** (本セッションで違反したため強調)
> - 並行 PR 化したい場合は task 03 (P1-02 deprecation-marker) が依存無し候補。user 確認の上で判断

## 関連ファイル

- 親 plan: `.agentops/plans/current.md`
- task-plan: `.agentops/task-plans/current.md`
- 着手 task: `.agentops/tasks/02-p1-01-glossary.md`
- Plan agent 詳細: `~/.claude/plans/2026-04-28-design-review-p0-p1.md` (リポジトリ外)
- 報告書: `docs/reviews/2026-04-28-cross-repo-design-review.md`
- task 01 review (P0-02 タスク): `.agentops/archive/2026-04-28-design-review-p0-p1/reviews/p0-02.md`
- task 07 review (本セッション): `.agentops/reviews/p1-06.md` (Round 1, 2, 3 含む)
- task 07 archive: `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/07-p1-06-archive-auto-update.md`
- archive CLI 仕様: `docs/11-monitoring-cli.md` §archive サブコマンド
- 規約: `docs/04-model-routing.md`, `docs/05-review-policy.md`, `CLAUDE.md`, `AGENTS.md`

## 未解決リスク (本 plan の他 task に影響しうるもの)

- **archive task CLI の P2 残課題**: `completed_tasks: []` がファイル末尾改行なしで終わる極端ケースで unsupported 扱いになる（Round 3 P2）。実害は表示と実体の整合性が保たれているため軽微だが、次 plan で 1 行 regex hardening 候補（`block_pattern` の先頭 `\n` を optional 化）
- **archive task CLI が next-session.md 本文を更新しない既知制約**: 責務分離のため意図的だが、結果として「本文の手動書き直し」が運用に必須。次 plan で:
  - 案 a: `archive task` を拡張して `## 今回完了したこと` などを section 単位で template 注入
  - 案 b: 別 CLI `agentops session-log` を新設してセッションログ生成を支援
  - 案 c: CLAUDE.md / AGENTS.md auto-merge 後手順に「next-session.md 本文書き直し」を明示追加
  のいずれかを採用するか議論
- **archive task で git add 漏れ**: CLI は `git mv` で task md を staged にするが、`next-session.md` は通常 write のため unstaged のまま残る（PR #32 で発覚）。次 plan で CLI 側に `git add` を追加する hardening 候補
- **task 09 (P1-08)**: `@AGENTS.md` import が Claude Code / Codex 両方で確実に動作するか着手前に再確認必要（公式仕様変化が速い）
- **task 07 (P1-06) の発火タイミング選択**は本 task で完結（archive plan / archive task の手動 CLI 起動方式を採用、pre-commit / post-commit hook は不採用）
- **task 08 (P1-07)**: GitHub Actions が無料枠を超えないか着手時確認（public リポジトリなら問題なし）
- 監視 CLI 側で stop_conditions spec を読んで警告する実装は task 01 範囲外で次 plan の handoff 候補
- skills / workflows 側の逆参照列追加は task 06 範囲外で次 plan の handoff 候補
