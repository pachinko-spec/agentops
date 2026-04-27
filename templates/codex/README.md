# Codex templates

Codex のグローバル設定、Skill、subagent を生成するための雛形です。

## 確認先

- [AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- [config reference](https://developers.openai.com/codex/config-reference)
- [skills](https://developers.openai.com/codex/skills)
- [subagents](https://developers.openai.com/codex/subagents)
- [hooks](https://developers.openai.com/codex/hooks)
- [agent approvals and security](https://developers.openai.com/codex/agent-approvals-security)

## ファイル

- `AGENTS.md`: global guidance の生成雛形。
- `skill/SKILL.md`: Codex Skill の生成雛形。
- `subagent/agent.toml`: Codex subagent の生成雛形。

## 方針

- `AGENTS.md` には安定した作業思想だけを置く。
- Skill は 1 つの仕事に絞り、description に用途と発火条件を前置きする。
- subagent は TOML schema、model、sandbox、tool 権限、MCP 設定を現在仕様で確認してから生成する。
