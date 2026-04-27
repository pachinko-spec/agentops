# agentops

Claude Code / Codex のグローバル設定を設計・見直すときに参照する、設計思想、判断材料、設定テンプレート、チェックリスト、補助ツールを管理するリポジトリです。

各 CLI のエージェントはこのリポジトリを参照し、ユーザー個人の開発方針、ワークフロー、品質ゲート、クロスモデル委譲、ドキュメント更新方針を理解します。そのうえで、現在の CLI 仕様、実環境、既存グローバル設定を調査し、採用する内容、編集する内容、見送る内容を計画します。

このリポジトリ自体は、汎用 AI 運用フレームワークや、`rules/`、`skills/`、`workflows/` をそのまま各 CLI に採用させるための管理元ではありません。`rules/`、`skills/`、`workflows/` は、agentops の保守だけでなく、`~/dev` 配下の実プロジェクトで設計、実装、レビュー、運用、収益化、docs更新、リリースを進めるときに参照できる判断材料と反映候補として扱います。

dotfiles は明示依頼がない限り実プロジェクト対象から除外します。主な想定スタックは Nuxt、Next.js、PHP、Go などの Web システムで、主なリリース先は Cloudflare Workers / Pages、Xserver レンタルサーバー、GCP、一部ローカルサーバーです。

## 採否と反映に関する前提

このリポジトリはグローバル設定の設計思想と雛形を管理する場所であり、ここを変更しただけで Claude Code や Codex の実際のグローバル設定へ自動反映されるわけではありません。各 CLI エージェントは、実環境に合わせて採用する内容、調整する内容、見送る内容を判断します。

運用へ取り込む場合は、対象クライアントの実設定ファイル、MCP 設定、shell profile、GitHub リモート設定を確認し、反映後に読み込み状態まで検証します。

## 目的

- Claude Code / Codex のグローバル設定時に参照する設計思想と判断材料を整理する
- グローバル設定に置くべき rule / workflow / skill と、プロジェクトローカルに置くべき設定を分離する
- `rules/`、`skills/`、`workflows/`、`docs/`、`config/` を、各 CLI や実プロジェクトで採否を判断する参照資料として管理する
- 実プロジェクトへ持ち出した時に使える、設計・実装・レビュー・運用・収益化・docs更新・リリースのテンプレートを整備する
- AIエージェントが古い知識で実装しないよう、最新LTS・公式docs・GitHub・release notesの確認を運用に組み込む
- 設計、実装、テスト、PR、レビュー、マージ、ドキュメント更新までを一貫した開発サイクルにする
- 長い作業を別セッション・別モデルへ安全に引き継げるようにする

## グローバル設定見直しプロンプト

以下を Claude Code または Codex に渡し、対象CLIのグローバル設定見直し計画を作らせる。プロンプト本文は共通とし、CLIごとの差分は見直し時点の公式docsと実環境を見て判断する。

対象CLIごとの主な確認先:

- Claude Code: `~/.claude/CLAUDE.md` 相当のユーザー設定、settings、MCP、hooks、skills、subagents、permission。
- Codex: `~/.codex/AGENTS.md` 相当のユーザー設定、config、MCP、hooks、skills、subagents、sandbox、approval。

