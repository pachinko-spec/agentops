# Task 02: 表記揺れ / 用語ぶれ統一

- 親 plan: `2026-04-28-agentops-followup-after-global-review`
- 状態: 進行中

## 経緯

PR #25 (運用ルール反映) のレビューで「表記揺れ / 用語ぶれ統一」が P3 として残った。事前 grep で以下の揺れが顕著:

| 術語 | 揺れパターン | 出現件数 |
|---|---|---|
| ハンドオフ | `ハンドオフ` (86) vs `引き継ぎ` (25) vs `申し送り` (少数) | 111 |
| 主 orchestrator | `主エージェント` / `メインエージェント` / `主 agent` / `主 orchestrator` | ~13 |
| cross-review | `クロスレビュー` / `cross-review` / `クロス・レビュー` | 多数 |
| cross-model | `クロスモデル` / `cross-model` / `クロス・モデル` | 19 |
| task-plan | `task-plan` (74) vs `実行計画` (7) | 81 |

## 方針 (スコープ限定)

**全置換ではない**。術語 (機能名 / コード近似名 / 判断主体名) として使われている箇所のみ統一し、日常語の文中表現は残す。

1. **`ハンドオフ` 統一**: `.agentops/handoffs/` の機能を指す箇所のみ。日常語の「引き継ぎ」「申し送り」は残す
2. **`主 orchestrator` 統一**: モデル選定の判断主体を指す術語のみ。日常語の「エージェント」「主担当」は残す
3. **`cross-review` / `cross-model` 統一**: 半角ハイフン形 (英字) に揃える。日本語側「クロスレビュー」「クロスモデル」が文中で自然な箇所は残す
4. **`task-plan` 統一**: handoff/task-plan 機能を指す術語のみ。「実行計画」は日常語として残す

## 実行内容

- 各キーワードを `grep -rn` で列挙
- 1 ヒットずつ「術語か日常語か」を判断
- 術語なら統一形へ書き換え
- 変更想定ファイル: `docs/02-workflow.md`, `docs/04-model-routing.md`, `docs/05-review-policy.md`, `docs/15-reference-kit-structure.md`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `.agentops/handoffs/README.md`, `rules/catalog.md`, `skills/catalog.md`, `workflows/catalog.md`

## 検証

- 統一後の `grep` で術語使用箇所がすべて統一形に揃っていること (日常語残存は OK)
- AGENTS.md と CLAUDE.md の対応箇所で同じ術語に揃っていること
- 各 catalog (rules/skills/workflows) でクロスリファレンス整合

## 停止条件

- 全置換が必要かどうかで判断が割れる → ユーザー確認
- 修正規模が想定 (~30 ヒット) を大きく超える → 別 task に切り出し

## 次セッションへ残すこと

なし
