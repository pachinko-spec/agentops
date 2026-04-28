# Task Plan: 設計レビュー報告書 起草・検証・委譲セッション

plan_id: 2026-04-28-cross-repo-design-review
status: in-progress
created_at: 2026-04-28
timezone: Asia/Tokyo

## 今回の目的

`docs/reviews/2026-04-28-cross-repo-design-review.md` を約 12,000 字で起草し、出典・引用検証を経て、Codex 側 cross-review まで実行して取り込みを完了させる。

## 実行順

1. 既存 docs（01-philosophy.md / 03-dbc / 04-model-routing.md / 12-harness / 13-design-evaluation.md）と CLAUDE.md / AGENTS.md / config を必要箇所だけ確認。Phase 1 / 2 結果は plan ファイルに既に集約済みなので過剰な再読は避ける。
2. `docs/reviews/2026-04-28-cross-repo-design-review.md` を Write で一括生成（章立て §0–§10 + Appendix A/B）。
3. 出典 URL の生存確認（curl -sIL）を実行し、結果を Appendix A の表へ反映。
4. リポジトリ内引用パス（docs/01-..., config/..., rules/... など）を `ls` で存在確認。
5. 自己レビューを review / review-loop-guard skill で実施し、修正があれば反映。
6. cross-model レビューを `scripts/agentops delegate --to codex --role review_frontier --input docs/reviews/2026-04-28-cross-repo-design-review.md` で実行（dry-run 先行 → 本実行）。
7. Codex 所見を P0/P1/P2/P3 で分類し、必須修正を反映。レビューループは最大 2 周。
8. 完了タスクと plan を `.agentops/archive/2026-04-28-cross-repo-design-review/` へ移動、`archive/README.md` 時系列インデックスに行追加。`prompts/next-session.md` は現状不要なので生成しない（残作業なしで完結する見込み）。
9. commit → push → PR 作成（日本語本文）。

## 今回は行わないこと

- 提案項目の実装（P0/P1 を含め、別 plan で扱う）。
- グローバル `~/.claude/CLAUDE.md` への反映。
- 既存 docs/13-design-evaluation.md の改廃（報告書からの参照のみ）。
- cross-review 結果を待たずに最終マージすること。

## 停止条件

- 出典 URL 半数以上が dead の場合、ユーザー確認。
- Codex 委譲が 2 回連続 timeout / 失敗した場合、設定を確認したうえでユーザー判断を仰ぐ。
- レビュー修正が 2 周を超えそうな場合、統合判断またはユーザー確認。
- 報告書中で扱う固有名詞（ABC 論文 ID, AAIF 設立日等）に誤認が見つかった場合、訂正してから先へ進む。
