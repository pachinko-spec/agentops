# 正本分離ルール

## 目的

AIエージェントがどのファイルを正として読むべきか迷わないようにします。

## 責務

- `rules/`: 常時適用する短いルール。
- `skills/`: 特定観点や用途で発火する再利用可能な能力。
- `workflows/`: 作業の順序と完了条件。
- `docs/`: 背景、理由、設計思想、仕様説明。
- `config/`: Claude Code、Codexなどへ反映する雛形。
- `.agentops/`: projectまたはセッション固有の状態。

## 優先順位

1. ユーザーの明示指示。
2. プロジェクト固有の `AGENTS.md`、`CLAUDE.md`、docs、`.agentops/`。
3. このリポジトリの `rules/`、`skills/`、`workflows/`、`docs/`。
4. 一般的な知識。
