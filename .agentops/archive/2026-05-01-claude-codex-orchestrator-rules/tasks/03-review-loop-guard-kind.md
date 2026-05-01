---
task-id: 03-review-loop-guard-kind
plan-id: 2026-05-01-claude-codex-orchestrator-rules
status: approved
pr-number: PR-03
depends-on: 02-model-routing-rule
---

# Task 03: review-loop-guard skill kind 分岐手順追加

## 目的

`~/.claude/skills/review-loop-guard/SKILL.md` の Procedure (line 30-37) に「kind 分岐」手順を追加し、修正者と修正経路を明確化する。ループカウント定義は不変 (修正したら +1、修正者は問わない)。

## 変更対象

- `/home/otaku/.claude/skills/review-loop-guard/SKILL.md` (line 30-37 Procedure)

## 追記内容

Procedure に以下を追加:

```md
### kind 分岐 (P0 / P1 修正後)

cross-review reviewer の出力に `kind` ラベルが付いている場合:

- `kind: mechanical` (patch / 行番号 / 具体書き換え提示) → Claude が直接 patch 適用 (`git apply` 等)。test 実行はコスト判断で Claude or Codex 再委譲のいずれか
- `kind: design` (抽象指摘、判断要) → Codex (run A) に再委譲

`kind` ラベル無しの review 出力は保守的に `design` 扱い (Codex 再委譲)。

### ループカウント

修正したらループ +1。修正者 (Claude / Codex) は問わない。3 周目到達 → kind 不問で user 確認。詳細は `~/.claude/rules/model-routing.md` 「## 実装 → レビュー → 分岐フロー」節を参照。
```

## DbC

- **前提条件**:
  - `~/.claude/skills/review-loop-guard/SKILL.md:25` で「Maximum 2 review-fix iterations」記述済み
  - line 26-27, 37 で 3 周目処理 (user 確認 / merge with documented residual or stop) 記述済み
  - kind 分岐記述は現状なし
- **不変条件**:
  - 2 周制限は維持
  - P0 / P1 / P2 / P3 severity tier 区分は維持
- **完了条件**:
  - Procedure に kind 分岐セクションが追加され、ループカウント定義 (修正者問わず +1) が明記
  - `~/.claude/rules/model-routing.md` への参照リンクあり
  - markdown lint 通過
  - `/Skill review-loop-guard` で invoke 時に kind 分岐手順が応答に反映される (再起動後確認)
- **禁止事項**:
  - 2 周制限の変更
  - severity tier (P0-P3) の再定義
  - kind ラベル判定者を Claude にする記述 (cross-review reviewer 自身が付与)
- **停止条件**:
  - SKILL.md が長大化 (kind 判定基準が肥大) → 詳細は model-routing.md に集約、SKILL.md は参照のみ
  - skill invoke が壊れる → frontmatter 確認、description 維持

## 検証

```sh
# (1) markdown lint
markdownlint ~/.claude/skills/review-loop-guard/SKILL.md || true

# (2) skill invoke 確認 (Claude Code 再起動後)
# 新セッションで /Skill review-loop-guard を invoke、kind 分岐手順が含まれることを確認
```

## cross-review

PR-01 と同様に Codex review run B で実行。SKILL.md は markdown のみだが、文言の整合性 (用語 mechanical / design / ループカウント定義 / 3 周目処理) を design 観点でチェック。

## 反映側 (~/.claude/) の作業

`~/.claude/skills/review-loop-guard/SKILL.md` を直接編集する task のため、本 task は repo 管理外の作業のみ。`~/.claude/.agentops/handoffs/2026-05-01-review-loop-guard-sync.md` に変更点メモを残す。
