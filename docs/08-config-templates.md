# 実設定雛形

このリポジトリの正本は `rules/`、`skills/`、`workflows/`、`docs/` に置く。`config/` はClaude Code、Codex、監視CLI、harnessなどへ反映するための雛形であり、正本ではない。正本を変更した場合は、必要な範囲だけconfigへ投影する。

このリポジトリでは、設計思想だけでなく Claude Code / Codex に投入できる雛形を `config/` に置く。

雛形を編集しても実際のグローバル設定には自動反映されない。運用へ反映する場合は、配置先の実ファイル、MCP 設定、shell profile、GitHub リモート設定を確認し、対象クライアントで読み込み状態まで検証する。

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

## グローバル設定の境界

グローバル設定には、日本語運用、GitHub を正とするバージョン管理、ブランチ保護、DbC、曖昧指示の扱い、レビュー修正ループ、最新性確認、ドキュメント更新必須ルール、汎用 MCP 導入確認方針を置く。

プロジェクト固有のビルド、テスト、デプロイ、禁止事項、MCP の詳細設定、hook の詳細は各プロジェクト側に置く。Context7 と Google Stitch のような汎用 MCP はグローバルで導入確認方針を持ち、プロジェクト側では利用可否、追加 allowlist、secret 管理方法を具体化する。

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
