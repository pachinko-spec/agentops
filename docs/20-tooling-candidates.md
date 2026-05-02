---
last_reviewed: 2026-05-02
next_review_by: 2026-08-02
reviewer: pachinko-spec
language: ja
applies-to: global
---

# 導入候補ツール

## 目的

AI 任せの 1 人開発では、コードを直接読む時間が少なくなりやすい。agentops はすべての外部 tool を global に強制導入するのではなく、project ごとの効果、運用負荷、CI 影響、security 境界を確認してから採用する。

本 docs は「導入候補」を置く catalog であり、実 project への導入手順書ではない。導入する場合は対象 project の `.agentops/` plan / task で、対象、非対象、検証、rollback を決める。

## 採否ルール

- global では候補として覚えるだけにする。MCP server、CI、pre-commit、shell profile、plugin install は project plan なしに反映しない。
- 既存の test / lint / typecheck と競合する場合は、既存品質ゲートを優先し、sentrux は補助 signal として扱う。
- secret、認証情報、private repo path、Webhook URL の値を sentrux 設定や run log に保存しない。
- CI gate 化する前に local dry-run で false positive を確認する。

## sentrux

### 概要

sentrux は Rust 製の single binary CLI / GUI / MCP server。tree-sitter plugin を使った多言語解析、quality signal、rules engine、CI 向け `sentrux check .`、AI agent 向け MCP (`sentrux --mcp`) を提供する。

公式 README は 52 言語対応、`scan` / `health` / `session_start` / `session_end` / `check_rules` などの MCP tool、`.sentrux/rules.toml` の rules engine を説明している。rules sample の現行形は `[constraints]`、`[[layers]]`、`[[boundaries]]` の 3 要素で構成される。

### 適合 project

- 中規模以上で、`src/core`、`src/app`、`packages/*` などの層境界を定義できる project。
- AI が広範囲に編集し、循環依存、god file、層越え依存を早く検知したい project。
- CI / pre-commit に quality gate を増やしても、開発速度より構造維持を優先したい project。

小規模 prototype、単発 script、明確な層境界がない project、既存 CI が不安定な project では、まず inventory のみに留める。

### 採用方針

- global 強制導入はしない。
- `project-localize-inventory` の中で候補として確認する。
- 導入する場合は `templates/projects/sentrux/.sentrux/rules.toml.template` を project 事情に合わせてコピーし、層名、path、boundary を調整する。
- CI gate 化は local `sentrux check .` が安定してから行う。
- MCP (`sentrux --mcp`) は editor / CLI ごとの公式設定と権限を確認してから追加する。

### 導入手順の最小 skeleton

1. 対象 project の既存構造を inventory 化する。
2. `.sentrux/rules.toml` を作成し、まず `max_cycles` と 2-3 層の layer だけで開始する。
3. `sentrux check .` を local で実行し、false positive と例外 path を調整する。
4. CI / pre-commit gate 化するかを task 内で判断する。
5. MCP を使う場合は `sentrux --mcp` を client 設定に追加し、secret 値を含まないことを確認する。

### 既知リスク

- 層境界が曖昧な project では、rules が形式だけになりやすい。
- CI gate を急に有効化すると既存 debt で作業が止まる。baseline 運用や warning-only 期間を検討する。
- MCP server は AI agent に追加の観測面を渡すため、private path やファイル名の扱いを project ごとに確認する。
- sentrux 自体の CLI / MCP / rules schema は変わり得るため、導入時に公式 README と sample rules を再確認する。

## Understand-Anything

Understand-Anything は現時点では将来検討対象に留める。1 人 + AI 任せ + user がコードをあまり読まない運用では、追加の知識 graph / document layer より、構造劣化を検知できる sentrux の方が先に効く可能性が高い。雛形は作らない。

## 関連

- [sentrux README](https://github.com/sentrux/sentrux)
- [sentrux rules sample](https://raw.githubusercontent.com/sentrux/sentrux/main/.sentrux/rules.toml)
- [skills/catalog.md](../skills/catalog.md) — tooling adoption candidates
- [templates/projects/sentrux/.sentrux/rules.toml.template](../templates/projects/sentrux/.sentrux/rules.toml.template)
