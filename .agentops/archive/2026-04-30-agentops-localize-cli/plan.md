---
plan-id: 2026-04-30-agentops-localize-cli
created: 2026-04-30
status: in-progress
parent-docs: docs/19-project-localization.md, docs/10-cli-wrapper.md
last_reviewed: 2026-04-30
---

# Plan: `agentops localize` CLI 実装

## Context

- docs/19-project-localization.md (PR #59 で merge 済) で **仕様確定**
- docs/10-cli-wrapper.md に CLI 形式 (`scripts/agentops localize --project <path> [--dry-run] [--strategy auto|...]`) 規定済 (実装ステータス: **契約段階**)
- 直前 plan で B (Discord 通知経路) 修復完了。ユーザー判断で B-rest / C / D を本セッションで自律処理することに
- `tools/agentops_cli/__main__.py` には `delegate` / `runs` / `doctor` / `archive` 実装済、`localize` のみ未実装
- `templates/claude/skill/agentops-localize/SKILL.md` は仕様メモあり (skill 雛形)、本 plan では skill 実体は touch しない

## 親 task 一覧

- [01-localize-implementation](../tasks/01-localize-implementation.md) — agentops localize CLI 本体 + tests + docs

## スコープ外

- 既存 `~/dev/` 5 プロジェクトの実マイグレーション (各プロジェクト個別 plan、user 承認後)
- skill `/agentops:localize` の実体 (本 plan では skill 雛形だけ参照)
- `--apply` モード (本反映、将来仕様)

## 完了条件

- task 01 の DbC 完了条件すべて
- Codex `review_frontier --effort high` cross-review で P0/P1 0 件 (or 反映済)
- 既存 agentops_cli テストを破壊しない (regression なし)
- `scripts/agentops localize --project <path> --dry-run` で意思決定木に基づく戦略推奨 + inventory が stdout + run log に出力される
- secret (Webhook URL / API key / 個人 file path 値) を inventory / log / docs に書かない
- archive 移動 + commit + push + PR + 自動マージ (auto-merge 許諾条件下) + main 同期

## 停止条件

- レビュー修正 2 周超過
- secret 値が誤って混入
- docs/19 仕様と実装が大きく乖離
- 既存 `delegate` / `archive` 実装の挙動を破壊
- 4 戦略すべてに該当しない / 判定軸不足のケースで自動推奨を強制 (docs/19 §DbC §停止条件 と整合)
