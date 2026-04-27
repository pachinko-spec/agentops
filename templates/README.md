# templates

Claude Code / Codex / `.agentops` へ反映する内容を生成するための雛形を置く場所です。

このディレクトリのファイルも、そのまま機械的にコピーするものではありません。対象 CLI の公式 docs、実環境、既存設定、ユーザーの開発方針を確認し、必要な範囲だけ採用、調整、見送りを判断します。

## 構成

- `claude/`: Claude Code 向けの CLAUDE.md、Skill、subagent 生成雛形。
- `codex/`: Codex 向けの AGENTS.md、Skill、subagent 生成雛形。
- `agentops/`: `.agentops` の plan、task-plan、task、next-session prompt サンプル。

## 公式 docs

- Claude Code: [memory](https://code.claude.com/docs/en/memory)、[settings](https://code.claude.com/docs/en/settings)、[skills](https://code.claude.com/docs/en/skills)、[subagents](https://code.claude.com/docs/en/sub-agents)
- Codex: [AGENTS.md](https://developers.openai.com/codex/guides/agents-md)、[config](https://developers.openai.com/codex/config-reference)、[skills](https://developers.openai.com/codex/skills)、[subagents](https://developers.openai.com/codex/subagents)
