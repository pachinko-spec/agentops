# task 03 — P1-02: archive/reference-kit-v1 deprecation マーカー

> 親 plan: `2026-04-28-design-review-p0-p1`  
> 提案 ID: P1-02  
> 優先度: P1  
> 状態: 未着手  
> 想定コスト: S（30 分）  
> 想定 PR ブランチ: `claude/design-review-impl-p1-02`  
> 依存: なし（task 02 と並行可だが PR 単位で順番）

---

## 前提条件

- 触ってよい範囲: `archive/reference-kit-v1/`、`README.md`（archive を参照している場合）、`config/claude/CLAUDE.md` テンプレ（archive を参照する 1 行が既存）。
- 触らない範囲: 現役 `rules/`、`skills/`、`workflows/` カタログ、`docs/`、archive 配下の個別 rule / workflow Markdown 本文。
- 事前確認: `archive/reference-kit-v1/` の実構造は `rules/README.md` / `skills/README.md` / `workflows/README.md` + 個別ファイル。`catalog.md` は存在しない。`README.md` で archive を参照している記述。
- 業界出典: 一般的 deprecation 慣行（DEPRECATED.md / NOTICE / TOMBSTONE 等）。

## 不変条件

- archive 内の旧版コンテンツは削除・移動しない（参照可能な状態を保つ）。
- 現役カタログ（`rules/catalog.md` など）と混同されない明示マーカーを置く。

## 実行内容

1. `archive/reference-kit-v1/DEPRECATED.md` を新規作成。内容:
   - 廃止日: 2026-04-28（または旧版 archive 化日付。decisions/ から取得）
   - 廃止理由: 現役カタログ（`rules/catalog.md` / `skills/catalog.md` / `workflows/catalog.md`）への参照キット pivot 完了
   - 現役カタログへのリンク
   - 再有効化条件（基本的に「再有効化しない」、必要なら新規 catalog として復活させる）
   - 想定読者: 過去の commit 経由でこの archive にたどり着いた人
2. `archive/reference-kit-v1/{rules,skills,workflows}/README.md` の冒頭に `> DEPRECATED — see /archive/reference-kit-v1/DEPRECATED.md` を 1 行追記。配下の個別 Markdown（`rules/<rule-id>.md` 等）には触れない（README.md の注記から辿れる）。
3. `README.md` で archive を参照している箇所があれば deprecation 注記を補足（必要最小限）。
4. `config/claude/CLAUDE.md` テンプレで archive を参照している行があれば deprecation 注記を補足。

## 完了条件

- `archive/reference-kit-v1/DEPRECATED.md` が存在し、廃止日・理由・現役リンク・再有効化条件が書かれている。
- archive 配下の各 `{rules,skills,workflows}/README.md` 先頭に DEPRECATED 注記がある。
- 新規参照者が現役カタログと archive を混同しない。
- Codex cross-review 完了、所見反映済み。
- PR が main にマージされ、ローカル main が同期。

## 検証

- `ls archive/reference-kit-v1/DEPRECATED.md`
- `head -3 archive/reference-kit-v1/rules/README.md`（DEPRECATED 行が見えること）
- `head -3 archive/reference-kit-v1/skills/README.md`
- `head -3 archive/reference-kit-v1/workflows/README.md`
- `scripts/agentops delegate --to codex --role review_frontier --effort high --input archive/reference-kit-v1/DEPRECATED.md`
- 結果は `.agentops/runs/<timestamp>-p1-02/` に保存、所見を `.agentops/reviews/p1-02.md` に転記。

## 禁止事項

- main 直 push。
- archive の旧版コンテンツ削除・移動・書き換え（各サブディレクトリ `README.md` 先頭への注記行追加のみ許容）。
- 報告書本体への編集。

## 完了時の後処理

- 本ファイルを `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/03-p1-02-deprecation-marker.md` へ移す（commit 前）。
- `prompts/next-session.md` を次 task に更新。
- PR マージ後 main 同期確認。

## 停止条件

- archive 配下の構造が想定と大きく異なる場合（README.md が無い、未知のサブディレクトリがあるなど）→ 構造を本ファイルに書き留めて user 確認。
- レビュー修正 2 周超え。

## 次セッションへ残すこと

- archive をいつか完全削除するかどうかは別 plan の検討事項として `handoffs/` 候補にする（本 task では決めない）。
