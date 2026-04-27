# 実設定雛形

`docs/` は設計思想、`rules/`、`skills/`、`workflows/` は候補カタログ、`templates/` は Claude Code / Codex / `.agentops` 向け生成雛形です。`config/` は Claude Code、Codex、監視CLI、harness などで使う反映候補の雛形であり、実環境と対象 CLI の仕様を確認したうえで、必要な範囲だけ採否を判断し、要約・調整して使います。

このリポジトリでは、設計思想だけでなく Claude Code / Codex に投入できる雛形を `config/` に置く。

雛形を編集しても実際のグローバル設定には自動反映されない。運用へ取り込む場合は、配置先の実ファイル、MCP 設定、shell profile、GitHub リモート設定を確認し、対象クライアントで読み込み状態まで検証する。

## 配置先

| 対象 | 雛形 | 配置先 |
| --- | --- | --- |
| Claude Code | `config/claude/CLAUDE.md` | `~/.claude/CLAUDE.md` |
| Codex | `config/codex/AGENTS.md` | `~/.codex/AGENTS.md` |
| hooks 環境変数 | `config/hooks.env.example` | shell profile、direnv、CI secret |
| 監視対象 | `config/projects.yml` | このリポジトリ、または監視ホスト側 |
| 陳腐化ソース | `config/freshness-sources.yml` | このリポジトリ、または監視ホスト側 |
| モデルカタログ | `config/model-catalog.yml` | 定期更新する運用ファイル |
| harness | `config/harness.yml` | 各プロジェクトの `.agentops/harness.yml` または `.agentops/harnesses/<task>.yml` |

## 設定ファイルごとの役割

`CLAUDE.md` と `AGENTS.md` には、安定して使う作業思想、参照優先順位、ユーザー個人の開発方針、停止条件、検証方針を書く。対象 CLI の機械可読な settings、config、permission、sandbox、approval、hook、MCP の具体値は、グローバル本文へ埋め込みすぎず、反映時点の公式 docs と実環境を確認して対象ファイルへ分ける。

グローバル設定本文に置くもの:

- 日本語運用、GitHub PR 運用、計画承認、DbC、レビュー修正ループ、最新性確認、docs 更新方針。
- `agentops` を参照資料として読む方針と、採用する内容、調整する内容、見送る内容を計画する方針。
- MCP、hooks、skills、subagents、permission、sandbox、approval を反映前に確認する観点。
- 実プロジェクトではプロジェクト固有の `CLAUDE.md` / `AGENTS.md` / docs / `.agentops/` を優先する方針。

グローバル設定本文に置きすぎないもの:

- 実プロジェクト固有の test / build / deploy / rollback コマンド。
- secret、API key、個別アカウント名、環境名、監視先、remote URL。
- 変化しやすい model id、CLI 引数、MCP transport、hook event、permission rule の詳細。
- 対象 CLI の settings / config で表現すべき機械可読設定。

## CLI 別の確認観点

CLI 固有仕様はこのリポジトリで固定しきらない。反映時には、対象 CLI の公式 docs、`--help`、実設定ファイル、実際の読み込み状態を確認する。

