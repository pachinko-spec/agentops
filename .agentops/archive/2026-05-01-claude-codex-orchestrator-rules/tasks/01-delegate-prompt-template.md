---
task-id: 01-delegate-prompt-template
plan-id: 2026-05-01-claude-codex-orchestrator-rules
status: approved
pr-number: PR-01
---

# Task 01: agentops delegate prompt template 拡張 (kind ラベル + patch 形式)

## 目的

`scripts/agentops delegate --to codex --role review_frontier` 実行時に、Codex reviewer 出力に以下を期待する prompt を組み込む:

- 修正指摘ごとに `kind: mechanical | design` ラベルを付与
- `mechanical` の場合は unified diff patch を併記 (Claude が `git apply` できる形式)
- `design` の場合は抽象指摘のみで OK
- すべての出力を `artifacts/review.md` に保存

## 変更対象

- `/home/otaku/agentops/tools/agentops_cli/__main__.py` `build_request` (line 164-180)
  - `--role review_frontier` のとき prompt 末尾に「reviewer 出力期待値」セクションを追加
  - 他 role (coding_frontier 等) は変更なし
- `/home/otaku/agentops/docs/10-cli-wrapper.md`
  - 「reviewer 出力期待値」セクション追加 (kind ラベル定義 / patch 形式 / artifacts/review.md)

## DbC

- **前提条件**: `tools/agentops_cli/__main__.py:164-180` の build_request が `role` 引数を持ち、`--role review_frontier` を受け取れること (現状確認済み)
- **不変条件**: 既存 role (coding_frontier / coding_fast / orchestrator_frontier 等) の prompt 出力は変更しない
- **完了条件**:
  - `python3 -c "from tools.agentops_cli.__main__ import build_request; print(build_request(role='review_frontier', ...))"` で reviewer 出力期待値が prompt 末尾に含まれる
  - `--role coding_frontier` の prompt は従来通り (差分なし)
  - docs/10 に該当節が追加され markdown lint 通過
  - `python3 -m compileall tools/` exit 0
- **禁止事項**:
  - 既存 prompt 構造の破壊的変更 (header / meta lines / `## Task` セクションは維持)
  - effort / model 取り扱いロジック変更
  - secret 値の prompt 混入
- **停止条件**:
  - Codex CLI 側で出力期待値を完全無視する観察 → docs にだけ書き Claude 読解で吸収する fallback に切替
  - prompt 拡張が他 role に影響 → role 分岐を明確化、coding_frontier prompt は不変保証

## 検証

```sh
# (1) prompt 出力確認 (dry run)
echo "test review target" > /tmp/review-input.md
scripts/agentops delegate --to codex --role review_frontier --effort high --input /tmp/review-input.md --dry-run
# → 生成される request.md に「reviewer 出力期待値」が含まれることを目視確認

# (2) coding_frontier 不変確認
scripts/agentops delegate --to codex --role coding_frontier --effort high --input /tmp/review-input.md --dry-run
# → 「reviewer 出力期待値」が含まれないことを確認

# (3) 自己検証
python3 -m compileall tools/
```

## cross-review

`scripts/agentops delegate --to codex --role review_frontier --effort high --input <該当 PR diff>` を別 session (run_id B) で実行、kind ラベル + patch 形式で結果取得 → P0/P1 ゼロまで対応。

## 反映側 (~/.claude/) の作業

なし (本 task は agentops repo 内のみ)。
