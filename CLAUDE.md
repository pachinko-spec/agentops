# agentops プロジェクト指示 (Claude Code 向け)

このファイルは `/home/otaku/agentops` リポジトリで作業する Claude Code 向けのプロジェクト固有指示です。グローバル設定や `config/claude/CLAUDE.md` より、このリポジトリ内の作業ではこのファイルを優先します。

Codex 向けの対応指示は同階層の `AGENTS.md` にあります。両ファイルは章立てを揃えてあるので、片方を更新したら他方も同期してください。

## このリポジトリの位置づけ

- `agentops` は Claude Code / Codex のグローバル設定、運用思想、雛形、候補カタログを保守するリポジトリです。
- `config/claude/CLAUDE.md` は `~/.claude/CLAUDE.md` へ反映するための雛形です。このリポジトリを変更しただけでは Claude Code の実グローバル設定には反映されません。
- `rules/`、`skills/`、`workflows/` は完成品ではなく候補カタログとして扱います。実設定へ採用する場合は、Claude Code の現在仕様、公式 docs、実環境、既存設定を確認して調整します。

## 記録先の使い分け

- `/home/otaku/agentops` 内の設計、実装、docs、テンプレート、補助 script を触る作業は、プロジェクトローカルの `/home/otaku/agentops/.agentops/` に plan、task-plan、task、review、handoff、run log を残します。
- `~/.claude/CLAUDE.md`、`~/.claude/settings.json`、`~/.claude/skills/`、`~/.claude/agents/`、`~/.claude/plugins/`、`~/.claude` 配下の hooks、MCP 設定、permission、その他 Claude Code 実グローバル設定を読む、生成する、変更する、検証する作業では、`~/.claude/.agentops/` にも記録を残します。
- 1つの作業でこのリポジトリと `~/.claude` の両方を扱う場合は、`/home/otaku/agentops/.agentops/` を主記録にし、`~/.claude/.agentops/` にはグローバル設定側の変更内容、検証結果、未解決リスク、次回引き継ぎだけを短く残します。
- project local の一時ファイルは `/home/otaku/agentops/.agentops/.tmp/` を使います。Claude Code global 側の一時ファイルは `~/.claude/.agentops/.tmp/` を使います。
- 機密値、認証情報、環境変数ファイル、個人情報、本番データ、巨大な依存 cache は、どちらの `.agentops/` や `.agentops/.tmp/` にも保存しません。

## `~/.claude` を触る作業

- `~/.claude` 配下の実ファイルは、このリポジトリ外のユーザーグローバル設定です。読み取り、書き込み、削除、移動、生成、MCP / plugin / hook / skill / subagent / permission 設定の導入、shell profile 変更、外部反映の前に、対象、非対象、リスク、検証方法を短く計画し、ユーザー承認を得ます。
- 反映前に、現在の `~/.claude/CLAUDE.md`、`~/.claude/settings.json`、関連する実ファイル、`claude --version`、`claude --help`、必要な公式 docs を確認します。
- 反映後に、実際に変更したファイル、変更しなかったファイル、読み込み確認、検証結果、残リスクを `~/.claude/.agentops/` と最終報告に残します。読み込み確認には `/memory`、`/config`、`/mcp` など現在の Claude Code が提供する確認方法を使います。
- 機密値は表示、保存、ログ出力しません。MCP や shell profile を扱う場合も、環境変数名や参照方式だけを記録します。

## Git と作業ブランチ

- 作業前に `git status --short --branch` で branch と dirty worktree を確認します。
- `main` / `master` / `develop` など保護対象ブランチへ直接 commit / push しません。
- このリポジトリの変更は原則 `claude/` プレフィックスの作業ブランチで行います。
- ユーザーの未コミット変更は巻き戻しません。関係する場合は内容を読み、共存する形で作業します。

## 完了条件

- 実装または docs 更新のあと、意図した差分だけになっていることを確認します。
- 必要な検証、自己レビュー、docs 更新要否確認を行います。
- レビュー起点で修正した場合は、最後に再レビューして終えます。
- 完了済み task は `.agentops/tasks/` 直下に残さず、必要に応じて `.agentops/archive/<plan-id>/` へ移します。

## 停止条件

- 機密値、個人情報、本番データ、課金、外部公開、本番反映、破壊的操作が必要になった場合。
- `~/.claude` の実設定を変更する範囲が当初計画より広がる場合。
- 公式 docs または実 CLI 仕様と、このリポジトリの雛形が食い違う場合。
- テスト修正またはレビュー修正が 2 周を超えそうな場合。
