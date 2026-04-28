---
last_reviewed: 2026-04-28
scope: glossary
---

# 用語集

agentops リポジトリで使う中核用語の定義表。docs / config / rules / skills / workflows / CLAUDE.md / AGENTS.md からは原則本ファイルへ参照を張り、用語の同義語ゆれを発生させない。

> 上位文書: [docs/01-philosophy.md](./01-philosophy.md)

## 許容語リスト（grep 検証用）

旧用語 0 件化の検証コマンドで除外するパターン。本リスト以外で `orchestrator` / `cross-review` / `cross-model-delegate` / `harness` 系の単独使用が見つかった場合は、本表のいずれかへ統一する。

- **orchestrator 系**: `主 orchestrator`（決定権者を指す日本語）/ `orchestrator_frontier`（`config/model-catalog.yml` のロール名）/ `orchestrator role`（役割としての言及）/ `orchestrators`（複数形）/ `orchestrator-workers`（Anthropic Building Effective Agents の pattern 名、proper noun）/ `orchestrator_may_override`（`config/model-catalog.yml` の YAML スキーマフィールド名）/ 本ファイル `docs/00-glossary.md` 自身（解説文中で `orchestrator` を引用するため）/ `docs/reviews/` 配下（過去レビュー報告は当時の文言を保つため、grep からも path で除外）。
- **cross-review / cross-model-delegate**: `cross-review` は **行為・運用名**、`cross-model-delegate` は cross-review を起動する **CLI ラッパ名**（`scripts/agentops delegate`）。両者は同義ではないので置換しない。
- **harness 系**: `harness` 単独使用は OK。`harness spec` は task 単位の harness 契約、`harness engineering` は harness 自体を設計・保守・検証する分野。文脈に応じて使い分け、`docs/12-harness-engineering.md` 用語表（L43–48）に揃える。

検証コマンド（task 02 / P1-01 の DbC §検証）:

```sh
rg -n "orchestrator" docs/ config/ rules/ skills/ workflows/ CLAUDE.md AGENTS.md \
  | rg -v "orchestrator_frontier|主 orchestrator|orchestrator role|orchestrators|orchestrator-workers|orchestrator_may_override|docs/00-glossary.md|docs/reviews/"
```

→ 0 件であること（許容語付き 0 件、完全 0 件は求めない）。

## 業界・学術用語