```md
あなたは日本語話者の1人開発者を支援するAI開発エージェントです。

このプロンプトを受け取ったら、まずこの `agentops` リポジトリの README、docs、rules、workflows、skills、config を読み込み、設計思想と運用方針を理解する。リポジトリの場所が不明な場合は、作業前にユーザーへ確認する。

次に、対象CLIの実グローバル設定、現在の環境、MCP設定、plugin/skill/subagent/hook設定、shell profile、GitHubリモート設定、現在の読み込み状態を調査し、このリポジトリの設計思想との差分を整理する。

そのうえで、次を含むグローバル設定見直し計画をユーザーへ提示する。
- 確認対象ファイルと反映候補ファイル
- 現在の設定との差分
- 採用候補とする思想、ルール、workflow、skill の要約
- CLI固有設定として公式docs確認が必要な項目
- MCP、plugin、hook、shell profile、GitHub remote への影響
- 不明点、懸念点、代替提案
- ユーザー判断が必要なリスク
- 検証方法と反映後の読み込み確認方法

実設定への書き込み、MCP/plugin導入、shell profile変更、外部反映は、計画提示とユーザー承認の後に行う。

各CLI固有の settings、config、MCP、hooks、permission、sandbox、approval、model の具体値やファイル形式は、このプロンプトで固定しすぎない。見直し時点の公式docsと対象クライアントの現在仕様を確認し、この設計思想に沿って最小限かつ保守しやすい採用案を作る。CLI固有の判断は対象CLIのエージェントに委ね、実際に反映した設定と未反映の残タスクを報告する。

詳細な基本方針、作業サイクル、レビュー修正ループ、計画承認、Git運用、最新性確認、ドキュメント更新方針は、この README に重複して展開しすぎない。`docs/`、`rules/`、`workflows/`、`skills/` は参照資料として読み、`config/` は対象 CLI の反映候補となる設定雛形として確認する。対象 CLI の実設定へ必要な要点だけを、実環境に合わせて要約・調整する。
```

## ドキュメント

- [設計思想](docs/01-philosophy.md)
- [常時適用ルール](rules/README.md)
- [汎用skills](skills/README.md)
- [汎用workflows](workflows/README.md)
- [ワークフロー](docs/02-workflow.md)
- [DbCと品質ゲート](docs/03-dbc-and-quality-gates.md)
- [モデルルーティング](docs/04-model-routing.md)
- [レビュー方針](docs/05-review-policy.md)
- [最新性と監視](docs/06-freshness-and-monitoring.md)
- [グローバル設定とプロジェクト設定](docs/07-global-vs-project.md)
- [実設定雛形](docs/08-config-templates.md)
- [hooks品質ゲート](docs/09-hooks-quality-gates.md)
- [CLI Wrapper仕様](docs/10-cli-wrapper.md)
- [監視CLI仕様](docs/11-monitoring-cli.md)
- [Harness Engineering](docs/12-harness-engineering.md)
- [設計思想の評価](docs/13-design-evaluation.md)
- [実プロジェクト向けテンプレート方針](docs/14-real-project-template-policy.md)
- [参照キット構造整理案](docs/15-reference-kit-structure.md)
- [グローバル設定反映チェックリスト](docs/16-global-settings-application-checklist.md)
- [設計判断ログ](decisions/README.md)
- [このセッションの設計プラン](.agentops/archive/2026-04-27-design-foundation/plan.md)
- [次セッション用プロンプト](.agentops/prompts/next-session.md)

## 設計判断ログ

`docs/` は現役の設計思想と参照資料を置く場所です。`decisions/` は、設計思想やリポジトリ構造に関わる重要判断の背景、代替案、採用理由、影響範囲を記録する場所です。Claude Code / Codex のグローバル設定時に毎回読む現役 docs ではなく、判断の背景確認が必要なときに参照します。

## 実装済み入口

- Claude Code 設定雛形: `config/claude/CLAUDE.md`
- Codex 設定雛形: `config/codex/AGENTS.md`
- グローバル設定反映チェックリスト: `docs/16-global-settings-application-checklist.md`
- hooks 品質ゲート: `scripts/check-protected-branch`、`scripts/check-tests-before-push`
- hooks インストール: `scripts/install-hooks --target . --mode copy`
- CLI Wrapper: `scripts/agentops`
- 監視 CLI: `scripts/agentops-watch`
- harness 雛形: `config/harness.yml`

例:

```sh
scripts/agentops delegate --to codex --role review_frontier --dry-run --input README.md
scripts/agentops-watch check --projects config/projects.yml
```
