# 計画外観察事項: docs/10, docs/11 の DbC prose 残存

> 発見セッション: 2026-04-28 task 05 (P1-05 DbC 集約) 実装中
> 発見元: Codex cross-review Round 1 P2 advisory (run_id `20260428T215000+0900-p1-05-r1`)
> 親 plan: `2026-04-28-design-review-p0-p1`（task 05 として消化したのは docs/01,02,03,09,12 のみ）
> 種別: 計画外で発生した観察事項（別 task / 別 plan への申し送り）
> 優先度推定: P3（task 05 完了条件には影響しない、機能的な不具合ではない、ドキュメント整合性向上）

---

## 何を発見したか

task 05 (P1-05) は `docs/03-dbc-and-quality-gates.md` を DbC 5 条件の canonical 単一真ソース化し、`docs/01,02,09,12` から重複本文を削除する作業だった。task 05 の完了条件は満たしたが、Codex Round 1 advisory として **`docs/10-cli-wrapper.md` と `docs/11-monitoring-cli.md` にも同様の DbC prose（`前提条件:` / `不変条件:` / `完了条件:` / `停止条件:` リスト形式）が残存** していることが指摘された。

具体的な残存箇所:

```
docs/10-cli-wrapper.md:123:前提条件:
docs/10-cli-wrapper.md:129:不変条件:
docs/10-cli-wrapper.md:135:完了条件:
docs/10-cli-wrapper.md:140:停止条件:

docs/11-monitoring-cli.md:86:前提条件:
docs/11-monitoring-cli.md:92:不変条件:
docs/11-monitoring-cli.md:98:完了条件:
docs/11-monitoring-cli.md:103:停止条件:
docs/11-monitoring-cli.md:164:前提条件:
docs/11-monitoring-cli.md:172:不変条件:
docs/11-monitoring-cli.md:180:完了条件:
docs/11-monitoring-cli.md:187:停止条件:
```

合計 12 箇所（docs/10 が 4 箇所、docs/11 が 8 箇所 = `agentops` CLI の DbC + `agentops-watch` CLI の DbC + `agentops archive` サブコマンドの DbC）。

## なぜ task 05 で対応しなかったか

- `tasks/05-p1-05-dbc-consolidation.md` §前提条件「触ってよい範囲」に **docs/10, docs/11 は含まれない**。
- task 05 の不変条件「各 docs の章立てを破壊しない」「重複本文を削除して参照リンクに置換するのみ」と整合させるためには、CLI の具体 DbC をどこまで残し、どこから docs/03 への参照に切り替えるかの判断が必要。これは task 05 の S(1h) 想定を超える。
- AI auto-merge 許諾条件 5「PR スコープ単一」を破らないため、観察事項として handoff に残し別 task 起票で対応する判断。

Codex Round 1/2/3 の確認:

- **Round 1**: P2 advisory として記録、task 05 の P0/P1 ではないため修正不要。次 plan で別 task として整理する方針で OK と Codex も同意。
- **Round 2 / Round 3**: docs/10, docs/11 に差分なしを再確認、Round 1 の handoff 化方針で問題なしと結論。

## 次 plan で何を判断する必要があるか

1. **docs/10, docs/11 の DbC prose を docs/03 参照化するか、そのまま残すか**:
   - 残す案: docs/10, docs/11 の prose は **CLI 仕様の具体的な DbC 適用節** であり、docs/03 のテンプレートとは抽象度が異なる。docs/09 (hooks) と同様に「docs/03 を参照しつつ CLI 固有の前提・不変・完了・停止を述べる」形に再構成する選択もある。
   - 削除案: docs/03 が canonical なので、docs/10, docs/11 の DbC prose を「→ docs/03 を参照」リンク + 1 段適用 prose に再構成し、5 条件の見出し形式は廃止する（docs/09 と同じパターン）。
2. **task 06 (cross-reference) の対象に含めるか別 task にするか**:
   - task 06 は rule ↔ skill ↔ workflow ↔ hook 逆参照テーブル新設なので、CLI の DbC 整理とはスコープが別。別 task として起票するのが自然。
3. **task の優先度**:
   - 機能的な不具合ではない、auto-merge を阻害しない、現状でドキュメントは読める。P3 推定で他 P1 task 後回しが妥当。

## 推奨 task spec（次 plan 着手時の参考）

```md
# task XX — Pn-XX: DbC 適用節を docs/10, docs/11 で docs/03 参照化

## 前提条件
- 触ってよい範囲: docs/10-cli-wrapper.md, docs/11-monitoring-cli.md
- 触らない範囲: その他 docs、scripts、tools

## 不変条件
- CLI 仕様の意味（agentops / agentops-watch / agentops archive の挙動）を変えない
- DbC 用語の意味は docs/03 canonical を変えない
- 各 CLI セクションの章立てを破壊しない（archive サブコマンドの DbC など、固有挙動に密着した記述は保持）

## 実行内容
1. docs/10, docs/11 の `前提条件:` / `不変条件:` / `完了条件:` / `停止条件:` リスト形式を、docs/09 と同様のパターン（関係文 + docs/03 参照リンク + 1 段適用 prose）に再構成する
2. CLI 固有の挙動（例: archive plan の `--dry-run` セマンティクス）は適用節として保持
3. `rg -n "^前提条件:|^不変条件:|^完了条件:|^停止条件:" docs/10-cli-wrapper.md docs/11-monitoring-cli.md` が 0 件になることを確認

## 完了条件
- docs/10, docs/11 の DbC prose 12 箇所が削除または再構成されている
- docs/03 への参照リンクが docs/10, docs/11 から両方向で機能する
- CLI の動作仕様情報は失われていない

## 想定コスト
- S（1h）想定。docs/09 で確立したパターンの適用なので低リスク

## 業界出典
- task 05 (P1-05) で確立した「DbC 集約」パターンの再適用
```

## 関連ファイル

- 親 plan: `.agentops/archive/2026-04-28-design-review-p0-p1/plan.md`（plan 完了後 archive 予定）
- task 05 archive: `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/05-p1-05-dbc-consolidation.md`
- task 05 review (Round 1 P2 advisory 詳細): `.agentops/archive/2026-04-28-design-review-p0-p1/reviews/p1-05.md`（plan 完了後 archive される）
- 残存箇所: `docs/10-cli-wrapper.md` L123-140, `docs/11-monitoring-cli.md` L86-103, L164-187
- canonical: `docs/03-dbc-and-quality-gates.md`
- 先行パターン例: `docs/09-hooks-quality-gates.md` §DbC（task 05 で再構成済み）

## 完了 handoff の扱い

本 handoff は **本 plan (`2026-04-28-design-review-p0-p1`) 完了時に新 plan へ引き継ぐ** ための観察事項。新 plan 着手時に task 化されたら、本 handoff は対応する archive へ移動する（新 plan の archive ではなく `archive/2026-04-28-design-review-p0-p1/handoffs/` に置くのが筋: 観察事項は本 plan 内で発生したため）。
