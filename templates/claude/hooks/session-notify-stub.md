# Claude Code SessionStart / SessionEnd 通知 hook 仕様メモ

> agentops は **実フックを持たない方針** (AGENTS.md / CLAUDE.md)。本ファイルは Claude Code グローバル設定 (`~/.claude/hooks/`) に通知 hook を追加する **仕様メモ** であり、コード雛形そのものではない。実装は別 plan で対象 CLI の現在仕様 (公式 hooks docs / settings.json schema) を確認した上で行う。

## 目的

Claude Code セッションの **開始 / 終了 / Stop failure / PermissionRequest 待ち** を `ANT_TIME` channel に Discord 通知する。`next-session.md` があるプロジェクトで「セッションが開始された」「セッションが終了した」をユーザーが即時把握できるようにする。

設計思想は [docs/18-notification-strategy.md](../../../docs/18-notification-strategy.md)、CLI 仕様は [docs/11-monitoring-cli.md](../../../docs/11-monitoring-cli.md) を参照する。

## 対象 hook event (公式仕様確認は別 plan で実施)

- `SessionStart`: セッション開始時に発火
- `Stop` (正常終了相当): セッション終了時に `--kind session-end` を発火、失敗時は `--kind stop-failure`
- `PermissionRequest`: tool 承認待ちで `--kind permission-wait` を発火 (発火境界は対象 CLI の hook event 仕様で確認)

実 event 名・schema は Claude Code 公式 hooks docs (https://code.claude.com/docs/en/hooks) と現行 `~/.claude/settings.json` の hook 定義で確認する。本ファイル作成時点で `agentops_guard.py` ベースの 6 event 別分散 (SessionStart / UserPromptSubmit / PreToolUse / PermissionRequest / PostToolUse / Stop) が稼働している前提で、追加するのではなく **既存 hook script から `agentops-watch notify` を呼ぶ薄い stub** を組み込む方針が誤検知・競合リスクが低い。

## 呼び出し契約

各 hook script から以下の形で呼ぶ:

```sh
# SessionStart
/home/<user>/agentops/scripts/agentops-watch notify \
  --kind session-start \
  --project "$CLAUDE_PROJECT_DIR" \
  >/dev/null 2>&1 || true

# Stop (正常終了 → session-end / 異常終了 → stop-failure)
/home/<user>/agentops/scripts/agentops-watch notify \
  --kind session-end \
  --project "$CLAUDE_PROJECT_DIR" \
  >/dev/null 2>&1 || true

# PermissionRequest 待ち
/home/<user>/agentops/scripts/agentops-watch notify \
  --kind permission-wait \
  --project "$CLAUDE_PROJECT_DIR" \
  --message "$REQUESTED_TOOL" \
  >/dev/null 2>&1 || true
```

- 標準出力・標準エラーは hook を遅延させないために抑制する (`>/dev/null 2>&1`)。
- exit code 失敗時も hook 全体を停止させない (`|| true`)。通知失敗で本来の Claude Code 動作を阻害しない。
- 環境変数 `DISCORD_WEBHOOK_URL_ANT_TIME` が未設定なら CLI 側で exit 2 stop。hook は `|| true` で吸収する設計のため、ユーザーが `~/.bashrc` 等に export していない環境では **通知が静かに skip** される (運用観察上の許容)。

## 発火境界 (誤爆防止)

- セッション開始時に `next-session.md` が存在しないプロジェクトでも `session-start` を発火させてよい (ANT_TIME 頻度上限ガードで制御)。
- ただし `~/dev/` 範囲外 (例: `/tmp/`、`~/.config/`、`~/.claude/` 等のグローバル作業) では **default で発火させない** 設定を推奨。プロジェクトパスの allow list を hook script 側に持つか、CLI 側 `--project` で `~/dev/*` 限定オプションを設けるかは実装 plan で判断。
- `permission-wait` は同一 tool が短時間に複数回承認待ちになるとフラッディングの恐れがあるため、CLI 側 ANT_TIME 頻度上限ガード (default: 1 分 5 件 / 1 時間 60 件) で抑止する。

## 既存 hook と競合させないこと

`~/.claude/hooks/` 配下には既に `agentops_guard.py` ベースの SECRET 漏洩ガード等が稼働している。本仕様メモの hook 追加は **既存 hook の振る舞いを変更しない** 形で挿入する:

- 既存 hook の末尾または前段で `agentops-watch notify` を呼び、戻り値を捨てる
- 既存 hook の SECRET 検出ロジックや停止判断と独立させる
- 通知 payload に SECRET / Webhook URL の値が混入しないよう、`agentops-watch notify` 側でも payload sanitization を実装 (実装 plan で確認)

## DbC との関係

- **適用前提**: 対象 hook event が稼働中、`agentops-watch` が PATH または絶対パスで起動可能、`DISCORD_WEBHOOK_URL_ANT_TIME` が export 済み (未 export 時は静かに skip)
- **適用不変**: hook 全体を停止させない (`|| true`)、Claude Code 動作を遅延させない (`&` background も実装 plan で検討)、SECRET を payload に出さない
- **適用完了**: hook event 発火時に `agentops-watch notify --kind <kind>` が exec され、通知が ANT_TIME に届く (失敗時は静かに skip)
- **適用停止**: ANT_TIME 頻度上限超過 (CLI 側で skip)、Webhook URL 未設定 (CLI 側で exit 2)、payload に SECRET 検出 (CLI 側で stop) — いずれも本 hook script ではなく `agentops-watch` 側で扱う

## スコープ外

- 本 hook script の実体追加 (実装 plan で `~/.claude/hooks/session_start.py` 等に組み込み)
- `agentops-watch notify --kind` の実装本体
- 既存 `agentops_guard.py` の改修

## 関連

- [docs/18-notification-strategy.md](../../../docs/18-notification-strategy.md) — 通知戦略
- [docs/11-monitoring-cli.md](../../../docs/11-monitoring-cli.md) — CLI 仕様
- [docs/09-hooks-quality-gates.md](../../../docs/09-hooks-quality-gates.md) — hook 品質ゲート
