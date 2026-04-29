# task 01 (cross-reference 双方向化) Codex cross-review 記録

> task: `.agentops/tasks/01-cross-reference-bidirectional.md`
> 旧 handoff: `.agentops/handoffs/2026-04-28-cross-reference-skill-workflow-side.md`
> branch: `claude/handoff-followup-impl-01-cross-reference-bidirectional`
> reviewer: Codex CLI (model: adapter default / `--model` 未指定、effort=high, role=review_frontier)
> 主 orchestrator: Claude Opus 4.7 (1M context)

---

## 採用方針メモ

旧 handoff §次 plan で検討すべきこと の 4 件への回答:

1. **代表 rule 1 件 vs 全件列挙**: **代表 1 件**を採用（複数候補がある場合は最も近い rule、docs/17 と同パターン）。情報損失が懸念される場合は Codex Round 1 P1/P2 で指摘可能、その時点で全件列挙へ切り替え判断。
2. **catalog vs docs/17 の責務分離**: docs/17 は「rule 起点表」固定、catalog 側に逆参照列を追加で双方向化。
3. **frontmatter (last_reviewed) 追加**: 本 task でスコープ外、catalog 側 frontmatter 追加は handoff 候補で記録。
4. **skill / workflow 側に hook 列追加**: 本 task でスコープ外、rule 経由で hook 到達可能、別 task 候補。

## 実装概要

- `skills/catalog.md`: 4 セクション (design 10 / impl 4 / review 9 / docs/ops 8 = 31 skill) に「関連 rule（代表）」列追加。テーブルヘッダ + 区切り行 + データ行を 5 列に拡張
- `workflows/catalog.md`: 単一 table (15 workflow) に「関連 rule（代表）」列追加。テーブルヘッダ + 区切り行 + データ行を 5 列に拡張
- `docs/17-cross-reference.md` §残課題: skill / workflow 逆参照行を「task 01 で実装済み」に更新、複数候補網羅と catalog frontmatter は handoff 候補として残置

## マッピング根拠

skills/catalog.md (代表 rule マッピング、rules/catalog.md の id を参照):

| skill | 代表 rule | 根拠 |
|---|---|---|
| requirements-review | planning-approval | rule §関連 skill 列が指す |
| architecture-boundary-review | project-scope | rule §関連 skill 列が指す |
| api-contract-review | design-policy | API 契約は設計範疇 |
| data-model-review | design-policy | スキーマ変更は設計範疇 |
| security-design-review | secret-policy | secret 管理は本 rule に最も近い |
| privacy-design-review | secret-policy | PII / secret 同一カテゴリ |
| reliability-design-review | destructive-operation-policy | rule §関連 skill 列が指す |
| performance-design-review | design-policy | 設計時の品質特性 |
| accessibility-design-review | design-policy | 設計時の品質特性 |
| profitability-review | design-policy | 設計時の収益要件 |
| web-frontend-implementation | review-policy | 実装の最終 gate は review-policy |
| web-backend-implementation | review-policy | 同上 |
| deployment-adapter | deployment-target-policy | rule §関連 skill 列が指す |
| test-automation | review-policy | 「regression、tests を優先してレビュー」 |
| correctness-review | review-policy | rule §関連 skill 列が指す |
| security-review | secret-policy | rule §関連 skill 列が指す |
| testability-review | review-policy | review カテゴリ |
| maintainability-review | review-policy | 同上 |
| performance-review | review-policy | 同上 |
| dependency-supply-chain-review | secret-policy | supply-chain は secret 領域 |
| cross-review | review-policy | 「レビュー修正後」が含まれる |
| release-readiness-review | git-and-branch-policy | rule §関連 skill 列が指す |
| docs-review | language-policy | rule §関連 skill 列が指す |
| docs-maintainer | documentation-policy | rule §関連 skill 列が指す |
| decision-log-writer | documentation-policy | docs 系 |
| runbook-writer | documentation-policy | docs 系 |
| changelog-release-notes | documentation-policy | docs 系 |
| session-handoff | agentops-task-policy | rule §関連 skill 列が指す |
| freshness-audit | freshness-policy | rule §関連 skill 列が指す |
| cross-model-delegate | review-policy | cross-review 系 |
| review-loop-guard | review-policy | レビュー修正ループ |

