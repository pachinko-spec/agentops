---
task-id: 05-rules-source-and-mirror
plan-id: 2026-05-01-claude-coding-frontier-model-id-realign
status: approved
pr-number: (Step 7 で全 task 1 PR にまとめる予定)
depends-on: 04-catalog-docs-agent
---

# Task 05: rules 編集 (model-routing / global-content-boundary、source + 反映先)

## 目的

parent plan §Step 3 に対応。`model-routing.md` で実 model id 確認先を反映先 catalog (`~/.claude/agentops/model-catalog.yml`) と source 雛形 (`/home/otaku/agentops/config/model-catalog.yml`、全 null 維持) に分けて明記する。`global-content-boundary.md` 例外節に「機械可読 spec (`*.yml` catalog) は固定値 OK、本文 markdown には固定 model id を埋めない」を 1 行追加する。`global-content-boundary.md` は agentops source 側に未存在のため、反映先のみ更新する。

## 変更対象

- `/home/otaku/agentops/rules/model-routing.md` (source、line 5-10 周辺)
  - 「論理ロール → 実 model id の確認先」を反映先 catalog (`~/.claude/agentops/model-catalog.yml`) と明記、source 雛形は全 null 維持と分離
- `/home/otaku/.claude/rules/model-routing.md` (反映先、line 10 周辺)
  - 同等変更
- `/home/otaku/.claude/rules/global-content-boundary.md` (反映先、line 15-26 例外節)
  - 「機械可読 spec (`*.yml` catalog) は固定値 OK。本文 markdown には固定 model id を埋めない」を 1 行追加

## DbC

- **前提条件**:
  - Task 02-04 完了、catalog 編集済み (実 model id が反映先 catalog に存在)
  - 既存 rules ファイルの構造 (frontmatter / 章立て) を把握済み
- **不変条件**:
  - 既存 7 論理ロール定義は触らない
  - 「実装 → レビュー → 分岐フロー」既存節 (3 工程版) は Task 06 で 5 工程に拡張するため、本 task では触らない
  - frontmatter の paths / applies-to は変更しない
- **完了条件**:
  - source `rules/model-routing.md` と反映先 `~/.claude/rules/model-routing.md` で実 model id 確認先記述が同期
  - 反映先 `~/.claude/rules/global-content-boundary.md` で例外節 1 行追記
  - `rules/model-routing.md` は source / 反映先で frontmatter / paths 以外の意図差分がない
- **禁止事項**:
  - 本文 markdown に固定 model id (`gpt-5.5` / `gpt-5.3-codex` / `claude-sonnet-4-6` 等) を新規流入させる
  - 5 工程フロー追記 (Task 06 のスコープ)
  - secret 値混入
- **停止条件**:
  - source / 反映先で章立てが大きく異なり同期できない → user 確認、再調査
  - 既存固定 model id の流入が判明 → 即 revert、grep で全件再確認

## 検証

```sh
# (1) source と反映先の差分 (frontmatter 以外同一)
diff <(grep -v "^---$\|^name:\|^description:\|^paths:" /home/otaku/agentops/rules/model-routing.md) \
     <(grep -v "^---$\|^name:\|^description:\|^paths:" /home/otaku/.claude/rules/model-routing.md)

# (2) 本文 markdown に固定 model id が新規流入していないこと
grep -nR "gpt-5\.5\|gpt-5\.3-codex\|claude-sonnet-4-6\|claude-opus-4-7" \
  /home/otaku/.claude/rules/ /home/otaku/agentops/rules/
# → catalog yml への参照行のみ可。本文記述に id が混じれば違反
```

## メモ

- Task 06 (5 工程フロー) と密接、編集ファイルが重なるため、Task 05 の編集は「実 model id 参照先明記 + 例外節 1 行追加」だけに限定し、5 工程フローは Task 06 で別 commit / 別 patch として扱う
