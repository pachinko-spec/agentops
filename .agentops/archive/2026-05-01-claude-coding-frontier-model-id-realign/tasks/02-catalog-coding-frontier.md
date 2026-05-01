---
task-id: 02-catalog-coding-frontier
plan-id: 2026-05-01-claude-coding-frontier-model-id-realign
status: approved
pr-number: (Step 7 で全 task 1 PR にまとめる予定)
depends-on: 01-design-cross-review
---

# Task 02: `~/.claude/agentops/model-catalog.yml` の `coding_frontier` を Codex primary 復元

## 目的

`coding_frontier` ロールの candidates を user 意図表通り `[codex/gpt-5.5 (primary), claude/claude-opus-4-7 (escalation)]` に再揃えする。Sonnet 4.6 entry は削除し、Codex primary を復元することで「Claude main 時の coding 委譲先 = gpt-5.5」を機械可読 spec として確立する。

## 変更対象

- `/home/otaku/.claude/agentops/model-catalog.yml` (line 139-152 周辺、`coding_frontier` セクション)
  - candidates を `[codex/gpt-5.5 (primary), claude/claude-opus-4-7 (escalation)]` に
  - Sonnet 4.6 entry (line 146 周辺) は削除
  - notes に「Codex 主実装、Opus 4.7 は最高難度時のフォールバック」を反映
- `last_reviewed: 2026-05-01` への更新は Task 04 完了時に一括で行う (catalog 全体の最終編集箇所)

## DbC

- **前提条件**:
  - Task 01 (設計段階 cross-review) 完了、P0/P1=0
  - `/home/otaku/.claude/agentops/model-catalog.yml` の現状 line 139-152 が user 意図と乖離 (claude-sonnet-4-6 / claude-opus-4-7 のみ、Codex 候補 entry なし)
- **不変条件**:
  - cross-review 別系列原則を維持 (`review_frontier` の candidates 順序は変更しない)
  - `research_fast` ロールは無変更
  - resolution rule (line 26-29 周辺の「null は実行に使わない」記述) は触らない
- **完了条件**:
  - `coding_frontier` の candidates が `codex/gpt-5.5` (primary) → `claude/claude-opus-4-7` (escalation) の順に並ぶ
  - Sonnet 4.6 entry は `coding_frontier` セクションから消えている
  - `python3 -c "import yaml; yaml.safe_load(open('/home/otaku/.claude/agentops/model-catalog.yml'))"` が exit 0
- **禁止事項**:
  - agentops repo source (`/home/otaku/agentops/config/model-catalog.yml`) の `model_id:` 行を編集する (Trinity template-source 層、Task 07 で notes だけ追記)
  - `architect_frontier` / `review_frontier` / `orchestrator_frontier` の candidates 順序変更
  - secret 値、私的環境変数値の混入
- **停止条件**:
  - yaml.safe_load 失敗 → 即 revert、user 確認
  - 編集後の構造が想定 (parent plan §user 意図表) と一致しない → 即停止
  - Sonnet 4.6 削除に伴って他ロールの参照が壊れる (anchor / alias 利用が判明) → 即停止、構造再調査

## 検証

```sh
# (1) yaml load
python3 -c "import yaml; yaml.safe_load(open('/home/otaku/.claude/agentops/model-catalog.yml'))"

# (2) coding_frontier の primary 確認
python3 -c "
import yaml
d = yaml.safe_load(open('/home/otaku/.claude/agentops/model-catalog.yml'))
for r in d['roles']:
    if r['role'] == 'coding_frontier':
        print([c['target_cli'] + '/' + (c.get('model_id') or 'null') for c in r['candidates']])
"
# → ['codex/gpt-5.5', 'claude/claude-opus-4-7'] が出ること
```

## メモ

- 本 task 単独では `last_reviewed` を更新せず、Task 04 で catalog 編集を完結させる時に一括で `2026-05-01` に更新する
- 編集箇所は `~/.claude/agentops/model-catalog.yml` のみ。agentops repo source 側は Task 07 で notes 追記のみ
