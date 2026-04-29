# task 02 — 02: docs/10, 11 の DbC prose を docs/03 参照化

> 親 plan: `2026-04-29-handoff-followups`
> 旧 handoff: `.agentops/handoffs/2026-04-28-dbc-prose-remnants-docs-10-11.md`
> 優先度: 単独 task（前 plan task 05 の補完）
> 状態: 未着手
> 想定コスト: S（1h）
> 想定 PR ブランチ: `claude/handoff-followup-impl-02-dbc-prose-cleanup-docs-10-11`
> 依存: なし（前 plan task 05 で docs/03 canonical 化、docs/09 で再構成パターン確立済み）

---

## 前提条件

- 触ってよい範囲: `docs/10-cli-wrapper.md`、`docs/11-monitoring-cli.md`
- 触らない範囲: その他 docs、scripts/、tools/、config/
- 事前確認:
  - `docs/03-dbc-and-quality-gates.md`: DbC 5 条件 canonical 真ソース
  - `docs/09-hooks-quality-gates.md`: 前 plan task 05 で再構成済みの先行パターン例（関係文 + docs/03 参照リンク + 1 段適用 prose）
  - `docs/10-cli-wrapper.md` L123-140: agentops CLI の DbC prose（前提・不変・完了・停止）
  - `docs/11-monitoring-cli.md` L86-103: agentops-watch CLI の DbC prose
  - `docs/11-monitoring-cli.md` L164-187: agentops archive サブコマンドの DbC prose

## 不変条件

- CLI 仕様の意味（agentops / agentops-watch / agentops archive の挙動）を変えない
- DbC 用語の意味は docs/03 canonical を変えない
- 各 CLI セクションの章立てを破壊しない（archive サブコマンドの DbC など、固有挙動に密着した記述は保持）
- docs/10, 11 の他章（CLI options / examples / output 形式）には触らない
- 既存 frontmatter (`last_reviewed` 等、前 plan task 04 で追加済み) を維持

## 実行内容

1. `docs/10-cli-wrapper.md` の DbC prose 4 箇所 (L123-140) を docs/09 と同じパターン（関係文 + docs/03 参照リンク + 1 段適用 prose）に再構成。
2. `docs/11-monitoring-cli.md` の DbC prose 8 箇所 (L86-103, L164-187) を同様に再構成。各 CLI（agentops / agentops-watch / archive サブコマンド）ごとに 1 セクションに統合。
3. CLI 固有の挙動（例: archive plan の `--dry-run` セマンティクス）は適用節として保持。
4. `rg -n "^前提条件:|^不変条件:|^完了条件:|^停止条件:" docs/10-cli-wrapper.md docs/11-monitoring-cli.md` が **0 件**になることを確認。

## 完了条件

- docs/10, 11 の DbC prose 12 箇所が削除または再構成されている。
- docs/03 への参照リンクが docs/10, 11 から両方向で機能する（markdown-link-check pass）。
- CLI の動作仕様情報は失われていない（agentops / agentops-watch / archive サブコマンドの挙動が読み取れる）。
- Codex cross-review 通過、所見反映済み。

## 検証

- `rg -n "^前提条件:|^不変条件:|^完了条件:|^停止条件:" docs/10-cli-wrapper.md docs/11-monitoring-cli.md` が 0 件
- `rg -nE "docs/03-dbc-and-quality-gates" docs/10-cli-wrapper.md docs/11-monitoring-cli.md` で参照リンクが docs/10, 11 両方に存在
- `python3 -m compileall tools` exit 0
- `python3 -m unittest discover -s tests` 12/12 pass
- CI 4 job 全 pass（markdown-link-check で docs/10, 11 から docs/03 への link 検証）
- `scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/10-cli-wrapper.md`
- 結果を `.agentops/runs/<timestamp>-02-dbc-prose-cleanup-docs-10-11/` に保存、所見を `.agentops/reviews/02-dbc-prose-cleanup-docs-10-11.md` に転記

## 禁止事項

- main 直 push
- docs/10, 11 の他章（CLI options / examples / output 形式）の編集
- docs/03 の canonical 内容の変更
- CLI 仕様の意味変更
- secret 値の混入

## 完了時の後処理

- 本ファイルを `.agentops/archive/2026-04-29-handoff-followups/tasks/02-dbc-prose-cleanup-docs-10-11.md` へ移す（commit 前、または `scripts/agentops archive` 経由）
- 旧 handoff `.agentops/handoffs/2026-04-28-dbc-prose-remnants-docs-10-11.md` を `.agentops/archive/2026-04-28-design-review-p0-p1/handoffs/` へ移す（前 plan に紐づく handoff、本 task で実装完了したため archive 化）
- 本 task が plan 最終 task のため、`scripts/agentops archive plan --plan-id 2026-04-29-handoff-followups --summary "<text>"` で plan 全体 archive
- PR マージ後 main 同期確認

## 停止条件

- docs/10, 11 の DbC prose の意味が docs/03 だけでは表現できないと判明（CLI 固有の挙動を保持する適用節が prose 形式必須） → user 確認、scope 拡張判断
- CLI 仕様の他章（options / examples）への影響が出る → user 確認
- レビュー修正 2 周超え

## 次セッションへ残すこと

- 本 task が plan 最終なら次 plan は user 判断（次 plan 候補は前 plan 完了時 handoff の P2/P3 延期分）
