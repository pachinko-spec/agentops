---
plan-id: 2026-05-01-claude-codex-orchestrator-rules
status: approved
started: 2026-05-01T11:53:28+09:00
owner: claude
parent-plan-file: /home/otaku/.claude/plans/gpt5-5-opus4-7-codex-pc-tranquil-quilt.md
---

# Claude orchestrator + Codex 実装/cross-review 体制への運用ルール整備

## 背景

main session を Claude Code (Opus 4.7) に固定、コード実装 + test 生成 + test 実行 + cross-review を Codex (GPT-5.5) に常時委譲する運用へ寄せる。Opus は意図汲み / 設計 / 最終判断、Codex は実装 + 別 session の cross-review。cross-review reviewer は修正指摘に `kind: mechanical | design` ラベルを付与し、mechanical は Claude 直接 patch、design は Codex 再委譲、ループカウントは修正者問わず +1。

詳細は parent plan file (`~/.claude/plans/gpt5-5-opus4-7-codex-pc-tranquil-quilt.md`) を参照。

## 目的

a-d 一括変更で運用ルールを durable instruction 化:

- (a) `agentops delegate --to codex --role review_frontier` の prompt template 拡張: 出力期待値 (kind ラベル / mechanical なら unified diff patch / `artifacts/review.md` 保存)
- (b) `review-loop-guard` skill: kind 分岐手順追加、ループカウント定義は不変
- (c) `model-routing` rule: 雛形側を新規作成、反映側に「実装 run A / review run B / kind 分岐」3 工程フロー節を追加
- (d) `AGENTS.md` auto-merge / `auto-merge-permission.md`: cross-review 通過条件に kind ラベル運用を補記

## 非目的

- 実 model id の固定 (model-catalog.yml の論理ロール指定方式は維持)
- review-loop-guard 2 周制限の変更
- AAIF import 構造の見直し
- 他 rule の雛形化波及作業 (model-routing.md だけが本 plan のスコープ)
- `.agentops/runs/` 監視ツール拡張 (現状 + Discord ANT_TIME digest で運用、必要が見えたら別 plan)

## PR 分割

- **PR-01**: agentops delegate prompt template 拡張 (a) — `tools/agentops_cli/__main__.py` + `docs/10-cli-wrapper.md`
- **PR-02**: model-routing rule (c) — `rules/model-routing.md` 新規 + `~/.claude/rules/model-routing.md` 追記
- **PR-03**: review-loop-guard skill kind 分岐 (b) — `~/.claude/skills/review-loop-guard/SKILL.md`
- **PR-04**: AGENTS.md / auto-merge-permission 同期補記 (d) — `AGENTS.md` + `~/.claude/rules/auto-merge-permission.md`

PR-01 → PR-02 → PR-03 → PR-04 の順で出す (kind ラベル仕様 → 3 工程フロー → skill 反映 → auto-merge 条項補記)。

`~/.claude/` 配下は repo 管理外のため PR 化不可、各 PR 内で「反映側手動同期メモ」として `~/.claude/.agentops/handoffs/` に変更点を残す。

## 完了条件

- PR-01 〜 PR-04 全て main に merge 済み (auto-merge 許諾条件 1-6 を満たし squash merge)
- `~/.claude/rules/model-routing.md` / `~/.claude/skills/review-loop-guard/SKILL.md` / `~/.claude/rules/auto-merge-permission.md` の手動反映完了
- Claude Code 再起動後 `/memory` で追記節が context に load されることを確認
- cross-review (Codex review run) で本 plan 全変更に対し P0 / P1 = 0
- main 同期 + archive 移動完了

## 停止条件

- a の prompt 拡張に対し Codex CLI が出力フォーマットを無視 → docs にだけ期待値を書き、Claude 側読解で吸収する fallback
- model-routing.md 雛形作成に他 rule の雛形化作業が波及 → 本 plan は model-routing.md だけに限定
- AGENTS.md と auto-merge-permission.md の補記内容に解釈差 → 同一文言に揃える
- レビュー修正が 2 周を超えそう / 観察事実食い違い / secret 混入リスク → user 確認

## 関連 task

- `.agentops/tasks/01-delegate-prompt-template.md`
- `.agentops/tasks/02-model-routing-rule.md`
- `.agentops/tasks/03-review-loop-guard-kind.md`
- `.agentops/tasks/04-agents-md-auto-merge-sync.md`
