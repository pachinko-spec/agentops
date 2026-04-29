# task-plan: handoff フォローアップ plan セッション (2026-04-29)

> 親 plan: `2026-04-29-handoff-followups` (`.agentops/plans/current.md`)
> session: 2026-04-29 (前 plan archive 完了直後の同セッション継続)
> branch (現): `claude/handoff-followup-impl-01-cross-reference-bidirectional`
> 想定セッション範囲: task 01 + 02 を sequential 実行、可能なら本セッションで plan 完了まで

---

## セッション目的

前 plan (`2026-04-28-design-review-p0-p1`) 完了時に handoffs/ 配下に残った 2 件 (P3 サイズ + S/M サイズ) を消化する。user 判断 (A: 実装する) を受けて 1 plan 2 task で起票、各 task 2 PR 構成 (実装 + archive ドッグフード) で進める。

## フェーズ別実行計画

### Phase 0: plan / task 起票 (本 update で完了)

| step | 内容 | 状態 |
|---|---|---|
| 0.1 | 前 plan archive で誤って handoffs を移そうとした PR を巻き戻し (main へ復帰) | ✅ 完了 |
| 0.2 | user 確認: 2 件とも実装する (A 選択) | ✅ 完了 |
| 0.3 | `.agentops/plans/current.md` 新規 (新 plan 起票) | ✅ 完了 |
| 0.4 | `.agentops/tasks/01-cross-reference-bidirectional.md` 新規 | ✅ 完了 |
| 0.5 | `.agentops/tasks/02-dbc-prose-cleanup-docs-10-11.md` 新規 | ✅ 完了 |
| 0.6 | `.agentops/task-plans/current.md` 新規 (本ファイル) | ✅ 完了 |

### Phase 1: task 01 実装 (skill / workflow → rule 逆参照)

branch: `claude/handoff-followup-impl-01-cross-reference-bidirectional` (現ブランチ)

