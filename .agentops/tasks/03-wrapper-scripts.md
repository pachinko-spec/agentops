---
task-id: 03-wrapper-scripts
plan-id: 2026-04-30-discord-cron-3tier-redesign
status: pending-merge
branch: claude/discord-cron-3tier-pr-c-wrappers
pr-target: C
started: 2026-04-30T15:30:00+09:00
---

> **status note**: wrapper 3 file 配置と DbC 完了条件は満たしているが、AGENTS.md §AI auto-merge 許諾の post-merge archive 規定に従い、PR-C が main へ merge されるまで `pending-merge` で保持する。merge 後に `completed` へ更新し `scripts/agentops archive task --task-id 03-wrapper-scripts` を別 commit で実行する (task 02 と同じ運用パターン)。

# PR-C: agentops/scripts/audit-{daily,weekly,monthly}.sh wrapper 新設

## 目的

cron から呼ばれる wrapper script を agentops repo (`scripts/`) に集約する。daily は CLI 軽量集計のみ (Claude 起動なし)、weekly / monthly は `claude -p /{weekly,monthly}-audit` skill を起動した後 tail 50 行を `agentops-watch notify --kind {weekly,monthly} --auto-discover --message ...` に渡す。

旧 `/home/otaku/bin/audit-{weekly,monthly,quarterly}.sh` は touch せず並存。crontab 切替は PR-D で行うため、本 PR 単体ではまだ cron に組み込まない。

## 変更ファイル

- `scripts/audit-daily.sh` (新規、Claude 起動なし)
- `scripts/audit-weekly.sh` (新規、claude -p /weekly-audit + agentops-watch)
- `scripts/audit-monthly.sh` (新規、claude -p /monthly-audit + agentops-watch、quarterly 吸収)

## DbC

### 前提条件
- PR-A merged (`agentops-watch notify --auto-discover` が main 上で動く)
- PR-B merged (`~/.claude/skills/{weekly,monthly}-audit/SKILL.md` 配置済)
- `~/.local/bin/claude` が executable
- `~/.bashrc` で `DISCORD_WEBHOOK_URL_{DAILLY,WEEKLY,MONTHLY,ANT_TIME}` export 済 (cron で `BASH_ENV=$HOME/.bashrc` を使う想定)

### 不変条件
- `set -x` を絶対に有効化しない (secret leak 防止)
- log に webhook URL や API token を出さない
- `unset ANTHROPIC_API_KEY` を冒頭で実行 (Max/Pro OAuth 経路を強制、API 課金経路 bypass)
- 旧 `/home/otaku/bin/audit-*.sh` を touch しない (並存維持)
- dotfiles 側 `notify-pending-discord.sh` を touch しない

### 完了条件
- 3 file 全て `bash -n` で構文 OK
- 各 wrapper の手動実行で `~/.cache/agentops-watch/logs/audit-{daily,weekly,monthly}-*.log` が生成
- daily wrapper の dry-run (env を `DISCORD_WEBHOOK_URL_DAILLY=` で空にして agentops-watch を `--dry-run` 渡しに切替えて構文確認) で payload 出力
- weekly / monthly wrapper は `claude -p` 呼び出し前段までは構文として走る (実 skill 起動は本 PR では検証しない、PR-D 後の観察期で行う)
- secret regex (`sk-` `xoxb-` `ghp_` `discord.com/api/webhooks`) が wrapper 自体に含まれない
- shellcheck (host 導入済なら) warning 0

### 禁止事項
- `--projects config/projects.yml` を hardcode (auto-discover を default に)
- `set -x`
- `CLAUDE_BIN` を絶対 path で hardcode (env 上書き可能であること)
- `notify-send` (cron 環境で no-op、用途は手動実行 fallback)
- secret 値の直接記述
- crontab 編集 (本 PR scope 外、PR-D 担当)

### 停止条件
- 旧 wrapper との競合を発見
- secret 漏洩経路を発見
- shellcheck warning が解消できない

## 設計詳細

### scripts/audit-daily.sh
```bash
#!/usr/bin/env bash
set -uo pipefail

# Claude 起動なし、CLI のみ軽量集計。auto-discover で 4 root を scan、
# build_digest_embed が project field に集約するため --message は付与しない。

unset ANTHROPIC_API_KEY  # Max/Pro OAuth 経路強制 (将来 weekly/monthly 経路と統一)

LOG_DIR="${HOME}/.cache/agentops-watch/logs"
LOG_FILE="${LOG_DIR}/audit-daily-$(date +%Y%m%d).log"
mkdir -p "$LOG_DIR"

{
  echo "=== Daily digest: $(date -Iseconds) ==="
} >> "$LOG_FILE"

/home/otaku/agentops/scripts/agentops-watch notify \
  --kind daily \
  --auto-discover \
  >> "$LOG_FILE" 2>&1 || true

exit 0
```

