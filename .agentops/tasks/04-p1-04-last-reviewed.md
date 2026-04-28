# task 04 — P1-04: docs/01–16 に last-reviewed フロントマター追加

> 親 plan: `2026-04-28-design-review-p0-p1`  
> 提案 ID: P1-04  
> 優先度: P1  
> 状態: 未着手  
> 想定コスト: S（1 時間）  
> 想定 PR ブランチ: `claude/design-review-impl-p1-04`  
> 依存: task 02（glossary）完了後（用語統一が反映された状態でフロントマターを追加）

---

## 前提条件

- 触ってよい範囲: `docs/` 直下の番号付き Markdown 全件（`docs/00-glossary.md` task 02 新規 / `docs/01–16` 既存 / `docs/17-cross-reference.md` task 06 新規）と、本 plan 完了後に新設される番号付き docs があればそれも対象に含める設計。
- 触らない範囲: 本文の意味変更、`docs/reviews/`、`archive/`、サブディレクトリ docs。
- 事前確認: 報告書冒頭のフロントマター形式（`> 評価日: ... > last-reviewed: 2026-04-28 > next-review-by: 2026-07-31 > 言語: 日本語`）と整合。
- 業界出典: AAIF agents.md の updated 日付推奨、Anthropic Managed Agents の append-only event log 思想。

## 不変条件

- 既存の本文・章立てを変更しない（フロントマター追加のみ）。
- フロントマター形式は YAML 風 quoted block style と Markdown blockquote style のどちらかに統一（task 08 の CI freshness-check で機械可読にできること）。
- すべての docs で同一形式・同一順序・同一キー名。

## 実行内容

1. フロントマター形式を選択する（推奨: YAML フロントマター。CI でパースしやすい）。
   ```yaml
   ---
   last_reviewed: 2026-04-28
   next_review_by: 2026-07-31
   reviewer: pachinko-spec
   language: ja
   ---
   ```
   または既存報告書に合わせた blockquote style:
   ```md
   > last-reviewed: 2026-04-28
   > next-review-by: 2026-07-31
   > reviewer: pachinko-spec
   > 言語: 日本語
   ```
2. `docs/` 直下の番号付き Markdown 全件（`00-glossary.md`、`01-16` 既存、`17-cross-reference.md` task 06 新規）の冒頭にフロントマターを追加。task 06 が本 task より前に完了している場合は `docs/17` も対象。後から完了する場合は task 06 のチェックリストに「フロントマター追加」を含めて漏れを防ぐ。
3. 形式選択の根拠を `docs/06-freshness-and-monitoring.md` に 1 段落で記録。
4. `next_review_by` は四半期後の 2026-07-31 を既定とし、ファイルごとにずらす必要がない。

## 完了条件

- `docs/` 直下の番号付き Markdown 全件にフロントマターが入っている（task 06 の `docs/17` も含むこと、依存順上 task 06 完了後の状態を想定）。
- `rg -L "^last_reviewed|^> last-reviewed" docs/[0-9]*.md` の結果が空。
- 形式選択の根拠が `docs/06` に記録されている。
- Codex cross-review 完了、所見反映済み。
- PR が main にマージされ、ローカル main が同期。

## 検証

- `rg -L "^last_reviewed|^> last-reviewed" docs/[0-9]*.md` が空
- `rg "^last_reviewed: 2026-04-28" docs/[0-9]*.md` の件数が docs/ 直下の番号付き Markdown 全件と一致（task 04 と task 06 の完了順により 17 件または 18 件）
- `python3 -m compileall tools`
- `scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/06-freshness-and-monitoring.md`（フロントマター形式選択の妥当性を中心にレビュー）
- 結果を `.agentops/runs/<timestamp>-p1-04/` に保存、所見を `.agentops/reviews/p1-04.md` に転記。

## 禁止事項

- main 直 push。
- 本文の意味変更（フロントマター追加のみ）。
- フロントマター形式の docs ごとの不統一。
- 報告書本体や archive への編集。

## 完了時の後処理

- 本ファイルを `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/04-p1-04-last-reviewed.md` へ移す（commit 前）。
- `prompts/next-session.md` を次 task（05）に更新。
- PR マージ後 main 同期確認。

## 停止条件

- フロントマター形式の選択で markdown link check や既存 docs ビルドツールが壊れる場合 → 形式を blockquote 互換に変更し、CI freshness-check を grep ベースに切り替える。
- レビュー修正 2 周超え。

## 次セッションへ残すこと

- task 08（P1-07 CI）で freshness-check job が本フロントマターをパースする。形式が変わった場合は task 08 へ申し送り。
