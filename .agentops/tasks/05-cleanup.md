---
task-id: 05-cleanup
plan-id: 2026-04-30-discord-cron-3tier-redesign
status: pending-merge
branch: claude/discord-cron-3tier-pr-e-cleanup
pr-target: E
started: 2026-04-30T16:30:00+09:00
---

> **status note (起票時)**: 本 task md を最初に起票していなかった点を反省し、PR-E 着手時にまとめて起票。本来は plan 承認時に 01〜05 全 task md を一括起票するのが agentops 運用の理想。今後の plan で改善する。
>
> **status note (cleanup 実施済)**: PR-E 内容を実施完了 — 旧 `/home/otaku/bin/audit-{weekly,monthly}.sh` を `agentops/scripts/audit-{weekly,monthly}.sh` への symlink に置換、`audit-quarterly.sh` 削除、ADR (`decisions/2026-04-30-discord-cron-3tier-migration.md`) 起票。本 commit には本 task md / 03 archive status fix / 04 archive 移動 / ADR を含める。`scripts/agentops archive plan` は本 PR merge 後に main 同期した上で別途実行する。

# PR-E: 旧 bin/ symlink 化 + audit-quarterly.sh 削除 + ADR + plan archive

## 目的

PR-D の crontab 反映 + 1 サイクル観察期間 (D+5 〜 D+12 で daily/weekly/monthly 各 1 通受信確認) を経て、旧 wrapper を整理し、本 plan を archive する最終 PR。

## 前提

- PR-A / B / C / D が main へ merged
- crontab が 3-tier 構成に切替済 (user 手動操作)
- D+1 朝 9:10 に DAILLY channel digest 受信確認済
- D+? 月曜 9:00 に WEEKLY channel digest 受信確認済
- D+? 月初 11:00 に MONTHLY channel digest 受信確認済 (or 着手時点で次の月初を待たない判断)
- secret 値が embed / log / commit history に出ていないことを目視確認済

## 変更ファイル

### 旧 wrapper の symlink 化 / 削除 (host-local、git 管理外)
- `/home/otaku/bin/audit-weekly.sh` → `/home/otaku/agentops/scripts/audit-weekly.sh` への symlink (`ln -sf`)
- `/home/otaku/bin/audit-monthly.sh` → 同上
- `/home/otaku/bin/audit-quarterly.sh` 削除 (quarterly 廃止に伴う)

### agentops repo 側 commit
- `decisions/2026-05-DD-discord-cron-3tier-migration.md` ADR 起票 (新規)
  - 廃止対象列挙 (notify-pending-discord daily/weekly cron 行 / audit-quarterly.sh / 関連 sanity-check 経路)
  - dotfiles 側 deprecation guard 追加を **dotfiles 側別 PR で対応すべき** と recommend
  - rollback path (cron snapshot from PR-D)
  - Codex cross-review scope 違反事例の教訓 (cross-reviewer は所見のみ、archive 等の作業は実行しない)
- `.agentops/archive/2026-04-30-discord-cron-3tier-redesign/` への plan / task-plan / current.md / task md 全件移動 + `archive/README.md` 時系列 index に新規 row 追加 (`scripts/agentops archive plan` 経由)
- `.agentops/tasks/05-cleanup.md` 自身の archive 移動 (本 PR の最後の commit)

## DbC

### 前提条件
- PR-A〜PR-D merged + 観察期間で digest 受信確認済
- 旧 wrapper を含む `/home/otaku/bin/` の現状確認済 (symlink / 削除前の権限とファイル一覧を snapshot 推奨)

### 不変条件
- dotfiles repo を touch しない
- `~/.claude/hooks/` を touch しない
- `~/.claude/skills/{weekly,monthly}-audit/SKILL.md` を touch しない (PR-B で配置済、本 PR では確認のみ)
- crontab を再変更しない (PR-D で完了済、本 PR では確認のみ)
- secret 値を docs / ADR / commit に出さない

### 完了条件
- `/home/otaku/bin/audit-weekly.sh` が `agentops/scripts/audit-weekly.sh` を指す symlink (or 削除) になっている
- `/home/otaku/bin/audit-monthly.sh` が同上
- `/home/otaku/bin/audit-quarterly.sh` が削除されている
- 旧 wrapper の動作確認 (例: `bash /home/otaku/bin/audit-weekly.sh` が新 wrapper 経由で動く or 旧経路は無効)
- ADR が `decisions/2026-05-DD-discord-cron-3tier-migration.md` として commit
- plan archive が `scripts/agentops archive plan --plan-id 2026-04-30-discord-cron-3tier-redesign --summary "..."` で完了
- `.agentops/plans/current.md` `.agentops/task-plans/current.md` `.agentops/tasks/` (README 除く) が空
- `archive/README.md` 時系列 index に新規 row 追加済

### 禁止事項
- dotfiles repo の `notify-pending-discord.sh` 編集
- `~/.claude/hooks/_common.py` への変更
- crontab snapshot file (`~/.claude/.agentops/runs/<ts>-pr-d-crontab-snapshot/crontab.before`) の削除
- `~/.claude/skills/{weekly,monthly}-audit/SKILL.md` の削除 (本 plan で配置した skill は plan 完了後も残置)

### 停止条件
- 観察期間中に Discord 受信失敗発生 → 旧 cron 復元 (`crontab - < snapshot`) で rollback、本 PR は中止
- symlink 作成エラー (`/home/otaku/bin/` 書き込み権限不足等)
- ADR 起票で agentops の `decisions/` directory 構造が不明 (template 確認が必要)

## 検証手順

```bash
# 1. 旧 wrapper の確認
ls -la /home/otaku/bin/audit-*.sh

# 2. symlink 化 (ln -sf で既存 file を上書き)
ln -sf /home/otaku/agentops/scripts/audit-weekly.sh /home/otaku/bin/audit-weekly.sh
ln -sf /home/otaku/agentops/scripts/audit-monthly.sh /home/otaku/bin/audit-monthly.sh
rm /home/otaku/bin/audit-quarterly.sh

# 3. symlink 動作確認
bash /home/otaku/bin/audit-weekly.sh  # → 新 wrapper 経由で実行される
bash /home/otaku/bin/audit-monthly.sh

# 4. ADR commit
# decisions/2026-05-DD-discord-cron-3tier-migration.md を作成して commit

# 5. plan archive
scripts/agentops archive plan --plan-id 2026-04-30-discord-cron-3tier-redesign --dry-run
scripts/agentops archive plan --plan-id 2026-04-30-discord-cron-3tier-redesign --summary "Discord 通知 cron を 3-tier (daily=CLI軽量 / weekly=/weekly-audit / monthly=/monthly-audit + quarterly 吸収) に再編、agentops/scripts/ に集約、auto-discovery で 4 root scan に拡張"
```

## auto-merge 許諾条件

- DbC 完了 (上記)
- 観察期間で digest 受信確認済
- secret 未混入
- scope 単一 (PR-E 範囲、cleanup のみ、新規機能追加なし)

## ロールバック path

- symlink 取消: `rm /home/otaku/bin/audit-{weekly,monthly}.sh` で旧 file 復元 (旧 file は git 管理外で残置)
- ADR revert: `git revert <hash>`
- plan archive 取消: archive directory から手動で plans/current.md / task-plans/current.md を戻す (plan archive コマンドの逆操作は手動)
- `~/.claude/skills/` の skill は plan 完了後も残置するため touch しない (rollback 不要)
