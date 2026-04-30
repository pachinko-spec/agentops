#!/usr/bin/env bash
# Purpose: 月次で /monthly-audit skill (~/.claude/skills/monthly-audit/SKILL.md, PR-B 配置)
#          を起動し、tail 50 行を agentops-watch notify --kind monthly --message に渡して
#          Discord に送信する。skill は重量監査 (旧 quarterly 吸収): docs drift / dependency
#          staleness via context7 / Trinity 境界違反 / archive 候補 / freshness。
# Trigger: crontab 例: 0 11 1 * * (毎月 1 日 11:00)、PR-D で crontab に反映予定。
# Failure mode: fail-soft (Claude CLI 不在や skill 失敗は log に残し exit 0 で抜ける、cron 連発防止)。
#               skill が exit 1 を返した場合は --message プレフィックスを WARN に切替 (旧
#               audit-quarterly.sh:51-58 と同パターン)。

set -uo pipefail

# Max/Pro OAuth 経路強制 (API 課金経路 bypass、旧 audit-monthly.sh 系列と整合)。
unset ANTHROPIC_API_KEY

LOG_DIR="${HOME}/.cache/agentops-watch/logs"
# YYYYMM 維持 (旧 audit-monthly.sh:9 互換、grep pattern を壊さない)。
LOG_FILE="${LOG_DIR}/audit-monthly-$(date +%Y%m).log"
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

# /monthly-audit skill 起動。timeout 2400 (旧 monthly 中量設定を維持、quarterly の重量
# context7 観点も吸収する想定)。skill 内部で freshness-audit skill を呼ぶ設計。
# claude_ec を保持して message プレフィックス切替に使うため、|| true を使わずに直接捕捉する。
OUTPUT=$(timeout 2400 "$CLAUDE_BIN" -p "/monthly-audit" 2>&1)
claude_ec=$?
echo "$OUTPUT" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# critical / deprecated 検出時の desktop 通知。cron 環境では no-op。
if echo "$OUTPUT" | grep -iqE "critical|high severity|deprecated|broken symlink|陳腐化|重大|高リスク"; then
  if command -v notify-send >/dev/null 2>&1; then
    notify-send -u critical "月次監査: 要対応検出" "$LOG_FILE を確認してください"
  fi
fi

# 旧 audit-quarterly.sh:51-58 と同パターンで claude_ec に応じて message プレフィックスを切替。
# WARN プレフィックスは Discord 受信側で人間が即座に判別できるよう短く保つ。
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
