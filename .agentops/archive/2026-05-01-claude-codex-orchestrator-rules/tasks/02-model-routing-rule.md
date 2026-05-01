---
task-id: 02-model-routing-rule
plan-id: 2026-05-01-claude-codex-orchestrator-rules
status: approved
pr-number: PR-02
depends-on: 01-delegate-prompt-template
---

# Task 02: model-routing rule 雛形作成 + 反映側 3 工程フロー追加

## 目的

`rules/model-routing.md` を agentops repo 配下に新規作成し (現在は反映先 `~/.claude/rules/` にしか存在しない)、雛形と反映側で「実装 run A / review run B / kind 分岐」3 工程フローを揃える。

## 変更対象

- `/home/otaku/agentops/rules/model-routing.md` (**新規作成**)
  - 既存反映側 `~/.claude/rules/model-routing.md` 全文を雛形側に取り込み
  - 末尾に「## 実装 → レビュー → 分岐フロー」節を追加 (3 工程 + kind 分岐表)
- `/home/otaku/.claude/rules/model-routing.md` (反映側、line 42 末尾)
  - 雛形と同一の追記節を反映 (手動同期)
- 必要なら `rules/catalog.md` の model-routing 参照を更新

## 追記節の内容

```md
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
```

## DbC

- **前提条件**:
  - `~/.claude/rules/model-routing.md` (line 1-42) が現状の 7 ロール定義 + 2 工程 cross-review フローのみ記述
  - `agentops/rules/` に既存 `catalog.md` / `README.md` のみ存在
- **不変条件**:
  - 既存 7 論理ロール定義は変更しない (orchestrator_frontier / architect_frontier / review_frontier / coding_frontier / coding_fast / research_fast / docs_agent)
  - `--effort high` 既定 / cross-review 委譲 wrapper 例 (`scripts/agentops delegate ...`) は維持
- **完了条件**:
  - `agentops/rules/model-routing.md` 新規作成、雛形として `applies-to: global` frontmatter 付き
  - `~/.claude/rules/model-routing.md` の末尾に同一追記節
  - `diff /home/otaku/agentops/rules/model-routing.md /home/otaku/.claude/rules/model-routing.md` で frontmatter / paths 以外は同一
  - `rules/catalog.md` で model-routing が参照されていれば link 確認
  - markdown lint 通過
- **禁止事項**:
  - 既存 ロール定義 / wrapper 例の破壊的変更
  - paths / frontmatter 重複定義
- **停止条件**:
  - 雛形作成に伴い他 rule の雛形化波及が必要 → 本 task は model-routing.md だけに限定、他は別 plan
  - 反映側手動同期に失敗 (Claude Code 再起動後 context 反映されず) → `/memory` 確認、必要なら paths frontmatter 確認

## 検証

```sh
# (1) 雛形と反映側の同期確認
diff <(grep -v "^---$\|^name:\|^description:\|^paths:" /home/otaku/agentops/rules/model-routing.md) \
     <(grep -v "^---$\|^name:\|^description:\|^paths:" /home/otaku/.claude/rules/model-routing.md)
# → frontmatter 以外は同一であること

# (2) 反映側 context load 確認
# Claude Code 再起動後、新セッションで /memory にて model-routing.md の追記節が表示されることを確認
```

## cross-review

PR-01 と同様に Codex review run B で実行、P0/P1 ゼロまで対応。

## 反映側 (~/.claude/) の作業

`~/.claude/rules/model-routing.md` 末尾に追記節を手動で書き写す。本 task PR には含めず、`~/.claude/.agentops/handoffs/2026-05-01-model-routing-sync.md` に反映済み確認メモを残す。
