---
task-id: 04-crontab-and-docs
plan-id: 2026-04-30-discord-cron-3tier-redesign
status: pending-merge
branch: claude/discord-cron-3tier-pr-d-crontab-docs
pr-target: D
started: 2026-04-30T15:50:00+09:00
---

> **status note**: docs 4 file 更新と config/cron.example 全文書き換えは完了。crontab 編集 (host global state) は **本 PR の commit に含めない**。PR-D が main へ merge された後、user が手動で `crontab -e` を実行する手順を本 task md に記載済。merge 後に `status: completed` へ更新し archive。

# PR-D: crontab 切替 + docs 更新

## 目的

PR-A〜PR-C で実装した CLI 拡張 / skill / wrapper script を実 crontab に反映し、docs を 3-tier 構成に同期する。本 PR は **2 つに分かれた作業の片側 (docs 更新)** を agentops repo に commit する。crontab 編集は host global state なので user の手動操作で行う。

## 変更ファイル

- `docs/11-monitoring-cli.md` (`--auto-discover` 仕様追加、走査仕様節新設)
- `docs/18-notification-strategy.md` (4 root 走査ルール改訂、kind 表の起動方法を `agentops/scripts/audit-*.sh` に、cron 例を 3-tier に、quarterly 廃止節新設、移行完了記述)
- `docs/19-project-localization.md` (監視 / 通知の整合性チェック節新設)
- `config/cron.example` (全文書き換え、3-tier sample、`BASH_ENV=$HOME/.bashrc` 推奨明示)
- `.agentops/tasks/04-crontab-and-docs.md` (本 task)
- 03 archive 移動 (PR-C 完了分)
- archive 02 status fix (PR-B post-merge handler、PR-C で漏れた分)

## crontab 編集手順 (本 PR commit に含まれない、user 確認下で別途実行)

### before (現状の crontab)

```cron
# --- server metrics ---
*/5 * * * * /home/otaku/bin/metrics-collect.sh
0 */6 * * * /home/otaku/bin/server-report.sh

# --- Claude Code dotfiles 監査 ---
0 9 * * 1 /home/otaku/bin/audit-weekly.sh
0 9 1 1,4,7,10 * /home/otaku/bin/audit-quarterly.sh

# --- Claude Code dotfiles 通知 (Phase 5 追加) ---
10 9 * * * /home/otaku/dotfiles/bin/notify-pending-discord.sh --kind daily >/dev/null 2>&1
45 9 * * 1 /home/otaku/dotfiles/bin/notify-pending-discord.sh --kind weekly >/dev/null 2>&1
0 11 1 * * /home/otaku/bin/audit-monthly.sh >/dev/null 2>&1
```

### after (本 PR merge 後に user が `crontab -e` で適用)

```cron
BASH_ENV=$HOME/.bashrc

# --- server metrics ---
*/5 * * * * /home/otaku/bin/metrics-collect.sh
0 */6 * * * /home/otaku/bin/server-report.sh

# --- agentops digest cron (3-tier) ---
10 9 * * *  /home/otaku/agentops/scripts/audit-daily.sh
0 9 * * 1   /home/otaku/agentops/scripts/audit-weekly.sh
0 11 1 * *  /home/otaku/agentops/scripts/audit-monthly.sh
```

差分: 5 行削除 + 3 行追加 + `BASH_ENV` 1 行追加 (metrics 系 2 行は維持)

### 反映手順

```bash
# 1. snapshot (rollback ソース)
mkdir -p ~/.claude/.agentops/runs/$(date +%Y%m%dT%H%M%S+0900)-pr-d-crontab-snapshot
crontab -l > ~/.claude/.agentops/runs/$(date +%Y%m%dT%H%M%S+0900)-pr-d-crontab-snapshot/crontab.before

# 2. 編集
crontab -e
# 上の after 表通りに書き換える

# 3. 確認
crontab -l

# 4. 翌朝 9:10 / 翌週月曜 9:00 / 翌月 1 日 11:00 に Discord 各 channel で digest 1 通受信を確認
```

## DbC

### 前提条件
- PR-A merged
- PR-B merged
- PR-C merged (wrapper 3 file が main 上で executable)
- `~/.bashrc` で `DISCORD_WEBHOOK_URL_{DAILLY,WEEKLY,MONTHLY,ANT_TIME}` export 済
- `~/.local/bin/claude` executable

### 不変条件
- crontab 編集は user の手動操作のみ (本 commit には含めない)
- secret 値を docs / config / commit message に出さない
- dotfiles repo を touch しない
- `~/.claude/hooks/` を touch しない
- 旧 `/home/otaku/bin/audit-{weekly,monthly}.sh` を touch しない (PR-E で symlink 化)

### 完了条件
- 本 PR merge 済
- crontab snapshot が `~/.claude/.agentops/runs/<ts>/crontab.before` に保存 (user 操作)
- `crontab -l` の diff が above after と一致 (user 操作)
- D+1 朝 9:10 に DAILLY channel に digest 1 通受信 (user 観察)
- 翌週月曜 9:00 に WEEKLY channel に digest 1 通受信 (user 観察)
- 翌月 1 日 11:00 に MONTHLY channel に digest 1 通受信 (user 観察)
- いずれも secret 値が embed / log に出ていない

### 禁止事項
- crontab 編集を AI が直接実行 (user 確認必須)
- dotfiles repo の `notify-pending-discord.sh` 編集 (本 plan scope 外)
- `~/.claude/hooks/_common.py` への変更 (ANT_TIME wrapper 既に成立、touch しない)
- 旧 `/home/otaku/bin/audit-*.sh` 削除 (PR-E 担当、観察期間後)

### 停止条件
- crontab snapshot 取得失敗
- user 承認なしの crontab 反映
- Discord 受信失敗 → rollback (`crontab - < snapshot`)
- docs と実体の乖離発見

## 検証

### docs 更新確認
- `docs/11-monitoring-cli.md` で `--auto-discover` synopsis + 走査仕様節
- `docs/18-notification-strategy.md` で 4 root 表記 + 3-tier 起動例 + quarterly 廃止節 + 移行完了記述
- `docs/19-project-localization.md` で 監視 / 通知の整合性チェック節
- `config/cron.example` で 3-tier sample + `BASH_ENV` 推奨

### CI green
- markdown-link-check / yamllint / actionlint / freshness-check 全 pass

## auto-merge 許諾条件

本 PR は **AGENTS.md auto-merge 許諾の停止条件「crontab / 本番 / 課金 / 外部公開 / 破壊的操作」に該当しないが、host global state (crontab) と密接に関連する**。docs / config 更新部分は許諾条件適合だが、PR merge 後に user が手動で crontab を編集する手順を含むため、merge 自体は **user 承認下** で行う。

cross-review delegate (Codex) は docs 更新の整合性確認として実施可能 (任意、scope 違反リスクのため必須ではない)。

## ロールバック path

- 本 PR commit revert: `git revert <hash>` で docs / config を元に戻す
- crontab 反映後の rollback: `crontab - < ~/.claude/.agentops/runs/<ts>/crontab.before` で旧設定復元
- 旧 wrapper (`/home/otaku/bin/audit-{weekly,monthly}.sh`) は touch していないため、crontab を旧設定に戻すだけで動作回帰
