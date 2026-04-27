# 2026-04-27 設計思想の土台作成プラン

## このセッションの責務

- AIエージェント用グローバル設定の設計思想を整理する。
- READMEにClaude Code / Codex用のグローバル設定プロンプトを置く。
- 設計思想、workflow、DbC、レビュー、モデルルーティング、最新性、監視方針をdocs化する。
- `.agentops/` 配下に今後のセッション継続用ディレクトリを用意する。
- 次セッションで実装すべき内容のプロンプトを提示する。

## 決定事項

- Claude Code と Codex は相互にCLI Wrapper経由でサブエージェントとして呼び出す。
- 作業前に必ずブランチを切り、main直pushは禁止する。
- 1セッションの時間・トークン上限は設けず、作業範囲、レビュー修正回数、テスト修正回数、引き継ぎ可能性で分割判断する。
- レビュー修正ループは最大2周とする。
- 実装後は必ずテストし、テスト成功後のみcommit/push可能とする。
- ドキュメント更新は完了条件に含める。
- 最新LTS・公式docs・GitHub・release notes確認を導入時の標準手順にする。
- 設定陳腐化と各プロジェクト進行状況は監視CLI + cron/systemd timer + Discord webhookで通知する。

## 作成した構成

```text
docs/
  01-philosophy.md
  02-workflow.md
  03-dbc-and-quality-gates.md
  04-model-routing.md
  05-review-policy.md
  06-freshness-and-monitoring.md
  07-global-vs-project.md
.agentops/
  plans/
  tasks/
  runs/
  reviews/
  handoffs/
  prompts/
skills/
workflows/
scripts/
config/
```

## 次セッションの主な責務

- Claude Code / Codex の実設定ファイル雛形を作る。
- 共通CLI Wrapper `agentops` の設計と最小実装を作る。
- hooksで強制できる品質ゲートを定義する。
- 監視CLIのMVPを作る。
- skills/workflowsの初期セットを作る。

## 未解決事項

- Claude Code / Codex の最新CLI設定形式の厳密確認。
- 現在利用可能な正式モデルIDの確認。
- Context7導入方法と、更新遅延時の一次情報確認フロー。
- Discord webhookのsecret管理方法。
- GitHub CLI / API のどちらを監視CLIの主経路にするか。
