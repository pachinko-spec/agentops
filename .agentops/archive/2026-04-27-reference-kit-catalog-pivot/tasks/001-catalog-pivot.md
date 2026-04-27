# 001 catalog pivot

parent_plan: 2026-04-27-reference-kit-catalog-pivot
status: completed
completed_at: 2026-04-27

## 実行内容

- 方向転換の decision log を作る。
- `rules/`、`skills/`、`workflows/` を候補カタログへ再構成する。
- 旧実体を `archive/reference-kit-v1/` へ退避する。
- `templates/` に Claude Code、Codex、`.agentops` 向けの入口を作る。
- README、docs、config の参照を更新する。

## 完了条件

- 新構造が README と docs に反映されている。
- カタログとテンプレート入口がある。
- 旧実体が archive で参照可能。
- 検証コマンドが通る。

## 完了内容

- 方向転換の decision log を追加した。
- `rules/catalog.md`、`skills/catalog.md`、`workflows/catalog.md` を追加した。
- `templates/claude/`、`templates/codex/`、`templates/agentops/` を追加した。
- 旧 `rules/`、`skills/`、`workflows/` を `archive/reference-kit-v1/` へ退避した。
- README、docs、config、`.agentops/prompts/next-session.md` を更新した。

## 検証

- `rg -n "rules/|skills/|workflows/|templates/|archive/reference-kit-v1" README.md docs config rules skills workflows templates archive .agentops decisions`
- `git diff --check`
- `scripts/agentops-watch check --projects config/projects.yml`

## 完了時の後処理

- 完了した task は `.agentops/archive/<parent_plan>/tasks/` へ移す。
- 完了した task-plan は `.agentops/archive/<parent_plan>/task-plans/` へ移す。
- 完了した plan は `.agentops/archive/<parent_plan>/plan.md` へ移す。
- `.agentops/prompts/next-session.md` を次の入口に更新する。

## 停止条件

- 旧実体の退避により参照が壊れ、1PRで安全に直せない。
- 実グローバル設定への反映が必要になる。
