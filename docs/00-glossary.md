---
last_reviewed: 2026-04-28
next_review_by: 2026-07-31
reviewer: pachinko-spec
language: ja
applies-to: global
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

検証コマンド（task 02 / P1-01 の DbC §検証、**orchestrator 系の検証**）:

```sh
rg -n "orchestrator" docs/ config/ rules/ skills/ workflows/ CLAUDE.md AGENTS.md \
  | rg -v "orchestrator_frontier|主 orchestrator|orchestrator role|orchestrators|orchestrator-workers|orchestrator_may_override|docs/00-glossary.md|docs/reviews/"
```

→ 0 件であること（許容語付き 0 件、完全 0 件は求めない）。

**cross-review / cross-model-delegate の使い分け確認**（同義置換が混入していないか目視）:

```sh
rg -n "cross-review|cross-model-delegate" docs/ config/ skills/ workflows/ CLAUDE.md AGENTS.md
```

→ `cross-review` は行為 / 運用名、`cross-model-delegate` は CLI ラッパ名（`scripts/agentops delegate`）として一貫使用されていることを目視確認。

**harness 系の使い分け確認**（`docs/12-harness-engineering.md` 用語表 L43–48 と整合しているか目視）:

```sh
rg -n "\bharness\b|harness spec|harness engineering" docs/12-harness-engineering.md docs/03-dbc-and-quality-gates.md
```

→ `harness` / `harness spec` / `harness engineering` が文脈ごとに正しく使い分けられていることを目視確認。

## 業界・学術用語

