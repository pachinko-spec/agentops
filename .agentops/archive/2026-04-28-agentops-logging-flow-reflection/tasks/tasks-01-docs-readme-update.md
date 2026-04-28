# tasks-01: docs と README 更新

親 plan: 2026-04-28-agentops-logging-flow-reflection
状態: in-progress
作業ブランチ: claude/agentops-logging-rule-reflection

## 実行内容

1. `docs/02-workflow.md` 強化
   - L11-16 責務リストを 3 列テーブル（パス・役割・解像度）へ置換
   - 表に `reviews/`, `runs/`, `prompts/next-session.md` 行を追加
   - `prompts/next-session.md` 行は動的判定ルール（tasks→handoffs→削除）を含める
   - `handoffs/` 行は「plan で考えた task の範囲を超えた持ち越しのみ。PR 単位の進捗には使わない」を含める
   - 標準サイクル L19-44 のステップ 6・23 表記を「実装着手前生成」「commit 前 archive 移動」へ微調整
   - ハンドオフ節 L86-96 に「plan で考えた task の範囲を超えた持ち越しのみ」を追記
2. `.agentops/archive/README.md` 時系列インデックス化
   - 既存「構成」セクションを残しつつ完了 plan 時系列テーブルを冒頭に追加
   - 既存 10 件 + 今回完了分（11 件）を新しい順
   - `plan.md` を持たない 5 件は task-plans/ からサマリ推定、リンクは plan-id ディレクトリへ
3. README 整備（plans / task-plans / tasks / handoffs）
   - `tasks/README.md` に「PR 単位、新作業は次番号ファイル」「commit 前 archive 移動」追記
   - `handoffs/README.md` に「plan で考えた task の範囲を超えた持ち越しのみ」追記
4. `.agentops/prompts/README.md` 新規作成（動的判定責務記述）
5. `.agentops/prompts/next-session.md` 削除
6. 雛形同期
   - `templates/agentops/prompts/next-session.md` を新ルール（動的判定前提）へ再構成
   - `docs/15-reference-kit-structure.md` L34 文言調整

## 検証

- `git diff` で意図差分のみ確認
- docs/02-workflow.md と各 README の用語整合確認
- docs/07, 15, 16 と非矛盾確認

## 停止条件

- 既存 docs と大きな矛盾発生 → ユーザー確認
- 機密値・破壊的操作 → 即停止
