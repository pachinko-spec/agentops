# Task plan: agentops 参照キット反映 セッション

- 親 plan: `2026-04-28-agentops-followup-after-global-review`
- 作業ブランチ: `claude/agentops-followup-after-global-review`
- 日時: 2026-04-28 (Asia/Tokyo)

## 進行順序

1. **Task 001 (軽量・独立)**: `AGENTS.md` 3 行目直後に CLAUDE.md と対称な相互参照 1 行を追加。文言を `CLAUDE.md` 側と完全対称にする
2. **Task 002 (中程度・独立)**: 表記揺れ統一。grep ベースで 1 ヒットずつ術語/日常語を判断
   - `ハンドオフ` 統一 (handoff 機能の術語のみ)
   - `主 orchestrator` 統一 (モデル選定の判断主体を指す術語のみ)
   - `cross-review` / `cross-model` 統一 (コード近似の術語表記)
   - `task-plan` 統一 (機能を指す術語のみ)
3. **Task 003 (順序依存)**: グローバル A 決定の引き写しを advisory に
   - `config/model-catalog.yml` 各ロール notes に採用例 (advisory) 追記。`model_id: null` は維持
   - `docs/04-model-routing.md` に「採用例 (参考)」節追加。系列表記 (例: `gpt-5.5 系`、`claude-sonnet-4-6 系`) のみ、固定 model id は埋めない
   - `templates/claude/` 内のステール参照点検、軽微編集のみ
4. **Task 004 (順序依存)**: `docs/09-hooks-quality-gates.md` 末尾に AI エージェント hook 設計方針メモ節追加
   - 構成 / 言語選定 / secret 検知単語境界 / live 判定 / コメント言語の 5 観点
   - 雛形コードは載せない (実フックを持たない方針継続)
5. **検証**: `git diff --stat`、`grep -rn "haiku" --include='*.md' --include='*.yml'` 0 件、章立て対称確認、術語統一確認
6. **レビュー**: `agentops-reviewer` 独立レビュー (最大 2 周)
7. **archive 移動**: commit 前に plan / task-plan / tasks 4 本を `archive/2026-04-28-agentops-followup-after-global-review/` 配下へ移動。`archive/README.md` 時系列インデックスへ 1 行追加
8. **commit / push / PR**: 4 commit (task 単位)、push、`gh pr create`、GitHub 上でマージ、main 同期確認

## 時間予測

- Task 001: 5 分
- Task 002: 30 分 (grep + 個別判断)
- Task 003: 25 分
- Task 004: 15 分
- 検証 + レビュー + 修正: 30 分
- archive 移動 + commit + PR: 15 分

合計: ~2 時間
