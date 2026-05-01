---
task-id: 04-catalog-docs-agent
plan-id: 2026-05-01-claude-coding-frontier-model-id-realign
status: approved
pr-number: (Step 7 で全 task 1 PR にまとめる予定)
depends-on: 03-catalog-coding-fast
---

# Task 04: `~/.claude/agentops/model-catalog.yml` の `docs_agent` に Codex secondary 新設 + `last_reviewed` 更新

## 目的

`docs_agent` ロールの candidates を `[claude/claude-sonnet-4-6 (primary), codex/gpt-5.3-codex (secondary)]` に再揃え。primary は日本語品質維持のため Sonnet 4.6 を据え、secondary に code 例を含む技術設計 docs 用途の Codex を新設する。本 task で catalog 全体の編集を完結させ、`last_reviewed: 2026-05-01` に更新する。

## 変更対象

- `/home/otaku/.claude/agentops/model-catalog.yml` (line 174-183 周辺、`docs_agent` セクション)
  - candidates 末尾に `codex/gpt-5.3-codex` (secondary) を新設
  - 既存 Sonnet 4.6 (primary) は順序維持
  - notes に「primary は日本語品質、secondary は code 例含む技術設計 docs 用途」反映
- header (line 1-10 周辺) の `last_reviewed` を `2026-05-01` に更新
- header コメントに「coding 系は Codex primary、cross-review 別系列、~/.claude/.agentops/ に変更同期 handoff」方針を追記 (parent plan §Scope 表参照)

## DbC

- **前提条件**:
  - Task 02 / 03 完了、`coding_frontier` / `coding_fast` 編集済み
  - `research_fast` (line 164-172) は無変更
- **不変条件**:
  - `docs_agent` primary (claude-sonnet-4-6) は順序維持 (日本語品質優先)
  - `research_fast` 無変更
  - `architect_frontier` / `review_frontier` / `orchestrator_frontier` 無変更
- **完了条件**:
  - `docs_agent` の candidates が `claude/claude-sonnet-4-6` (primary) → `codex/gpt-5.3-codex` (secondary)
  - `last_reviewed: 2026-05-01` に更新
  - header コメントに方針追記済み
  - `yaml.safe_load` exit 0
- **禁止事項**:
  - `research_fast` への Codex 候補追加 (parent plan §Non-Goals)
  - agentops repo source の `model_id:` 行編集
  - secret 値、私的環境変数値の混入
- **停止条件**:
  - yaml.safe_load 失敗 → 即 revert
  - `last_reviewed` 更新後に他ロール構造が壊れる → 即 revert、再調査

## 検証

```sh
# (1) yaml load
python3 -c "import yaml; yaml.safe_load(open('/home/otaku/.claude/agentops/model-catalog.yml'))"

# (2) 全ロール一覧確認
python3 -c "
import yaml, json
d = yaml.safe_load(open('/home/otaku/.claude/agentops/model-catalog.yml'))
print('last_reviewed:', d.get('last_reviewed'))
print(json.dumps({r['role']: [c['target_cli']+'/'+(c.get('model_id') or 'null') for c in r['candidates']] for r in d['roles']}, indent=2, ensure_ascii=False))
"
# → 期待値:
# last_reviewed: 2026-05-01
# coding_frontier: ['codex/gpt-5.5', 'claude/claude-opus-4-7']
# coding_fast: ['codex/gpt-5.3-codex', 'claude/claude-sonnet-4-6']
# docs_agent: ['claude/claude-sonnet-4-6', 'codex/gpt-5.3-codex']
# research_fast: ['claude/claude-sonnet-4-6']
# orchestrator_frontier / architect_frontier / review_frontier: 不変
```

## メモ

- 本 task で catalog 編集は完結。次は Task 05 (rules) / Task 06 (5 工程フロー) / Task 07 (source notes + docs)
