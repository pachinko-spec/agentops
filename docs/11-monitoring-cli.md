# 監視 / archive CLI 仕様

## 目的

`agentops-watch` は、ローカルまたは監視ホストから複数プロジェクトの状態を確認するための小さな CLI である。
cron / systemd timer / 手動実行から呼び出す。

`agentops archive` は、完了 plan / task を `.agentops/archive/<plan-id>/` に移し、`.agentops/prompts/next-session.md` を機械的に更新する CLI である。CLAUDE.md / AGENTS.md durable instructions の「auto-merge 後の必須手順」が要求する後処理を、人手忘れに頼らず一発で実行するためのもの。

## コマンド

```text
scripts/agentops-watch check --project .
scripts/agentops-watch check --projects config/projects.yml --freshness config/freshness-sources.yml
scripts/agentops-watch check --json
scripts/agentops-watch notify --dry-run --projects config/projects.yml

scripts/agentops archive plan --plan-id <id> --summary <text> [--date YYYY-MM-DD] [--include-runs] [--dry-run]
scripts/agentops archive task --task-id <basename>                                                    [--dry-run]
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
- `.agentops/tasks/*.md` の未完了タスク数。完了済みtaskは `.agentops/archive/<plan-id>/tasks/` に移す
- `.agentops/handoffs/` のハンドオフ数
- `freshness-sources.yml` の `last_checked` と `max_age_days`
- Discord webhook への digest 送信

GitHub API、CI 詳細、reviewDecision、mergeable、package registry の取得は今後の拡張点とする。

Harness spec の実行は監視 CLI の責務ではない。 `.agentops/tasks/` 直下のMarkdownは未完了、進行中、blockedのtaskだけに限定する。監視 CLI は `.agentops/runs/`、`.agentops/tasks/`、`.agentops/handoffs/`、freshness 設定を読み、harness の実行結果や artifact が run log として残っているかを将来確認対象にできる。

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

## archive サブコマンド

[DbCと品質ゲート](03-dbc-and-quality-gates.md) と CLAUDE.md / AGENTS.md durable instructions の「auto-merge 後の必須手順」を機械的に実行するための CLI。完了 task / plan の archive 移動と `prompts/next-session.md` 更新の人手忘れを防ぐ。

### `agentops archive task --task-id <basename>`

PR マージ直後の **個別 task の後処理** を一発で行う。

- `.agentops/tasks/<basename>.md` を `.agentops/archive/<active-plan-id>/tasks/<basename>.md` へ移動する。git 管理下なら `git mv` を、そうでなければ `shutil.move` を使う。
- `.agentops/prompts/next-session.md` の `entry_point` を、`tasks/` に残るファイルの最小番号に書き換える。残ゼロなら `(none — all tasks archived; consider removing this file)` のマーカー文字列に置換する（ファイル自体は削除しない）。
- `completed_tasks` 配列に当該 `<basename>` を末尾追記する（既に存在すればスキップ）。
- `updated_at` を Asia/Tokyo の今日の日付へ更新する。
- 本文（マニュアル記述部分）には触らない。
- `--dry-run` で予定動作のみレポートする。

active plan-id は `.agentops/plans/current.md` の `> plan-id: \`<id>\`` 行から抽出する。検出失敗時は exit 2 で停止し、user に修正を促すメッセージを stderr に出す。

### `agentops archive plan --plan-id <id> --summary <text>`

**plan 全体の完了** 時のみ実行する。`.agentops/plans/current.md` / `task-plans/current.md` / `tasks/*.md`（README.md 除く）/ `reviews/*` を `.agentops/archive/<plan-id>/` 配下へ移し、`.agentops/archive/README.md` の Markdown table 先頭（separator 行直後 = 新しい順）に `| <date> | [<display-name>](<plan-id>/plan.md) | <summary> |` の row を挿入する。

- `<display-name>` は `<plan-id>` から `YYYY-MM-DD-` 日付プレフィックスを除いた残り。慣行に合わせる。
- 既存 row は変更しない。
- `--date` 省略時は Asia/Tokyo の今日。
- `--include-runs` を指定した場合のみ `.agentops/runs/*` を archive へ移す。runs は plan-id と直接紐づかないことが多いため既定では移動しない。
- `--dry-run` で予定動作のみレポートする。

### 既定の挙動と安全性

- `--plan-id` / `--task-id` は `[A-Za-z0-9_.-]+` のみ許可（パストラバーサル防止）。
- README 編集は同ディレクトリの一時ファイルへ書き出してから rename する atomic write。途中で停止しても原本は無傷。
- next-session.md 更新も同様に atomic write。
- archive ディレクトリが存在しない場合は親ごと作成する。`README.md` 自体が存在しない場合は本コマンドでは作成しない（運用ガイド外の状態と判断し exit 2 で停止）。

### ロールバック手順

万一誤った plan-id / task-id で archive してしまった場合:

1. `git status` / `git log -1 --stat` で実際の差分を確認。
2. `git mv` 経由で移動した場合: `git mv <archive 先パス> <元パス>` で戻す。さらに README.md / next-session.md の差分を `git checkout HEAD -- <ファイル>` で巻き戻す。
3. `shutil.move` 経由（git 管理外）の場合: `mv <archive 先パス> <元パス>` で物理的に戻し、README.md / next-session.md は手作業で修正する。
4. 取り消しが完了したら `python3 -m compileall tools` と `scripts/agentops-watch check`（存在時）で healthchecks を再実行する。

### 既存 hook との責務分担

- `scripts/agentops-watch` は read-only な観測 CLI。`.agentops/` を変更しない。
- `scripts/agentops archive` は明示的に呼ばれた時のみ `.agentops/` を変更する。pre-commit / pre-push hook では起動しない（ヒューマンエラーをマージ後に CLI 一発で解消する設計のため）。
- 本 CLI は `--dry-run` を通じて差分確認できるので、自動化スクリプトから呼ぶ場合も `--dry-run` を先に走らせて確認する運用を推奨する。

### DbC（archive サブコマンド）

前提条件:

- `--task-id` 利用時に `.agentops/plans/current.md` が存在し、`> plan-id: \`<id>\`` 行から plan-id を一意に抽出できる。
- `--plan-id` の値が `[A-Za-z0-9_.-]+` で `..` を含まない。

不変条件:

- secret 値をログ・archive・README に書かない。
- `archive/README.md` の既存 row は改変しない（先頭挿入のみ）。
- `next-session.md` の本文（マニュアル記述部分）には触らない。
- 部分書き込みで停止せず atomic write で完結する。

完了条件:

- 移動完了後、`.agentops/tasks/<basename>.md` または対象 plan のファイル群が archive 配下に存在する。
- next-session.md の `entry_point` と `completed_tasks` が更新されている（task サブコマンドのみ）。
- README.md table の先頭に新規 row が 1 行追加されている（plan サブコマンドのみ）。
- exit code 0 で終了する。

停止条件:

- active plan-id が検出できない（exit 2）。
- 対象 task ファイルが存在しない（exit 2）。
- `--plan-id` / `--task-id` が検証に失敗（exit 2）。
- `git mv` が失敗した（exit 2、stderr に git のエラーを表示）。
