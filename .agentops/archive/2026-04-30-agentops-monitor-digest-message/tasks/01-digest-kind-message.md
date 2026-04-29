---
task-id: 01-digest-kind-message
parent-plan: ../plans/current.md
created: 2026-04-30
status: in-progress
pr-target: PR-C (digest kind に --message 拡張)
branch: claude/agentops-monitor-digest-message-2026-04-30
---

# Task 01: digest kind に `--message` 拡張 (PR-C)

## 前提条件

- PR #60 (notify CLI 本体) と PR #61 (cron sample / hook stub / docs) は merge 済 (main: `ede037d`)
- docs/18-notification-strategy.md と docs/11-monitoring-cli.md の契約は本 task で **追加更新**
- 既存 60 系単体テスト (実際は 68 件) すべて pass している
- `cmd_check` 既存挙動 / `build_anttime_embed` / 旧 envvar 後方互換 path は破壊しない (additive 拡張のみ)
- Python 3.11+ 標準ライブラリのみ

## 不変条件

- secret (Webhook URL) を log / stdout / stderr / commit / PR / docs / コメントに **値として** 出さない
- `allowed_mentions: {"parse": []}` を全 webhook payload に必須 (digest + ANT_TIME 共通)
- `--message` 経由の文字列は必ず `sanitize_mention_text` を通す
- 新 field "audit log" は Discord embed の field value 制限 (1024 char) を尊重して truncate
- message なしの digest 既存挙動を完全維持 (regression なし)

## 完了条件

- `tools/agentops_monitor/__main__.py` 編集:
  - `build_digest_embed(kind, report, now_jst, message: str | None = None)` シグネチャ拡張
  - message 指定時:
    - `sanitize_mention_text` を通す
    - `_truncate(value, _EMBED_FIELD_VALUE_LIMIT)` で 1024 文字制限
    - embed fields 末尾に `{"name": "audit log", "value": <sanitized + truncated>, "inline": False}` を追加
    - 既存 fields 25 件制限を尊重 (audit log を含めて 25 件、超過時は truncate)
  - message なし時: 既存挙動完全維持
  - `cmd_notify` の digest path (`if kind in DIGEST_KINDS`) で `args.message` を `build_digest_embed` に渡す
  - `cmd_notify` の ANT_TIME path は touch しない (`build_anttime_embed` の挙動維持)
  - 旧 path (`_legacy_notify`) は touch しない
- 単体テスト追加 (`tools/agentops_monitor/tests/`):
  - `test_payload_builder.py::BuildDigestEmbedTests`:
    - `test_message_added_to_embed_fields`: --message が "audit log" field として追加される
    - `test_message_sanitized_in_digest`: @everyone が無害化される
    - `test_message_truncated_to_1024`: 長文が truncate される
    - `test_no_message_preserves_existing_shape`: message 無しは既存挙動 (regression test)
  - `test_cmd_notify.py::CmdNotifyDryRunTests`:
    - `test_dry_run_daily_with_message`: `notify --kind daily --message "audit log" --dry-run` の payload 確認
- docs 更新:
  - `docs/18-notification-strategy.md`: §通知種別 表で daily/weekly/monthly の payload に "(任意 --message を audit log field として追加)" 追記、§payload 雛形 に audit log field 説明
  - `docs/11-monitoring-cli.md`: 実装ステータス注記更新、kind 別コマンド表に digest kind での --message 明示
- 検証:
  - `python3 -m compileall tools/` exit 0
  - `python3 -m unittest discover tools/agentops_monitor/tests` 既存 68 件 + 新規 5 件以上 pass
  - dry-run smoke 6 種 (daily / weekly / monthly + message / 各 message なし) すべて期待動作
  - `cmd_check --json` regression なし
  - secret (実 webhook URL) 混入なし (`grep -rn 'discord.com/api/webhooks/[0-9]' tools/ docs/ scripts/`)
- Codex `review_frontier --effort high` cross-review で P0/P1 0 件 (1〜2 round 想定)
- archive 移動 + commit + push + PR-C 作成

## 禁止事項

- 実 Webhook URL を log / commit / PR / docs / コメントに値として出すこと
- 単体テストで実 webhook へ送信すること (mock 必須)
- `cmd_check` / `build_anttime_embed` / `_legacy_notify` の既存仕様を変更すること
- `--message` を `--kind` 別必須化 / 拒否化に変更すること (alert / permission-wait / stop-failure では既存通り必須維持)
- crontab / dotfiles repo / `~/.claude/hooks/` を編集すること

## 停止条件

- レビュー修正が 2 周を超える → user 確認
- Webhook URL 値が誤って混入 → 即停止
- 既存テスト (68 件) のいずれかが fail → ロールバックして調査
- mock なしで実 webhook 送信が必要になる事象 → 設計変更してテスト可能化
- audit log field の truncate / sanitize で予期しない side effect → ユーザー確認

## 検証手順

1. `python3 -m compileall tools/`
2. `python3 -m unittest discover tools/agentops_monitor/tests -v`
3. `scripts/agentops-watch notify --kind daily --message "[sanity-check] OK" --dry-run` → audit log field 含む embed
4. `scripts/agentops-watch notify --kind weekly --project /home/otaku/agentops --message "[smoke]" --dry-run`
5. `scripts/agentops-watch notify --kind monthly --message "[monthly-audit] critical:0" --dry-run`
6. `scripts/agentops-watch notify --kind daily --dry-run` → 既存 (audit log field なし)
7. `scripts/agentops-watch notify --kind alert --message "x" --dry-run` → ANT_TIME 既存挙動
8. `scripts/agentops-watch check --json` → regression なし
9. `grep -rn 'discord.com/api/webhooks/[0-9]' tools/ docs/ scripts/` → 0 件
10. agentops-reviewer subagent 独立レビュー (correctness / security / tests)
11. `scripts/agentops delegate --to codex --role review_frontier --effort high --input tools/agentops_monitor/__main__.py` で cross-review
12. P0/P1 反映後、reviewer 再走で 0 件確認
13. `scripts/agentops archive task --task-id 01-digest-kind-message --dry-run` → 本番実行
14. commit → push → PR-C 作成 → user 手動マージ → main 同期

## DbC

- **適用前提**: PR #60 / #61 マージ済 / 既存 68 tests pass / docs/18 docs/11 整合
- **適用不変**: secret 値非露出 / allowed_mentions 必須 / sanitize_mention_text 必須 / 1024 truncate / 既存挙動維持
- **適用完了**: 上記「完了条件」全項目
- **適用禁止**: 上記「禁止事項」記載
- **適用停止**: 上記「停止条件」のいずれか発生
