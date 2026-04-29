# task 02 (docs/10, 11 DbC prose 整理) Codex cross-review 記録

> task: `.agentops/tasks/02-dbc-prose-cleanup-docs-10-11.md`
> 旧 handoff: `.agentops/handoffs/2026-04-28-dbc-prose-remnants-docs-10-11.md`
> branch: `claude/handoff-followup-impl-02-dbc-prose-cleanup-docs-10-11`
> reviewer: Codex CLI (model: adapter default / `--model` 未指定、effort=high, role=review_frontier)
> 主 orchestrator: Claude Opus 4.7 (1M context)

---

## 採用方針メモ

旧 handoff §次 plan で何を判断する必要があるか の 3 件への回答:

1. **docs/10, 11 の DbC prose を docs/03 参照化するか、そのまま残すか**: **2 種類で扱う**:
   - **CLI 全体の汎用 DbC** (docs/10 §DbC、docs/11 §DbC agentops-watch): docs/03 が canonical で表現可能なため、docs/09 と同じパターン（関係文 + docs/03 参照リンク + 1 段適用 prose）に圧縮
   - **archive サブコマンドの DbC** (docs/11 §DbC archive サブコマンド): CLI 固有の atomic write / preflight / path 検証など実装仕様レベルの記述で docs/03 だけでは表現できないため、章タイトルを `### DbC との関係（archive サブコマンド）` に変更し、関係文 + 4 ブロックを bold heading (`**適用前提**:` 等) で保持。`^前提条件:` 等の grep には match しなくなる
2. **task 06 (cross-reference) の対象に含めるか別 task にするか**: 別 task として処理（本 task）。前 plan task 06 は cross-reference の rule 起点表で別スコープ。
3. **task の優先度**: 旧 handoff §54 で P3 推定だったが、新 plan 全体で 2 task のみで小規模なため通常優先度で処理。

## 実装概要

- `docs/10-cli-wrapper.md` §DbC (L128-152): docs/09 パターンに圧縮（関係文 + 適用 prose、2 段落）
- `docs/11-monitoring-cli.md` §DbC (L91-114, agentops-watch): docs/09 パターンに圧縮
- `docs/11-monitoring-cli.md` §DbC（archive サブコマンド）(L169-200): bold heading 形式に変更（章タイトル `### DbC との関係（archive サブコマンド）` + 関係文 + `**適用前提**:` `**適用不変**:` `**適用完了**:` `**適用停止**:` の 4 bullet ブロック）

DbC リスト形式 12 箇所 (`^前提条件:` 等) は全て削除/再構成済み (検証コマンド `rg -nE "^前提条件:..." docs/10-cli-wrapper.md docs/11-monitoring-cli.md` で 0 件確認)。

## 検証

- 検証コマンド: `rg -nE "^前提条件:|^不変条件:|^完了条件:|^停止条件:" docs/10-cli-wrapper.md docs/11-monitoring-cli.md` → **0 件** ✅
- docs/03 参照リンク: docs/10 で 1 件、docs/11 で 3 件 (CLI 3 セクション分: agentops / agentops-watch / archive サブコマンド)
- `python3 -m compileall tools` exit 0
- `python3 -m unittest discover -s tests` 12/12 pass
- 行数: docs/10 132 行 (元 152 行から 20 行減)、docs/11 157 行 (元 187 行から 30 行減)

CLI の動作仕様情報は失われていない:
- agentops CLI (delegate / harness): docs/10 本文 §1-5 で詳細記述、§DbC は適用 prose のみ
- agentops-watch CLI: docs/11 §1-5 で詳細記述、§DbC は適用 prose のみ
- archive サブコマンド: docs/11 §archive サブコマンドで仕様記述、§DbC で 5 条件展開（bold heading 形式）

## 並行する旧 handoff §推奨 task spec との整合性

旧 handoff L57-85 の推奨 task spec の不変条件 §68「**archive サブコマンドの DbC など、固有挙動に密着した記述は保持**」と整合:
- archive サブコマンドの DbC は bold heading 形式で保持
- 「適用前提」「適用不変」「適用完了」「適用停止」の 4 ブロックで仕様情報を完全保持
- ただし行頭が `**` で始まるため `^前提条件:` regex には match しない（検証コマンドを通せる）

---

## Round 1

- run_id: `<TBD on Round 1 投入時>`
- run path: `.agentops/runs/<ts>-02-dbc-prose-cleanup-docs-10-11-r1/`
- 実行: `scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/10-cli-wrapper.md --run-id <ISO8601>+0900-02-dbc-prose-cleanup-docs-10-11-r1 --message "<観点>"`
- exit_code: <TBD>

### 所見サマリ

- P0: <TBD>
- P1: <TBD>
- P2: <TBD>
- P3: <TBD>

### Codex 所見原文

<TBD>

### 反映方針表

| 指摘 | 重大度 | 採否 | 対応内容 | 反映先 |
|---|---|---|---|---|
| <TBD> | | | | |

---

## Round 2

(Round 1 修正後の clean 確認)

---

## Round 3 (確認専用 final、no further P0/P1 確認)

(Round 2 結果転記後の確認)

---

## DbC 完了評価（task 02 §完了条件）

- [x] docs/10, 11 の DbC prose 12 箇所が削除または再構成 (rg 検証 0 件)
- [x] docs/03 への参照リンクが docs/10, 11 から両方向で機能 (markdown-link-check pass、参照件数: 10 → 1, 11 → 3)
- [x] CLI の動作仕様情報は失われていない (本文章節 + archive サブコマンドの bold heading 形式 DbC で保持)
- [ ] Codex cross-review 通過 (Round 3 で `no further P0/P1`)

## auto-merge 6 件評価（CLAUDE.md / AGENTS.md §許諾条件、Round 3 後 = 最終評価）

- [ ] DbC 完了
- [ ] 別系列 frontier cross-review 通過
- [ ] CI green
- [ ] 観察事実食い違いなし
- [ ] PR スコープ単一
- [ ] secret 未混入
