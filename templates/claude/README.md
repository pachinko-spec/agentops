# Claude Code templates

Claude Code のグローバル設定、Skill、subagent を生成するための雛形です。

## 確認先

- [memory / CLAUDE.md](https://code.claude.com/docs/en/memory)
- [settings](https://code.claude.com/docs/en/settings)
- [skills](https://code.claude.com/docs/en/skills)
- [subagents](https://code.claude.com/docs/en/sub-agents)
- [hooks](https://code.claude.com/docs/en/hooks)

## ファイル

- `CLAUDE.md`: global memory の生成雛形。
- `skill/SKILL.md`: Claude Code Skill の生成雛形。
- `subagent/agent.md`: Claude Code subagent の生成雛形。

## 方針

- `CLAUDE.md` には安定した作業思想だけを置く。
- 長い手順は Skill や command に分ける。
- Skill の `description` は、何をするか、いつ使うかを明確にする。
- subagent は役割、tool 権限、成果物、メインエージェントの統合責任を明確にする。
