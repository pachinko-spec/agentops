---
last_reviewed: 2026-04-28
next_review_by: 2026-07-31
reviewer: pachinko-spec
language: ja
applies-to: shared-cli-spec
---

# CLI Wrapper 仕様

## 目的

`agentops` は Claude Code / Codex を相互に呼び出すための薄い wrapper である。
依頼内容、実行コマンド、stdout/stderr、結果、状態を `.agentops/runs/` に保存し、セッションをまたいだ追跡を可能にする。

再現性が必要な委譲では、request に harness spec のパスを含める。harness は入力契約、CLI Wrapper は実行記録という責務に分ける。詳細は [Harness Engineering](12-harness-engineering.md) を参照する。

## コマンド

```text
scripts/agentops delegate --to codex --role review_frontier --model <codex-model-id> --effort xhigh --input .agentops/plans/current.md
scripts/agentops delegate --to claude --role architect_frontier --model <claude-model-id> --effort xhigh --message "設計をレビューしてください"
scripts/agentops delegate --to codex --role review_frontier --dry-run --input README.md
scripts/agentops runs
scripts/agentops doctor

# 将来実装 (別 plan で追加、本 docs は spec のみ)
scripts/agentops localize --project <path> [--dry-run] [--strategy auto|greenfield|inventory-rebuild|coexistence|freeze]
```

> **実装ステータス注記**: `delegate` / `runs` / `doctor` / `archive` / `localize` は実装済 (`tools/agentops_cli/`)。`localize` は dry-run のみで、`--strategy auto` (既定) で docs/19 §4 戦略の意思決定木を機械適用し、判定不能ケースは `needs-user-confirmation` で escalate する。`--apply` (本反映) は将来仕様。

## 入力境界

- `--run-id` は ASCII の英数字、`-`、`_` を中心にした slug へ正規化し、`.agentops/runs/` 配下にだけ run directory を作る。`../` などの path traversal は run path としては使われない。明示した run_id が既存の場合は、過去の run log を上書きせずエラーにする。
- `--input` は `--project` で指定した project root 配下だけを読む。相対パスは project root 基準で解決し、絶対パスや symlink が project 外へ出る場合はエラーにする。
- `--effort` は `low`、`medium`、`high`、`xhigh`、`max` のみ受け付ける。対象 CLI 側の対応状況はバージョンに依存するため、実行前に対象 CLI の `--help` や公式 docs で確認する。

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

既定コマンドは最小の雛形であり、実運用では公式 docs と CLI 現物で現在の仕様を確認してから環境変数で上書きする。

Codex CLI 0.125.0 では `codex exec --reasoning-effort ...` は受け付けず、`-c model_reasoning_effort=...` で推論レベルを渡す。Claude Code 2.1.119 では `--effort` と `--print` を併用する。
これより古い CLI では既定 template が動かない可能性があるため、対象バージョンに合わせて `AGENTOPS_CODEX_CMD` / `AGENTOPS_CLAUDE_CMD` または `--command-template` で明示的に上書きする。

```sh
export AGENTOPS_CODEX_CMD='codex exec {model_arg} -c model_reasoning_effort={effort} -'
export AGENTOPS_CLAUDE_CMD='claude {model_arg} --effort {effort} --print'
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

template 変数の値は argv 注入を避けるため shell quoting してから `shlex.split` する。未知の `{var}` や format 修飾はエラーにし、利用可能な変数名を表示する。

`--model` を組み立てる場合は `{model}` より `{model_arg}` を推奨する。`{model_arg}` は `--model <model>` 全体を生成し、`--model` 未指定時は空になるため、空の model 値で次の option を誤って消費しにくい。

依頼本文は既定では stdin で外部 CLI に渡す。stdin を読まない CLI に切り替える場合は、template 側で `{request_file}` を参照する。

`--command-template` や `AGENTOPS_*_CMD` に secret、token、API key、auth file の中身を書かない。展開後の command は `status.json` と dry-run の `result.md` に平文で残る。

`result.md` の stdout / stderr は Markdown code block として保存する。出力本文に backtick fence が含まれる場合は、本文内の連続 backtick より長い fence を選び、表示用 Markdown の構造が崩れにくいようにする。`stdout.log` / `stderr.log` には外部 CLI の出力本文をそのまま保存する。

## 状態

| state | 意味 |
| --- | --- |
| `dry_run` | 記録だけ作成し、外部 CLI は実行していない |
| `running` | 外部 CLI 実行中 |
| `succeeded` | exit code 0 で完了 |
| `failed` | exit code 非 0、コマンド不明、template error、起動時の OS error |
| `timeout` | timeout で停止 |

## smoke test の実行環境

dry-run は sandbox 内で実行してよい。外部 CLI を実際に呼ぶ smoke test は、ユーザー承認後に通常環境で実行する。

Codex / Claude Code CLI は、認証、セッション初期化、ネットワーク、ローカル設定の読み込みを行う。Codex App や他の sandbox 内では、read-only filesystem、ネットワーク制限、session persistence 制限により、CLI wrapper ではなく実行環境側の理由で失敗または timeout することがある。

実 smoke test では、session log を増やしにくいオプションを優先する。

```sh
scripts/agentops delegate --to codex --role smoke --effort xhigh --message "Return exactly: OK" --timeout 120 --command-template 'codex exec {model_arg} -c model_reasoning_effort={effort} --ephemeral -'
scripts/agentops delegate --to claude --role smoke --effort xhigh --message "Return exactly: OK" --timeout 120 --command-template 'claude {model_arg} --effort {effort} --print --no-session-persistence'
```

通常環境で成功し、stdout が期待値どおりであることを `.agentops/runs/{run_id}/` に残す。sandbox 内の失敗 run がある場合は、通常環境での再実行結果と区別して報告する。

## DbC との関係

`scripts/agentops` CLI wrapper は DbC のうち、別 CLI / 別モデルへの委譲とその実行記録の永続化層を機械的に支える。DbC 5 条件（前提・不変・完了・禁止・停止）の単一真ソースは [DbCと品質ゲート](03-dbc-and-quality-gates.md) であり、本章ではそれを **delegate / harness 文脈にどう適用するか** だけを記す。

CLI wrapper の適用範囲: `.agentops/runs/` に書き込め、対象 CLI がインストール済みで、コマンドテンプレートが現在の仕様に合っていること。harness spec を使う場合は、参照先がプロジェクトローカルに存在し、setup・oracle・artifact 方針が読めることが前提。実行中は依頼本文と実行結果を同じ `run_id` の下に保存し、dry-run では外部 CLI を実行せず、stdout/stderr を破棄しない。完了は `status.json` と `result.md` の作成（実実行では exit code を呼び出し元へ返す）まで。CLI が見つからない・timeout・公式 docs と実コマンド仕様の不整合があれば、wrapper をスキップせずに作業を停止し DbC 停止条件として扱う。
