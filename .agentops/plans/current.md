---
plan-id: 2026-05-01-claude-coding-frontier-model-id-realign
status: approved
started: 2026-05-01T16:00:00+09:00
owner: claude
parent-plan-file: /home/otaku/.claude/plans/claude-gtp5-5-claude-snappy-zebra.md
---

# Plan: ~/.claude/agentops/model-catalog.yml の coding 系ロールを user 意図に再揃え + 設計段階 cross-review 導入

## 背景

ユーザー指摘「Claude グローバル設定でコーディングのモデルが GPT-5.5 になっていない」を裏取りした結果、`~/.claude/agentops/model-catalog.yml` の `coding_frontier` / `coding_fast` / `docs_agent` の Codex 候補 entry が 2026-04-28 の Phase B (Sonnet 4.6 baseline 化) trim によって意図せず削除されていたことが判明した。本 plan で user 意図表通りに再揃え、加えて再発防止として「**設計段階 cross-review (durable instructions)**」を 5 工程フローとして導入する。

詳細・観察事実・user 意図は parent plan file (`/home/otaku/.claude/plans/claude-gtp5-5-claude-snappy-zebra.md`) を参照。

## Goals (parent plan §Goals 1-8 サマリ)

1. `~/.claude/agentops/model-catalog.yml` の coding 系 3 ロールを user 意図表通りに編集 (`research_fast` は無変更)
2. agentops repo source (`config/model-catalog.yml`) は **全 model_id null 維持** (Trinity の template-source 層)
3. cross-review の Anthropic ↔ OpenAI 別系列原則を catalog 上で機械可読に維持
4. 別セッションで「Claude main 時の coding_frontier 委譲先」が `gpt-5.5` と返る
5. `~/.claude/rules/model-routing.md` で実 model id 確認先を反映先 catalog (`~/.claude/agentops/model-catalog.yml`) と明記
6. `~/.claude/rules/global-content-boundary.md` 例外節に「機械可読 spec (`*.yml` catalog) は固定値 OK」を追加
7. **設計段階 cross-review を durable instructions として導入** (5 工程フロー: 設計 → 設計レビュー → 実装 → 実装レビュー → 最終判断)
8. **本 plan 自体を高リスク事例として、Step 0.5 で Codex review_frontier (gpt-5.5) に設計段階 cross-review を委譲**

## 親 task 一覧

- `.agentops/tasks/01-design-cross-review.md` (Step 0.5 対応)
- `.agentops/tasks/02-catalog-coding-frontier.md` (Step 1 の coding_frontier 編集)
- `.agentops/tasks/03-catalog-coding-fast.md` (Step 1 の coding_fast 編集)
- `.agentops/tasks/04-catalog-docs-agent.md` (Step 1 の docs_agent 編集)
- `.agentops/tasks/05-rules-source-and-mirror.md` (Step 3: rules 編集 source + 反映先)
- `.agentops/tasks/06-design-cross-review-rule-extension.md` (Step 3.5: 5 工程フロー導入)
- `.agentops/tasks/07-source-notes-and-docs.md` (Step 2 + 4: source notes + docs/04 整合)
- `.agentops/tasks/08-impl-cross-review-and-merge.md` (Step 6 + 7: 実装後 cross-review + commit/PR/merge)

## 想定期間

1-2 セッション (半日 〜 1 日)。Step 0.5 設計レビューと Step 6 実装後 cross-review は別 session の Codex (gpt-5.5) に委譲するため、待ち時間込み。

## 完了条件

- 全 8 task の DbC 完了条件を満たす
- `~/.claude/agentops/model-catalog.yml` で coding_frontier=gpt-5.5 / coding_fast=gpt-5.3-codex / docs_agent secondary=gpt-5.3-codex に再揃え済み
- `~/.claude/rules/model-routing.md` / `~/.claude/rules/global-content-boundary.md` / `~/.claude/rules/high-risk-escalation.md` / `~/.claude/CLAUDE.md` および agentops repo source 側 rules / docs / AGENTS.md / CLAUDE.md に 5 工程フロー反映済み
- agentops PR (Step 7) が main にマージ済み (auto-merge 許諾条件 1-6 全件評価)
- main 同期 + archive 移動完了
- `~/.claude/.agentops/handoffs/2026-05-01-coding-frontier-model-id-realign.md` に反映 diff 記録

## 停止条件

- Step 0.5 設計レビューで Codex CLI (gpt-5.5) が起動しない、または kind: design 指摘が出る → user 確認
- 設計レビュー / 実装後 cross-review が 3 周到達 → 本 plan pause、user 確認
- yaml 編集後 `yaml.safe_load` 失敗 → 即停止、user 確認
- agentops source の `model_id:` 行に diff が出る → 即 revert (Trinity 違反)
- delegate dry-run が想定 model id を展開しない → user 確認
- secret / 本番 / 課金 / 外部公開 / 破壊的操作が必要になった場合
