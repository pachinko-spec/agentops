# task 01 — 01: cross-reference skill / workflow → rule 逆参照列追加

> 親 plan: `2026-04-29-handoff-followups`
> 旧 handoff: `.agentops/handoffs/2026-04-28-cross-reference-skill-workflow-side.md`
> 優先度: 単独 task（前 plan task 06 の補完）
> 状態: 進行中（PR #54 push 済、Codex Round 1 で P1=1 採用反映後 Round 2 待ち）
> 想定コスト: S–M（1h–半日）
> 想定 PR ブランチ: `claude/handoff-followup-impl-01-cross-reference-bidirectional`
> 依存: なし（前 plan task 06 は完了済み、frontmatter task 04 も完了で catalog 側の参照基盤が整っている）

---

## 前提条件

- 触ってよい範囲: `skills/catalog.md`、`workflows/catalog.md`、`docs/17-cross-reference.md`（任意の skill/workflow 起点表追記、本 task では基本 catalog 側で完結）
- 触らない範囲: `rules/catalog.md`（前 plan task 06 完了済み、本 task では参照のみ）、`docs/00-17` 本文、scripts/、tools/
- 事前確認:
  - `rules/catalog.md` の rule リスト（task 06 で列追加済みの 12 rule + 列構成）を読み、skill / workflow 側からどの rule に逆参照を張るかをマッピング
  - 旧 handoff §次 plan で検討すべきこと の 4 件を判断材料として整理

## 不変条件

- 既存 catalog エントリの行（id / 概要 / 既存属性）を破壊しない。列追加のみ
- rule の意味（rules/catalog.md の説明）を変えない
- docs/17 の rule 起点表（task 06 で実装済み）を破壊しない
- catalog 表は markdown 標準の `| ... | ... |` テーブル形式を維持

## 実行内容

1. **判断 (Codex Round 1 投入時に明記)**:
   - **代表 rule 1 件 vs 全件列挙**: 本 task では **代表 1 件、複数候補がある場合も最も近い rule のみ採用**（docs/17 の pattern と同様）。情報損失が懸念される場合は Codex Round 1 P1/P2 で指摘可能、その時点で全件列挙へ切り替え判断。
   - **catalog vs docs/17 の責務分離**: docs/17 は「rule 起点の最小マッピング表」固定。catalog 側に逆参照列を追加し、責務分離を維持。
   - **frontmatter (last_reviewed) 追加**: 本 task ではスコープ外（catalog は frontmatter なしで運用、別 task 候補）。
   - **hook 列追加**: 本 task ではスコープ外（rule 経由で hook 到達可能、必要なら別 task）。
2. `skills/catalog.md` の各 skill 行に `関連 rule（代表）` 列を追加。
3. `workflows/catalog.md` の各 workflow 行に `関連 rule（代表）` 列を追加。
4. catalog 内の表ヘッダ・区切り行 (`|---|`) を skill / workflow 数に応じて整える。
5. 列の値は rule id（rules/catalog.md の id 列値）を使い、**最も近い rule 1 件**を選定（複数候補がある場合も代表 1 件のみ。網羅は docs/17 と本表の併読で対応）。対応 rule なしの場合は `—`。

## 完了条件

- `skills/catalog.md` の全 skill 行に `関連 rule（代表）` 列が入っている。
- `workflows/catalog.md` の全 workflow 行に `関連 rule（代表）` 列が入っている。
- 列値の rule id は `rules/catalog.md` に存在する id と一致（typo / 存在しない id がない）。
- markdown 標準 table 形式を維持（broken pipe / 列数不整合がない）。
- Codex cross-review 通過、所見反映済み。

## 検証

- `grep -E "^\| .* \| .* \| .* \|" skills/catalog.md` で列数確認
- `grep -E "^\| .* \| .* \| .* \|" workflows/catalog.md` で列数確認
- catalog の各値が `rules/catalog.md` の id と一致することを目視 + grep（`rg "^\| <rule-id> \|" rules/catalog.md` で 1 件ヒット）
- `python3 -m compileall tools` exit 0
- `python3 -m unittest discover -s tests` 12/12 pass
- CI 4 job 全 pass（特に markdown-link-check で broken link なし、yamllint / actionlint は本 task 範囲外）
- `scripts/agentops delegate --to codex --role review_frontier --effort high --input skills/catalog.md` (or workflows/catalog.md)
- 結果を `.agentops/runs/<timestamp>-01-cross-reference-bidirectional/` に保存、所見を `.agentops/reviews/01-cross-reference-bidirectional.md` に転記

## 禁止事項

- main 直 push
- `rules/catalog.md` の編集（前 plan task 06 完了済み、本 task では参照のみ）
- 既存 catalog 行（id / 概要 / 既存属性）の削除・変更
- skill / workflow の用途定義の変更
- secret 値の混入

## 完了時の後処理

- 本ファイルを `.agentops/archive/2026-04-29-handoff-followups/tasks/01-cross-reference-bidirectional.md` へ移す（commit 前、または `scripts/agentops archive` 経由）
- 旧 handoff `.agentops/handoffs/2026-04-28-cross-reference-skill-workflow-side.md` を `.agentops/archive/2026-04-28-design-review-p0-p1/handoffs/` へ移す（前 plan に紐づく handoff、本 task で実装完了したため archive 化）
- `.agentops/prompts/next-session.md` を次 task（02）に更新
- PR マージ後 main 同期確認

## 停止条件

- 1 skill / 1 workflow が複数 rule に対応するケースで、代表 1 件方式が情報損失すると Codex Round 1 P1 で判定 → 全件列挙方式に切り替え（本 task 内で対応）
- catalog 側の用語整理が必要と判明（例: 既存 skill / workflow の用途定義が rule マッピングに合わない） → user 確認
- レビュー修正 2 周超え

## 次セッションへ残すこと

- catalog の frontmatter 追加（last_reviewed 等）は次 plan の handoff 候補
- skill / workflow 側に hook 列も追加するかは次 plan 候補
