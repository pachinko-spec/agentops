# Task plan: agentops-reviewer P2 修正セッション

- 親 plan: `2026-04-28-agentops-followup-after-global-review` (archive 済み、PR #26)
- 作業ブランチ: `claude/agentops-followup-after-global-review`
- 日時: 2026-04-28 (Asia/Tokyo)
- 性質: PR #26 マージ前の review-fix 1 周目 (最大 2 周)

## 背景

agentops-reviewer subagent (sanitize 後リトライで成功、agentId `ab18dd35f224247f0`) から以下の P2 指摘を受領:

1. `.agentops/handoffs/README.md:15` 「進行中の引き継ぎだけ」 → 「進行中のハンドオフだけ」 (用語統一漏れ)
2. archive 済み plan.md と 4 tasks の「状態: 進行中」フィールドが残存 (将来監査時の状態判別に影響)
3. `docs/04-model-routing.md:66` の用途範囲表現が誤読されうる (orchestrator/architect は reviewer 用途限定でない)

## 進行順序

1. 修正対象 7 ファイルを Read & Edit
   - `.agentops/handoffs/README.md` ✅ 修正済み
   - archive 内 plan.md ✅ 修正済み
   - archive 内 tasks-01 ✅ 修正済み
   - archive 内 tasks-02 (要 Read & Edit)
   - archive 内 tasks-03 (要 Read & Edit)
   - archive 内 tasks-04 (要 Read & Edit)
   - `docs/04-model-routing.md` ✅ 修正済み
2. 修正後の grep / cat 検証
3. 再レビュー (sanitize 済みプロンプトで agentops-reviewer)
4. P0/P1/P2 が 0 になっていることを確認
5. fixup 用 commit を 1 本追加 → push
6. PR #26 が更新されることを確認 → ユーザーへ最終報告
7. この task-plan は本セッション完結のため、commit 前に archive へ移動する (archive/2026-04-28-agentops-followup-after-global-review/task-plans/ に既存 current.md があるので別 suffix で保存、またはレビューループ範囲を plan 履歴に追記)

## 完了条件

- 再レビューで P0/P1 = 0、P2 残存も妥当な理由で延期された状態
- PR #26 に 1 fixup commit 追加済み
