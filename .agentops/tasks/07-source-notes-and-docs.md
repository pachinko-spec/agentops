---
task-id: 07-source-notes-and-docs
plan-id: 2026-05-01-claude-coding-frontier-model-id-realign
status: approved
pr-number: (Step 7 で全 task 1 PR にまとめる予定)
depends-on: 06-design-cross-review-rule-extension
---

# Task 07: agentops source `config/model-catalog.yml` notes 整合 + `docs/04-model-routing.md` 整合 (Step 2 + 4 対応)

## 目的

parent plan §Step 2 (source notes 整合) + §Step 4 (docs 整合) を一括で扱う。agentops repo source (`config/model-catalog.yml`) の advisory notes に「2026-05-01 採用例」段落を追記し、`docs/04-model-routing.md` 行 72-77 周辺には 2026-05-01 更新分の参照先として反映先 catalog を示す。`model_id:` 行は **絶対に触らない** (Trinity template-source 層)。docs の「実装 → レビュー → 分岐フロー」相当節も 5 工程に拡張する。

## 変更対象

- `/home/otaku/agentops/config/model-catalog.yml`
  - 該当ロール (`coding_frontier` / `coding_fast` / `docs_agent`) の notes に「2026-05-01 採用例 (advisory)」段落追記
  - `model_id:` 行は不変 (全 null 維持)
- `/home/otaku/agentops/docs/04-model-routing.md`
  - 行 72-77 周辺の採用例 advisory に「2026-05-01 更新分は反映先 catalog (`~/.claude/agentops/model-catalog.yml`) の `coding_frontier` / `coding_fast` / `docs_agent` を参照」と追記し、新規 model id は docs 本文に直接書かない
  - 旧採用例 (2026-04-28) は archive 接続のため日付付きで保持
  - 「実装 → レビュー → 分岐フロー」相当節を 5 工程に拡張、発動条件 (高リスク plan) を docs 化

## DbC

- **前提条件**:
  - Task 06 完了、5 工程フロー rules / AGENTS.md 反映済み
  - `git diff config/model-catalog.yml` 着手前は空
- **不変条件**:
  - `config/model-catalog.yml` の `model_id:` 行は全 null 維持 (Trinity template-source 層)
  - `docs/04-model-routing.md` の旧採用例 (2026-04-28) は削除せず日付付きで保持 (archive 接続)
  - 7 論理ロール定義は触らない
- **完了条件**:
  - `config/model-catalog.yml` の `coding_frontier` / `coding_fast` / `docs_agent` notes に「2026-05-01 採用例」段落が追記
  - `git diff config/model-catalog.yml | grep -E '^[+-]\s+model_id:'` が空
  - `docs/04-model-routing.md` 行 72-77 周辺に 2026-05-01 更新分の catalog 参照を追記、5 工程フロー節拡張
  - markdown lint / yaml load 通過
- **禁止事項**:
  - `config/model-catalog.yml` の `model_id:` 行に値を入れる (Trinity 違反)
  - 旧採用例 (2026-04-28) の削除
  - 本文 markdown / docs に 2026-05-01 更新分の固定 model id を直接埋める。旧 2026-04-28 採用例は historical record として保持する
  - secret 値混入
- **停止条件**:
  - `git diff config/model-catalog.yml` で `model_id:` 行差分が出る → 即 revert、Trinity 違反として停止
  - yaml.safe_load 失敗 → 即 revert
  - docs 5 工程節と rules 5 工程節 (Task 06) で文言乖離 → 文言統一

## 検証

```sh
# (1) source の model_id: 行不変確認 (Trinity 違反検出)
git -C /home/otaku/agentops diff config/model-catalog.yml | grep -E '^[+-]\s+model_id:'
# → 出力が空であること

# (2) source yaml load
python3 -c "import yaml; yaml.safe_load(open('/home/otaku/agentops/config/model-catalog.yml'))"

# (3) docs 整合
grep -n "coding_frontier\|coding_fast\|docs_agent\|2026-05-01" /home/otaku/agentops/docs/04-model-routing.md
grep -n "5 工程\|設計レビュー\|設計段階 cross-review" /home/otaku/agentops/docs/04-model-routing.md
```

## メモ

- 本 task は agentops repo の docs / source notes 整合を完結させる。`~/.claude/` 側 docs は touch しない (グローバル側 docs ファイルは存在しない)
- Task 08 で実装後 cross-review + commit / PR / merge に進む
