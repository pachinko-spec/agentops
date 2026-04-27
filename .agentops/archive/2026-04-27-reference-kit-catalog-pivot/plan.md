# Plan: reference kit catalog pivot

plan_id: 2026-04-27-reference-kit-catalog-pivot
status: completed
created_at: 2026-04-27
completed_at: 2026-04-27
timezone: Asia/Tokyo

## 背景

`rules/`、`skills/`、`workflows/` に具体的な実体が多く残っていると、Claude Code / Codex のグローバル設定を行う AI エージェントが、それらをそのままコピーすべき完成品として扱いやすい。

今後は、agentops を「完成品集」ではなく、ユーザーの開発方針、公式 docs、実環境、既存設定を確認した AI エージェントが、適切なグローバル設定、Skill、subagent、workflow を生成するための参照キットとして整理する。

## 目的

- 方向転換の設計判断ログを `decisions/` に残す。
- 旧 `rules/`、`skills/`、`workflows/` 実体を `archive/reference-kit-v1/` に退避する。
- 現役の `rules/`、`skills/`、`workflows/` は候補カタログとして再構成する。
- Claude Code / Codex / `.agentops` 向けのテンプレート入口を `templates/` に作る。
- README、docs、config の参照を新構造へ更新する。

## 非目的

- 実際の `~/.claude`、`~/.codex` グローバル設定へ反映すること。
- CLI 固有の最新仕様をこのリポジトリ側で固定しきること。
- 旧実体を削除して参照不能にすること。

## 影響範囲

- `README.md`
- `decisions/`
- `docs/15-reference-kit-structure.md`
- `docs/16-global-settings-application-checklist.md`
- `config/claude/CLAUDE.md`
- `config/codex/AGENTS.md`
- `config/understand-anything-policy.json`
- `rules/`
- `skills/`
- `workflows/`
- `templates/`
- `archive/`
- `.agentops/`

## 完了条件

- 方向転換の decision log がある。
- `rules/`、`skills/`、`workflows/` が候補カタログになっている。
- 旧実体が `archive/reference-kit-v1/` へ退避されている。
- `templates/claude/`、`templates/codex/`、`templates/agentops/` に入口 README と最小テンプレートがある。
- README、docs、config が新構造を説明している。
- `git diff --check` と `scripts/agentops-watch check --projects config/projects.yml` が通る。

## 完了結果

- `decisions/2026-04-27-reference-kit-catalog-pivot.md` に方向転換を記録した。
- 旧 `rules/`、`skills/`、`workflows/` 実体を `archive/reference-kit-v1/` へ退避した。
- 現役の `rules/`、`skills/`、`workflows/` は README と `catalog.md` の候補カタログに再構成した。
- `templates/claude/`、`templates/codex/`、`templates/agentops/` を追加した。
- README、docs、config、next-session prompt を新構造へ更新した。

## 停止条件

- 旧実体の退避により README、docs、config、scripts の参照が大きく破綻する。
- Claude Code / Codex の公式 docs とテンプレート方針に矛盾が出る。
- 実グローバル設定への反映が必要になり、ユーザー承認がない。

## 検証方針

```sh
rg -n "rules/|skills/|workflows/|templates/|archive/reference-kit-v1" README.md docs config rules skills workflows templates archive .agentops decisions
git diff --check
scripts/agentops-watch check --projects config/projects.yml
```
