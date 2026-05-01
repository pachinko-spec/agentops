# plan: 2026-05-02-rule-strengthen-post-merge-1pr-scope

> plan-id: `2026-05-02-rule-strengthen-post-merge-1pr-scope`

## 背景

2026-05-02 に pachi-studio repo (PR #15、Step 1.5 PR-D) で、Claude Code orchestrator が
post-merge 整理 (`tasks/<NN>-*.md` → archive 移動 / `plans/current.md` 更新 /
`prompts/next-session.md` 更新 / `task-plans/current.md` archive) を「別 chore PR で
実施する」と誤解する事故が発生した (惰性で過去 PR #14 を踏襲)。

合わせて、本 plan 策定中の対話で、5 工程フローの工程 2 (設計レビュー = Codex
cross-review) タイミングが既存 docs (`docs/04-model-routing.md` L92 / `AGENTS.md`
「実装着手前」) で曖昧であることが判明。Plan agent (Claude 同系列内部レビュー)
と cross-review (別モデルファミリー) の区別、および通常運用 (user 承認後
cross-review) と特殊運用 (user 提示前 cross-review 必須) の境界も未明文化。

`~/.claude/hooks/_common.py` L226-227 の `inspect_agentops` block (Stop 時に
completed task 残存を検知して `"before finalizing"` block message を emit する設計)
は同セッション内整理を意図しており、別 chore PR 分離は hook 意図と逆向き。

## 目的

agentops 雛形リポ (本リポ `/home/otaku/agentops`) 側の rule / docs / catalog /
AGENTS.md を強化し、以下 2 つの再発と曖昧解釈を防ぐ:

1. **post-merge 整理 1 PR scope 完結原則**: archive 移動 / plans 更新 /
   next-session 更新は merge 前 commit に含める (user 明示許可がある場合のみ
   別 chore PR 分離を許容)
2. **cross-review タイミング明文化**: Plan agent と cross-review の区別 +
   通常運用 (user 承認後) と特殊運用 (user 提示前) の判定基準

## 非目的

- `~/.claude/*` への実反映 (PR scope 外、別作業として handoff へ)
- 他プロジェクト (pachi-studio 等) への伝播 (別 plan)
- hook 仕様そのものの変更 (`_common.py` / `stop.py` は触らない、rule 側で hook 整合説明を追記するのみ)

## 採用方針

A 案: agentops repo 内に新規 `rules/auto-merge-permission.md` /
`rules/session-record-and-handoff.md` を template-source として作成、既存
`rules/model-routing.md` に新節 3 つ追加、`docs/03` に post-merge 新節 append、
`docs/04` の 5 工程フロー節を拡張、`AGENTS.md` の cross-review 記述を明示化、
`rules/catalog.md` に新規 entry 追加。

`~/.claude/*` への反映は **別 PR / 別 commit / 別 handoff** で実施し、本 PR scope 外。
これにより特殊運用判定基準 (a)「実グローバル反映を同一作業で行う」に該当しない
通常運用 plan として処理する。

## 完了条件

- agentops repo 内 7 ファイルが意図した修正のみで更新されている
- `rules/catalog.md` の新規 2 entry が既存形式と整合
- 新規 2 ファイルの frontmatter が repo 側 rule 形式 (`name` / `description` / `applies-to`)
- 設計段階 cross-review (Codex review_frontier) で P0/P1=0
- 実装後 cross-review (Codex review_frontier) で P0/P1=0
- AI auto-merge 許諾条件 6 (DbC 完了 / cross-review 通過 / CI green / 観察事実
  食い違いなし / PR スコープ単一 / secret 未混入) を全て満たす
- `tasks/01-rule-strengthen-post-merge.md` の DbC 完了条件をすべて満たす
- merge 後 `git status --short` で dirty diff が無い (Phase 4.5 で archive 実施済)

## 停止条件

- cross-review 所見に P0/P1 が反映困難
- 修正範囲が当初計画 (agentops repo 内 7 ファイル + `~/.claude/` 側 5 ファイル別作業) を超える
- レビュー修正が 2 周を超える (3 周目到達 → user 確認、auto-merge 許諾発動せず)
- agentops repo / `~/.claude/rules/` の他 rule (例: `model-routing.md`) と新規追記内容が矛盾
- hook 仕様の現在状態と修正後 rule 記述が齟齬する

## 親 task 一覧

- `tasks/01-rule-strengthen-post-merge.md` — 修正対象 7 ファイルの新規作成 / 編集 + Phase 4.5 archive
