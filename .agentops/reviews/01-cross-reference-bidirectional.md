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

- run_id: `<TBD on Round 1 投入時>`
- run path: `.agentops/runs/<ts>-01-cross-reference-bidirectional/`
- 実行: `scripts/agentops delegate --to codex --role review_frontier --effort high --input skills/catalog.md --run-id <ISO8601>+0900-01-cross-reference-bidirectional-r1 --message "<観点>"`
- exit_code: <TBD>

### 所見サマリ

- P0: <TBD>
- P1: <TBD>
- P2: <TBD>
- P3: <TBD>

### Codex 所見原文

<TBD>

### 反映方針表

| 指摘 | 重大度 | 採否 | 対応内容 | 反映先 |
|---|---|---|---|---|
| <TBD> | | | | |

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
