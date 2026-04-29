# Plan: 横断設計レビュー 2026-04-28 P0+P1 改善実装

> plan-id: `2026-04-28-design-review-p0-p1`  
> 起票: 2026-04-28 (Asia/Tokyo)  
> 対象: `/home/otaku/agentops` リポジトリ  
> 主 orchestrator: Claude Opus 4.7 (1M)  
> Reviewer (cross-model): Codex CLI（GPT-5.5 系）。所見のみ、最終判断は主 orchestrator  
> 出典: `docs/reviews/2026-04-28-cross-repo-design-review.md` (PR #27, `07d26f4` で main マージ済み)

---

## 1. 背景

横断設計レビュー報告書 §7 で列挙された改善提案 18 件のうち、**P0 = 1 件 / P1 = 8 件 = 計 9 件**を 1 plan で潰す。報告書 §9 ロードマップで「1–2 週」「1 ヶ月」に該当。P2 / P3 は本 plan に含めず、次以降の plan に分ける（依存関係を見ながら段階的に潰す方針）。

報告書の観察事実は本 plan 起票時に裏取り済み。`.github/` 不在、`.gitignore` の secret 拡張子未列挙、`archive/reference-kit-v1/` の deprecation マーカー不在、`docs/01–16` に `last-reviewed` 不在、CLAUDE.md / AGENTS.md 47 行ずつの対称運用、すべて報告書記述と一致。

## 2. 目的

- P0-02 で tool 実行層の停止条件（max_tool_calls / no_progress / circuit_breaker / cost_cap）を `docs/03` + `config/harness.yml` に導入し、業界事例（cordum.io 引用 $47k/11 日 loss）を予防する。
- P1-01〜P1-08 で次の評価軸別スコア改善を達成する。
  - A 一貫性 B → A
  - B 契約と停止 B+ → A
  - C マルチモデル A− → A
  - D 鮮度 B− → B+
  - E 運用負荷 B− → B+
  - F 拡張性 B → B+

## 3. 非目的

- P2 / P3 提案 9 件は本 plan の対象外。次以降の plan で扱う。
- グローバル `~/.claude/CLAUDE.md` への実反映作業。本 plan は `config/claude/CLAUDE.md` 雛形までを範囲とする。
- 学術論文の採録・引用件数の追加検証（残存不確実性として明記）。
- L コスト提案（P3-01 replay-driven テスト等）の取り込み。
- model-routing の `model_id` 確定（意図的 null を維持）。

## 4. 影響範囲

| 領域 | 変更対象 | 種別 |
|---|---|---|
| docs | `docs/00-glossary.md`（新規）, `docs/03`, `docs/01`, `docs/09`, `docs/12`, `docs/17-cross-reference.md`（新規）, `docs/01–16` 全件にフロントマター | 追加・編集 |
| config | `config/harness.yml`, `config/claude/CLAUDE.md`, `config/codex/AGENTS.md` | 編集 |
| ルート | `CLAUDE.md`, `AGENTS.md`, `.gitignore` | 編集 |
| archive | `archive/reference-kit-v1/DEPRECATED.md`（新規） + 各 catalog 先頭注記 | 追加・編集 |
| scripts | `scripts/agentops` または `scripts/hooks/` 拡張 | 追加・編集 |
| CI | `.github/workflows/ci.yml`（新規）, `.github/PULL_REQUEST_TEMPLATE.md`（任意） | 追加 |

## 5. 完了条件

- 本 plan 配下の親 task 9 件すべてが各 PR としてマージされ、`main` に取り込まれている。
- 各 PR は Codex で cross-review 済み、P0/P1 所見が反映済み。`runs/` に実行記録あり。
- 報告書 §3 の評価軸スコアが §2 の目的通りに改善できる差分になっている（再評価は次回設計レビュー）。
- 各 task の完了条件（個別 task ファイル参照）をすべて満たしている。
- `.agentops/archive/2026-04-28-design-review-p0-p1/` 配下に plan.md / task-plan / tasks / reviews / runs が移動済み。
- `.agentops/archive/README.md` に本 plan のサマリ行が追加済み。
- 全 CI が green。`.github/workflows/ci.yml` が `actionlint` / `yamllint` / `markdown-link-check` を強制（fail）し、`freshness-check` を可視化（warn のみ、fail にしない）として実行している（task 08 完了後）。

## 6. 停止条件（plan レベル）

- 報告書の観察事実と現リポジトリ状態に新たな食い違いが見つかった場合 → ユーザー確認。
- レビュー修正が 2 周を超えそうな task が出た場合 → 統合判断またはユーザー確認。
- secret / 本番データ / 課金 / 外部公開 / 破壊的操作が必要になった場合（本 plan 範囲では発生想定なし）。
- AAIF 公式の `@AGENTS.md` import 仕様が CLAUDE.md 公式 docs（`code.claude.com/docs/en/memory`）の現在仕様と食い違う場合（task 09 着手時に確認）。
- task 単独で半日を大きく超えるコスト見込みになった場合 → plan 分割を検討。

## 7. 検証方針

- 各 task は実装 → 自己レビュー → Codex cross-review → P0/P1 反映 → PR 作成 → main マージ。
- 共通検証コマンド: `git status --short --branch`, `python3 -m compileall tools`, `scripts/agentops doctor`（存在時）, `scripts/agentops-watch check`（存在時）, grep による旧用語 / 旧フォーマット 0 件確認。
- task 08 (P1-07) 完了以降は CI の fail 系（actionlint / yamllint / markdown-link-check）が全 PR でブロッカーとして機能。freshness check は warn のみで fail にしない。
- plan 全体の最終レビューも Codex に委譲し、所見を反映してから完了宣言。

## 8. 親 task 一覧（依存順）

| # | task ファイル | ID | タイトル | コスト | 依存 |
|---|---|---|---|---|---|
| 01 | `tasks/01-p0-02-tool-stop-conditions.md` | P0-02 | tool 実行層停止条件を docs/03 + harness.yml に追加 | M（1 日） | なし |
| 02 | `tasks/02-p1-01-glossary.md` | P1-01 | 用語統一表 docs/00-glossary.md 追加 + 旧用語 0 件化 | S（2h） | 01 |
| 03 | `tasks/03-p1-02-deprecation-marker.md` | P1-02 | archive/reference-kit-v1 deprecation マーカー | S（30m） | なし（02 と並行可） |
| 04 | `tasks/04-p1-04-last-reviewed.md` | P1-04 | docs/01–16 に last-reviewed フロントマター追加 | S（1h） | 02 |
| 05 | `tasks/05-p1-05-dbc-consolidation.md` | P1-05 | DbC 記述を docs/03 に集約 | S（1h） | 02 |
| 06 | `tasks/06-p1-03-cross-reference.md` | P1-03 | rule ↔ skill ↔ workflow ↔ hook 逆参照テーブル | M（半日） | 02 |
| 07 | `tasks/07-p1-06-archive-auto-update.md` | P1-06 | archive 自動更新 hook | M（半日） | なし |
| 08 | `tasks/08-p1-07-ci-and-gitignore.md` | P1-07 | 最小 CI + .gitignore secret 拡張子追加 | S–M（半日） | 04 |
| 09 | `tasks/09-p1-08-agents-md-unify.md` | P1-08 | AGENTS.md 一本化 + CLAUDE.md は import + 差分のみ | M（半日） | 02, 04, 05, 06 |

合計 9 PR。コスト 4–5 日想定（半日〜1 日 / PR）。

## 9. クロスレビュー方針

- 各 task 実装完了後に `scripts/agentops delegate --to codex --role review_frontier --effort high --input <該当ファイルまたは PR diff>` で Codex に委譲。
- 委譲依頼 / stdout / stderr / 結果は `.agentops/runs/<timestamp>-<task-id>/` に保存。secret は記録しない。
- 主 orchestrator（Opus 4.7）が最終判断権を保持。Codex は所見のみ。これは `docs/04-model-routing.md` cross-review 節 / `docs/05-review-policy.md` 最終判断節 / user グローバル `~/.claude/CLAUDE.md` クロスモデル委譲節と一致。
- plan 全体の最終レビューも Codex に委譲し、所見を反映してマージ判断。

## 10. ブランチ運用

- 本 plan の起票・計画ファイル作成は `claude/design-review-2026-04-28` ブランチで行う。
- 実装フェーズは別ブランチ `claude/design-review-impl-p0-p1` を main から切り直す。1 task = 1 PR で運用するため、必要に応じてさらに `claude/design-review-impl-p0-p1-<task-id>` のような子ブランチへ細分化する。
- main 直 push 禁止、`claude/` プレフィックス必須。
- 各 PR は GitHub 上でマージし、ローカル main は `git fetch && git status` で同期確認。

## 11. リスクと未解決事項

- **task 09 (P1-08) の import 仕様**: `@AGENTS.md` import が Claude Code / Codex 両方で確実に動作するか、着手前に公式 docs 再確認。動かない場合は symlink / include script の代替を検討。
- **CI コスト**: GitHub Actions が無料枠を超えないか確認。public なら問題なし。
- **archive 自動更新 hook の発火タイミング**: pre-commit / post-commit / 手動 CLI のどれが最適か task 07 実装時に決定。
- **last-reviewed の自動鮮度チェック**: task 08 で freshness-check job 実装方針を確定（GitHub Action 内 bash で日付計算）。
- **本 plan 進行中に Claude Code / Codex / AAIF が大きな仕様変更を発表した場合**: 該当 task の前提が変わるため、stop して plan 見直し。

## 12. 関連リンク

- 報告書本体: `docs/reviews/2026-04-28-cross-repo-design-review.md`
- Plan agent ファイル: `~/.claude/plans/2026-04-28-design-review-p0-p1.md`
- 親 plan (この plan): `.agentops/plans/current.md`（archive 後は `.agentops/archive/2026-04-28-design-review-p0-p1/plan.md`）
- 各 task 詳細: `.agentops/tasks/01-09-*.md`
- task-plan（セッション実行計画）: `.agentops/task-plans/current.md`
