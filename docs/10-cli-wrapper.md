# CLI Wrapper 仕様

## 目的

`agentops` は Claude Code / Codex を相互に呼び出すための薄い wrapper である。
依頼内容、実行コマンド、stdout/stderr、結果、状態を `.agentops/runs/` に保存し、セッションをまたいだ追跡を可能にする。

## コマンド

```text
scripts/agentops delegate --to codex --role review_frontier --model <codex-model-id> --effort xhigh --input .agentops/plans/current.md
scripts/agentops delegate --to claude --role architect_frontier --model <claude-model-id> --effort xhigh --message "設計をレビューしてください"
scripts/agentops delegate --to codex --role review_frontier --dry-run --input README.md
scripts/agentops runs
scripts/agentops doctor
```

## 実行記録

```text
.agentops/runs/{run_id}/
  request.md
  status.json
  stdout.log
  stderr.log
  result.md
  artifacts/
```

`status.json` には次を保存する。

`created_at`、`started_at`、`completed_at` は `Asia/Tokyo` の日本時間で、timezone offset つき ISO 形式にする。

- `run_id`
- `state`
- `to`
- `role`
- `model`
- `effort`
- `project`
- `request_file`
- `command`
- `started_at`
- `completed_at`
- `exit_code`

## ロールとモデル

- `--role` は `orchestrator_frontier`、`architect_frontier`、`review_frontier` などの論理ロールを渡す。
- `--model` は対象 CLI で確認済みの実 model id を渡す。論理ロール名をそのまま渡さない。
- `--model` を省略した場合は、外部 CLI や wrapper template 側の既定値に委ねる。
- `config/model-catalog.yml` は候補表であり、この最小 wrapper はまだ自動解決しない。

## 外部 CLI への接続

既定コマンドは最小の雛形であり、実運用では公式 docs で現在の CLI 仕様を確認してから環境変数で上書きする。

```sh
export AGENTOPS_CODEX_CMD='codex exec --model {model} --reasoning-effort {effort} -'
export AGENTOPS_CLAUDE_CMD='claude --model {model} --print'
```

使用可能なテンプレート変数:

| 変数 | 意味 |
| --- | --- |
| `{to}` | `codex` または `claude` |
| `{role}` | 委譲ロール |
| `{model}` | 対象 CLI で確認済みの実 model id。省略時は空文字 |
| `{model_arg}` | `--model <model>` 形式の引数。`--model` 未指定時は空文字 |
| `{effort}` | 推論レベル |
| `{request_file}` | 生成された依頼ファイル |
| `{run_dir}` | 実行記録ディレクトリ |

## 状態

| state | 意味 |
| --- | --- |
| `dry_run` | 記録だけ作成し、外部 CLI は実行していない |
| `running` | 外部 CLI 実行中 |
| `succeeded` | exit code 0 で完了 |
| `failed` | exit code 非 0 またはコマンド不明 |
| `timeout` | timeout で停止 |

## DbC

前提条件:

- `.agentops/runs/` に書き込める。
- 実実行する場合は対象 CLI がインストール済みで、コマンドテンプレートが現在の仕様に合っている。

不変条件:

- 依頼本文と実行結果を同じ `run_id` の下に保存する。
- dry-run では外部 CLI を実行しない。
- stdout/stderr を破棄しない。

完了条件:

- `status.json` と `result.md` が作成される。
- 実実行では exit code が呼び出し元へ返る。

停止条件:

- CLI が見つからない。
- timeout した。
- 公式 docs と実コマンド仕様が合わない。
