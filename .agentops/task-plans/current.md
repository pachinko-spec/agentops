---
plan-id: 2026-05-01-claude-coding-frontier-model-id-realign
session-date: 2026-05-01
session-status: implementation-in-progress
next-action: step-0.5-design-cross-review
---

# task-plan: coding 系 model id 再揃え + 設計段階 cross-review 導入

## 今回セッション (2026-05-01) の作業

- parent plan file 取得・観察事実裏取り済 (`/home/otaku/.claude/plans/claude-gtp5-5-claude-snappy-zebra.md`)
- 作業 branch: `claude/2026-05-01-claude-coding-frontier-model-id-realign` (agentops repo 側、切替済)
- Step 0 (前準備): `.agentops/plans/current.md` / `task-plans/current.md` / `tasks/01-08` を agentops repo / `~/.claude/.agentops/` 双方に生成
- Step 0.5 以降は本 task-plan のフェーズ表に従う

## フェーズ・所要時間予測

| phase | 内容 | 担当 | 予測時間 |
|---|---|---|---|
| Step 0 | 前準備 (`.agentops/` 構造生成) | Claude | 15 min |
| Step 0.5 | 設計段階 cross-review 委譲 (`scripts/agentops delegate --to codex --role review_frontier --model gpt-5.5 --effort high --input <plan file>`)、所見反映、P0/P1=0 確認 | Codex (gpt-5.5) + Claude | 30-60 min |
| Step 1 | catalog 編集 (`~/.claude/agentops/model-catalog.yml` の coding_frontier / coding_fast / docs_agent、yaml.safe_load 検証) | Claude | 20-30 min |
| Step 2 | source notes 整合 (`config/model-catalog.yml` advisory notes、`model_id:` 行不変) | Claude | 15 min |
| Step 3 | rules 編集 (source + 反映先): `model-routing.md` 実 model id 参照先明記、`global-content-boundary.md` 例外節追記 | Claude | 20-30 min |
| Step 3.5 | 5 工程フロー導入: `model-routing.md` (source + 反映先) / `high-risk-escalation.md` (source + 反映先) / `AGENTS.md` / `CLAUDE.md` (agentops + 反映先) | Claude | 30-45 min |
| Step 4 | docs 整合 (`docs/04-model-routing.md`) | Claude | 15 min |
| Step 5 | 検証 (yaml load / delegate dry-run / grep / docs 整合) | Claude | 20-30 min |
| Step 6 | 実装後 cross-review 委譲 (Codex review_frontier、agentops PR 差分対象)、所見反映、P0/P1=0 確認 | Codex (gpt-5.5) + Claude | 30-60 min |
| Step 7 | commit / PR / auto-merge 許諾条件 1-6 評価 / merge / main 同期確認 / archive 移動 | Claude | 30-45 min |
| Step 8 | グローバル handoff 記録 (`~/.claude/.agentops/handoffs/2026-05-01-coding-frontier-model-id-realign.md`) | Claude | 15 min |

合計予測: 4-6 時間 (1 セッション完了が目標、伸びれば 2 セッション)

## 注意点

- 各 task は単一スコープ厳守 (auto-merge 許諾条件 5)
- Step 0.5 / Step 6 の cross-review は別系列 frontier reviewer (Codex / gpt-5.5)、Claude 主 orchestrator と context 共有しない
- `~/.claude/` 配下変更は repo 管理外 → PR には含めず Step 8 で handoff 記録
- secret 値 (API key / token / Webhook URL) を diff / log / PR / handoff に出さない、env 名のみ参照
- agentops source の `model_id:` 行は Trinity template-source 層のため絶対に値を入れない (notes のみ追記)

## 現セッション残作業

Step 0.5 以降。本 task-plan のフェーズ順に進行。
