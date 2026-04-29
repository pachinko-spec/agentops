---
session: 2026-04-30
parent-plan: ../plans/current.md
status: in-progress
---

# Task Plan: digest kind に --message 拡張 + audit-*.sh 切替

## 今回セッションの実行順

1. **task 01 (PR-C / Phase A)** 実装本体
   - `tools/agentops_monitor/__main__.py`:
     - `build_digest_embed(kind, report, now_jst, message=None)` シグネチャ拡張
     - message 指定時: sanitize → 1024 文字 truncate → embed fields 末尾に "audit log" field 追加
     - message なし時: 既存挙動完全維持 (regression なし)
     - `cmd_notify` の digest path で `args.message` を渡す
2. **単体テスト追加**
   - `test_payload_builder.py::BuildDigestEmbedTests`:
     - test_message_added_to_embed_fields
     - test_message_sanitized_in_digest
     - test_message_truncated_to_1024
     - test_no_message_preserves_existing_shape
   - `test_cmd_notify.py::CmdNotifyDryRunTests`:
     - test_dry_run_daily_with_message
3. **docs 更新**
   - `docs/18-notification-strategy.md`: kind 表 / payload 雛形に --message を追記
   - `docs/11-monitoring-cli.md`: 実装ステータス + コマンド表
4. **検証 + cross-review**: dry-run smoke / regression / Codex `review_frontier --effort high`
5. **archive + commit + push + PR-C 作成** → user 手動マージ
6. **task 02 (Phase B)**: /home/otaku/bin/audit-*.sh × 3 を直接 edit + dry-run smoke

## 想定時間

- task 01 (1〜5 までセッション内): 90〜150 分
- task 02 (6 セッション内 host-local): 30 分

## branch / PR

- PR-C: `claude/agentops-monitor-digest-message-2026-04-30` (現ブランチ)

## 検証コマンド

```sh
# 構文 + テスト
python3 -m compileall tools/
python3 -m unittest discover tools/agentops_monitor/tests -v

# 新機能 dry-run
scripts/agentops-watch notify --kind daily --message "[smoke]" --dry-run
scripts/agentops-watch notify --kind weekly --project /home/otaku/agentops --message "[sanity-check] OK" --dry-run
scripts/agentops-watch notify --kind monthly --project /home/otaku/agentops --message "[monthly-audit] critical:0" --dry-run

# regression smoke
scripts/agentops-watch notify --kind daily --dry-run
scripts/agentops-watch notify --kind alert --message "x" --dry-run
scripts/agentops-watch check --json | head -10

# secret 漏洩確認
grep -rn "discord.com/api/webhooks/[0-9]" tools/ docs/ scripts/ 2>/dev/null

# cross-review
scripts/agentops delegate --to codex --role review_frontier --effort high \
  --input tools/agentops_monitor/__main__.py
```

## 機微情報の取り扱い

- 単体テストで実 webhook URL を **絶対に使わない** (常に `https://discord.invalid/...`)
- 環境変数操作は `mock.patch.dict(os.environ, ..., clear=False)`
- ユーザー実環境 envvar の値を取得 / 表示しない
- audit-*.sh 修正でも sample コマンドに実 URL を書かない (envvar 名のみ)
