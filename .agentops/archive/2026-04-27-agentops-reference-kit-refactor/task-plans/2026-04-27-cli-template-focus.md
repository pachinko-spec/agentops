# Task Plan: cli template focus

plan_id: 2026-04-27-agentops-reference-kit-refactor
status: completed
created_at: 2026-04-27
timezone: Asia/Tokyo

## 今回セッションの目的

`.agentops/tasks/004-cli-template-focus.md` から着手し、Claude Code / Codex のグローバル設定を書くためのベストプラクティス、テンプレート、チェックリストの境界を整理する。

## 実行順

1. 作業ブランチを切る。
2. `.agentops/tasks/004-cli-template-focus.md` を読む。
3. `docs/15-reference-kit-structure.md` の分類案を確認する。
4. README、docs、config にある Claude Code / Codex の設定雛形と反映プロンプトを確認する。
5. 共通思想、CLI 固有設定、MCP、hooks、skills、subagents、permissions、sandbox、approval の確認観点を分ける。
6. グローバル設定反映時に使うチェックリスト案を文書化する。
7. `.agentops/tasks/004-cli-template-focus.md` の状態と残タスクを更新する。
8. `004` が完了した場合は、完了済み task と今回の `current.md` を `.agentops/archive/<plan-id>/` へ移す。
9. 次に着手する task に合わせて `.agentops/task-plans/current.md` と `.agentops/prompts/next-session.md` を更新する。
10. 差分を確認する。
11. `git diff --check` と `scripts/agentops-watch check --projects config/projects.yml` を実行する。
12. commit、push、PR作成、GitHub上でのmerge、main同期確認を行う。

## 今回は行わないこと

- `rules/`、`skills/`、`workflows/` の大規模な移動、削除、archive 化。
- Claude Code / Codex の実グローバル設定変更。
- CLI 固有仕様を公式 docs 未確認のまま固定すること。

## 停止条件

- 公式 docs 確認が必要な仕様を、未確認のまま固定しそうになった。
- Claude Code と Codex の差分を共通テンプレートで吸収できない。
- 実設定へ反映するにはユーザー承認が必要な変更が出た。

## 完了内容

- 作業ブランチ `codex/004-cli-template-focus` を作成した。
- `docs/08-config-templates.md` にグローバル設定本文と CLI 固有設定の境界を追加した。
- `docs/16-global-settings-application-checklist.md` を作成した。
- `config/claude/CLAUDE.md` と `config/codex/AGENTS.md` に CLI 固有設定の確認観点を追加した。
- README の docs 一覧と実装済み入口を更新した。
- 完了済み task を `.agentops/archive/2026-04-27-agentops-reference-kit-refactor/tasks/` へ移した。
