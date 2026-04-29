---
last_reviewed: 2026-04-28
next_review_by: 2026-07-31
reviewer: pachinko-spec
language: ja
---

# 監視 / archive CLI 仕様

## 目的

`agentops-watch` は、ローカルまたは監視ホストから複数プロジェクトの状態を確認するための小さな CLI である。
cron / systemd timer / 手動実行から呼び出す。

`agentops archive` は、完了 plan / task を `.agentops/archive/<plan-id>/` に移し、`.agentops/prompts/next-session.md` を機械的に更新する CLI である。CLAUDE.md / AGENTS.md durable instructions の「auto-merge 後の必須手順」が要求する後処理を、人手忘れに頼らず一発で実行するためのもの。

## コマンド

> **実装ステータス注記**: `notify --kind <kind>` サブコマンドと kind 別 envvar マッピング、ANT_TIME 頻度上限ガード、HTTP 429 / 5xx 停止条件は **実装済** ([docs/18](18-notification-strategy.md) §通知種別と §DbC との関係 / §ANT_TIME 頻度上限ガード を満たす)。`--kind` 未指定での旧 envvar `AGENTOPS_DISCORD_WEBHOOK_URL` への fallback path は **deprecated** で、stderr に deprecation 警告を出した上で動作する後方互換 path として残してある (将来撤去)。`check` と `archive` は実装済。`localize` は仕様のみ規定の **契約段階** ([docs/19](19-project-localization.md))。

```text
scripts/agentops-watch check --project .
scripts/agentops-watch check --projects config/projects.yml --freshness config/freshness-sources.yml
scripts/agentops-watch check --json

# notify の現行 (kind 必須、4 channel)
scripts/agentops-watch notify --kind daily|weekly|monthly --projects config/projects.yml [--dry-run]
scripts/agentops-watch notify --kind session-start|session-end --project <path>          [--dry-run]
scripts/agentops-watch notify --kind permission-wait --project <path> --message <tool>   [--dry-run]
scripts/agentops-watch notify --kind alert [--project <path>] --message <text>           [--dry-run] [--bypass-rate-limit]
scripts/agentops-watch notify --kind stop-failure --project <path> --message <text>      [--dry-run]

# notify の旧 path (deprecated、--kind 未指定時のみ動作、AGENTOPS_DISCORD_WEBHOOK_URL を参照)
scripts/agentops-watch notify [--dry-run] --projects config/projects.yml

scripts/agentops archive plan --plan-id <id> --summary <text> [--date YYYY-MM-DD] [--include-runs] [--dry-run]
scripts/agentops archive task --task-id <basename>                                                    [--dry-run]
```

Discord 通知を実送信する場合は、kind 別に Webhook URL を環境変数に置く。設計思想と channel 区分は [通知戦略](18-notification-strategy.md) を参照する。

```sh
# kind → envvar マッピング (本 CLI は env 名の固定マッピングを内部で持つ)
export DISCORD_WEBHOOK_URL_DAILLY='https://discord.com/api/webhooks/...'    # --kind daily
export DISCORD_WEBHOOK_URL_WEEKLY='https://discord.com/api/webhooks/...'    # --kind weekly
export DISCORD_WEBHOOK_URL_MONTHLY='https://discord.com/api/webhooks/...'   # --kind monthly
export DISCORD_WEBHOOK_URL_ANT_TIME='https://discord.com/api/webhooks/...'  # --kind session-* / permission-wait / alert / stop-failure

scripts/agentops-watch notify --kind daily --projects config/projects.yml
```

旧 envvar `AGENTOPS_DISCORD_WEBHOOK_URL` は deprecated。新規 cron / 新規 hook では使用せず、上記 4 本立てへ移行する。互換性のため本 CLI は envvar 名を **kind の固定マッピング** で解決し、対象 envvar が未設定の場合は exit 2 で停止する (旧名へのフォールバックは行わない方針)。

実反映前の動作確認は `--dry-run` で payload だけ生成し、Webhook へ送信させない:

```sh
# digest 系 dry-run (~/dev/ 配下プロジェクトの集計を payload 化)
scripts/agentops-watch notify --kind daily --projects config/projects.yml --dry-run

# ANT_TIME 系 dry-run (project / message を渡して embed payload を確認)
scripts/agentops-watch notify --kind alert --message "smoke test" --dry-run
scripts/agentops-watch notify --kind session-start --project /home/<user>/dev/<proj> --dry-run
```

cron / systemd timer / hook への組み込み雛形は [`config/cron.example`](../config/cron.example) と [`templates/claude/hooks/session-notify-stub.md`](../templates/claude/hooks/session-notify-stub.md) を参照する。

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
- Discord webhook への digest 送信 (channel と kind の対応は [通知戦略](18-notification-strategy.md) を参照)

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

