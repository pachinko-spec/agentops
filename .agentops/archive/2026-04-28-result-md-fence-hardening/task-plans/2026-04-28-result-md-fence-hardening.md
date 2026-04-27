# Task Plan: result.md code fence hardening

plan_id: 2026-04-28-result-md-fence-hardening
status: completed
created_at: 2026-04-28
completed_at: 2026-04-28T04:24:42+09:00
timezone: Asia/Tokyo
branch: codex/fix-result-md-fence

## 今回の目的

PR #20 cross-review で P3 として延期した `result.md` の code fence 表示崩れ対策を、`/home/otaku/agentops` リポジトリ内だけで最小実装した。

## 実施内容

1. `git status --short --branch`、README、`docs/10-cli-wrapper.md`、`tools/agentops_cli/__main__.py`、PR #20 / #21 の archive / run 記録を確認した。
2. `tools/agentops_cli/__main__.py` に `markdown_code_block()` を追加した。
3. `result.md` の dry-run command、stdout、stderr の code block 生成を helper 経由にした。
4. stdout/stderr の本文に含まれる最長連続 backtick より長い fence を選び、Markdown 表示用の fence collision を避けるようにした。
5. `stdout.log` / `stderr.log` は外部 CLI の出力本文をそのまま保存する契約を維持した。
6. `tests/test_agentops_cli.py` に helper 単体テスト、空本文の compact 表示、stdout/stderr に fence を含む実行結果の回帰テストを追加した。
7. `docs/10-cli-wrapper.md` に `result.md` は fence collision を避け、stdout/stderr log は原文保存であることを短く追記した。

## 検証

- `python3 -m compileall tools`: pass
- `python3 -m unittest discover`: pass, 12 tests
- `python3 -m tools.agentops_cli doctor --project .`: pass
- `git diff --check`: pass
- `scripts/agentops-watch check --projects config/projects.yml`: pass with expected dirty worktree warning
- `scripts/agentops delegate --to codex --role smoke --effort xhigh --message "Return exactly: OK" --dry-run`: pass, run `20260428T042420+0900-codex-smoke`
- `scripts/agentops delegate --to claude --role smoke --effort xhigh --message "Return exactly: OK" --dry-run`: pass, run `20260428T042420+0900-claude-smoke`

## 今回は行わなかったこと

- 実 Codex / Claude CLI 呼び出し。
- `~/.codex`、`~/.agents`、shell profile、Claude/Codex global 設定の変更。
- stdout/stderr の内容自体の変換、削除、escape。
- P2 safety hardening の追加。

## 残リスク

- `result.md` の Markdown 表示品質改善であり、外部 CLI の出力内容そのものの安全性検査ではない。
- 追加 cross-review は、小さな P3 表示品質改善で既存の指定テストと自己レビューで十分と判断して省略した。
