# Task Plan: PR20 delegate CLI P2 hardening

plan_id: 2026-04-28-pr20-delegate-p2-hardening
status: completed
created_at: 2026-04-28
completed_at: 2026-04-28T03:54:00+09:00
timezone: Asia/Tokyo
branch: codex/pr20-p2-hardening

## 今回の目的

PR #20 の cross-review で確認された `scripts/agentops delegate` / `tools/agentops_cli` の P2 hardening を、`/home/otaku/agentops` 内だけで最小実装した。

## 実施内容

1. README、`docs/10-cli-wrapper.md`、`tools/agentops_cli/__main__.py`、PR #20 archive / run 記録を確認した。
2. `--run-id` の slug 化、`.agentops/runs/` 配下制約、既存 run log の上書き防止を追加した。
3. `--input` を project root 配下に制限し、project 外の絶対パスや symlink 解決先を拒否するようにした。
4. `--effort` を `low`、`medium`、`high`、`xhigh`、`max` に制限した。
5. command template の値を shell quoting してから `shlex.split` し、未知変数や format 修飾を分かりやすいエラーにした。
6. template error、FileNotFoundError、PermissionError を含む OSError、KeyboardInterrupt で run status を `failed` に確定しやすくした。
7. `tests/` を追加し、expand_command、delegate dry-run、run_id、input path、effort、template error、missing command を `unittest` で固定した。
8. `docs/10-cli-wrapper.md` に hardening 後の仕様、`{model_arg}` 推奨、secret を command template に書かない注意を追記した。

## 検証

- `python3 -m compileall tools`: pass
- `python3 -m unittest discover`: pass, 9 tests
- `python3 -m tools.agentops_cli doctor --project .`: pass
- `git diff --check`: pass
- `scripts/agentops-watch check --projects config/projects.yml`: pass with expected dirty worktree warning
- `scripts/agentops delegate --to codex --role smoke --effort xhigh --message "Return exactly: OK" --dry-run`: pass, run `20260428T035422+0900-codex-smoke`
- `scripts/agentops delegate --to claude --role smoke --effort xhigh --message "Return exactly: OK" --dry-run`: pass, run `20260428T035422+0900-claude-smoke`

## 今回は行わなかったこと

- `~/.codex`、`~/.agents`、shell profile、Claude/Codex global 設定の変更。
- 実 Codex / Claude CLI 呼び出し。
- model catalog 自動解決や harness 実行機能の追加。

## 残リスク

- `--command-template` 自体に利用者が危険な argv を直書きした場合、それは wrapper の検証対象外。docs で secret を書かないことを明記した。
- CLI 側の `--effort` 許容値はバージョンや model に依存しうる。wrapper は入力値の形を絞り、実対応は対象 CLI の docs / help 確認に委ねる。
