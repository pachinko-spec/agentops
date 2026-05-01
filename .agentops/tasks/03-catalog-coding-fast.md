---
task-id: 03-catalog-coding-fast
plan-id: 2026-05-01-claude-coding-frontier-model-id-realign
status: approved
pr-number: (Step 7 で全 task 1 PR にまとめる予定)
depends-on: 02-catalog-coding-frontier
---

# Task 03: `~/.claude/agentops/model-catalog.yml` の `coding_fast` に Codex primary 新設

## 目的

`coding_fast` ロールの candidates を `[codex/gpt-5.3-codex (primary), claude/claude-sonnet-4-6 (secondary)]` に再揃え。coding-optimized な Codex を primary に据え、Sonnet 4.6 (1M ctx baseline) を secondary に降格する。

## 変更対象

- `/home/otaku/.claude/agentops/model-catalog.yml` (line 154-162 周辺、`coding_fast` セクション)
  - candidates 先頭に `codex/gpt-5.3-codex` (primary) を新設
  - 既存 Sonnet 4.6 entry (line 161 周辺) を secondary に降格 (順序を後ろへ)
  - notes に「Codex は coding-optimized、Sonnet は 1M ctx baseline」反映

## DbC

- **前提条件**:
  - Task 02 完了、`coding_frontier` セクション編集済み
  - `~/.codex/models_cache.json` で `gpt-5.3-codex` が listable (2026-05-01 確認済み)
- **不変条件**:
  - cross-review 別系列原則 (`review_frontier` 不変) を維持
  - `research_fast` / `architect_frontier` / `orchestrator_frontier` の構造は触らない
  - resolution rule (null は実行に使わない) は維持
- **完了条件**:
  - `coding_fast` の candidates が `codex/gpt-5.3-codex` (primary) → `claude/claude-sonnet-4-6` (secondary) の順
  - `yaml.safe_load` exit 0
- **禁止事項**:
  - agentops repo source (`config/model-catalog.yml`) の `model_id:` 行編集 (Trinity 違反)
  - Sonnet 4.6 entry の **削除** (secondary として残す、primary 降格のみ)
  - secret 値、私的環境変数値の混入
- **停止条件**:
  - yaml.safe_load 失敗 → 即 revert、user 確認
  - `gpt-5.3-codex` が `~/.codex/models_cache.json` の listable から外れた (2026-05-01 後の cache 更新で消えた) → 即停止、user 確認 (gpt-5.4 / gpt-5.4-mini への降格判断は Non-Goal、別 plan)

## 検証

```sh
# (1) yaml load
python3 -c "import yaml; yaml.safe_load(open('/home/otaku/.claude/agentops/model-catalog.yml'))"

# (2) coding_fast の primary 確認
python3 -c "
import yaml
d = yaml.safe_load(open('/home/otaku/.claude/agentops/model-catalog.yml'))
for r in d['roles']:
    if r['role'] == 'coding_fast':
        print([c['target_cli'] + '/' + (c.get('model_id') or 'null') for c in r['candidates']])
"
# → ['codex/gpt-5.3-codex', 'claude/claude-sonnet-4-6'] が出ること
```

## メモ

- 実 CLI 起動テスト (Step 5) で `codex exec --model gpt-5.3-codex` が起動できなければ user 確認 escalate
- gpt-5.3-codex-spark / gpt-5.4 / gpt-5.4-mini / gpt-5.2 は今回 catalog 採用しない (parent plan §Non-Goals)
