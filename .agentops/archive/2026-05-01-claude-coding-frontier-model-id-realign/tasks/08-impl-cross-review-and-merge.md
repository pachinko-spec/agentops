---
task-id: 08-impl-cross-review-and-merge
plan-id: 2026-05-01-claude-coding-frontier-model-id-realign
status: approved
pr-number: (本 task で確定)
depends-on: 07-source-notes-and-docs
---

# Task 08: 実装後 cross-review (Step 6) + commit / PR / merge / archive (Step 7) + グローバル handoff (Step 8)

## 目的

parent plan §Step 6 / §Step 7 / §Step 8 を一括で扱う最終 task。

1. **Step 6**: agentops PR 差分 (Task 02-07 のうち agentops repo に commit する分) を Codex review_frontier (gpt-5.5) に cross-review 委譲、所見 P0/P1=0 を確認
2. **Step 7**: commit / PR 作成 / auto-merge 許諾条件 1-6 評価 / `gh pr merge --squash --delete-branch` / main 同期 / archive
3. **Step 8**: `~/.claude/.agentops/handoffs/2026-05-01-coding-frontier-model-id-realign.md` に反映 diff 記録

## 変更対象

- `claude/2026-05-01-claude-coding-frontier-model-id-realign` branch から PR 作成
- PR 内容: agentops repo 側変更のみ (Task 05 source rules / Task 06 source rules + AGENTS.md + CLAUDE.md / Task 07 config notes + docs/04 + `.agentops/`)
- `~/.claude/` 側変更 (catalog / 反映先 rules / 反映先 CLAUDE.md) は PR 対象外、Step 8 で handoff 記録
- `.agentops/runs/<run_id>/` に Codex cross-review 委譲記録
- マージ後 `scripts/agentops archive task` で各 task md を archive へ移動、`scripts/agentops archive plan` で plan 全体 archive

## 実行コマンド (要点)

```sh
# (1) cross-review 委譲 (Step 6)
scripts/agentops delegate \
  --to codex --role review_frontier --effort high \
  --input <PR 差分ファイル一覧 or unified diff>

# (2) commit / PR
git add -A
git commit -m "..."
git push -u origin claude/2026-05-01-claude-coding-frontier-model-id-realign
gh pr create --title "..." --body "..."

# (3) auto-merge 許諾条件 1-6 評価 → 満たすなら
gh pr merge --squash --delete-branch <PR-URL>

# (4) main 同期 + archive
git checkout main && git fetch origin && git pull --ff-only origin main
scripts/agentops archive task --task-id <basename> --dry-run  # 各 task で
scripts/agentops archive plan --plan-id 2026-05-01-claude-coding-frontier-model-id-realign --summary "..."

# (5) Step 8 グローバル handoff
# /home/otaku/.claude/.agentops/handoffs/2026-05-01-coding-frontier-model-id-realign.md に反映 diff を記録
```

## DbC

- **前提条件**:
  - Task 02-07 完了、catalog / rules / docs / AGENTS.md / CLAUDE.md 編集済み (source + 反映先双方)
  - Task 01 (設計段階 cross-review) P0/P1=0 完了済み
  - parent plan §Verification 全項目通過済み (yaml load / delegate dry-run / grep / docs 整合)
- **不変条件**:
  - PR スコープは本 plan の変更のみ (auto-merge 許諾条件 5)
  - 主 orchestrator (Claude) と reviewer (Codex) は別系列 (許諾条件 2)
  - secret 値が diff / commit message / PR 本文 / run log / handoff に混入しない (許諾条件 6)
- **完了条件**:
  - `.agentops/runs/<run_id>/result.md` に Codex cross-review 所見 + kind ラベル + P0/P1=0
  - PR 作成済み、CI green (許諾条件 3)
  - auto-merge 許諾条件 1-6 全件評価結果が PR 本文 or `.agentops/reviews/` に記録
  - 条件全 AND 成立なら `gh pr merge --squash --delete-branch` 実行、main 同期確認まで完了
  - 条件未満なら user 確認 (停止条件)
  - 完了 task md が `.agentops/archive/<plan-id>/tasks/` に移動
  - plan 全体完了時は `scripts/agentops archive plan` で archive/README.md table 更新
  - `~/.claude/.agentops/handoffs/2026-05-01-coding-frontier-model-id-realign.md` に反映 diff 記録、agentops PR-XX と紐付け
- **禁止事項**:
  - PR スコープ外リファクタの混入 (許諾条件 5 違反)
  - secret 値の混入 (許諾条件 6 違反)
  - `main` への直接 push、force push、`git reset --hard` 等の破壊的操作
  - `~/.claude/` 配下を PR に含める (git 管理外、handoff 記録で代替)
  - kind: design 指摘を Claude が独断で反映 (Codex run A への再委譲が必須)
- **停止条件**:
  - cross-review 所見に P0 / P1 が残る → auto-merge 停止、user 確認 (parent plan §停止条件)
  - レビュー修正が 2 周を超える / 3 周目到達 → handoff 作成、user 確認
  - `git pull --ff-only origin main` 失敗、CI fail、同期不整合 → 停止
  - 観察事実食い違い、L コスト超過 → 停止
  - 公式仕様確認が必要 → 停止
  - secret / 本番 / 課金 / 外部公開 / 破壊的操作が必要 → 停止

## 検証

```sh
# (1) cross-review 完了確認
ls ~/.claude/.agentops/runs/ | tail -3  # or /home/otaku/agentops/.agentops/runs/
cat <run_dir>/result.md | grep -E "kind:\s*(mechanical|design)"
grep -cE "^(P0|P1):" <run_dir>/result.md  # = 0

# (2) PR / CI / merge
gh pr view --json state,mergeStateStatus,statusCheckRollup
git log --oneline origin/main..HEAD  # マージ前
git checkout main && git fetch origin && git pull --ff-only origin main  # マージ後

# (3) archive 確認
ls /home/otaku/agentops/.agentops/archive/2026-05-01-claude-coding-frontier-model-id-realign/

# (4) グローバル handoff 記録
ls /home/otaku/.claude/.agentops/handoffs/2026-05-01-coding-frontier-model-id-realign.md
```

## メモ

- 本 plan は durable instructions 編集 + catalog 編集の高リスク変更のため、auto-merge 許諾条件 2 (cross-review 通過) を厳格に評価する
- 連続 auto-merge ではなく単一 PR にまとめる方針 (Task 02-07 を 1 PR、auto-merge 許諾条件は 1 回評価)
- `~/.claude/` 配下変更は repo 管理外のため PR に含めず、Step 8 (本 task) で handoff 記録に集約