- **ACI (Agent-Computer Interface)**: AI エージェントが触る CLI / ファイル / ログ / 状態を設計対象とする概念。SWE-agent (NeurIPS 2024, arXiv:2405.15793) が発祥。内部参照: [docs/01-philosophy.md](./01-philosophy.md), [docs/12-harness-engineering.md](./12-harness-engineering.md)。
- **AAIF (Agentic AI Foundation)**: 2025-12-09 に OpenAI / Anthropic が AGENTS.md を寄贈して設立した Linux Foundation 配下の組織。出典: [agents.md](https://agents.md/)。
- **ABC (Agent Behavioral Contracts)**: AI エージェント契約形式（6-tuple + (p, δ, k)-satisfaction）。出典: arXiv:2602.22302（一次性が弱いため、本リポジトリの停止条件閾値根拠は参考扱い）。
- **DbC (Design by Contract)**: Bertrand Meyer 由来の契約プログラミング概念。本リポジトリでは前提・不変・完了・禁止・停止の 5 条件として運用。内部参照: [docs/03-dbc-and-quality-gates.md](./03-dbc-and-quality-gates.md)。
- **freshness audit**: 公式 docs / GitHub / release notes / package registry / security advisory を AI 記憶より優先する確認運用。内部参照: [docs/06-freshness-and-monitoring.md](./06-freshness-and-monitoring.md)。

## harness 系

- **harness**: agent run の実行環境（task spec / setup / oracle / artifact / replay / sandbox を含む作業契約）。test harness / evaluation harness / agent harness の総称として使う場合は文脈で判別する。内部参照: [docs/12-harness-engineering.md](./12-harness-engineering.md) §用語表（L43–48）。
- **harness spec**: task 単位の harness 契約。`config/harness.yml` の `task_template` 構造を `.agentops/harnesses/<task>.yml` で具体化したもの。DbC を再現条件まで展開した拡張契約。内部参照: [docs/12-harness-engineering.md](./12-harness-engineering.md) §task spec。
- **harness engineering**: harness 自体を設計・保守・検証する分野。OpenHands SDK 4 層 / awesome-harness-engineering 8 ドメインに整合。内部参照: [docs/12-harness-engineering.md](./12-harness-engineering.md)。

## 役割・運用名

- **orchestrator (主 orchestrator / orchestrator_frontier)**: 決定権を持つ主モデル。日本語で言及するときは `主 orchestrator`、`config/model-catalog.yml` のロール名としては `orchestrator_frontier`、複数形は `orchestrators`。agentops では Claude Code (`claude-opus-4-7`) または Codex (GPT-5.5 系) のいずれかが想定既定。内部参照: [docs/04-model-routing.md](./04-model-routing.md), [docs/05-review-policy.md](./05-review-policy.md)。
- **cross-review**: 主 orchestrator とは別系列・別 CLI・別モデルファミリーの `review_frontier` で設計や差分を確認するレビュー方式（行為・運用名）。所見の採否・修正範囲・延期・統合判断は主 orchestrator が持つ。内部参照: [docs/05-review-policy.md](./05-review-policy.md), [docs/04-model-routing.md](./04-model-routing.md) §cross-review の選び方。
- **cross-model-delegate**: cross-review を起動する CLI ラッパ名。実体は `scripts/agentops delegate --to <別系列> --role review_frontier --effort high --input <ファイル>` で、run 記録を `.agentops/runs/<ISO8601>-<task-id>/` へ保存する。内部参照: [docs/10-cli-wrapper.md](./10-cli-wrapper.md)。

## ツール / プロトコル

- **MCP (Model Context Protocol)**: Anthropic 主導の tool / context 連携プロトコル。`http` 推奨、`sse` deprecated（2025-12 時点）。出典: [modelcontextprotocol.io](https://modelcontextprotocol.io/)。
- **Skills**: 2025-12 に open standard 化された agent capability 単位。`SKILL.md` + frontmatter で定義し、Claude Code / Codex 双方で参照可能。内部参照: [skills/catalog.md](../skills/catalog.md)。出典: [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)。
- **Plugins**: Claude Code の機能拡張パッケージ。slash command / hooks / agents / MCP servers を 1 つの単位にまとめて配布する。出典: [code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins)。
- **Auto memory**: Claude Code の自動メモリ機能。`~/.claude/projects/*/memory/MEMORY.md` を中心に user / feedback / project / reference 4 種を保存し、複数会話を跨いで参照する。出典: [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)。

## 検証・テスト方針

- **replay-driven**: テスト・検証を replay 可能性（同じ commit / harness spec / setup commands / oracle checks / artifact paths で再実行できるか）ベースに設計するアプローチ。本 plan の P3-01 候補として handoff 化されている。内部参照: [docs/12-harness-engineering.md](./12-harness-engineering.md) §replay。

## 停止条件

停止条件は **2 階層** で構成する。プロセス層は人間判断・ループ防止、tool 実行層は個別ツール呼び出しの暴走防止に対応する。閾値の機械可読 spec は `config/harness.yml` の `defaults.stop_conditions.tool_layer` に保持し、プロジェクトごとに上書きできる。

- **停止条件（プロセス層）**: テスト失敗修正 2 周超え / レビュー修正 2 周超え / 仕様判断必要 / セキュリティ・データ損失リスク。内部参照: [docs/03-dbc-and-quality-gates.md](./03-dbc-and-quality-gates.md) §停止条件。
- **停止条件（tool 実行層）**: 以下 4 種の閾値で halt する。閾値根拠は runaway agent の代表事例（cordum.io / blog.meganova.ai、一次性は弱い参考扱い）と ABC 論文 (arXiv:2602.22302) の (p, δ, k)-satisfaction。内部参照: [config/harness.yml](../config/harness.yml) `defaults.stop_conditions.tool_layer`。
  - **max_tool_calls**: 単一 agent run でのツール呼び出し上限（既定 200 回）。
  - **no-progress (`no_progress_steps`)**: N ステップ進捗無しで halt（既定 10 ステップ）。
  - **circuit breaker (`circuit_breaker_cycle_threshold`)**: 同一サイクル N 回検知で halt（既定 3 回）。
  - **cost cap (`cost_cap_usd_per_session`)**: USD 単位の停止上限（既定 USD 20 / session、超過時 halt、支出許可ではない）。

## 関連

- 上位文書: [docs/01-philosophy.md](./01-philosophy.md)
- DbC 詳細: [docs/03-dbc-and-quality-gates.md](./03-dbc-and-quality-gates.md)
- モデルロール: [docs/04-model-routing.md](./04-model-routing.md)
- レビュー方針: [docs/05-review-policy.md](./05-review-policy.md)
- harness engineering: [docs/12-harness-engineering.md](./12-harness-engineering.md)
- 停止条件 spec: [config/harness.yml](../config/harness.yml)