| 観点 | Claude Code | Codex |
| --- | --- | --- |
| 指示ファイル | `~/.claude/CLAUDE.md` とプロジェクト側 `CLAUDE.md` の階層、読み込み状態、`/memory` などの確認方法を確認する。 | `~/.codex/AGENTS.md`、必要なら `AGENTS.override.md`、プロジェクト側 `AGENTS.md` の階層と読み込み状態を確認する。 |
| settings / config | `~/.claude/settings.json`、project/local/managed settings、CLI 引数の優先順位を確認する。 | `~/.codex/config.toml`、profile、project trust、CLI 引数の優先順位を確認する。 |
| MCP | `claude mcp`、MCP scope、secret 管理、OAuth、出力上限、project shared config の承認を確認する。 | `codex mcp`、`config.toml` の MCP server 設定、tool approval、parallel tool call の安全性を確認する。 |
| hooks | settings 側 hook、event、matcher、blocking 可否、ログ、timeout、失敗時挙動を確認する。 | Codex hooks の対応状況、設定場所、sandbox / approval との関係、実行環境を確認する。 |
| skills | user / project / plugin skill の置き場、frontmatter、手動起動と自動起動、tool pre-approval を確認する。 | Codex skills の置き場、plugin 連携、読み込み条件、実行環境を確認する。 |
| subagents | user / project subagent、tool 権限、MCP tool 継承、役割分担を確認する。 | Codex subagents の設定場所、利用可能な tool、delegation と workspace 共有条件を確認する。 |
| permissions / sandbox / approval | permission allow / ask / deny、bypass 系 mode の扱い、追加 directory、project trust を確認する。 | `sandbox_mode`、workspace-write の writable roots / network、approval policy、app-server 経由時の実挙動を確認する。 |
| 反映後確認 | `claude --version`、`claude --help`、`/memory`、`/config`、`/mcp`、hook/skill/subagent の読み込み確認を行う。 | `codex --version`、`codex --help`、`codex sandbox`、読み込み済み instruction の確認、app-server 再起動後の挙動確認を行う。 |

反映時の詳細な手順は [グローバル設定反映チェックリスト](16-global-settings-application-checklist.md) を参照する。

## グローバル設定の境界

グローバル設定には、日本語運用、GitHub を正とするバージョン管理、ブランチ保護、DbC、曖昧指示の扱い、レビュー修正ループ、最新性確認、ドキュメント更新必須ルール、汎用 MCP 導入確認方針を置く。

また、実プロジェクト作業の既定対象は `~/dev` 配下、dotfiles は明示依頼がない限り対象外、主なWebスタックは Nuxt / Next.js / PHP / Go、主なリリース先は Cloudflare Workers / Pages、Xserver、GCP、ローカルサーバーというテンプレート前提を置く。

プロジェクト固有のビルド、テスト、デプロイ、禁止事項、MCP の詳細設定、hook の詳細は各プロジェクト側に置く。Context7 と Google Stitch のような汎用 MCP はグローバルで導入確認方針を持ち、プロジェクト側では利用可否、追加 allowlist、secret 管理方法を具体化する。

Cloudflare、Xserver、GCP、ローカルサーバーの実デプロイコマンド、アカウント、環境名、secret、rollback手順、監視先は各プロジェクト側に置く。

harness の実体もプロジェクト固有に置く。`config/harness.yml` は、task spec、setup、allowed commands、fixtures、oracle、artifact、replay、sandbox/network/secret 条件を揃えるためのコピー元に留める。

## モデル名の扱い

モデル名や CLI 引数は変化しやすい。グローバル設定本文には固定モデル名を増やしすぎず、`config/model-catalog.yml` の論理ロールを更新して扱う。

`config/model-catalog.yml` はこのプロジェクト専用ではなく、共通雛形である。実運用では `role` と `target_cli` の組み合わせで候補を選ぶ。たとえば `architect_frontier` でも、Codex CLI なら OpenAI 側、Claude Code CLI なら Anthropic 側の model id を使う。

`model_id: null` は未確認を表す。公式 docs 確認後に、グローバル設定または各プロジェクトの `.agentops/model-catalog.yml` で埋める。

CLI Wrapper から実コマンドを呼ぶ場合は、次のどちらかを使う。

- `AGENTOPS_CODEX_CMD`
- `AGENTOPS_CLAUDE_CMD`

例:

```sh
export AGENTOPS_CODEX_CMD='codex exec --model {model} --reasoning-effort {effort} -'
export AGENTOPS_CLAUDE_CMD='claude --model {model} --print'
```

使用前に、それぞれの公式 docs で現在の CLI 仕様を確認する。
