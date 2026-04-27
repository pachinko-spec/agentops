# rules

`rules/` は、Claude Code / Codex のグローバル指示やプロジェクト指示へ採用しうる rule 候補のカタログです。

ここに置く内容は完成済みのグローバル設定ではありません。対象 CLI の公式 docs、実環境、既存設定、ユーザーの開発方針を確認したうえで、AI エージェントが採用、調整、見送りを判断します。

## ファイル

- `catalog.md`: rule 候補の名前、用途、適用先、採用判断。

## 生成時の確認先

- Codex: [AGENTS.md](https://developers.openai.com/codex/guides/agents-md)、[Rules](https://developers.openai.com/codex/rules)、[agent approvals and security](https://developers.openai.com/codex/agent-approvals-security)
- Claude Code: [memory](https://code.claude.com/docs/en/memory)、[settings](https://code.claude.com/docs/en/settings)、[hooks](https://code.claude.com/docs/en/hooks)

## 旧実体

旧 rule 実体は `archive/reference-kit-v1/rules/` にあります。