workflows/catalog.md:

| workflow | 代表 rule | 根拠 |
|---|---|---|
| project-intake | project-scope | rule §関連 workflow 列が指す |
| plan-approval | planning-approval | rule §関連 workflow 列が指す |
| feature-delivery | git-and-branch-policy | rule §関連 workflow 列が指す |
| web-system-design | design-policy | 設計 |
| deployment-target-selection | deployment-target-policy | rule §関連 workflow 列が指す |
| code-review | review-policy | rule §関連 workflow 列が指す |
| design-review | design-policy | rule §関連 workflow 列が指す |
| cross-review | review-policy | レビュー修正後の独立確認 |
| docs-update | documentation-policy | rule §関連 workflow 列が指す |
| dependency-introduction | secret-policy | supply-chain / license は secret 領域に近い |
| freshness-audit | freshness-policy | rule §関連 workflow 列が指す |
| release-readiness | git-and-branch-policy | rule §関連 workflow 列が指す |
| production-operations | destructive-operation-policy | 本番運用変更 |
| session-handoff | agentops-task-policy | rule §関連 workflow 列が指す |
| reference-kit-migration | agentops-task-policy | catalog / archive 整理 |

---

## Round 1

- run_id: `20260429t1527080900-01-cross-reference-bidirectional-r1`
- run path: `.agentops/runs/20260429t1527080900-01-cross-reference-bidirectional-r1/`
- 実行: `scripts/agentops delegate --to codex --role review_frontier --effort high --input skills/catalog.md --run-id 20260429T152708+0900-01-cross-reference-bidirectional-r1 --message "<観点 8 件>"`
- exit_code: 0
- started_at: 2026-04-29T15:27:08+09:00
- completed_at: 2026-04-29T15:30:23+09:00

### 所見サマリ

- P0: 0 件
- P1: 1 件
- P2: 2 件
- P3: 1 件

### Codex 所見原文

> **Round 1 所見**
>
> **P1**: `docs/17-cross-reference.md:22` がまだ「skill / workflow から rule への逆引きは次 plan の handoff」と説明しており、同ファイル `:57` の「task 01 で実装済み」と矛盾しています。catalog 側で逆引きを扱う方針なら、22 行目は「docs/17 本表には skill/workflow 起点表を持たず、逆引きは catalog 側の `関連 rule（代表）` 列で扱う。複数候補の網羅は対象外」程度に更新した方がよいです。隣の 23 行目も frontmatter 既存状態と合わないため、同時に整理対象です。
>
> **P2**: 代表リンクが非相互になるケースが複数ありますが、その性質が明記されていません。例: docs/17 は `design-policy -> requirements-review` としていますが、`skills/catalog.md:13` の `requirements-review` は `planning-approval` へ戻ります。同様に `release-readiness` は docs/17 では `destructive-operation-policy` 側の代表ですが、`workflows/catalog.md:20` では `git-and-branch-policy` です。代表 1 件方式自体は運用上許容できますが、「相互リンクの完全一致は保証しない」と明記するか、docs/17 と catalog の代表選定を相互一致に寄せるかを決めた方が安全です。
>
> **P2**: `.agentops` 記録が PR 現況とずれています。`.agentops/tasks/01-cross-reference-bidirectional.md:6` は `状態: 未着手` のまま、`.agentops/task-plans/current.md:35` 以降も実装・PR・CI が未完了扱いです。記録ファイルも今回のスコープなので、少なくとも task 01 の実装済み範囲と CI green までの状態は更新しておくべきです。
>
> **P3**: `.agentops/tasks/01-cross-reference-bidirectional.md:31` と `.agentops/plans/current.md:64` に「複数なら `/` 区切り」と残っていますが、実装方針は「複数候補でも最も近い rule 1 件」です。将来の読み違い防止として文言を実装方針に合わせるとよいです。
>
> **検証結果**: `git diff --check` OK、rule id 機械検証は skill 31 件 / workflow 15 件で invalid 0、table 列数は全行 5 列、`python3 -m compileall tools` OK、`python3 -m unittest discover -s tests` は 12 tests OK。P0 はありません。現時点では P1 が残っているため Round 1 は clean ではありません。

