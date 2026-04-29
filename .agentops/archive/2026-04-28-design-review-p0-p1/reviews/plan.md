# Codex cross-review of design-review-p0-p1 plan

> 親 plan: `2026-04-28-design-review-p0-p1`  
> Reviewer: Codex (`scripts/agentops delegate --to codex --role review_frontier --effort high`)  
> Run: `.agentops/runs/20260428T181235+0900-codex-review_frontier/`  
> 主 orchestrator (Claude Opus 4.7) による最終判断: 採用。下記反映後、ユーザー提示。

---

## サマリ判定（Codex）

- 計画全体の採否: **条件付き採用**
- 「9 件の対応関係と実装フェーズ分割は概ね妥当。ただし archive 対象ファイル不一致、CI/freshness の強制条件矛盾、P0-02 の『監視・予防』表現と実装範囲のズレは、承認前に直した方がよい」

## 主 orchestrator の採否判断

- **P0**: 0 件
- **P1**: 4 件、全件反映
- **P2**: 4 件、全件反映（軽量な修正で運用品質改善）
- **P3**: 3 件、軽微修正は反映、運用整理は反映

レビュー修正は 1 周内で完了見込み。CLAUDE.md ループ防止ルール（最大 2 周）の範囲内。

---

## P1 指摘と反映方針

### P1-1. task 03 (P1-02): archive/reference-kit-v1 の実構造誤認

- 指摘: `archive/reference-kit-v1/{rules,skills,workflows}/catalog.md` が存在しない（実体は `README.md` + 個別 rule / workflow ファイル）。検証コマンド `head -3 .../catalog.md` が失敗する。
- 一次裏取り: `find archive/reference-kit-v1 -type f` で確認済み。`rules/README.md`, `workflows/README.md`, `skills/README.md` + 個別ファイル。
- 反映: task 03 の実行内容・検証を「`archive/reference-kit-v1/{rules,skills,workflows}/README.md` の先頭に DEPRECATED 注記を入れる」「個別 rule/workflow Markdown には注記しない」に修正。

### P1-2. task 07 (P1-06): archive README は table 形式

- 指摘: `.agentops/archive/README.md` は table 形式（`| 完了日 | plan-id | サマリ |`）。bullet 行追記の仕様は既存形式を壊す。
- 一次裏取り: `cat .agentops/archive/README.md` で確認済み。table 3 列。
- 反映: task 07 の実行内容・検証を「table の 1 行目（直近）に新 row を挿入」に修正。`--dry-run` も table row を表示。bullet 案は削除。

### P1-3. task 01 (P0-02): 表現と実装範囲のズレ

- 指摘: 計画は `docs/03` と `harness.yml` の追加が中心で、`agentops-watch` の監視実装は含まない。一方で目的・完了条件は「予防」「監視」と読める。
- 反映: task 01 を「機械可読な停止条件 spec の導入」に表現修正。`agentops-watch` 側の警告実装は次 plan へ持ち越し（handoff 対象）。出典 `$47k / 11 日` は「runaway agent の代表事例（一次性弱、参考扱い）」と注記。

### P1-4. task 08 (P1-07) と plan: freshness-check の強制 vs warn の矛盾

- 指摘: plan 全体は freshness check を「強制」と書いているが、task 08 では warn 方針（fail にすると四半期で pipeline が落ちる）。
- 反映: plan / task 08 を統一して「warn ベース（fail にしない）」に揃える。CI 強制対象は actionlint / yamllint / markdown-link-check（broken link 自体の検出は fail）。freshness は可視化のみ。

---

## P2 指摘と反映方針

### P2-1. task 02 (P1-01): 「旧用語 0 件化」の grep が過剰

- 反映: 許容語リスト（`主 orchestrator`、`orchestrator_frontier`、`orchestrator role`）を許可した上で grep。完全 0 件は求めない。

### P2-2. task 06 (P1-03): 双方向マッピング半日見積もりが楽観的

- 反映: 初回 PR は rule 起点の最小表（rule × 関連 skill 1 列、関連 workflow 1 列、関連 hook 1 列）に限定。skill/workflow 側の逆参照列追加は必要なら次 plan へ。

### P2-3. task 04 (P1-04) / task 06 (P1-03): docs/17 も freshness-check 対象

- 反映: plan / task 04 / task 06 / task 08 を「docs 直下の番号付き Markdown 全件（00 / 01–16 / 17 / 以後新設も）」に表現を統一。

### P2-4. task 09 (P1-08): AGENTS.md も 200 行未満目安

- 反映: task 09 完了条件に「AGENTS.md ≤ 200 行を目安、CLAUDE.md ≤ 50 行」を併記。Claude `@import` は context 共有なので CLAUDE.md だけ短縮しても context 削減にならない点を停止条件にも記録。

---

## P3 指摘と反映方針

### P3-1. task 08 (P1-07): wrangler.toml 全体 ignore は不適

- 反映: task 08 の `.gitignore` 追記対象から `wrangler.toml` を除外。`.dev.vars` は維持。コメントで「wrangler secret はリポジトリに置かない」運用注記を残す。

### P3-2. task-plan: P1-02 と P1-06 は並行候補

- 反映: task-plan の実行順表に「03 (P1-02) と 07 (P1-06) は依存なしのため、実装フェーズで並行 PR 可」を追記。

### P3-3. P0-02 の `$47k / 11 日` 出典が一次性弱

- 反映: task 01 の根拠コメントを「runaway agent の代表事例（cordum.io / meganova.ai が引用、一次性は弱い）」に修正。値そのものを harness.yml コメントに固定しない。

---

## 反映後の検証（最終）

- 各 task ファイルの修正を grep で確認。
- 観察事実誤認が再発しないよう task 03 / task 07 の検証コマンドを実構造に合わせる。
- plan 全体の最終レビューを再度 Codex に出すかは、修正が軽微（1 周）であれば省略する（P3 まで含めても全件 1 周内に反映できる範囲）。ユーザーに修正内容を提示して採否確認するのが最終ステップ。

## 学術・公式仕様確認（Codex 一次情報メモ）

- Claude Code は CLAUDE.md から `@AGENTS.md` import を公式に推奨: `code.claude.com/docs/en/memory`
- Codex CLI は `~/.codex/AGENTS.md`、`AGENTS.override.md`、fallback filename、検証方法を公式 docs に明記: `developers.openai.com/codex/guides/agents-md`
- GitHub Actions は public repo 標準 runner は無料、private は quota 超過で課金: `docs.github.com/en/billing/concepts/product-billing/github-actions`
- actionlint は GitHub Actions workflow の静的検査として妥当: `github.com/rhysd/actionlint`

これらは task 09 / task 08 着手時に再確認すること。
