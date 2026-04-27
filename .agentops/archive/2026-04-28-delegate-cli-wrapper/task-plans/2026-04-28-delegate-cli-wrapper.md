# agentops delegate CLI wrapper smoke確認

- plan_id: 2026-04-28-delegate-cli-wrapper
- branch: codex/delegate-cli-wrapper
- completed_at: 2026-04-28T03:25:00+09:00
- scope: `/home/otaku/agentops` 内の `scripts/agentops`、`tools/agentops_cli/__main__.py`、関連docs、`.agentops/runs/`

## 実施内容

1. README、docs、CLI wrapper 実装、model catalog、`.agentops/`、Codex/Claude CLI help、公式docsを確認した。
2. 修正前 dry-run で、Codex 既定 template が現行 CLI で拒否される `--reasoning-effort` を記録し、Claude 既定 template が `--effort` を渡していないことを確認した。
3. `DEFAULT_TEMPLATES`、CLI wrapper docs、config template、hook env example を現行 CLI に合わせて最小修正した。
4. 修正後 dry-run で Codex/Claude の request/status/stdout/stderr/result 作成と command 記録を確認した。
5. ユーザー承認後、実 Codex / Claude smoke test を実行した。
6. `docs/10-cli-wrapper.md` に、実 smoke test は通常環境で行うこと、sandbox 内失敗と通常環境成功を区別して記録することを追記した。
7. Claude Code による実 cross-review を wrapper 経由で実行した。
8. compile、doctor、diff check、agentops-watch を実行した。

## dry-run

- `dryrun-current-codex-smoke`: 修正前 Codex 既定。`codex exec --model <verified-codex-model> --reasoning-effort xhigh -`
- `dryrun-current-claude-smoke`: 修正前 Claude 既定。`claude --model <verified-anthropic-model> --print`
- `dryrun-template-claude-effort`: 明示 template。`claude --model <verified-anthropic-model> --effort xhigh --print`
- `dryrun-fixed-codex-smoke`: 修正後 Codex 既定。`codex exec --model <verified-codex-model> -c model_reasoning_effort=xhigh -`
- `dryrun-fixed-claude-smoke`: 修正後 Claude 既定。`claude --model <verified-anthropic-model> --effort xhigh --print`
- `dryrun-template-codex-config`: 明示 template。`codex exec --model <verified-codex-model> -c model_reasoning_effort=xhigh -`

## 実 smoke test

- `smoke-codex-actual`: sandbox 内で read-only session 初期化に失敗。
- `smoke-codex-actual-escalated`: 通常環境で成功。stdout は `OK`。
- `smoke-claude-actual`: sandbox 内で timeout。
- `smoke-claude-actual-escalated`: 通常環境で成功。stdout は `OK`。

## cross-review

- `cross-review-claude-delegate-wrapper`: Claude Code / Anthropic reviewer として通常環境で成功。
- 結果: P0/P1 なし。
- P2: `--effort` / `--run-id` / `--input` hardening、ユニットテスト、例外処理、バージョン下限明記など。
- 採否: 今回の目的は cross-review が実際に動くことの確認なので、P2 は次 hardening フェーズ候補として記録し、この変更の blocker とはしない。
- `.agentops/runs/` と `.agentops/.tmp/` は session id、ローカルパス、stderr、model output を含みうるため、Git には載せず要約だけを archive に残す。

## 検証

- `python3 -m compileall tools`: pass
- `python3 -m tools.agentops_cli doctor --project .`: pass
- `git diff --check`: pass
- `scripts/agentops-watch check --projects config/projects.yml`: pass with expected dirty worktree warning
- `cross-review-claude-delegate-wrapper`: pass, P0/P1 none

## 不変条件

- `~/.codex`、`~/.agents`、shell profile、Claude Code global 設定は変更していない。
- secret、token、auth file、session log は表示・保存していない。
- main 直 push、破壊的操作、plugin 導入はしていない。
