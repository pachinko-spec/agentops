---
task-id: 06-design-cross-review-rule-extension
plan-id: 2026-05-01-claude-coding-frontier-model-id-realign
status: approved
pr-number: (Step 7 で全 task 1 PR にまとめる予定)
depends-on: 05-rules-source-and-mirror
---

# Task 06: 5 工程フロー導入 (設計段階 cross-review durable instruction 化、Step 3.5 対応)

## 目的

parent plan §Goals 7 / §Step 3.5 に対応。現行「実装 → レビュー → 分岐フロー」(4 工程) を「**設計 → 設計レビュー → 実装 → 実装レビュー → 最終判断**」(5 工程) に拡張し、設計段階 cross-review の発動条件を durable instructions として明記する。rules / docs / AGENTS.md / CLAUDE.md の該当節を source + 反映先双方で更新する。

## 変更対象

- `/home/otaku/agentops/rules/model-routing.md` (source、「実装 → レビュー → 分岐フロー」節)
  - 5 工程フロー table に拡張: 工程 1 設計 (Claude orchestrator) / 工程 2 設計レビュー (Codex review_frontier、新設) / 工程 3 実装 (Codex coding_frontier) / 工程 4 実装レビュー (Codex review_frontier、別 session) / 工程 5 最終判断 (Claude)
  - 発動条件を明記: 高リスク plan (durable instructions / catalog / AGENTS.md / global rules / migration / security / public API / 課金 / deploy 影響)。軽微 plan (typo / docs 単純追記) は任意
  - kind 分岐 / ループカウント / 3 周ループ防止は既存「実装後 cross-review」と共通仕様であることを明記
- `/home/otaku/.claude/rules/model-routing.md` (反映先) — 同等変更
- `/home/otaku/.claude/rules/high-risk-escalation.md` (反映先) — 「設計段階 cross-review が高リスク plan で必須」を 1 行追加。agentops source 側に同名 rule は未存在のため触らない
- `/home/otaku/agentops/AGENTS.md` (auto-merge 許諾文脈) — 「設計段階 cross-review (高リスク plan で必須)」を 1 段落追記。実装後 cross-review (条件 2) と並ぶ柱として位置づけ
- `/home/otaku/agentops/CLAUDE.md` (Claude 固有差分があれば) — 必要に応じて追記
- `/home/otaku/.claude/CLAUDE.md` (反映先) — 同等変更

## DbC

- **前提条件**:
  - Task 05 完了、rules の実 model id 参照先記述が同期済み
  - 既存 4 工程フロー table が source / 反映先双方に存在
- **不変条件**:
  - kind 分岐仕様 (mechanical / design ラベル + 3 周ループ防止) は既存仕様維持
  - 7 論理ロール定義は触らない
  - auto-merge 許諾条件 1-6 の文言 (実装後 cross-review 条件 2) は触らない、設計段階 cross-review は **追記** で並ぶ柱として導入
- **完了条件**:
  - source / 反映先 `model-routing.md` で 5 工程フロー table + 発動条件明記が同期
  - 反映先 `~/.claude/rules/high-risk-escalation.md` で「設計段階 cross-review 必須」1 行追記
  - `agentops/AGENTS.md` / `agentops/CLAUDE.md` / `~/.claude/CLAUDE.md` で auto-merge 許諾文脈に設計段階 cross-review 段落追記
  - parent plan §Verification の `grep -nR "設計レビュー\|設計段階 cross-review\|5 工程"` で全対象ファイルが hit
- **禁止事項**:
  - 既存 auto-merge 許諾条件 1-6 の文言改変 (条文番号変更を含む)
  - kind 分岐 / ループカウント仕様の変更
  - 本文 markdown に固定 model id の新規流入
  - secret 値混入
- **停止条件**:
  - 5 工程フロー table の解釈差で source / 反映先が同期できない → user 確認、文言統一
  - auto-merge 許諾条件 1-6 との関係性 (条件 2 と独立か AND か) で解釈分岐 → user 確認、文言確定
  - レビュー修正が 2 周を超える → handoff 作成

## 検証

```sh
# (1) 5 工程フロー反映確認
grep -nR "設計レビュー\|設計段階 cross-review\|5 工程" \
  /home/otaku/.claude/rules/model-routing.md \
  /home/otaku/.claude/rules/high-risk-escalation.md \
  /home/otaku/agentops/rules/model-routing.md \
  /home/otaku/agentops/AGENTS.md \
  /home/otaku/agentops/CLAUDE.md \
  /home/otaku/.claude/CLAUDE.md

# (2) source と反映先の同期確認
diff <(grep -v "^---$\|^name:\|^description:\|^paths:" /home/otaku/agentops/rules/model-routing.md) \
     <(grep -v "^---$\|^name:\|^description:\|^paths:" /home/otaku/.claude/rules/model-routing.md)
```

## メモ

- 本 task と Task 05 はファイルが重複するため、Task 05 → Task 06 の順序を厳守し、commit / patch を分けて適用する
- 本 plan 自体が「設計段階 cross-review 初回発動例」となるため、Task 01 で実施した Codex 委譲記録 (`~/.claude/.agentops/runs/<run_id>/`) が docs / handoff の reference になる
