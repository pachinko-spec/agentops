# Plan: agentops 参照キット反映 (グローバル model/hook 決定 + PR 残課題整理)

- plan-id: `2026-04-28-agentops-followup-after-global-review`
- 作業ブランチ: `claude/agentops-followup-after-global-review`
- 開始日: 2026-04-28
- 状態: 進行中

## 背景

直前セッション (`~/.claude/.agentops/archive/2026-04-28-claude-global-model-haiku-hook-review/`) で、`~/.claude` グローバル設定に対して以下が確定した:

- **Phase A**: `model-catalog.yml` の `*_frontier` 系 Codex 候補に GPT 高推論モデル (例: gpt-5.5 系) を採用。出典 5 URL を header に付記。`ChatGPT auth 限定 / API key auth では下位 model へ override` を notes に明記。
- **Phase B**: agents 2 件 + catalog 3 ロール、計 5 箇所の haiku を `claude-sonnet-4-6` へ置換。`model_family` を `fast *` → `balanced *` 化。サブスクプラン下で品質優先 baseline 化。
- **Phase C**: `agentops_guard.py` (380 行集約) を `_common.py` + 6 event handler へ分散。`SECRET_PATTERNS` の OpenAI 型 prefix を否定先読み付きへ修正。`PermissionRequest` を settings.json に登録して live 化。Python 維持理由を明文化。

これらグローバル個別実装を、agentops 参照キット側に **採用例 / 判断方針** として、雛形の advisory 性 (`model_id: null` 方針、固定 model 名を docs に埋めない方針、agentops は実フックを持たない方針) を壊さずに反映する。

## 目的

1. PR #24 残 P2: `AGENTS.md` から `CLAUDE.md` への対称クロスリファレンス追加
2. PR #25 残 P3: 表記揺れ / 用語ぶれ統一 (術語のみ、日常語は残す)
3. Phase A: `config/model-catalog.yml` notes と `docs/04-model-routing.md` に採用例 (advisory) 追記
4. Phase B: `docs/09-hooks-quality-gates.md` に AI エージェント hook 設計方針メモ追記

## 親 task 一覧

- [tasks-01-symmetric-cross-reference.md](../tasks/tasks-01-symmetric-cross-reference.md) — AGENTS.md → CLAUDE.md 逆リンク追加
- [tasks-02-terminology-consistency.md](../tasks/tasks-02-terminology-consistency.md) — 表記揺れ統一
- [tasks-03-model-routing-adoption.md](../tasks/tasks-03-model-routing-adoption.md) — モデルルーティング雛形 / docs に採用例追記
- [tasks-04-hook-design-policy.md](../tasks/tasks-04-hook-design-policy.md) — フック設計方針メモ追記

## 完了条件

- 4 task すべて完了し、対応する archive へ移動
- agentops-reviewer 独立レビューで P0/P1 が 0
- PR 作成、GitHub 上でマージ、main 同期確認

## 停止条件

- archive を読んでも採用判断が確定不能 → ユーザー確認
- B のフック雛形新設が広範囲に及ぶ → 別 plan に切り出してユーザー承認
- グローバル決定が agentops 既存設計思想と整合しない → 統合判断をユーザーに相談
- レビュー修正 2 周超過
- 機密値 / 破壊的操作 / スコープ大幅拡張

## 参照

- 一次情報: `~/.claude/.agentops/archive/2026-04-28-claude-global-model-haiku-hook-review/`
- 設計原案: `/home/otaku/.claude/plans/claude-code-refactored-candy.md`
