# agentops

AIエージェント用グローバル設定の設計思想と、実プロジェクトへ持ち出す rule / skill / workflow テンプレートを管理するプロジェクトです。

Claude Code と Codex がこのリポジトリを参照し、ユーザー個人の開発方針、ワークフロー、品質ゲート、クロスモデル委譲、ドキュメント更新方針をそれぞれのグローバル設定へ反映することを目的にしています。

このリポジトリ自体はグローバル設定用の設計思想保守リポジトリです。一方で、`rules/`、`skills/`、`workflows/` は、agentops の保守だけでなく、`~/dev` 配下の実プロジェクトで設計、実装、レビュー、運用、収益化、docs更新、リリースを進めるための参照テンプレートとして設計します。

dotfiles は明示依頼がない限り実プロジェクト対象から除外します。主な想定スタックは Nuxt、Next.js、PHP、Go などの Web システムで、主なリリース先は Cloudflare Workers / Pages、Xserver レンタルサーバー、GCP、一部ローカルサーバーです。

## 反映に関する前提

このリポジトリはグローバル設定の設計思想と雛形を管理する場所であり、ここを変更しただけで Claude Code や Codex の実際のグローバル設定へ自動反映されるわけではありません。

運用へ反映する場合は、対象クライアントの実設定ファイル、MCP 設定、shell profile、GitHub リモート設定を確認し、反映後に読み込み状態まで検証します。

## 目的

- Claude Code / Codex の共通設計思想を一元管理する
- グローバル設定に置くべき rule / workflow / skill と、プロジェクトローカルに置くべき設定を分離する
- `rules/`、`skills/`、`workflows/`、`docs/`、`config/` の正本と投影物をDRYに管理する
- 実プロジェクトへ持ち出した時に使える、設計・実装・レビュー・運用・収益化・docs更新・リリースのテンプレートを整備する
- AIエージェントが古い知識で実装しないよう、最新LTS・公式docs・GitHub・release notesの確認を運用に組み込む
- 設計、実装、テスト、PR、レビュー、マージ、ドキュメント更新までを一貫した開発サイクルにする
- 長い作業を別セッション・別モデルへ安全に引き継げるようにする

## グローバル設定反映プロンプト

以下を Claude Code または Codex に渡し、対象CLIのグローバル設定反映計画を作らせる。プロンプト本文は共通とし、CLIごとの差分は反映時点の公式docsと実環境を見て判断する。

対象CLIごとの主な確認先:

- Claude Code: `~/.claude/CLAUDE.md` 相当のユーザー設定、settings、MCP、hooks、skills、subagents、permission。
- Codex: `~/.codex/AGENTS.md` 相当のユーザー設定、config、MCP、hooks、skills、subagents、sandbox、approval。

```md
あなたは日本語話者の1人開発者を支援するAI開発エージェントです。

このプロンプトを受け取ったら、まずこの `agentops` リポジトリの README、docs、rules、workflows、skills、config を読み込み、設計思想と運用方針を理解する。リポジトリの場所が不明な場合は、作業前にユーザーへ確認する。

次に、対象CLIの実グローバル設定、現在の環境、MCP設定、plugin/skill/subagent/hook設定、shell profile、GitHubリモート設定、現在の読み込み状態を調査し、このリポジトリの設計思想との差分を整理する。

そのうえで、次を含むグローバル設定反映計画をユーザーへ提示する。
- 反映対象ファイル
- 現在の設定との差分
- 反映する思想、ルール、workflow、skill の要約
- CLI固有設定として公式docs確認が必要な項目
- MCP、plugin、hook、shell profile、GitHub remote への影響
- 不明点、懸念点、代替提案
- ユーザー判断が必要なリスク
- 検証方法と反映後の読み込み確認方法

実設定への書き込み、MCP/plugin導入、shell profile変更、外部反映は、計画提示とユーザー承認の後に行う。

各CLI固有の settings、config、MCP、hooks、permission、sandbox、approval、model の具体値やファイル形式は、このプロンプトで固定しすぎない。反映時点の公式docsと対象クライアントの現在仕様を確認し、この設計思想に沿って最小限かつ保守しやすく設定する。CLI固有の判断は対象CLIのエージェントに委ね、実際に反映した設定と未反映の残タスクを報告する。

詳細な基本方針、作業サイクル、レビュー修正ループ、計画承認、Git運用、最新性確認、ドキュメント更新方針は、この README に重複して展開しすぎない。`docs/`、`rules/`、`workflows/`、`skills/` を正本として読み、`config/` は対象CLIへ反映する参照用の投影物として確認する。対象CLIの実設定へ必要な要点だけを要約・投影する。
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
- [このセッションの設計プラン](.agentops/archive/2026-04-27-design-foundation/plan.md)
- [次セッション用プロンプト](.agentops/prompts/next-session.md)

## 実装済み入口

- Claude Code 設定雛形: `config/claude/CLAUDE.md`
- Codex 設定雛形: `config/codex/AGENTS.md`
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
