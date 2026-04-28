# Next session プロンプト（2026-04-28 plan 完結後）

parent_plan: 2026-04-28-cross-repo-design-review（archive 済み）
status: pending
created_at: 2026-04-28
timezone: Asia/Tokyo

## 状況

- plan「2026-04-28-cross-repo-design-review」は実装・自己レビュー・cross-review・修正反映・archive まで完了。
- PR #27 を `claude/design-review-2026-04-28` ブランチで作成済み。GitHub 上でユーザーレビュー → マージ承認待ち。
- リポジトリ内の plan / task-plan / tasks 直下は空（README.md のみ）。完了 task は `.agentops/archive/2026-04-28-cross-repo-design-review/` に格納済み。

## 次セッションでの残作業

1. PR #27 (https://github.com/pachinko-spec/agentops/pull/27) のレビュー結果を確認。指摘があれば P0/P1/P2/P3 で分類のうえ、最大 2 周のレビュー修正ループで対応（既に self-review + Codex cross-review を 1 周ずつ通しているため、3 周目は統合判断またはユーザー確認）。
2. main マージ後、ローカルで:
   - `git checkout main`
   - `git fetch origin`
   - `git status --short --branch` で `main...origin/main` 同期確認
   - 同期完了したら本ファイル（`.agentops/prompts/next-session.md`）を削除
3. 残った `.claude/scheduled_tasks.lock`（Claude Code ScheduleWakeup ランタイムが生成する一時ロックファイル）は plan 外。本 PR スコープを汚さないため commit 対象から除外したが、後続 plan（提案 P1-07: 最小 CI + `.gitignore` 拡充）で `.gitignore` に `.claude/` と secret 拡張子を追加することで根本解消する。次に `.gitignore` を触るときに合わせて入れる。

## 触らないこと

- 本セッションで追加した報告書 `docs/reviews/2026-04-28-cross-repo-design-review.md` は cross-review 反映済みの最終版。新規 plan で改善提案を実装する作業は別 plan として起票する。
- 18 件の改善提案（P0=1 / P1=8 / P2=6 / P3=3）の実装はそれぞれ独立 plan で扱う。本ファイルでは触れない。

## 停止条件

- PR レビュー指摘で 2 周を超えそうな場合はユーザー確認。
- main マージ前に追加機能・依存変更が必要になる場合は新 plan を起こしてから着手。