- **ACI (Agent-Computer Interface)**: AI エージェントが触る CLI / ファイル / ログ / 状態を設計対象とする概念。SWE-agent (NeurIPS 2024, arXiv:2405.15793) が発祥。内部参照: [docs/01-philosophy.md](./01-philosophy.md), [docs/12-harness-engineering.md](./12-harness-engineering.md)。
- **AAIF (Agentic AI Foundation)**: 2025-12-09 に Linux Foundation 配下で設立された組織。OpenAI が AGENTS.md を、Anthropic が MCP（Model Context Protocol）を、Block が Goose をそれぞれ寄贈して founding contribution に加えた。出典: [AAIF launch announcement (Linux Foundation)](https://aaif.io/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation-aaif-anchored-by-new-project-contributions-including-model-context-protocol-mcp-goose-and-agents-md/), [agents.md](https://agents.md/)。
- **ABC (Agent Behavioral Contracts)**: AI エージェント契約形式（6-tuple + (p, δ, k)-satisfaction）。出典: arXiv:2602.22302（一次性が弱いため、本リポジトリの停止条件閾値根拠は参考扱い）。
- **DbC (Design by Contract)**: Bertrand Meyer 由来の契約プログラミング概念。本リポジトリでは前提・不変・完了・禁止・停止の 5 条件として運用。内部参照: [docs/03-dbc-and-quality-gates.md](./03-dbc-and-quality-gates.md)。
- **freshness audit**: 公式 docs / GitHub / release notes / package registry / security advisory を AI 記憶より優先する確認運用。内部参照: [docs/06-freshness-and-monitoring.md](./06-freshness-and-monitoring.md)。

## harness 系

- **harness**: agent run の実行環境（task spec / setup / oracle / artifact / replay / sandbox を含む作業契約）。test harness / evaluation harness / agent harness の総称として使う場合は文脈で判別する。内部参照: [docs/12-harness-engineering.md](./12-harness-engineering.md) §用語表（L43–48）。
- **harness spec**: task 単位の harness 契約。`config/harness.yml` の `task_template` 構造を `.agentops/harnesses/<task>.yml` で具体化したもの。DbC を再現条件まで展開した拡張契約。内部参照: [docs/12-harness-engineering.md](./12-harness-engineering.md) §task spec。
- **harness engineering**: harness 自体を設計・保守・検証する分野。OpenHands SDK 4 層 / awesome-harness-engineering 8 ドメインに整合。内部参照: [docs/12-harness-engineering.md](./12-harness-engineering.md)。

## 役割・運用名

- **orchestrator (主 orchestrator / orchestrator_frontier)**: 決定権を持つ主モデル。日本語で言及するときは `主 orchestrator`、`config/model-catalog.yml` のロール名としては `orchestrator_frontier`、複数形は `orchestrators`。agentops では Claude Code / Anthropic 系 frontier reasoning model または Codex / OpenAI 系 frontier reasoning model のいずれかが候補。実 model id は固定せず、使用直前に公式 docs と CLI の現在仕様で確認する（`config/model-catalog.yml` の `model_id: null` 方針に整合）。内部参照: [docs/04-model-routing.md](./04-model-routing.md), [docs/05-review-policy.md](./05-review-policy.md)。
- **cross-review**: 主 orchestrator とは別系列・別 CLI・別モデルファミリーの `review_frontier` で設計や差分を確認するレビュー方式（行為・運用名）。所見の採否・修正範囲・延期・統合判断は主 orchestrator が持つ。内部参照: [docs/05-review-policy.md](./05-review-policy.md), [docs/04-model-routing.md](./04-model-routing.md) §cross-review の選び方。
- **cross-model-delegate**: cross-review を起動する CLI ラッパ名。実体は `scripts/agentops delegate --to <別系列> --role review_frontier --effort high --input <ファイル>` で、run 記録は `.agentops/runs/<run_id>/` 配下に保存される。`run_id` は `--run-id` で明示しない場合 `<JST タイムスタンプ>-<to>-<role>` 形式（`%Y%m%dT%H%M%S+0900-<to>-<role>`、実装は `tools/agentops_cli/__main__.py:339` 周辺）。内部参照: [docs/10-cli-wrapper.md](./10-cli-wrapper.md)。

## docs 分類 / リポジトリ責務

- **applies-to (frontmatter field)**: 各 `docs/*.md` が「どこへ適用される設計か」を機械可読に表す frontmatter フィールド。別 AI エージェントが当 repo の docs を読んだとき、グローバル設定への反映候補か、agentops repo 内部運用向けか、shared CLI 仕様か、雛形カタログかを誤判定なく分類できるようにする。値は次の 4 種に固定する（`templates/` / `rules/` / `skills/` / `workflows/` 配下の md には現状未付与だが、用語としては予約）:
  - **`global`**: 全 project / 全 CLI に適用される設計思想。グローバル設定 (`~/.claude/` / `~/.codex/`) への反映候補となる。例: `01-philosophy` / `02-workflow` / `18-notification-strategy` / `19-project-localization`。
  - **`shared-cli-spec`**: agentops repo 内 CLI (`scripts/agentops` / `scripts/agentops-watch` 等) の仕様で、host や他 repo から呼ばれる。別 AI への指針は「**実装本体は touch せず、共有 CLI を呼ぶだけ**」。例: `10-cli-wrapper` / `11-monitoring-cli`。
  - **`agentops-internal`**: agentops repo 自身の内部運用 docs。グローバル設定や他プロジェクトへの反映対象外。例: `08-config-templates` / `13-design-evaluation` / `14-real-project-template-policy` / `15-reference-kit-structure` / `16-global-settings-application-checklist` / `17-cross-reference`。
  - **`template-source`**: 雛形 / 候補カタログの **md ファイル自体** (`templates/<...>.md` / `rules/catalog.md` / `skills/catalog.md` / `workflows/catalog.md` 等) に直接付与する予約値。`docs/` 配下で雛形・カタログ運用について説明する **meta docs** (例: [`docs/14-real-project-template-policy.md`](./14-real-project-template-policy.md) / [`docs/15-reference-kit-structure.md`](./15-reference-kit-structure.md)) は本 repo の運用方針を述べる internal docs として `agentops-internal` を付与する（「テンプレート運用について書いた agentops 内部 docs」と「テンプレート md 自体」を区別する）。本リスト時点で `docs/` 配下に該当無し（用語のみ予約、将来 `templates/` 内 md 等に拡張する場合に使う）。
- **三役 (Trinity)**: agentops repo が同時に担う 3 つの責務。docs / config / scripts / tools の置き場所と「どれが他層から呼ばれる入口で、どれが反映候補で、どれが内部運用か」を 1 つの語で系統化する。
  - **(a) 設計思想カタログ (catalog)**: `docs/` (`applies-to: global` のもの) / `rules/` / `skills/` / `workflows/` / `templates/`。別 AI が判断して採用する候補集として機能する。
  - **(b) 共有 CLI / ライブラリ (shared CLI)**: `tools/agentops_cli` (`scripts/agentops`) / `tools/agentops_monitor` (`scripts/agentops-watch`)。host や他 repo から呼ばれる集約点。`applies-to: shared-cli-spec` の docs はこの実体の仕様を規定する。
  - **(c) 雛形配布元 (template source)**: `config/claude/CLAUDE.md` / `config/codex/AGENTS.md` / `config/harness.yml` / `config/cron.example` 等。`~/.claude/` / `~/.codex/` などのグローバル設定への反映 source として機能する（変更しただけでは実反映されない、明示反映が必要）。
- **shared-cli-spec パターン**: 「**思想は global、実装は agentops の共有 CLI、各層は CLI を呼ぶだけ**」という多層責務分離パターン。Discord 通知・archive 後処理・monitoring 集計など、host 全体で共通の運用を扱う設計に適用する。
  - 思想層 (`applies-to: global`): kind / channel / DbC / rate-limit / 起動契約を docs/ で固定する (例: `docs/18-notification-strategy.md`)。
  - 実装層 (`applies-to: shared-cli-spec`): 共有 CLI 仕様を docs/ で固定し、実体は `tools/agentops_*` に持つ (例: `docs/11-monitoring-cli.md` + `tools/agentops_monitor`)。
  - 利用層 (host / 他 repo / hook / cron / shell scripts): 共有 CLI を呼び出すだけで、実装本体を touch しない。
  - 別 AI への指針: 「実装が agentops repo 内にあるからといって、それが agentops 内部専用とは限らない」「`applies-to: shared-cli-spec` の docs は agentops が他層へ提供する CLI 契約として読む」。

検証コマンド:

```sh
# 全 docs に applies-to が付与されているか (出力なしが正)
grep -L 'applies-to:' docs/*.md

# 各値の分布 (合計を集計)
grep -h '^applies-to:' docs/*.md | sort | uniq -c

# 想定外の値が紛れ込んでいないか
grep -h '^applies-to:' docs/*.md | sort -u
```

→ 値は `global` / `shared-cli-spec` / `agentops-internal` / `template-source` のみ。

## ツール / プロトコル

- **MCP (Model Context Protocol)**: Anthropic 主導の tool / context 連携プロトコル。標準 transport は `stdio` と `Streamable HTTP`（2025-06-18 spec、Streamable HTTP 内で SSE stream を使う）。旧 `HTTP+SSE transport`（2024-11-05 spec）は deprecated / replaced、後方互換のため一部実装に残る。出典: [MCP transports spec (2025-06-18)](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports), [modelcontextprotocol.io](https://modelcontextprotocol.io/)。
- **Skills**: 2025-12 に open standard 化された agent capability 単位。`SKILL.md` + frontmatter で定義し、Claude Code / Codex 双方で参照可能。内部参照: [skills/catalog.md](../skills/catalog.md)。出典: [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)。
- **Plugins**: Claude Code の機能拡張パッケージ。slash command / hooks / agents / MCP servers を 1 つの単位にまとめて配布する。出典: [code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins)。
- **Auto memory**: Claude Code の自動メモリ機能。プロジェクトごとの `~/.claude/projects/<project>/memory/` 配下に `MEMORY.md` を entrypoint として置き、build commands / debugging insights / architecture notes などをトピック別ファイルに保存して複数会話を跨いで参照する。本リポジトリのユーザーグローバル指示では user / feedback / project / reference の 4 分類で運用しているが、これは公式 docs の規定ではなく運用ルールである。出典: [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)。

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
