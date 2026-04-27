# 最新性と監視

## 最新性ポリシー

- ライブラリ、ランタイム、CLI、API、モデルはAIの記憶だけで判断しない。
- 原則として最新LTSまたは安定版を使う。
- 破壊的変更が大きい場合は採用理由と回避理由を書く。
- Context7などの知識取得ツールは使ってよいが、更新遅延を前提に一次情報も確認する。
- 導入時は公式docs、GitHub、package registry、release notes、security advisoryを確認する。

## 陳腐化チェック対象

- Claude Code / Codex の公式docs
- OpenAI / Anthropic のモデル一覧、推奨モデル、料金、制限
- hooks、subagents、skills、plugins、MCPの仕様
- Node.js、Python、Rust、Goなど主要ランタイムのLTS
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
