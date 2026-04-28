---
last_reviewed: 2026-04-28
next_review_by: 2026-07-31
reviewer: pachinko-spec
language: ja
---

# reference kit structure

## 位置づけ

この文書は、agentops の参照キット構造を「具体的な rule / skill / workflow 実体集」から「候補カタログ + CLI 別テンプレート + 旧実体 archive」へ転換した後の構造を説明します。

## 現役構造

```text
rules/
  README.md
  catalog.md
skills/
  README.md
  catalog.md
workflows/
  README.md
  catalog.md
templates/
  claude/
  codex/
  agentops/
archive/
  reference-kit-v1/
```

## 役割

- `rules/`: グローバル指示やプロジェクト指示へ採用しうる rule 候補のカタログ。
- `skills/`: Claude Code / Codex へ採用しうる Skill 候補のカタログ。
- `workflows/`: AI エージェントに生成させる workflow 候補のカタログ。
- `templates/claude/`: Claude Code 向けの CLAUDE.md、Skill、subagent 生成雛形。
- `templates/codex/`: Codex 向けの AGENTS.md、Skill、subagent 生成雛形。
- `templates/agentops/`: `.agentops` の plan、task-plan、task、next-session prompt サンプル。`next-session prompt` は動的判定（tasks ベース／handoffs ベース／生成しない）の雛形として読む。
- `archive/reference-kit-v1/`: 旧 `rules/`、`skills/`、`workflows/` 実体の退避先。

## 設計方針

`rules/`、`skills/`、`workflows/` は完成品ではありません。グローバル設定を行う AI エージェントは、候補カタログを読み、対象 CLI の公式 docs、実環境、既存設定、ユーザーの開発方針を確認して、採用する内容、調整する内容、見送る内容を決めます。

Claude Code と Codex では、Skill、subagent、global guidance、hooks、permission / approval の形式や命名ベストプラクティスが異なります。そのため、共通の具体 `SKILL.md` を正とせず、CLI 別テンプレートと公式 docs を入力にして生成します。

## 旧実体の扱い

旧 `rules/`、`skills/`、`workflows/` は `archive/reference-kit-v1/` に退避しました。

- 削除せず、詳細な見本として参照できるようにする。
- 現役設定へ直接コピーしない。
- 必要な内容は catalog または template に再抽出する。
- `.agentops/archive/` は作業履歴専用なので、参照キット本体の旧実体とは混ぜない。

## カタログの使い方

1. `rules/catalog.md`、`skills/catalog.md`、`workflows/catalog.md` から候補を選ぶ。
2. 対象 CLI の公式 docs を確認する。
3. 実グローバル設定、MCP、hooks、skills、subagents、permission / approval、shell profile、GitHub remote を確認する。
4. `templates/claude/` または `templates/codex/` を素材に、対象 CLI 向けのファイルを生成する。
5. 反映前にユーザーへ計画、影響範囲、検証方法を提示する。
6. 反映後に対象 CLI が実際に読み込んでいることを検証する。

## 公式 docs 確認先

- Claude Code: [memory](https://code.claude.com/docs/en/memory)、[settings](https://code.claude.com/docs/en/settings)、[skills](https://code.claude.com/docs/en/skills)、[subagents](https://code.claude.com/docs/en/sub-agents)、[hooks](https://code.claude.com/docs/en/hooks)
- Codex: [AGENTS.md](https://developers.openai.com/codex/guides/agents-md)、[config reference](https://developers.openai.com/codex/config-reference)、[skills](https://developers.openai.com/codex/skills)、[subagents](https://developers.openai.com/codex/subagents)、[hooks](https://developers.openai.com/codex/hooks)、[rules](https://developers.openai.com/codex/rules)

## 参照更新時の確認

```sh
rg -n "rules/|skills/|workflows/|templates/|archive/reference-kit-v1" README.md docs config rules skills workflows templates archive .agentops decisions
git diff --check
scripts/agentops-watch check --projects config/projects.yml
```

## 注意

Codex 公式 docs の `Rules` は sandbox 外コマンド実行の制御を指すため、このリポジトリの `rules/` にある「作業思想や運用ルール候補」と混同しないようにします。
