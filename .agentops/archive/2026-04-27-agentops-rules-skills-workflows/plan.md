# agentops rules/skills/workflows 整理計画

日付: 2026-04-27
状態: done
承認: explicit-approved

## 目的

既存の `docs/`、`skills/`、`workflows/`、`config/` 構成を尊重し、前回生成した `/ai` を撤去する。

あわせて、`rules/` の新設、実装前計画承認、DRY原則、`.agentops` のplan/task運用、汎用skill/workflow、Understand-Anything導入・更新運用を設計思想と実設定雛形へ反映する。

## 範囲

- `.agentops/`
- `rules/`
- `skills/`
- `workflows/`
- `docs/`
- `config/`
- `README.md`
- `scripts/ua-bootstrap.mjs`
- `scripts/ua-graph-controller.mjs`

## 完了条件

- `/ai` が残っていない。
- rootに不要な `AGENTS.md` / `CLAUDE.md` がない。
- `rules/`、`skills/`、`workflows/` に汎用雛形がある。
- `.agentops` のplan/task/task-plan/archive運用が文書化されている。
- `config/claude/CLAUDE.md` と `config/codex/AGENTS.md` に実装前承認と小分け計画が反映されている。
- 検証コマンドが通る。
