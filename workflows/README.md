# workflows

`workflows/` は、AI エージェントに生成させる workflow 候補のカタログです。

ここに完成済み手順を大量に置くのではなく、どのような workflow を作るべきか、いつ使うべきか、`.agentops` とどう連携するかを整理します。

## ファイル

- `catalog.md`: workflow 候補の名前、用途、発火条件、出力先。

## 生成時の確認先

- Codex: [Workflows](https://developers.openai.com/codex/workflows)、[AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- Claude Code: [skills and commands](https://code.claude.com/docs/en/skills)
- `.agentops` サンプル: `templates/agentops/`

## 旧実体

旧 workflow 実体は `archive/reference-kit-v1/workflows/` にあります。
