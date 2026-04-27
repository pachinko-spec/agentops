# Self Review: agentops delegate CLI wrapper smoke確認

- reviewed_at: 2026-04-28T03:25:00+09:00
- branch: codex/delegate-cli-wrapper

## 結論

P0/P1 なし。

## 確認観点

- Codex 現行 CLI 0.125.0 は `codex exec --reasoning-effort` を受け付けないため、`-c model_reasoning_effort={effort}` へ寄せた。
- Claude Code 2.1.119 は `--effort` と `--print` を help と公式docsで確認し、既定 template に追加した。
- dry-run の request/status/stdout/stderr/result が残ることを修正前後で確認した。
- ユーザー承認後、実 smoke test は Codex/Claude とも通常環境で成功した。
- 通常環境で実 smoke test する必要があることを `docs/10-cli-wrapper.md` に明記した。
- Claude Code による実 cross-review も wrapper 経由で成功した。P0/P1 はなし。
- `.agentops/runs/` と `.agentops/.tmp/` は Git ignore 対象にし、実行ログの要約だけを archive に残す方針にした。

## 残リスク

- sandbox 内では外部 CLI が通常動作しないため、実 smoke は escalated 実行が必要だった。
- `model_reasoning_effort=xhigh` は今回の Codex 既定 model で成功したが、利用可否は選択 model に依存する。
- cross-review で出た P2 hardening は、今回の実動作確認の blocker ではないが、次フェーズで修正候補にする。
