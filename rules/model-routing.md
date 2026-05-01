---
name: model-routing
description: 論理ロール 7 種 (orchestrator / architect / review / coding (frontier+fast) / research / docs)、cross-review reviewer の別系列選定、`scripts/agentops delegate` の wrapper 使用、`.agentops/runs/` への記録、実装 → レビュー → 分岐フロー (kind: mechanical | design)。
applies-to: global
---

# クロスモデル委譲とモデルルーティング

## 論理ロール

モデルカタログ（[`config/model-catalog.yml`](file:///home/otaku/agentops/config/model-catalog.yml)）の論理ロールで指定し、実 model id は使用直前に公式 docs と CLI の現在仕様で確認する。

| ロール | 用途 |
|---|---|
| `orchestrator_frontier` | 複雑タスクの分解、委譲計画、統合判断、停止条件判断 |
| `architect_frontier` | 複雑な設計、アーキテクチャ判断、ハイリスク実装方針 |
| `review_frontier` | 設計レビュー、コードレビュー、セキュリティ観点、cross-review |
| `coding_frontier` | 通常実装、難所の修正 |
| `coding_fast` | typo、軽微修正、レビュー後の小修正 |
| `research_fast` | コード調査、docs 調査、差分整理 |
| `docs_agent` | docs 更新、PR 本文、ハンドオフ整備 |

## cross-review

- 高リスク変更、新機能、リファクタ、依存追加、API 契約変更、デプロイ影響、レビュー修正後は cross-review を検討する。
- 主 orchestrator とは **別系列、別 CLI、別モデルファミリー** の `review_frontier` を候補にする。
  - 主 orchestrator が Claude Code（Anthropic 系）→ reviewer は Codex / OpenAI 系
  - 主 orchestrator が Codex（OpenAI 系）→ reviewer は Claude Code / Anthropic 系
  - 片方の CLI が使えない場合は同 CLI 内で別モデルファミリー、別ロール、別コンテキストの reviewer
- 共通 wrapper:

  ```sh
  /home/otaku/agentops/scripts/agentops delegate \
    --to codex --role review_frontier --effort high --input <file>
  ```

  `--effort` は AI auto-merge 許諾条件と整合するため `high` を既定とする。コスト・レイテンシで下げる場合のみ調整、難所では `xhigh` へ昇格。

- 委譲依頼、進捗、stdout / stderr、結果は `~/.claude/.agentops/runs/<run_id>/` に残す（`request.md` / `status.json` / `stdout.log` / `stderr.log` / `result.md` / `artifacts/`）。
- reviewer の所見は参考情報。採否、修正範囲、延期、統合判断はメインエージェントが持つ。

実行手順は skill `cross-model-delegate` / `cross-review` を参照。

## 実装 → レビュー → 分岐フロー

main session が Claude Code の場合の標準フロー:

| 工程 | 担当 | 用途 |
|---|---|---|
| 設計 / 計画 / 調査 | Claude (orchestrator_frontier) | user 意図汲み、harness spec、stop conditions |
| 実装 (run A) | Codex (coding_frontier) | コード + test 生成 + test 実行 |
| cross-review (run B) | Codex (review_frontier、別 session) | 独立性確保、kind ラベル付与 |
| 成果物チェック / 最終判断 | Claude | diff + test result + cross-review 結果 (3 点セット) で判定 |

cross-review reviewer は修正指摘ごとに `kind: mechanical | design` ラベルを付与する:

- `kind: mechanical` (patch / 行番号 / 具体書き換え提示) → Claude が直接 patch 適用、ループ +1
- `kind: design` (抽象指摘、判断要) → Codex (run A) に再委譲、ループ +1

ループカウントは修正者問わず +1。3 周目到達 → kind 不問で user 確認。kind ラベル無し → 保守的に `design` 扱い。

reviewer 出力期待値 (kind ラベル / unified diff / `artifacts/review.md` 保存) は `scripts/agentops delegate --to <reviewer> --role review_frontier` 実行時に wrapper が自動付与する。詳細は `docs/10-cli-wrapper.md` の `## Reviewer 出力期待値 (review_frontier)` 節を参照。
