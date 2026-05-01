---
task-id: 01-design-cross-review
plan-id: 2026-05-01-claude-coding-frontier-model-id-realign
status: approved
pr-number: (n/a — 設計段階 cross-review、PR 化なし)
depends-on: (none — Step 0 完了が前提)
---

# Task 01: 設計段階 cross-review 委譲 (Step 0.5 対応)

## 目的

本 plan 自体を高リスク事例 (durable instructions / catalog 編集) として、Step 1 着手前に Codex review_frontier (gpt-5.5) に設計段階 cross-review を委譲し、P0/P1=0 を確認する。これは parent plan §Step 0.5 に対応し、Goals 7-8 (5 工程フロー durable instructions 化) の最初の発動例である。

## 変更対象

- `/home/otaku/agentops/.agentops/runs/<run_id>/` に Codex 委譲記録 (`request.md` / `status.json` / `stdout.log` / `stderr.log` / `result.md` / `artifacts/`) を残す (wrapper 既定挙動)。グローバル側記録のため要約 or コピーを `~/.claude/.agentops/runs/<run_id>-summary.md` にも残す
- 所見の `kind: mechanical` 指摘 → 私 (Claude orchestrator) が parent plan ファイル (`/home/otaku/.claude/plans/claude-gtp5-5-claude-snappy-zebra.md`) を直接 patch
- 所見の `kind: design` 指摘 → user 確認再取得してから plan 再設計 (orchestrator 独断禁止)

## 実行コマンド

```sh
scripts/agentops delegate \
  --to codex --role review_frontier --model gpt-5.5 --effort high \
  --input /home/otaku/.claude/plans/claude-gtp5-5-claude-snappy-zebra.md
```

## レビュー観点 (parent plan §Step 0.5 から踏襲)

- 観察事実食い違い (catalog 構造 / 行番号 / models_cache 内容)
- user 意図との乖離 (coding_frontier=gpt-5.5 / coding_fast=gpt-5.3-codex / docs_agent secondary=gpt-5.3-codex)
- Trinity 違反リスク (template-source への実値混入)
- cross-review 別系列原則違反 (Anthropic ↔ OpenAI)
- stop conditions 不足
- 検証手段不足
- scope 単一性

## DbC

- **前提条件**:
  - Step 0 完了 (`.agentops/plans/current.md` / `task-plans/current.md` / `tasks/01-08` 生成済み)
  - `scripts/agentops delegate` が動作可能 (`codex --version` で 0.128.0 系)
  - `~/.codex/config.toml` の `model = "gpt-5.5"` が有効、`~/.codex/models_cache.json` で `gpt-5.5` が listable
  - parent plan file (`/home/otaku/.claude/plans/claude-gtp5-5-claude-snappy-zebra.md`) が読み取り可能
- **不変条件**:
  - cross-review reviewer は Codex (OpenAI 系)、主 orchestrator (Claude/Anthropic 系) と別系列
  - reviewer 所見は kind ラベル付き (`kind: mechanical | design`)、無ければ保守的に `design` 扱い
  - ループカウント上限 2 周、3 周目到達なら user 確認 escalate
- **完了条件**:
  - `/home/otaku/agentops/.agentops/runs/<run_id>/result.md` に Codex 所見 + kind ラベル + P0/P1 = 0 が記録
  - `/home/otaku/agentops/.agentops/runs/<run_id>/status.json` の state が `succeeded`
  - グローバル側記録 (`~/.claude/.agentops/runs/<run_id>-summary.md`) も作成済み
  - mechanical 指摘は parent plan に反映済み
  - design 指摘は user 確認済み + 反映または不採用判断確定
- **禁止事項**:
  - kind: design 指摘を Claude が独断で反映する (orchestrator 独走の再発)
  - reviewer に Anthropic 系 model を使う (cross-review 別系列原則違反)
  - 委譲を skip して Step 1 (catalog 編集) に着手する
  - secret 値を `request.md` / `result.md` / `stdout.log` に書く
- **停止条件**:
  - Codex CLI で gpt-5.5 が起動しない / delegate template が失敗 → 即停止、user 確認 (Step 1 着手不可)
  - ループ 3 周到達 / P0/P1 が消えない → 本 plan pause、user 確認
  - kind ラベル付与なし、かつ複数指摘で design / mechanical 判別困難 → 保守的に全 design 扱い、user 確認

## 検証

```sh
# (1) Codex 委譲 run 記録の存在確認
ls -la /home/otaku/agentops/.agentops/runs/ | tail -5
cat /home/otaku/agentops/.agentops/runs/<run_id>/status.json
# state が "succeeded"

# (2) 所見の kind ラベル確認
grep -E "kind:\s*(mechanical|design)" /home/otaku/agentops/.agentops/runs/<run_id>/result.md

# (3) P0/P1 残件確認 (0 であること)
grep -cE "severity:\s*P[01]\b|^P[01]\b" /home/otaku/agentops/.agentops/runs/<run_id>/result.md /home/otaku/agentops/.agentops/runs/<run_id>/artifacts/review.md
```

## メモ

- Step 0.5 が走らない場合は Step 1 着手禁止 (parent plan §停止条件)
- 実行先は agentops repo のため runs 保存先は `/home/otaku/agentops/.agentops/runs/<run_id>/`。グローバル側には `~/.claude/.agentops/runs/<run_id>-summary.md` を別途作成
- 完了後は Step 1 (Task 02 / 03 / 04) に進む