| step | 内容 | 状態 |
|---|---|---|
| 1.1 | rules/catalog.md / skills/catalog.md / workflows/catalog.md 構造確認 | ✅ 完了 |
| 1.2 | docs/17 と整合する rule マッピング決定 (代表 1 件、最も近い rule) | ✅ 完了 |
| 1.3 | skills/catalog.md 4 セクション (design 10 / impl 4 / review 9 / docs/ops 8 = 31 skill) に「関連 rule（代表）」列追加 | ✅ 完了 |
| 1.4 | workflows/catalog.md 単一 table (15 workflow) に「関連 rule（代表）」列追加 | ✅ 完了 |
| 1.5 | docs/17 §残課題 §57 行目「skill / workflow 側からの逆参照」を「task 01 で実装済み」に更新 | ✅ 完了 |
| 1.6 | `.agentops/reviews/01-cross-reference-bidirectional.md` 新規 (Codex Round 1/2/3 枠) | ✅ 完了 |
| 1.7 | ローカル smoke (compileall / unittest / 列数 grep / rule id 整合性) | ✅ 完了 (rule id invalid 0 件) |
| 1.8 | commit + push + PR 作成 | ✅ 完了 (PR #54) |
| 1.9 | CI 4 job 全 pass 確認 | ✅ 完了 (Actions run 25094190520) |
| 1.10a | Codex Round 1 起動 + 結果反映 | ✅ 完了 (P1=1/P2=2/P3=1 採用、docs/17 §22-23 §57 整合化、代表非相互性注記、tasks/plans の `/` 区切り削除と状態更新) |
| 1.10b | Codex Round 2 (clean 確認) | ⏳ |
| 1.10c | Codex Round 3 (`no further P0/P1` 確認) | ⏳ |
| 1.11 | auto-merge 6 件評価 → squash merge | ⏳ |
| 1.12 | main 同期 → archive ドッグフード PR (task 01 archive + 旧 handoff 1 を `archive/2026-04-28-design-review-p0-p1/handoffs/` へ + next-session.md は plan 進行中なので task 02 を entry_point に) | ⏳ |

### Phase 2: task 02 実装 (docs/10, 11 DbC prose 整理)

branch: `claude/handoff-followup-impl-02-dbc-prose-cleanup-docs-10-11`

| step | 内容 |
|---|---|
| 2.1 | docs/03 / docs/09 (先行パターン) 確認 |
| 2.2 | docs/10-cli-wrapper.md L123-140 の DbC prose 4 箇所を docs/09 と同様の関係文 + 参照リンク + 1 段適用 prose 形式に再構成 |
| 2.3 | docs/11-monitoring-cli.md L86-103 / L164-187 の DbC prose 8 箇所を同様に再構成 |
| 2.4 | `rg -nE "^前提条件:\|^不変条件:\|^完了条件:\|^停止条件:" docs/10-cli-wrapper.md docs/11-monitoring-cli.md` が 0 件確認 |
| 2.5 | `.agentops/reviews/02-dbc-prose-cleanup-docs-10-11.md` 新規 |
| 2.6 | ローカル smoke + commit + push + PR + CI 確認 |
| 2.7 | Codex 3 Round + auto-merge → squash merge |
| 2.8 | main 同期 + archive ドッグフード PR (task 02 archive + 旧 handoff 2 を archive へ + plan 全体 archive) |

### Phase 3: plan 全体 archive

`scripts/agentops archive plan --plan-id 2026-04-29-handoff-followups --summary <text>` で plan 全体を archive。`prompts/next-session.md` は plan 完了に伴い削除 (CLAUDE.md グローバル方針)。

## 不変条件

- 前 plan archive (PR #53) と整合性を保つ。前 plan 関連ファイルは触らない
- handoffs/ 配下の 2 件は **実装完了後** に対応する archive (`archive/2026-04-28-design-review-p0-p1/handoffs/`) へ移す。未実装のまま archive へ移さない (user 確認済み方針)
- 前 plan task 06 で確立した docs/17 「rule 起点表」は破壊しない
- 前 plan task 05 で確立した docs/03 canonical / docs/09 再構成パターンに整合させる

## 触ってよい範囲

- `skills/catalog.md`, `workflows/catalog.md` (task 01)
- `docs/10-cli-wrapper.md`, `docs/11-monitoring-cli.md` (task 02)
- `docs/17-cross-reference.md` §残課題 (task 01 任意更新)
- `.agentops/{plans,tasks,task-plans,reviews}/` 新規/更新
- `.agentops/handoffs/` 配下 2 件は task 完了時に archive へ移動

## 触らない範囲

- `rules/catalog.md` (前 plan task 06 で完了済、参照のみ)
- `docs/00-09, 12-16, 17 本文` (frontmatter は前 plan task 04 で完了済)
- `scripts/`, `tools/`, `templates/`, `config/` (本 plan のスコープ外)

## 想定リスクと縮退

| ID | リスク | 縮退案 |
|---|---|---|
| R1 | catalog の rule マッピングで「複数 rule に対応」と「代表 1 件」のどちらを採用するかで Codex から指摘 | 代表 1 件先行 (docs/17 と同パターン)、Codex Round 1 P1/P2 で全件列挙への切り替え判断 |
| R2 | docs/10, 11 の DbC prose 削除で CLI 仕様情報が失われる懸念 | 関係文 + docs/03 参照リンク + 1 段適用 prose に再構成 (docs/09 パターン) |
| R3 | catalog.md の link が markdown-link-check で fail | rule 名のリンクは `(../rules/catalog.md)` ファイル指定 (anchor は使わない、docs/17 の同パターン) |
| R4 | レビュー 2 周超え | CLAUDE.md ループ防止ルールで統合判断 / user 確認 |
| R5 | task 02 の DbC 再構成で CLI 仕様情報の保持と簡潔さのトレードオフ | docs/09 (前 plan task 05 で再構成済み) を参照、同等粒度で揃える |

## 停止条件

- レビュー修正 2 周超え
- catalog 側の用語整理が必要と判明 (scope 拡張で user 確認)
- docs/10, 11 の DbC prose を削除すると CLI 仕様が表現できないと判明 (user 確認)
- secret / 本番 / 課金 / 外部公開 / 破壊的操作

## 次セッション申し送り

- 本セッションで plan 完了まで進める想定だが、context 残量により task 02 を次セッションへ持ち越す可能性あり
- 持ち越し時は `prompts/next-session.md` で task 02 を entry_point に指定
