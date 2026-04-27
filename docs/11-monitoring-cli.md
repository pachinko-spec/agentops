# 監視 CLI 仕様

## 目的

`agentops-watch` は、ローカルまたは監視ホストから複数プロジェクトの状態を確認するための小さな CLI である。
cron / systemd timer / 手動実行から呼び出す。

## コマンド

```text
scripts/agentops-watch check --project .
scripts/agentops-watch check --projects config/projects.yml --freshness config/freshness-sources.yml
scripts/agentops-watch check --json
scripts/agentops-watch notify --dry-run --projects config/projects.yml
```

Discord 通知を実送信する場合は、Webhook URL を環境変数に置く。

```sh
export AGENTOPS_DISCORD_WEBHOOK_URL='https://discord.com/api/webhooks/...'
scripts/agentops-watch notify --projects config/projects.yml
```

## 現在の実装範囲

標準ライブラリだけで次を確認する。

監視レポートの `generated_at` と freshness の日付判定は `Asia/Tokyo` の日本時間を基準にする。

- Git worktree の dirty file 数
- 現在ブランチ
- `origin/{default_branch}` との ahead / behind
- `.agentops/runs/` の stuck run
- `.agentops/tasks/` の未完了タスク数
- `.agentops/handoffs/` の引き継ぎ数
- `freshness-sources.yml` の `last_checked` と `max_age_days`
- Discord webhook への digest 送信

GitHub API、CI 詳細、reviewDecision、mergeable、package registry の取得は今後の拡張点とする。

Harness spec の実行は監視 CLI の責務ではない。監視 CLI は `.agentops/runs/`、`.agentops/tasks/`、`.agentops/handoffs/`、freshness 設定を読み、harness の実行結果や artifact が run log として残っているかを将来確認対象にできる。

## 設定

`config/projects.yml`:

```yaml
projects:
  - name: agentops
    path: .
    default_branch: main
    stuck_run_hours: 2
    max_behind_commits: 10
    max_ahead_commits: 50
```

`config/freshness-sources.yml`:

```yaml
sources:
  - name: OpenAI docs
    kind: docs
    url: https://platform.openai.com/docs
    max_age_days: 30
    last_checked: 2026-04-27
```

この YAML パーサは雛形に必要な浅い list-of-map だけを扱う。複雑な YAML が必要になったら Python 依存関係として PyYAML を採用し、その採用理由を docs に追記する。

## 終了コード

| exit code | 意味 |
| --- | --- |
| 0 | 実行成功 |
| 2 | 対象プロジェクトが読めない、Git リポジトリではない、通知設定がない |

警告だけの場合は cron 通知のため exit code 0 とする。

## DbC

前提条件:

- 監視対象 `path` が存在する。
- Git 情報を読む権限がある。
- Discord 通知を実送信する場合、Webhook URL が環境変数にある。

不変条件:

- secret をリポジトリに保存しない。
- 監視 CLI はプロジェクトのファイルを変更しない。
- 警告とエラーを区別する。

完了条件:

- text または JSON の report を出力する。
- dry-run 通知では送信 payload だけを表示する。

停止条件:

- 監視対象が存在しない。
- Git コマンドが失敗する。
- Discord webhook が未設定で実送信を求められた。
