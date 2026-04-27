# Self Review: PR20 delegate CLI P2 hardening

- reviewed_at: 2026-04-28T03:54:00+09:00
- branch: codex/pr20-p2-hardening
- scope: `tools/agentops_cli/__main__.py`、`scripts/agentops` 経由の delegate、`docs/10-cli-wrapper.md`、`tests/`

## 結論

P0/P1 なし。

## 確認観点

- `--run-id` は slug 化し、`.agentops/runs/` 配下に解決されることを確認してから run_dir を作る。明示 run_id の既存 run は上書きしない。
- `--input` は `Path.resolve()` 後に project root 配下かを確認し、project 外の絶対パスや symlink 解決先を拒否する。
- `--effort` は argparse choices と delegate 内 validation の両方で許可値に制限している。
- command template の値は `shlex.quote` 済みの値を `format` に渡し、`shlex.split` 後に argv 配列として `subprocess.run` へ渡す。未知変数と format 修飾は `CommandTemplateError` として扱う。
- template error と外部 command 起動時の OSError は `status.json` を `failed` に更新し、exit code を返す。missing command は 127、permission error は 126 に寄せた。
- dry-run では外部 CLI を起動せず、`request.md`、`status.json`、`stdout.log`、`stderr.log`、`result.md` を作成する。
- docs は実装後の入力境界、template 変数、secret 注意、状態定義と一致している。

## P2 対応状況

- 修正済み: template 変数由来の argv 注入リスク。
- 修正済み: `--input` の project 外 path traversal。
- 修正済み: `--run-id` の path traversal と既存 run log 上書き。
- 修正済み: 既定 template のバージョン注意。
- 修正済み: ユニットテスト不在。
- 修正済み: FileNotFoundError 以外の OSError で `status.json` が `running` のまま残るリスク。

## P2/P3 の延期

- P2 延期なし。
- P3 の result.md code fence escape は今回の hardening 完了条件外。表示崩れのみで、今回の path / argv / status safety とは独立しているため見送り。

## cross-review

今回は local wrapper の P2 hardening と最小テスト追加であり、実 external CLI 呼び出しや API 契約変更はない。PR #20 の Claude cross-review で P0/P1 なしを確認済みの指摘修正でもあるため、追加 cross-review は省略した。

## 検証

- `python3 -m compileall tools`: pass
- `python3 -m unittest discover`: pass, 9 tests
- `python3 -m tools.agentops_cli doctor --project .`: pass
- `git diff --check`: pass
- `scripts/agentops-watch check --projects config/projects.yml`: pass with expected dirty worktree warning
- Codex dry-run: pass
- Claude dry-run: pass
