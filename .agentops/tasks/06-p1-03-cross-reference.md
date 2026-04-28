# task 06 — P1-03: rule ↔ skill ↔ workflow ↔ hook 逆参照テーブル

> 親 plan: `2026-04-28-design-review-p0-p1`  
> 提案 ID: P1-03  
> 優先度: P1  
> 状態: 未着手  
> 想定コスト: M（半日）  
> 想定 PR ブランチ: `claude/design-review-impl-p1-03`  
> 依存: task 02（glossary 確定後）

---

## 前提条件

- 触ってよい範囲: `docs/17-cross-reference.md`（新規）、`rules/catalog.md`、`skills/catalog.md`、`workflows/catalog.md`。必要なら `scripts/hooks/`、`scripts/install-hooks` のドキュメント参照。
- 触らない範囲: docs 既存、`templates/`、`config/`、`archive/`、報告書本体。
- 事前確認: rules/catalog.md L7-L18 の 12 候補、skills/catalog.md の 31 候補、workflows/catalog.md の 15 候補、scripts/hooks/{pre-commit, pre-push}。
- 業界出典: AAIF monorepo パターン、Claude Code public docs の skills / hooks 設計。

## 不変条件

- 既存 catalog.md の項目数・ID・意味を変更しない。列を追加するのみ。
- 新規 docs/17 は他 docs と章立て規約を揃える（last-reviewed フロントマター含む。task 04 後なら同形式）。
- 参照は双方向にする（rule から skill / hook を辿れ、skill から rule を辿れる）。

## 実行内容

本 task は **初回 PR では rule 起点の最小表に限定**する（rule 12 × skill 31 × workflow 15 を全て双方向マッピングするのは半日では収まらないため、Codex cross-review 所見 P2-2 を反映してスコープ縮小）。

1. `docs/17-cross-reference.md` を新規作成。内容:
   - **rule 起点の最小マッピング表**: 列は `rule_id / rule タイトル / 関連 skill (代表 1 件) / 関連 workflow (代表 1 件) / 関連 hook (代表 1 件)`。
   - 例: `rule: 保護ブランチ直 push 禁止` → `skill: protected-branch-check`（仮）/ `workflow: pr-creation` / `hook: scripts/hooks/pre-push`。
   - 該当が無い rule は明示（`—` または `（該当なし）`）。
2. `rules/catalog.md` の各行に `関連 skill / workflow / hook` 列を追加（既存列を破壊せず末尾に追加）。各列は代表 1 件で OK。
3. **skills/catalog.md と workflows/catalog.md への列追加は本 task 範囲外**。逆参照（skill → rule、workflow → rule）が必要なら次 plan へ持ち越す。`次セッションへ残すこと` に handoff 候補として記録。
4. `docs/17` の冒頭から `rules/catalog.md` へリンクを張り、`rules/catalog.md` から `docs/17` への戻りリンクも張る。

## 完了条件

- `docs/17-cross-reference.md` が新規追加されている（rule 起点の最小表）。
- 全 rule に対して関連 skill / workflow / hook の代表 1 件が対応している（該当なしなら明示）。
- `rules/catalog.md` から `docs/17` への戻りリンクがある。skills / workflows 側の列追加は本 task 範囲外。
- Codex cross-review 完了、所見反映済み。
- PR が main にマージされ、ローカル main が同期。

## 検証

- `rg -n "^\| " rules/catalog.md`（行数が変わらず、列が増えていること）
- `ls docs/17-cross-reference.md`
- `rg -n "docs/17" rules/catalog.md`
- `python3 -m compileall tools`
- `scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/17-cross-reference.md`
- 結果を `.agentops/runs/<timestamp>-p1-03/` に保存、所見を `.agentops/reviews/p1-03.md` に転記。

## 禁止事項

- main 直 push。
- 既存 rule / skill / workflow の意味・ID 変更。
- スコープ外の catalog リファクタ。
- 報告書本体や archive への編集。

## 完了時の後処理

- 本ファイルを `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/06-p1-03-cross-reference.md` へ移す（commit 前）。
- `prompts/next-session.md` を次 task（07）に更新。
- PR マージ後 main 同期確認。

## 停止条件

- 関連付けが未確定な rule / skill が多く半日で終わらない場合 → 主要な rule（保護ブランチ、cross-review、freshness）からの最小マッピングだけ反映し、残りは次 plan へ。
- レビュー修正 2 周超え。

## 次セッションへ残すこと

- skills/catalog.md と workflows/catalog.md への逆参照列追加（skill → rule、workflow → rule）は本 task 範囲外。`handoffs/2026-MM-DD-cross-reference-skill-workflow-side.md` として残し、次 plan の検討対象にする。
- 残った未対応 rule のマッピングは同 handoff に追記。
