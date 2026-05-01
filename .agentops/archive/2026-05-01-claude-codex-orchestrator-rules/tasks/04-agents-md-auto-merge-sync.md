---
task-id: 04-agents-md-auto-merge-sync
plan-id: 2026-05-01-claude-codex-orchestrator-rules
status: approved
pr-number: PR-04
depends-on: 03-review-loop-guard-kind
---

# Task 04: AGENTS.md / auto-merge-permission.md 同期補記

## 目的

`AGENTS.md` の AI auto-merge 許諾条件 2 (cross-review 通過) と `~/.claude/rules/auto-merge-permission.md` の同条件に、kind ラベル運用への対応 (mechanical / design 分岐、ループカウント定義) を補記する。両ファイルを同一文言で揃え、解釈差を防ぐ。

## 変更対象

- `/home/otaku/agentops/AGENTS.md` (line 81-82 cross-review 条件)
- `/home/otaku/.claude/rules/auto-merge-permission.md` (line 13 cross-review 条件)

## 追記内容 (両ファイル同一)

cross-review 通過条件 (許諾条件 2) の後ろに以下を補記:

```md
reviewer は修正指摘ごとに `kind: mechanical | design` ラベルを付与する。`kind: mechanical` (patch / 行番号 / 具体書き換え提示) は Claude が直接 patch、`kind: design` (抽象指摘) は Codex (run A) に再委譲。修正したらループ +1、修正者問わず。3 周目到達 → kind 不問で user 確認 (本許諾発動せず)。kind ラベル無し → 保守的に `design` 扱い。詳細は `rules/model-routing.md` (雛形) / `~/.claude/rules/model-routing.md` (反映) の「## 実装 → レビュー → 分岐フロー」節。
```

## DbC

- **前提条件**:
  - `AGENTS.md:81-82` で cross-review 条件 (P0/P1 = 0 件、reviewer 別系列) 記述済み
  - `~/.claude/rules/auto-merge-permission.md:13` で同等記述済み
  - 両ファイルの 6 つの許諾条件は同一構造
  - PR-02 で `model-routing.md` の追記節が完了済み (depends-on)
- **不変条件**:
  - 6 つの許諾条件 (DbC 完了 / cross-review / CI green / 観察事実 / scope / secret) の構造維持
  - 停止条件 / 取消条件は変更しない
  - reviewer 選定の別系列原則 (Anthropic ↔ OpenAI) は維持
- **完了条件**:
  - 両ファイルの cross-review 条件節に同一追記文言が入る
  - `diff` で cross-review 条項の本文 (frontmatter / 序文除く) が一致
  - markdown lint 通過
  - 既存 auto-merge 後の必須手順 (main 同期 / archive 移動) は維持
- **禁止事項**:
  - 許諾条件番号変更 (1-6 のまま)
  - secret 値の混入 (env 名のみ参照)
  - kind ラベル運用を許諾条件追加 (条件 7 化) として書く → 既存 6 条件の中の精緻化として書く
- **停止条件**:
  - 両ファイルで補記文言の解釈差が出る → 同一文言に揃え、解釈を `model-routing.md` に集約
  - `model-routing.md` 参照 link 切れ → 雛形と反映側の両方を参照する形に修正

## 検証

```sh
# (1) 両ファイル cross-review 条項 diff
diff <(grep -A 5 "cross-review" /home/otaku/agentops/AGENTS.md | head -20) \
     <(grep -A 5 "cross-review" /home/otaku/.claude/rules/auto-merge-permission.md | head -20)
# → cross-review 条項の本文が一致 (frontmatter / 表記差は許容)

# (2) markdown lint
markdownlint /home/otaku/agentops/AGENTS.md || true
```

## cross-review

PR-01 と同様に Codex review run B で実行。docs 整合性を design 観点で重点チェック (kind 運用 / model-routing.md 参照 / 既存 6 条件構造維持)。

## 反映側 (~/.claude/) の作業

`~/.claude/rules/auto-merge-permission.md` を直接編集。本 task PR には含めず、`~/.claude/.agentops/handoffs/2026-05-01-auto-merge-permission-sync.md` に反映済み確認メモ。

## plan 全体完了 archive

本 task が PR-04 として最後の task。merge 後:

1. `scripts/agentops archive task --task-id 04-agents-md-auto-merge-sync --dry-run` → 本番実行で task ファイルを `.agentops/archive/2026-05-01-claude-codex-orchestrator-rules/tasks/` へ移動
2. `scripts/agentops archive plan --plan-id 2026-05-01-claude-codex-orchestrator-rules --summary "Claude orchestrator + Codex 実装/cross-review 体制への運用ルール整備"` で plan 全体を archive 化、`archive/README.md` に新規 row 追加
3. `~/.claude/.agentops/handoffs/` 下の同期メモは plan 完了とともに `~/.claude/.agentops/archive/` 該当 dir へ移動 (rule: session-record-and-handoff)
