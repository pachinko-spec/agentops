# Codex Global Guidance Template

このテンプレートは `~/.codex/AGENTS.md` を生成するときの素材です。反映前に Codex の公式 docs、`codex --help`、既存の `~/.codex` 設定を確認してください。

## Working Agreements

- 日本語で応答し、commit、PR、レビュー、handoff も日本語を基本にする。
- 実装、削除、外部反映、依存追加、本番影響がある作業の前に計画を提示する。
- 作業前に Git branch と dirty worktree を確認する。
- 保護ブランチへ直接作業しない。
- 実装後は lint、test、docs 更新、自己レビューを完了条件に含める。
- 必要な cross-review では、主 orchestrator とは別 CLI / 別モデルファミリーの frontier reviewer を候補にし、採否は主 orchestrator が判断する。
- 公式 docs、release notes、実環境を確認し、古い知識だけで判断しない。

## Reference Kit

- `agentops` の `rules/`、`skills/`、`workflows/` は候補カタログとして読む。
- 実際の Skill、subagent、config、hooks、approval は Codex の現在仕様に合わせて生成する。
- 旧版の具体例は `archive/reference-kit-v1/` を参照する。
