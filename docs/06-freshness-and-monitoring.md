---
last_reviewed: 2026-04-28
next_review_by: 2026-07-31
reviewer: pachinko-spec
language: ja
---

# 最新性と監視

## 最新性ポリシー

- ライブラリ、ランタイム、CLI、API、モデルはAIの記憶だけで判断しない。
- 原則として最新LTSまたは安定版を使う。
- 破壊的変更が大きい場合は採用理由と回避理由を書く。
- Context7などの知識取得ツールは使ってよいが、更新遅延を前提に一次情報も確認する。
- MCP対応クライアントで Context7 と Google Stitch が未導入なら導入する。導入時は現在の公式docs、GitHub、release notes、クライアント側MCP docsを確認する。
- API key は shell profile（例: `.bashrv`）で export 済みの `CONTEXT7_API_KEY` と `STITCH_API_KEY` を使い、secret値をリポジトリ、PR、ログへ出さない。
- 導入時は公式docs、GitHub、package registry、release notes、security advisoryを確認する。

## last_reviewed フロントマター形式

`docs/` 直下の番号付き Markdown 全件に YAML フロントマター（`---` 区切り）で `last_reviewed` / `next_review_by` / `reviewer` / `language` の 4 キーを記録する。Markdown 標準のメタデータ表記であり、task 08 (P1-07) の CI freshness-check ジョブが grep / yq でパースしやすく、既存 docs ビルドツールへの影響もない。blockquote 互換形式（`> last-reviewed: ...`）は本文と区別が曖昧で機械判別が脆くなるため不採用とする。`docs/00-glossary.md` のみ glossary 性のメタ情報として `scope: glossary` を 5 キー目に保持する例外を許容する。共通 4 キーが全 docs に存在することを不変条件とし、ファイル固有のキー追加（例: `scope`）は本不変条件を破らない。日付は ISO 8601 (`YYYY-MM-DD`)、`reviewer` は GitHub user 名、`language` は IETF BCP 47 sub-tag (`ja` / `en` 等) を記録する。

## 陳腐化チェック対象

- Claude Code / Codex の公式docs
- OpenAI / Anthropic のモデル一覧、推奨モデル、料金、制限
- hooks、subagents、skills、plugins、MCPの仕様
- Context7 MCP の install / API key / transport 仕様
- Google Stitch MCP / SDK / API key / transport 仕様
- Node.js、Python、Rust、Goなど主要ランタイムのLTS
- Nuxt、Next.js、PHP、Goなど主要Webスタック
- Cloudflare Workers / Pages、Xserver、GCP、ローカルサーバー運用に関わる公式docs
- 主要フレームワークとテストツール
- このリポジトリ内の設計docs、プロンプト、workflow、skill

## 監視プログラム案

このリポジトリに小さな監視CLIを置き、cronまたはsystemd timerから呼ぶ。

```text
scripts/
  agentops-watch
tools/
  agentops_monitor/
    __main__.py
    checks/
      freshness.py
      projects.py
      dependencies.py
      github.py
      agent_state.py
    notifiers/
      discord.py
config/
  projects.yml
  freshness-sources.yml
```

shell scriptはcronから呼ぶ薄い入口にする。JSON処理、GitHub API、Discord webhook、日付判定はPythonまたはNodeで実装する。

現在の最小実装は `scripts/agentops-watch` と `tools/agentops_monitor/` に置く。
標準ライブラリだけでローカル Git 状態、`.agentops/runs/`、`.agentops/tasks/`、`.agentops/handoffs/`、`freshness-sources.yml` の日付を確認する。
詳細は [監視CLI仕様](11-monitoring-cli.md) を参照する。

## Discord通知

Incoming Webhookを使う。Webhook URLはリポジトリに置かず、環境変数またはOS側のsecretに置く。

通知方針:

- 毎日: 全プロジェクトの作業状況ダイジェスト
- 1時間ごと: CI失敗、レビュー通過済みでマージ可能、stuck run、緊急リスク
- 週1: 設計思想、モデル、LTS、CLI仕様の陳腐化チェック

## 監視項目

- open PRのCI、reviewDecision、mergeable
- `.agentops/tasks/` の未完了タスク
- `.agentops/runs/` のstuck状態
- dirty worktreeが長時間続いているプロジェクト
- mainから大きく乖離した作業ブランチ
- model catalogやfreshness sourcesの最終確認日
- テスト失敗ログや未解決handoff

Harness spec は「何をどう再現し、何を成功とするか」を定義する。監視 CLI は harness を実行せず、run log、stuck run、handoff、freshness などの状態だけを読む。責務分離は [Harness Engineering](12-harness-engineering.md) を参照する。
