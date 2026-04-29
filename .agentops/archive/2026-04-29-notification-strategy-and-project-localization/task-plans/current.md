---
session: 2026-04-29
parent-plan: ../plans/current.md
status: in-progress
---

# Task Plan: 通知戦略 + ローカライズ docs 整備 (本セッション)

## 今回セッションの実行順

1. **task 01 (PR-B B-1)** を先行 — 既存 docs/06, 11 と整合させる editing が中心。新規 docs/18 + templates 1 件 + catalog 3 行追加 + ~/.claude/CLAUDE.md +5 行以内
2. task 01 ローカル検証 → archive 移動 → commit → push → PR-B 作成 → cross-review 依頼
3. PR-B レビュー結果待ちの間に **task 02 (PR-C)** を別ブランチで先行
4. PR-B マージ → main 同期 → PR-C ブランチを最新化 → push → PR-C 作成 → cross-review

## 想定時間

- task 01: 60 分 (新規 docs/18 が中核、catalog 3 ファイル + 17-cross-reference.md 整合)
- task 02: 90 分 (新規 docs/19 が中核、4 戦略意思決定木 + 既存 5 プロジェクト dry-run 表)
- レビュー / cross-review: 各 30 分

## branch / PR

- task 01: `claude/notification-strategy-discord-2026-04-29` (現ブランチ)
- task 02: `claude/project-localization-design-2026-04-29` (task 01 マージ後に作成)

## 検証コマンド

```sh
# markdown-link-check (CI と同等)
npx markdown-link-check docs/18-notification-strategy.md docs/11-monitoring-cli.md docs/06-freshness-and-monitoring.md docs/17-cross-reference.md

# envvar 残存確認
grep -rn "AGENTOPS_DISCORD_WEBHOOK_URL" docs/ rules/ skills/ workflows/ templates/ scripts/ tools/ 2>/dev/null | grep -v deprecated

# 行数チェック
wc -l ~/.claude/CLAUDE.md

# cross-review
scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/18-notification-strategy.md
```

## 完了条件

- task 01 / 02 の DbC 完了
- 各 PR が cross-review 通過 + auto-merge 許諾条件全て満たす
