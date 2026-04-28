# task 02 — P1-01: 用語統一表 docs/00-glossary.md 追加 + 旧用語 0 件化

> 親 plan: `2026-04-28-design-review-p0-p1`  
> 提案 ID: P1-01  
> 優先度: P1  
> 状態: 未着手  
> 想定コスト: S（2 時間）  
> 想定 PR ブランチ: `claude/design-review-impl-p1-01`  
> 依存: task 01 完了後（task 01 で停止条件用語を確定させてから glossary に取り込むため）

---

## 前提条件

- 触ってよい範囲: `docs/00-glossary.md`（新規）、`docs/01–16`（用語置換のみ）、`config/`、`rules/catalog.md`、`skills/catalog.md`、`workflows/catalog.md`、`CLAUDE.md`、`AGENTS.md`、`templates/{claude,codex,agentops}/`。
- 触らない範囲: `docs/reviews/`、`archive/`、`.agentops/archive/`。
- 事前確認: 報告書 §3.A の用語ゆれ箇所（"orchestrator" vs "orchestrator_frontier"、"cross-review" vs "cross-model-delegate"、"harness" vs "harness spec"）。docs/04-model-routing.md の論理ロール表。Appendix B の用語集。
- 業界出典: AAIF agents.md、`code.claude.com/docs/en/memory`、Claude Code public docs の用語慣用。

## 不変条件

- 既存の章立て・段落構造を破壊しない。用語置換と glossary 新設のみ。
- 機能変更なし（言語面のみの改修）。
- 用語の意味を変えるような置換はしない（同義語の表記揺れ統一に限る）。

## 実行内容

1. `docs/00-glossary.md` を新規作成し、以下の用語を 1 行ずつ定義する。
   - ACI / AAIF / ABC / DbC / freshness audit / harness（→ harness spec / harness engineering との関係）/ orchestrator (orchestrator_frontier) / cross-review / cross-model-delegate / MCP / Skills / Plugins / Auto memory / replay-driven / circuit breaker / cost cap / no-progress / max_tool_calls / 停止条件 (プロセス層 / tool 実行層)。
   - 報告書 Appendix B を出発点とし、task 01 で確定した停止条件用語も取り込む。
   - 各エントリに「公式出典 URL」または「内部参照（docs/0X.md）」を 1 つ添える。
2. `docs/01-philosophy.md` 冒頭から `→ 用語は docs/00-glossary.md を参照` のリンクを張る。
3. リポジトリ全体を grep し、用語ゆれを統一する。
   - `orchestrator` → 文脈に応じて `orchestrator_frontier`（ロール名）か `主 orchestrator`（決定権者）に統一。
   - `cross-review` と `cross-model-delegate` の使い分けを明確化（cross-review は行為、cross-model-delegate は CLI ラッパ）。
   - `harness` / `harness spec` / `harness engineering` を docs/12 の定義に揃える。
4. **許容語リスト**を glossary に明記し、grep の対象から除外する。完全 0 件は求めない。
   - 許容語例: `主 orchestrator`、`orchestrator_frontier`、`orchestrator role`、`orchestrators`（複数形）、glossary 内の解説例。
   - 検証 grep は許容語リストを `-v` で除外したパターンで実行する（後述）。

## 完了条件

- `docs/00-glossary.md` が新規追加されている。
- 各用語に出典 / 内部参照リンクがある。
- `rg -n "orchestrator" docs/ config/ rules/ skills/ workflows/ CLAUDE.md AGENTS.md` の結果が、glossary で定義した許容語リスト（`orchestrator_frontier` / `主 orchestrator` / `orchestrator role` / `orchestrators` / glossary 自身）以外でヒットしないこと。完全 0 件ではなく許容語付き 0 件とする。
- `docs/01-philosophy.md` から `docs/00` への双方向リンクがある。
- Codex cross-review 完了、所見反映済み。
- PR が main にマージされ、ローカル main が同期。

## 検証

- `rg -n "orchestrator" docs/ config/ rules/ skills/ workflows/ | rg -v "orchestrator_frontier|主 orchestrator|orchestrator role|orchestrators|docs/00-glossary.md"`（許容語と glossary 自身を除外して 0 件であること）
- `rg -n "cross-review|cross-model-delegate" docs/ config/ skills/`（用語の使い分けが揃っていること）
- `rg -n "harness" docs/12-harness-engineering.md docs/03-dbc-and-quality-gates.md`（spec / engineering の使い分けが揃っていること）
- `python3 -m compileall tools`
- `scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/00-glossary.md`
- 結果は `.agentops/runs/<timestamp>-p1-01/` に保存、所見を `.agentops/reviews/p1-01.md` に転記。

## 禁止事項

- main 直 push。
- 機能・ルールの意味を変える編集（用語統一の範囲を超える）。
- 報告書本体や `archive/` への編集。
- スコープ外の docs リファクタ。

## 完了時の後処理

- 本ファイルを `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/02-p1-01-glossary.md` へ移す（commit 前）。
- `prompts/next-session.md` を次 task（03 または 04）に更新。
- PR マージ後 main 同期確認。

## 停止条件

- 用語の意味が公式 docs（Claude Code / Codex / AAIF）と食い違う箇所があり、glossary でどちらを採用すべきか判断が分かれる場合 → user 確認。
- 置換対象が想定の 3 倍以上あり 2 時間で収まらない場合 → 範囲を docs/ 限定に縮小し、config/ 以下は別 task へ分割。
- レビュー修正 2 周超え。

## 次セッションへ残すこと

- glossary に追記すべき用語が新たに見つかった場合は、本ファイルの archive 後でも `docs/00-glossary.md` の last_reviewed を更新して追記可能。次 plan の対象に入れる場合は `handoffs/` へ。
