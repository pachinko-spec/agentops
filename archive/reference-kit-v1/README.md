# reference kit v1

このディレクトリは、`rules/`、`skills/`、`workflows/` に具体的なルール、Skill、作業手順の実体を置いていた旧構造の退避先です。

## 退避理由

現役の `rules/`、`skills/`、`workflows/` は、Claude Code / Codex のグローバル設定へそのままコピーする完成品集ではなく、AI エージェントが公式 docs、実環境、既存設定、ユーザーの開発方針を確認して生成するための候補カタログへ転換しました。

## 内容

- `rules/`: 旧ルール実体。
- `skills/`: 旧 `SKILL.md` 群。
- `workflows/`: 旧ワークフロー実体。

## 使い方

- 過去の詳細な観点や文章を確認したいときに参照する。
- 現役設定へ取り込む場合は、`templates/` と対象 CLI の公式 docs を優先して再生成する。
- この中のファイルを直接グローバル設定へコピーしない。
- 配下ファイル内の相対パスは、旧リポジトリ root 配置を前提にしている場合がある。現役の入口は root の `rules/`、`skills/`、`workflows/`、`templates/` を優先する。
