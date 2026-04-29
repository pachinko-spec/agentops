---
task-id: 02-audit-scripts-migration
parent-plan: ../plans/current.md
created: 2026-04-30
status: pending
pr-target: なし (host-local edit、commit なし)
target-files: /home/otaku/bin/audit-{weekly,monthly,quarterly}.sh
blocked-by: 01-digest-kind-message
---

# Task 02: /home/otaku/bin/audit-*.sh × 3 修正 (Phase B)

## 前提条件

- task 01 (PR-C) がマージ済 (digest kind の `--message` 受付が実装済)
- 3 スクリプトすべて `/home/otaku/bin/` 配下の host-local file (git 管理外)
- 修正は **commit を伴わない** (どの repo にも入っていないファイル)
- 修正の作業記録は本 task md と plan archive に残す

## 不変条件

- スクリプトの skill 実行ロジック (`claude /sanity-check` 等) を **touch しない**
- ログ出力先 (`~/.claude/logs/audit-*.log`) を **維持**
- desktop notify-send 通知 (critical 検出時) を **維持**
- exit code 分岐 (audit-quarterly.sh の success/warn 分け) を **維持**
- `|| true` の fail-safe を **維持** (cron が exit 0 で失敗を吸収する設計)
- secret (Webhook URL) を script 内に値として書かない

## 完了条件

各スクリプトの Discord 通知部を以下のように置換:

### audit-weekly.sh

```sh
# Before
bash "$HOME/.claude/hooks/discord-notify.sh" --kind sanity-check < "$LOG_FILE" || true

# After
/home/otaku/agentops/scripts/agentops-watch notify \
  --kind weekly \
  --project /home/otaku/dotfiles \
  --message "[sanity-check] $(tail -50 "$LOG_FILE" 2>/dev/null)" \
  >/dev/null 2>&1 || true
```

### audit-monthly.sh

```sh
# Before
bash "$HOME/.claude/hooks/discord-notify.sh" --kind monthly-audit < "$LOG_FILE" || true

# After
/home/otaku/agentops/scripts/agentops-watch notify \
  --kind monthly \
  --project /home/otaku/dotfiles \
  --message "[monthly-audit] $(tail -50 "$LOG_FILE" 2>/dev/null)" \
  >/dev/null 2>&1 || true
```

### audit-quarterly.sh

exit code 分岐を維持しつつ message プレフィックスで識別:

```sh
# Before
if [[ $exit_code -eq 1 ]]; then
  bash "$HOME/.claude/hooks/discord-notify.sh" --kind quarterly-review-warn < "$LOG_FILE" || true
else
  bash "$HOME/.claude/hooks/discord-notify.sh" --kind quarterly-review < "$LOG_FILE" || true
fi

# After
if [[ $exit_code -eq 1 ]]; then
  MSG_PREFIX="[quarterly-review WARN]"
else
  MSG_PREFIX="[quarterly-review]"
fi
/home/otaku/agentops/scripts/agentops-watch notify \
  --kind monthly \
  --project /home/otaku/dotfiles \
  --message "$MSG_PREFIX $(tail -50 "$LOG_FILE" 2>/dev/null)" \
  >/dev/null 2>&1 || true
```

## 検証 (smoke)

各スクリプト修正後:

1. **静的検証**: `bash -n /home/otaku/bin/audit-{weekly,monthly,quarterly}.sh` で構文 OK
2. **dry-run smoke**: 修正後 invocation を抜き出して dry-run:

   ```sh
   DUMMY_LOG=$(mktemp)
   echo "test audit output line 1" > "$DUMMY_LOG"
   echo "test audit output line 2" >> "$DUMMY_LOG"

   /home/otaku/agentops/scripts/agentops-watch notify --kind weekly \
     --project /home/otaku/dotfiles \
     --message "[sanity-check] $(tail -50 "$DUMMY_LOG")" --dry-run

   /home/otaku/agentops/scripts/agentops-watch notify --kind monthly \
     --project /home/otaku/dotfiles \
     --message "[monthly-audit] $(tail -50 "$DUMMY_LOG")" --dry-run

   /home/otaku/agentops/scripts/agentops-watch notify --kind monthly \
     --project /home/otaku/dotfiles \
     --message "[quarterly-review WARN] $(tail -50 "$DUMMY_LOG")" --dry-run
   ```

3. **本物 smoke** (user 判断): `bash audit-weekly.sh` 実行で claude CLI 経由の skill 実行 + 実 Discord 送信。
   - 実行時間が長い (timeout 1800〜3600秒 / claude API クォータ消費) ため、本セッションでは省略可
   - 翌週月曜の cron で結果を観察するルートも可

## 禁止事項

- スクリプトの skill 実行行 (`claude -p /sanity-check 2>&1 | tee "$LOG_FILE"` 等) を編集
- ログファイルパスを変更
- desktop notify-send 行を削除
- exit 0 の保証を破壊
- crontab を編集
- dotfiles repo を編集

## 停止条件

- 修正後の `bash -n` が syntax error
- dry-run smoke で payload に audit log field が出ない / sanitize されない
- スクリプト実行で skill 実行部が壊れた

## 完了報告先

- plan archive (`/home/otaku/agentops/.agentops/archive/2026-04-30-agentops-monitor-digest-message/tasks/02-audit-scripts-migration.md`) に修正前後の diff を記録
- next-session.md は本 plan 完了で削除 (or archive 移動)
