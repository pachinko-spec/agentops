# Plan: 2026-04-29 handoff フォローアップ (前 plan 残課題 2 件の消化)

> plan-id: `2026-04-29-handoff-followups`
> 起票: 2026-04-29 (Asia/Tokyo)
> 対象: `/home/otaku/agentops` リポジトリ
> 主 orchestrator: Claude Opus 4.7 (1M)
> Reviewer (cross-model): Codex CLI (OpenAI 系)。AGENTS.md §AI auto-merge 許諾条件 #2「主 orchestrator と別系列の frontier reviewer」に従う
> 出典: 前 plan `2026-04-28-design-review-p0-p1` 完了時の handoffs/ 2 件

---

## 1. 背景

前 plan `2026-04-28-design-review-p0-p1` (PR #30-53、9 task 全完了) で task 06 (P1-03) と task 05 (P1-05) からそれぞれ scope 外として申し送られた 2 件の handoff を消化する短い follow-up plan。

両 handoff とも S(1h)–M(半日) サイズで、各 task 単独で実装可能。前 plan 完了時に user 確認で「実装する」判断（A 選択）が取られた。

## 2. 目的

- handoff 1 (skill / workflow → rule 逆参照): cross-reference の双方向化を完成させる。前 plan task 06 の rule 起点表 (docs/17) を補完。
- handoff 2 (docs/10, 11 DbC prose 整理): 前 plan task 05 で確立した DbC 集約パターンを残存 12 箇所に適用、docs 整合性向上。

## 3. 非目的

- 新たな skill / workflow の追加、catalog の用途定義変更
- docs/10, 11 の CLI 仕様（agentops / agentops-watch / agentops archive）の意味変更
- handoffs/ 配下の 2 件の手動移動（plan 完了時に archive plan CLI または手動で archive へ）
- 前 plan の追加修正 (task 04/08/09 の P2/P3 延期分は別 plan 候補として handoff、本 plan では扱わない)

## 4. 影響範囲

| 領域 | 変更対象 | 種別 |
|---|---|---|
| docs | `docs/10-cli-wrapper.md`, `docs/11-monitoring-cli.md`, `docs/17-cross-reference.md` (任意更新) | 編集 |
| catalog | `skills/catalog.md`, `workflows/catalog.md` | 編集 |
| .agentops | `.agentops/tasks/01-cross-reference-bidirectional.md` (新規), `.agentops/tasks/02-dbc-prose-cleanup-docs-10-11.md` (新規), `.agentops/task-plans/current.md` (新規), `.agentops/reviews/01-cross-reference-bidirectional.md` (新規), `.agentops/reviews/02-dbc-prose-cleanup-docs-10-11.md` (新規) | 追加 |

## 5. 完了条件

- 親 task 2 件すべてが各 PR としてマージされ main に取り込まれている
- handoffs/ 配下の 2 件は対応する archive へ移動済み (本 plan archive 時)
- 前 plan archive と整合性が取れている

## 6. 親 task

| 番号 | task | 想定コスト | 依存 | 旧 handoff |
|---|---|---|---|---|
| 01 | `01-cross-reference-bidirectional`: skill / workflow → rule 逆参照列追加 | S–M (1h–半日) | なし | `2026-04-28-cross-reference-skill-workflow-side.md` |
| 02 | `02-dbc-prose-cleanup-docs-10-11`: docs/10, 11 の DbC prose を docs/03 参照化 | S (1h) | なし | `2026-04-28-dbc-prose-remnants-docs-10-11.md` |

各 task 独立、2 task 並行可能だが運用簡素化のため sequential で進める。

## 7. PR 構成方針 (前 plan 踏襲)

- 1 task = 2 PR (実装本体 PR + archive ドッグフード PR)
- Codex 3 Round (Round 1 → 修正 → Round 2 clean → Round 3 `no further P0/P1`)
- AI auto-merge 6 件評価 (CLAUDE.md / AGENTS.md §許諾条件)
- 各 PR の CI 4 job 全 pass

## 8. リスクと縮退

| ID | リスク | 縮退案 |
|---|---|---|
| R1 | catalog 側の rule マッピングで「複数 rule に対応」と「代表 1 件」のどちらを採用するかで Codex から指摘 | 代表 1 件（複数なら `/` 区切り）で先行、Codex Round 1 P1/P2 採用で全件列挙に切り替え |
| R2 | docs/10, 11 の DbC prose 削除で CLI 仕様情報が失われる懸念 | 関係文 + docs/03 参照リンク + 1 段適用 prose に再構成（docs/09 と同じパターン） |
| R3 | catalog.md の link が markdown-link-check で fail | rule 名の anchor link を相対パスで生成、CI で検証 |
| R4 | レビュー 2 周超え | CLAUDE.md ループ防止ルールで統合判断 / user 確認 |

## 9. 停止条件

- レビュー修正が 2 周を超える
- catalog 側の用語整理が必要と判明（scope 拡張で user 確認）
- secret / 本番 / 課金 / 外部公開 / 破壊的操作

## 10. 次 plan への申し送り候補

- 前 plan task 04/08/09 の P2/P3 延期分（actionlint binary checksum、`.env.example` 例外、config/ 雛形の同戦略適用、AGENTS.override.md override 挙動）
- 監視 CLI 側で stop_conditions spec を読んで警告する実装（前 plan task 01 範囲外）
