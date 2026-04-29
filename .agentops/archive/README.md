# archive

完了、中止、置き換え済みのplan単位の記録をまとめる場所です。

## 完了 plan（新しい順）

| 完了日 | plan-id | サマリ |
|---|---|---|
| 2026-04-30 | [agentops-monitor-kind-implementation](2026-04-29-agentops-monitor-kind-implementation/plan.md) | agentops-watch notify --kind 実装 + cron / hook 雛形 |
| 2026-04-29 | [notification-strategy-and-project-localization](2026-04-29-notification-strategy-and-project-localization/plan.md) | Discord 通知戦略 docs (4 channel + ANT_TIME) と関連 catalog / templates 整備 (PR-B #58) + プロジェクトローカライズ戦略 docs (4 戦略意思決定木 + 主要 5 件 dry-run + skill 雛形) (PR-C 本 PR)。Codex cross-review PR-B 2 round / PR-C 4 round で全 P0/P1 反映済。 |
| 2026-04-29 | [handoff-followups](2026-04-29-handoff-followups/plan.md) | 前 plan 2026-04-28-design-review-p0-p1 完了時の handoff 2 件を消化。task 01 で skill / workflow → rule 逆参照列追加 (cross-reference 双方向化、catalog 31+15 件)、task 02 で docs/10, 11 の DbC prose 12 箇所を docs/03 参照化 (docs/09 パターン適用、archive サブコマンドは bold heading 形式で仕様情報保持)。Codex 3 Round + AI auto-merge 6 件評価で全 PR 通過 (PR #54-56)。 |
| 2026-04-29 | [design-review-p0-p1](2026-04-28-design-review-p0-p1/plan.md) | 9 task 全完了。設計レビュー P0/P1 反映で agentops repo を D 帯から B+ 帯へ底上げ: tool stop_conditions, archive 自動更新 CLI, glossary, deprecation marker, DbC 集約, cross-reference, last_reviewed frontmatter, 最小 CI + .gitignore, AGENTS.md 一本化。Codex 3 Round + AI auto-merge 6 件評価で全 PR 通過 (PR #30-52)。 |
| 2026-04-28 | [cross-repo-design-review](2026-04-28-cross-repo-design-review/plan.md) | agentops 全体（docs / rules / skills / workflows / config / templates / scripts / .agentops / CLAUDE.md / AGENTS.md）を AI コーディングエージェント設計思想として 6 軸（一貫性 / 契約と停止 / マルチモデル / 鮮度 / 運用負荷 / 拡張性）で再評価し、強み・弱み・改善提案（P0=1 / P1=8 / P2=6 / P3=3 計 18 件）を `docs/reviews/2026-04-28-cross-repo-design-review.md` に格納。Codex cross-review で観察事実誤認 4 点を反映済み |
| 2026-04-28 | [agentops-followup-after-global-review](2026-04-28-agentops-followup-after-global-review/plan.md) | 直前の `~/.claude` グローバル設定見直し（`*_frontier` Codex 候補で gpt-5.5 系採用、軽量 3 ロールの Claude 候補で claude-sonnet-4-6 系 baseline 化、hook の event 別分散）を agentops 雛形側に「採用例 (advisory)」「設計方針メモ (参考)」として反映。あわせて PR #24 残 P2（AGENTS.md ↔ CLAUDE.md 対称リンク）と PR #25 残 P3（用語統一: 主 orchestrator / cross-model / ハンドオフ）を整理 |
| 2026-04-28 | [agentops-logging-flow-reflection](2026-04-28-agentops-logging-flow-reflection/plan.md) | グローバル側で確立した `.agentops/` 運用ルール階層化（plans / tasks / handoffs / next-session.md の責務分離、commit 前 archive 移動、archive/README.md 時系列インデックス化）を `docs/02-workflow.md` と各 README に反映 |
| 2026-04-28 | [agentops-claude-md](2026-04-28-agentops-claude-md/) | agentops リポジトリ用 Claude Code 向けプロジェクト指示 `CLAUDE.md` を追加。ルート `AGENTS.md` (Codex 向け) と章立てを揃える（PR #24） |
| 2026-04-28 | [result-md-fence-hardening](2026-04-28-result-md-fence-hardening/) | `tools/agentops_cli` の `result.md` で stdout/stderr に含まれる連続 backtick より長い fence を選び、Markdown 表示崩れを防ぐ（PR #23） |
| 2026-04-28 | [agentops-project-agents](2026-04-28-agentops-project-agents/) | agentops リポジトリ用 Codex 向けプロジェクト指示 `AGENTS.md` を追加（PR #22） |
| 2026-04-28 | [pr20-delegate-p2-hardening](2026-04-28-pr20-delegate-p2-hardening/) | PR #20 cross-review で挙がった `agentops delegate` の P2 hardening（run-id slug 化、input パス制限、effort 値制限、command quoting）を実装（PR #21） |
| 2026-04-28 | [delegate-cli-wrapper](2026-04-28-delegate-cli-wrapper/) | `agentops delegate` CLI wrapper の現行 Codex / Claude CLI 仕様への適合と smoke test 実施。`docs/10-cli-wrapper.md` と config テンプレートを最小修正（PR #20） |
| 2026-04-28 | [cross-review-design](2026-04-28-cross-review-design/plan.md) | cross-review / cross-model review の設計思想を docs、catalog、config テンプレートに反映。特定モデル固定ではなく別系列 frontier reviewer を入れる思想として整理（PR #18） |
| 2026-04-27 | [reference-kit-catalog-pivot](2026-04-27-reference-kit-catalog-pivot/plan.md) | `rules/`、`skills/`、`workflows/` を完成品集から候補カタログへ転換。旧実体を `archive/reference-kit-v1/` へ退避し、`templates/` を導入（PR #16 系列） |
| 2026-04-27 | [agentops-reference-kit-refactor](2026-04-27-agentops-reference-kit-refactor/plan.md) | agentops を「正本リポジトリ」から「Claude Code / Codex のグローバル設定参照キット」として再定義。`docs/`、`decisions/`、`.agentops/` 責務を分離（PR #8 系列） |
| 2026-04-27 | [agentops-rules-skills-workflows](2026-04-27-agentops-rules-skills-workflows/plan.md) | `rules/` 新設、`/ai` 撤去、実装前計画承認、DRY、`.agentops/` plan/task 運用、汎用 skill/workflow を設計思想と実設定雛形へ反映（PR #3 系列） |
| 2026-04-27 | [design-foundation](2026-04-27-design-foundation/plan.md) | AI エージェント用グローバル設定の設計思想を整理。Claude Code / Codex 相互サブエージェント運用、保護ブランチ禁止、レビュー修正最大 2 周、テスト後 commit、最新性確認、監視 CLI 通知方針を決定（PR #1-2 系列） |

`plan.md` を持たないエントリは plan-id ディレクトリへリンクする。サマリは当該ディレクトリ配下の `task-plans/` などから推定したものを記載している。

## 構成

```text
.agentops/archive/<plan-id>/
  plan.md          # 当該 plan が plans/current.md を持っていた場合
  task-plans/      # 当該 plan のセッション実行計画
  tasks/           # 完了済みの子 task
  reviews/         # 当該 plan のレビュー結果
  runs/            # クロスモデル委譲の実行記録（ある場合）
  handoffs/        # 完了した handoff（ある場合）
```

`plan.md`、`runs/`、`handoffs/` などのサブディレクトリは、当該 plan で該当する記録があるときのみ作成します。空のサブディレクトリは置きません。

`tasks/` 直下の未完了タスク数と監視CLIの表示を一致させるため、完了済みtaskは必ず対応するarchiveへ移します。完了 handoff は `archive/<plan-id>/handoffs/` に置き、`.agentops/handoffs/` 直下は進行中の引き継ぎだけにします。