## DbC との関係

`scripts/agentops-watch` 監視 CLI は DbC のうち、stuck run / dirty worktree / freshness 等の状態観測層を機械的に支える。DbC 5 条件の単一真ソースは [DbCと品質ゲート](03-dbc-and-quality-gates.md) であり、本章ではそれを **監視 CLI 文脈にどう適用するか** だけを記す。

監視 CLI の適用範囲: 監視対象 `path` が存在し、Git 情報を読む権限があり、Discord 通知を実送信する場合は kind に対応する Webhook URL (`DISCORD_WEBHOOK_URL_DAILLY` / `WEEKLY` / `MONTHLY` / `ANT_TIME`、設計は [通知戦略](18-notification-strategy.md)) が環境変数にあること。実行中は secret をリポジトリに保存せず、プロジェクトのファイルを変更せず、警告とエラーを区別する。完了は text または JSON の report 出力（dry-run 通知では送信 payload だけ表示）まで。監視対象不在・Git コマンド失敗・kind に対応する Discord webhook 未設定で実送信を求められた場合は監視 CLI をスキップせずに作業を停止し DbC 停止条件として扱う。旧 envvar `AGENTOPS_DISCORD_WEBHOOK_URL` は deprecated で本 CLI のフォールバック対象としない。

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

- `--plan-id` / `--task-id` は `^[A-Za-z0-9][A-Za-z0-9_.-]*$` のみ許可し、連続ピリオド (`..`) を弾く（パストラバーサル防止）。`detect_active_plan_id` の戻り値も同じ検証を通す（frontmatter 改変への二重防御）。
- `--date` は `YYYY-MM-DD` 形式のみ受け付ける。既定は Asia/Tokyo の今日。
- `--summary` に改行 (`\n` / `\r`) を含めると exit 2。`|` は archive README の table を壊さないよう `\|` に escape して書き出す。
- 移動先が既に存在する場合は move 前に exit 2 で停止する（途中まで move して残りで失敗、を防ぐ）。
- 実行順序は **preflight → 計画表示 → dry-run なら return → move 全件 → README 挿入 / next-session 更新**。`OSError` は `AgentOpsError` で包んで stderr へ。half-state を残さない。
- README 編集は同ディレクトリの一時ファイルへ書き出してから rename する atomic write。途中で停止しても原本は無傷。
- next-session.md 更新も同様に atomic write。`completed_tasks: []` のような inline 空配列はブロック形式へ正規化してから 1 行追記する。block 形式でも inline 空配列でもない場合は entry_point だけ更新し配列追記はスキップする。
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

### DbC との関係（archive サブコマンド）

archive サブコマンドは [DbCと品質ゲート](03-dbc-and-quality-gates.md) を **CLI 固有の atomic write / preflight / path 検証の文脈に適用したもの**。CLI 動作仕様そのものに密着しているため、5 条件の具体内容は以下のとおり個別に展開する（docs/03 の汎用テンプレに含まれない実装制約を含む）。

- **適用前提**: `--task-id` 利用時に `.agentops/plans/current.md` が存在し、`> plan-id: \`<id>\`` 行から plan-id を一意に抽出できる。`--plan-id` / 抽出された plan-id / `--task-id` がいずれも `^[A-Za-z0-9][A-Za-z0-9_.-]*$` を満たし `..` を含まない。`--date` を指定する場合は `YYYY-MM-DD`。`--summary` に改行を含めない。移動先（archive 配下の各 dst）が事前に存在しない。
- **適用不変**: secret 値をログ・archive・README に書かない。`archive/README.md` の既存 row は改変しない（先頭挿入のみ）。`next-session.md` の本文（マニュアル記述部分）には触らない。部分書き込みで停止せず atomic write で完結する。メタデータ更新（README row 挿入 / next-session.md 更新）は move 全件成功後に行う。
- **適用完了**: 移動完了後、`.agentops/tasks/<basename>.md` または対象 plan のファイル群が archive 配下に存在する。next-session.md の `entry_point` と（block 形式または inline 空配列 → 正規化後の block 形式の）`completed_tasks` が更新されている（task サブコマンドのみ）。README.md table の先頭に新規 row が 1 行追加されている（plan サブコマンドのみ）。exit code 0 で終了する。
- **適用停止**: active plan-id が検出できない / 抽出値が DbC を満たさない（exit 2）。対象 task ファイルが存在しない（exit 2）。`--plan-id` / `--task-id` / `--date` / `--summary` が検証に失敗（exit 2）。移動先が既に存在する（exit 2、preflight 失敗）。`git mv` または `shutil.move` が失敗した（exit 2、stderr に元エラーを表示）。