### scripts/audit-weekly.sh
```bash
#!/usr/bin/env bash
set -uo pipefail

# Max/Pro OAuth 強制 (旧 audit-weekly.sh:21 の意図と整合、API 課金経路 bypass)
unset ANTHROPIC_API_KEY

LOG_DIR="${HOME}/.cache/agentops-watch/logs"
LOG_FILE="${LOG_DIR}/audit-weekly-$(date +%Y%m%d).log"
mkdir -p "$LOG_DIR"

CLAUDE_BIN="${CLAUDE_BIN:-$HOME/.local/bin/claude}"
if [ ! -x "$CLAUDE_BIN" ]; then
  echo "[$(date -Iseconds)] Claude CLI not found at $CLAUDE_BIN — skipped" >> "$LOG_FILE"
  exit 0
fi

{
  echo "=== Weekly audit: $(date -Iseconds) ==="
  echo "CWD: $(pwd)"
} >> "$LOG_FILE"

# /weekly-audit skill (~/.claude/skills/weekly-audit/SKILL.md, PR-B 配置)
# 多 project 監査、agentops 設計思想 (Trinity / DbC / localize 4 戦略 / freshness drift)
OUTPUT=$(timeout 1800 "$CLAUDE_BIN" -p "/weekly-audit" 2>&1) || true
echo "$OUTPUT" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# critical 検出時の audio/desktop 通知 (cron では DISPLAY 未設定で no-op、手動実行向け)
if echo "$OUTPUT" | grep -iqE "critical|high severity|重大|高リスク"; then
  if command -v notify-send >/dev/null 2>&1; then
    notify-send -u critical "週次監査: critical 検出" "$LOG_FILE を確認してください"
  fi
fi

# tail 50 行を audit log field として agentops-watch notify --kind weekly --message に渡す
if [[ -s "$LOG_FILE" ]]; then
  /home/otaku/agentops/scripts/agentops-watch notify \
    --kind weekly \
    --auto-discover \
    --message "[weekly-audit] $(tail -n 50 "$LOG_FILE")" \
    >/dev/null 2>&1 || true
fi

exit 0
```

### scripts/audit-monthly.sh
```bash
#!/usr/bin/env bash
set -uo pipefail

# Max/Pro OAuth 強制 (旧 audit-monthly.sh と整合、API 課金経路 bypass)
unset ANTHROPIC_API_KEY

LOG_DIR="${HOME}/.cache/agentops-watch/logs"
LOG_FILE="${LOG_DIR}/audit-monthly-$(date +%Y%m).log"  # YYYYMM 維持 (旧 audit-monthly.sh:9 互換)
mkdir -p "$LOG_DIR"

CLAUDE_BIN="${CLAUDE_BIN:-$HOME/.local/bin/claude}"
if [ ! -x "$CLAUDE_BIN" ]; then
  echo "[$(date -Iseconds)] Claude CLI not found at $CLAUDE_BIN — skipped" >> "$LOG_FILE"
  exit 0
fi

{
  echo "=== Monthly audit: $(date -Iseconds) ==="
  echo "CWD: $(pwd)"
} >> "$LOG_FILE"

# /monthly-audit skill (~/.claude/skills/monthly-audit/SKILL.md, PR-B 配置)
# 重量監査、quarterly 吸収。docs drift / dependency staleness / Trinity 境界違反 / archive 候補
OUTPUT=$(timeout 2400 "$CLAUDE_BIN" -p "/monthly-audit" 2>&1)
claude_ec=$?
echo "$OUTPUT" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# critical 検出時の audio/desktop 通知 (cron では no-op)
if echo "$OUTPUT" | grep -iqE "critical|high severity|deprecated|重大|高リスク"; then
  if command -v notify-send >/dev/null 2>&1; then
    notify-send -u critical "月次監査: critical 検出" "$LOG_FILE を確認してください"
  fi
fi

# 旧 audit-quarterly.sh:51-58 と同パターンで claude_ec に応じて message プレフィックスを切替
if [[ -s "$LOG_FILE" ]]; then
  if [[ $claude_ec -ne 0 ]]; then
    _msg_prefix="[monthly-audit WARN]"
  else
    _msg_prefix="[monthly-audit]"
  fi
  /home/otaku/agentops/scripts/agentops-watch notify \
    --kind monthly \
    --auto-discover \
    --message "$_msg_prefix $(tail -n 50 "$LOG_FILE")" \
    >/dev/null 2>&1 || true
fi

exit 0
```

## 検証手順

```bash
# 1. 構文 check
bash -n scripts/audit-daily.sh
bash -n scripts/audit-weekly.sh
bash -n scripts/audit-monthly.sh

# 2. shellcheck (host 導入済なら)
shellcheck scripts/audit-daily.sh scripts/audit-weekly.sh scripts/audit-monthly.sh || true

# 3. secret hardcode 検出 (出力 0 行が期待)
grep -rE 'sk-|xoxb-|ghp_|discord\.com/api/webhooks' scripts/audit-{daily,weekly,monthly}.sh || echo "no secrets"

# 4. daily 手動実行 (実 webhook 送信回避は env を空にしないが、各 channel webhook 設定済前提なら届く)
# 安全のため一時 env で webhook を空に
DISCORD_WEBHOOK_URL_DAILLY= DISCORD_WEBHOOK_URL_WEEKLY= DISCORD_WEBHOOK_URL_MONTHLY= bash scripts/audit-daily.sh
ls -la ~/.cache/agentops-watch/logs/audit-daily-*.log

# 5. weekly / monthly は実 skill 起動を伴うため、本 PR では構文確認のみ。
#    実起動確認は PR-D の crontab 切替後の観察期 (D+5 ~ D+12) に行う。
```

## auto-merge 許諾条件

- DbC 完了 (上記)
- secret 未混入
- scope 単一 (PR-C 範囲内、CLI / skill / docs / crontab には触らない)
- shellcheck warning 0 (or 説明可能な warning のみ)
- cross-review delegate (Codex review_frontier) で P0/P1 = 0

## ロールバック path

- wrapper 削除: `rm scripts/audit-{daily,weekly,monthly}.sh`
- crontab には PR-D まで反映されないため、wrapper 削除で即時 rollback 完了
- 既存 `/home/otaku/bin/audit-*.sh` は touch していないため別経路で動作継続
