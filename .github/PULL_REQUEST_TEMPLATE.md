<!--
agentops PR template (P1-07)
docs/03-dbc-and-quality-gates.md の DbC 5 条件を最低限満たすチェックリスト。
不要セクションは削除して構いません。
-->

## 概要

<!-- このPRが解決する課題と、採用したアプローチを 2-3 行で。 -->

## DbC

- **前提条件**: <!-- 触ってよい範囲 / 事前確認 / 業界出典 -->
- **不変条件**: <!-- 触らない範囲 / 維持すべき性質 -->
- **完了条件**: <!-- 何が満たされたら done か -->
- **禁止事項**: <!-- main 直 push、secret 値書込み、責務混同 など -->
- **停止条件**: <!-- 何が起きたら user 確認に戻すか -->

## 検証コマンド

```bash
# 例（実際に走らせたものを書く）
python3 -m compileall tools
python3 -m unittest discover -s tests
```

## Codex cross-review

<!-- 該当する場合のみ。AI auto-merge 許諾条件 #2 が要求 -->

- Round 1: `.agentops/runs/<timestamp>-<task-id>-r1/` / `.agentops/reviews/<task>.md` 反映済み
- Round 2: clean 確認
- Round 3: `no further P0/P1` 確認

## auto-merge 許諾条件 (CLAUDE.md §許諾条件)

該当 PR が以下を満たす場合のみ、`gh pr merge --squash --delete-branch` で AI auto-merge 可能。

- [ ] DbC 完了
- [ ] Codex cross-review 通過 (P0/P1 = 0、または反映済み)
- [ ] CI green (actionlint / yamllint / markdown-link-check)
- [ ] 観察事実食い違いなし
- [ ] PR スコープ単一
- [ ] secret 未混入

## 未解決リスク / 申し送り

<!-- 次セッション / 次 plan へ繰越す観察事実があれば。`.agentops/handoffs/` 候補も。 -->
