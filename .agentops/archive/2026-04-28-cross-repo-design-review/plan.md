# Plan: agentops 横断設計レビュー報告書 2026-04-28

plan_id: 2026-04-28-cross-repo-design-review
status: approved
created_at: 2026-04-28
timezone: Asia/Tokyo

## 背景

agentops は Claude Code / Codex のグローバル設定参照キット（思想 docs / 候補カタログ / 雛形）。AAIF 設立（2025-12-09）や Skills 公開標準化、Claude Code commands→skills 統合、ABC 論文・Managed Agents の登場など、業界・学術側の急速な変化に対して、リポジトリの設計思想を **6 軸（一貫性 / 契約と停止 / マルチモデル / 鮮度 / 運用負荷 / 拡張性）** で再評価し、優先度付き改善提案までまとめる必要がある。

既存 docs/13-design-evaluation.md は短く（40 行程度）、業界比較が不足している。AAIF 標準化以降の動向を踏まえた再評価が未実施。

## 目的

- リポジトリ全体（docs / rules / skills / workflows / config / templates / scripts / .agentops / CLAUDE.md / AGENTS.md）を AI コーディングエージェント設計思想として評価する報告書を作成。
- 強み・弱み・改善提案（P0–P3）を構造化して `docs/reviews/2026-04-28-cross-repo-design-review.md` に格納。
- 完成後に Codex 側へ cross-review を委譲し、第三者視点で観察事実誤認 / 提案優先度妥当性 / 業界動向解釈の 3 点を再点検する。

## 非目的

- 設計思想評価で挙げた改善提案そのものの実装は行わない（別 plan）。
- グローバル設定 `~/.claude/CLAUDE.md` への反映は行わない。
- 機密値、本番データ、個人情報を扱う作業は含めない。

## 影響範囲

- 新規追加: `docs/reviews/2026-04-28-cross-repo-design-review.md`、`docs/reviews/`（新規ディレクトリ）
- メタ管理: `.agentops/plans/current.md`、`.agentops/task-plans/current.md`、`.agentops/tasks/01-draft-report.md` 等
- run log: cross-model 委譲時の `.agentops/runs/<timestamp>-codex-review/`
- 既存 docs / config / scripts / カタログ は読み取りのみ。変更しない。

## 完了条件

- 報告書 md が約 12,000 字で完成し、§0–§10 + Appendix A/B が網羅されている。
- 6 軸評価が A-E スコアで提示されている。
- 提案が 12–18 件、P0/P1/P2/P3 で分類されている。
- 出典 URL 全件の生存確認済み（HEAD 200 確認 + 取得日記載）。
- リポジトリ内引用パスが全件存在する。
- 自己レビュー（review skill）通過。
- cross-model レビュー（Codex）を実施し、結果を反映または「不採用とした理由」を残している。
- 完了 task / plan を `.agentops/archive/2026-04-28-cross-repo-design-review/` へ移動。
- commit → push → PR まで完了し、本人レビュー後 main マージで終える。

## 停止条件

- レビュー修正ループが 2 周を超えそうになったら統合判断またはユーザー確認。
- 出典 URL の半数以上が 200 を返さない場合、ユーザーに代替方針を確認。
- cross-model レビューが timeout / 失敗で 2 回連続失敗した場合、Codex 側のセットアップを確認するか単独完結に切り替える判断をユーザーに委ねる。
- スコープが当初の「設計思想評価 + 他プロジェクト派生可能性」を超える指摘が出た場合、別 plan へ分離する。

## 検証方針

- 出典 URL: `curl -sIL` で 200 / 3xx 確認、取得日を Appendix A に併記。
- リポジトリ内パス: `ls` または `test -e` で全件確認。
- 章間整合: review skill で再帰チェック（用語ゆれ / 矛盾 / 重複）。
- 業界比較: freshness audit で 2025-2026 動向の固有名詞（AAIF、ABC 論文、SWE-agent 等）を再確認。
- 第三者視点: Codex 側 cross-review。

## 親 task 一覧

- 01-draft-report: 報告書本体の起草
- 02-verify-citations: 出典 URL とリポジトリ内パスの検証
- 03-self-review: 自己レビュー（review skill / review-loop-guard skill）
- 04-cross-review: Codex 側 cross-model レビュー
- 05-finalize: 修正反映 → archive 移動 → commit → push → PR
