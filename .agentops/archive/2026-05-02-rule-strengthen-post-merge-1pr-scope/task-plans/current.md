# task-plan: 2026-05-02-rule-strengthen-post-merge-1pr-scope (session 1)

親 plan: `plans/current.md` (2026-05-02-rule-strengthen-post-merge-1pr-scope)
作業ブランチ: `claude/rule-strengthen-post-merge-1pr-scope`

## フェーズ

| # | フェーズ | 想定時間 | 主作業 |
|---|---|---|---|
| 1.5 | 設計段階 cross-review | 5 分 | Codex review_frontier に plan 委譲、P0/P1=0 確認 (実施済 P1=3 反映済) |
| 2 | branch 準備 | 1 分 | `git checkout -b claude/rule-strengthen-post-merge-1pr-scope` (済) |
| 3 | .agentops/ 準備 | 5 分 | plans/current.md / task-plans/current.md / tasks/01-*.md 作成 (本フェーズ) |
| 4 | 実装 | 30 分 | 修正対象 1〜7 (新規 2 + 編集 5) を順次作業 |
| 4.5 | archive 実行 (1 PR scope) | 3 分 | `scripts/agentops archive task` + `archive plan` を merge 前 commit に含める |
| 5 | 検証 | 10 分 | markdown lint / link / frontmatter / hook 整合確認 |
| 6 | 実装後 cross-review | 5 分 | Codex review_frontier に diff 委譲、P0/P1=0 確認 |
| 7 | PR 作成 → merge | 10 分 | gh pr create / CI 確認 / AI auto-merge 許諾 6 評価 / squash merge |
| 8 | post-merge read-only 確認 | 2 分 | main 同期確認 + dirty diff なし確認 |

`~/.claude/*` 反映 (Phase 9) は別作業 (別 commit / 別 handoff)。

## 残懸念

- `rules/catalog.md` の現状列構成が Plan agent 報告 (7 列) と差異がある可能性 →
  実装時に既存 1 行目を Read で再確認してから entry 追加
- 新規 2 ファイルの frontmatter 形式は既存 `rules/model-routing.md` を Read して
  実装直前に最終確認 (Codex F4 反映: `name` / `description` / `applies-to` 形式)
- Phase 4.5 で `scripts/agentops archive task --task-id 01-rule-strengthen-post-merge`
  を実行する際、本 task md の status が completed に更新されている必要がある
