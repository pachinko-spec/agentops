# task 08 — P1-07: 最小 CI + .gitignore secret 拡張子追加

> 親 plan: `2026-04-28-design-review-p0-p1`  
> 提案 ID: P1-07  
> 優先度: P1  
> 状態: 未着手  
> 想定コスト: S–M（半日）  
> 想定 PR ブランチ: `claude/design-review-impl-p1-07`  
> 依存: task 04（last-reviewed フロントマター完了後に freshness-check job が機能）

---

## 前提条件

- 触ってよい範囲: `.github/workflows/ci.yml`（新規）、`.github/PULL_REQUEST_TEMPLATE.md`（任意）、`.gitignore`、必要なら `docs/09-hooks-quality-gates.md` への参照追記。
- 触らない範囲: 既存 docs 本文、既存 hook 仕様、`config/`。
- 事前確認: GitHub Actions の actionlint / yamllint / markdown-link-check の最新バージョン、リポジトリの GitHub Actions 利用可否（public/private 確認）。
- 業界出典: GitHub Actions docs、一般的 secret hygiene 慣行（`.env*` / `*.key` / `credentials*.json` / `wrangler` secret 等）。

## 不変条件

- 既存 `.gitignore` の行を削除しない。追記のみ。
- 既存 hook（`scripts/hooks/pre-commit` / `pre-push`）と CI の責務分担を明確に保つ（CI は GitHub 側のゲート、hook はローカル fast feedback）。
- secret 値・本番設定を CI yaml に書かない。

## 実行内容

1. `.gitignore` に secret 拡張子を追記（コメント付き）:
   ```
   # secret artifacts (P1-07)
   .env
   .env.*
   *.key
   *.pem
   credentials*.json
   .dev.vars
   # NOTE: wrangler.toml itself is configuration (not secret). Do NOT ignore it.
   # Wrangler secrets must be set via `wrangler secret put`, never committed.
   ```
   `wrangler.toml` は ignore 対象に含めない。`.dev.vars` だけ ignore し、運用上の注記をコメントで残す。
2. `.github/workflows/ci.yml` を新規作成。Job 別に強制 / 可視化を明確に分ける。
   - **fail（強制ブロッカー）**:
     - `actionlint`: `.github/workflows/*.yml` を lint。
     - `yamllint`: `config/*.yml`、`.github/workflows/*.yml`。
     - `markdown-link-check`: `docs/*.md`（`docs/00–17` および以後新設の番号付き Markdown 全件）、`README.md`、`rules/`、`skills/`、`workflows/` の Markdown link を検査。外部 URL の rate limit に配慮（`config.json` で除外設定可能）。broken link は fail。
   - **warn（可視化のみ、fail にしない）**:
     - `freshness-check`: `docs/*.md`（番号付き Markdown 全件）のフロントマター `last_reviewed` / `next_review_by` をパースし、`next_review_by` が今日より過去の docs があれば PR コメントまたは job summary に warn 出力。fail にしない（四半期ごとに pipeline が落ちるのを避ける）。
3. `.github/PULL_REQUEST_TEMPLATE.md` を任意で追加。DbC チェック項目（前提・不変・完了・禁止・停止 / 検証コマンド / 未解決リスク）を最低限。
4. CI の実行コスト試算を `.agentops/reviews/p1-07.md` に書き留める（free tier 内に収まることを確認）。

## 完了条件

- `.gitignore` に secret 拡張子が追記されている。
- `.github/workflows/ci.yml` が存在し、fail 系 3 job (actionlint / yamllint / markdown-link-check) がすべて pass する。warn 系 1 job (freshness-check) が job summary に出力される（fail はしない）。
- 仮 PR で意図的に bad な YAML / dead link を入れて fail 系が reject、古い `last_reviewed` を入れて warn が表示されることを確認。
- Codex cross-review 完了、所見反映済み。
- PR が main にマージされ、以後の全 PR で CI が動く。

## 検証

- `actionlint .github/workflows/ci.yml`
- `yamllint config/`
- `markdown-link-check docs/01-philosophy.md`（ローカル smoke）
- `grep -E "^(\.env|\.env\.\*|\*\.key|\*\.pem|credentials\*\.json|\.dev\.vars)" .gitignore`
- 仮 PR を別ブランチで作成して CI 反応を確認
- `scripts/agentops delegate --to codex --role review_frontier --effort high --input .github/workflows/ci.yml`
- 結果を `.agentops/runs/<timestamp>-p1-07/` に保存、所見を `.agentops/reviews/p1-07.md` に転記。

## 禁止事項

- main 直 push。
- secret 値を CI yaml に書く。
- 既存 `.gitignore` 行を削除する。
- 既存 hook を CI に置き換える（責務を混同しない）。

## 完了時の後処理

- 本ファイルを `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/08-p1-07-ci-and-gitignore.md` へ移す（commit 前、または task 07 で完成した `agentops archive` コマンド経由）。
- `prompts/next-session.md` を次 task（09）に更新。
- PR マージ後 main 同期確認。

## 停止条件

- GitHub Actions が無料枠を超える / private リポジトリで billing が発生する場合 → CI 範囲を縮小（actionlint と yamllint のみ等）し、user 確認。
- markdown-link-check が外部 URL の rate limit で頻繁に false-positive する場合 → 内部 link のみに範囲を絞る。
- `last_reviewed` の形式が task 04 で blockquote になっていてパースが難しい場合 → grep ベースに切り替え。
- レビュー修正 2 周超え。

## 次セッションへ残すこと

- CI 拡張（unit test / lint 拡充）は次 plan の検討事項として `handoffs/` 候補。
