# task 05 — P1-05: DbC 記述を docs/03 に集約、01/09/12 は参照のみに

> 親 plan: `2026-04-28-design-review-p0-p1`  
> 提案 ID: P1-05  
> 優先度: P1  
> 状態: 未着手  
> 想定コスト: S（1 時間）  
> 想定 PR ブランチ: `claude/design-review-impl-p1-05`  
> 依存: task 02（glossary 確定後の方が用語ゆれが残らない）

---

## 前提条件

- 触ってよい範囲: `docs/01-philosophy.md`、`docs/02-workflow.md`、`docs/03-dbc-and-quality-gates.md`、`docs/09-hooks-quality-gates.md`、`docs/12-harness-engineering.md`。
- 触らない範囲: docs/04, 05, 06, 07, 08, 10, 11, 13, 14, 15, 16、`docs/reviews/`、`archive/`。
- 事前確認: 報告書 §3.A / §6.2 の DbC 重複指摘、philosophy.md L14 と workflow.md の 24 ステップサイクルのトーン差。
- 業界出典: 一般的 DRY 原則、ABC 論文 6-tuple との対応。

## 不変条件

- DbC の意味・5 条件（前提・不変・完了・禁止・停止）を変えない。
- 各 docs の章立てを破壊しない。重複本文を削除して参照リンクに置換するのみ。
- 任意の task が `docs/03` だけ読めば DbC を理解できる状態を作る。

## 実行内容

1. `docs/03-dbc-and-quality-gates.md` を DbC の単一真ソースとして整理する（task 01 で 2 階層停止条件が反映済みの前提）。
2. 以下から DbC の重複本文を削除し、`→ docs/03 を参照` のリンクに置換する。
   - `docs/01-philosophy.md`（DbC 概念の冒頭言及のみ残し、5 条件本文は削除）
   - `docs/09-hooks-quality-gates.md`（hooks と DbC の関係のみ残し、5 条件本文は削除）
   - `docs/12-harness-engineering.md`（DbC と harness spec の関係のみ残し、5 条件本文は削除）
3. `docs/01-philosophy.md` L14（「単純で合成可能な workflow を優先」）と `docs/02-workflow.md` の 24 ステップサイクルのトーン差を整理。
   - workflow.md 冒頭に「24 ステップは reference であり全てを毎回実行する必要はない。philosophy.md L14 の通り、単純で合成可能なものを優先する」を追記。
4. 各 docs から `docs/03` へのリンクが両方向で機能するか確認。

## 完了条件

- `docs/03` のみが DbC の本文を持ち、他は参照のみ。
- `docs/01`、`docs/02` のトーン差が解消されている（philosophy と workflow の関係が明示）。
- `rg -c "前提条件|不変条件|完了条件|禁止事項|停止条件" docs/`（reviews/ 除く）で `docs/03` 以外は 0 か 1（見出しのみ）になる。
- Codex cross-review 完了、所見反映済み。
- PR が main にマージされ、ローカル main が同期。

## 検証

- `rg -c "^## 前提条件" docs/*.md`（docs/03 のみ 1 になること）
- `rg -n "→ docs/03 を参照|→ \[" docs/01-philosophy.md docs/09-hooks-quality-gates.md docs/12-harness-engineering.md`
- `python3 -m compileall tools`
- `scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/03-dbc-and-quality-gates.md`
- 結果を `.agentops/runs/<timestamp>-p1-05/` に保存、所見を `.agentops/reviews/p1-05.md` に転記。

## 禁止事項

- main 直 push。
- DbC の意味・5 条件の変更。
- スコープ外の docs リファクタ。
- 報告書本体や archive への編集。

## 完了時の後処理

- 本ファイルを `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/05-p1-05-dbc-consolidation.md` へ移す（commit 前）。
- `prompts/next-session.md` を次 task（06）に更新。
- PR マージ後 main 同期確認。

## 停止条件

- 既存 docs の本文構造を壊さずに重複削除できない場合 → 範囲を縮小し、philosophy / workflow のトーン差整理だけ別 task に分割。
- レビュー修正 2 周超え。

## 次セッションへ残すこと

- なし（1 セッション完結想定）。
