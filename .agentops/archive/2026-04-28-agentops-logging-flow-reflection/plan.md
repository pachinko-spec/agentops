# agentops 運用ルール反映計画

plan_id: 2026-04-28-agentops-logging-flow-reflection
status: in-progress
created_at: 2026-04-28
作業ブランチ: claude/agentops-logging-rule-reflection

## Context

2026-04-28 に Claude Code グローバル側 (~/.claude/) で `.agentops/` 運用ルールを階層化する作業が完了した（PR #24 完了、`~/.claude/.agentops/archive/2026-04-28-claude-global-agentops-logging-rule/` に記録）。確立した新ルールは 4 点。

1. ファイル責務階層: `plans/current.md`（承認済み大計画 1 つ、親 task 一覧必須）／ `tasks/*.md`（plan 内の PR 単位作業、新作業は次番号ファイル）／ `handoffs/`（plan で考えた task の範囲を超えた持ち越しのみ — 別 plan 申し送り、長期 blocker、計画外観察事項）／ `prompts/next-session.md`（動的: tasks 未完了→tasks ベース／なければ handoffs ベース／両方なければ削除）
2. 運用フロー: 計画提示→承認→実装着手前に `plans/current.md`, `task-plans/current.md`, `tasks/*.md` 生成→実装・検証・レビュー→commit 前に完了 task と plan 類を `archive/<plan-id>/` へ移動
3. 完了 handoff は `archive/<plan-id>/handoffs/` へ。`handoffs/` 直下は進行中のみ
4. `archive/README.md` は完了 plan の時系列インデックス（完了日・plan-id・サマリを新しい順）

agentops プロジェクトは設計思想の正本を保守するリポジトリ。グローバル側 CLAUDE.md と本リポジトリ docs の意味が乖離した状態を残さない。

## 親 task 一覧

- tasks-01-docs-readme-update — 全 docs / README 更新 + `next-session.md` 削除 + `prompts/README.md` 新規 + 雛形同期
- tasks-02-independent-review — agentops-reviewer subagent 独立レビュー → 必要に応じ修正

## スコープ

ドキュメント反映のみ。コードや CLI の挙動は変更しない。

### 反映対象

1. `docs/02-workflow.md` — 既存 L11-16 の責務リストを 3 列テーブル（パス・役割・解像度）に置換し、`reviews/`, `runs/`, `prompts/next-session.md` 行を追加。`prompts/next-session.md` 行は動的判定ルールを含める。`handoffs/` 行は「plan で考えた task の範囲を超えた持ち越しのみ。PR 単位の進捗には使わない」を含める。標準サイクル L19-44 はステップ 6・23 の表記を「実装着手前生成」「commit 前 archive 移動」に微調整するに留める。ハンドオフ節 L86-96 に同様の限定文を追記。
2. `.agentops/archive/README.md` — 既存「構成」セクションを残しつつ、完了 plan 時系列インデックスを冒頭に追加。既存 10 件 + 今回完了分（合計 11 件）を新しい順に列挙。`plan.md` を持たない 5 件は `task-plans/` 等からサマリを推定し、リンク先は plan-id ディレクトリにする。
3. `.agentops/prompts/next-session.md` — 削除。
4. `.agentops/handoffs/README.md` — 「plan で考えた task の範囲を超えた持ち越しのみ。PR 単位の進捗には使わない」を明文化。完了 handoff の `archive/<plan-id>/handoffs/` 移動も明記。
5. `.agentops/tasks/README.md` — 「PR 単位、新作業は次番号ファイル」を補強。`agentops-watch` の挙動と「commit 前 archive 移動」の整合を一文追加。
6. `.agentops/prompts/README.md` — 新規作成。`next-session.md` の動的判定責務を記述。
7. `templates/agentops/prompts/next-session.md` — 雛形側も新ルールに合わせて再構成。
8. `docs/15-reference-kit-structure.md` L34 — `prompts/next-session.md` 参照文言調整。

## 検証

1. `git diff` で意図差分のみか目視確認。
2. docs/02-workflow.md の責務テーブルと各 README の表現整合。
3. 既存 docs（07-global-vs-project.md / 15-reference-kit-structure.md / 16-global-settings-application-checklist.md）と非矛盾確認。
4. archive インデックス 11 件のリンク切れ・サマリ欠落確認。
5. agentops-reviewer subagent で P0/P1 ゼロ確認。

## 停止条件

- 既存 docs と大きな矛盾発生
- レビュー修正 2 周超過
- 機密値・破壊的操作・スコープ大幅拡張
- archive 既存 5 件のサマリ推定不能レベル

## スコープ外

- リポジトリ直下 AGENTS.md / CLAUDE.md
- ~/.claude グローバル側
- ルート直下対称クロスリファレンス追記（PR #24 P2、別タスク）
- 監視 CLI 挙動変更
- archive 既存 5 件への plan.md 後追い補完