### 反映方針表

| 指摘 | 重大度 | 採否 | 対応内容 | 反映先 |
|---|---|---|---|---|
| docs/17 §22 (スコープ) と §57 (残課題) の矛盾、§23 frontmatter 説明の古い記述 | **P1** | **採用** | §22 を「逆引きは catalog 側の `関連 rule（代表）` 列で扱う」に更新、§23 を「frontmatter は前 plan task 04 で追加済」に更新、§残課題 から「skill/workflow 逆参照」行を削除（実装済みのため）、代わりに「代表選定の相互一致」「catalog 側 frontmatter 追加」を残課題に追加 | `docs/17-cross-reference.md` §17-23 / §残課題 |
| 代表選定の非相互性が明記されていない | P2 | **採用** | docs/17 §スコープ、skills/catalog.md / workflows/catalog.md の冒頭注記に「代表選定の非相互性」セクションを追加。「各方向で『最初に見るべき代表 1 件』を独立に選定、相互一致は保証しない、網羅性が必要なら両表 + rules/catalog.md 併読」を明記 | `docs/17-cross-reference.md` / `skills/catalog.md` / `workflows/catalog.md` 冒頭 |
| .agentops 記録が PR 現況と未同期（状態: 未着手 / Phase 1 ⏳ など） | P2 | **採用** | tasks/01 §状態 を「進行中」、task-plans/current.md Phase 1 step 1.1-1.10a を ✅ に更新 | `.agentops/tasks/01-cross-reference-bidirectional.md` §6 / `.agentops/task-plans/current.md` Phase 1 |
| tasks/01 §31 と plans/current.md §64 の「複数なら `/` 区切り」が実装方針と矛盾 | P3 | **採用** | 「最も近い rule 1 件」「最も近い rule のみ」に統一 | `.agentops/tasks/01-cross-reference-bidirectional.md` §実行内容 5 / `.agentops/plans/current.md` §8 R1 |

### Codex の確認済み事項 (Round 1)

- `git diff --check` OK
- rule id 機械検証: skill 31 件 / workflow 15 件で invalid 0
- table 列数: 全行 5 列で統一
- `python3 -m compileall tools` exit 0
- `python3 -m unittest discover -s tests` 12 tests OK

---

## Round 2

(Round 1 修正後の clean 確認)

---

## Round 3 (確認専用 final、no further P0/P1 確認)

(Round 2 結果転記後の確認)

---

## DbC 完了評価（task 01 §完了条件）

- [x] skills/catalog.md の全 skill 行に `関連 rule（代表）` 列が入っている (31 skill)
- [x] workflows/catalog.md の全 workflow 行に `関連 rule（代表）` 列が入っている (15 workflow)
- [ ] 列値の rule id が rules/catalog.md に存在する id と一致 (Codex Round 1 で機械的確認依頼)
- [ ] markdown 標準 table 形式維持 (CI markdown-link-check + 列数 grep)
- [ ] Codex cross-review 通過 (Round 3 で `no further P0/P1`)

## auto-merge 6 件評価（CLAUDE.md / AGENTS.md §許諾条件、Round 3 後 = 最終評価）

- [ ] DbC 完了
- [ ] 別系列 frontier cross-review 通過
- [ ] CI green
- [ ] 観察事実食い違いなし
- [ ] PR スコープ単一
- [ ] secret 未混入
