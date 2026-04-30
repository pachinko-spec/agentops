#!/usr/bin/env bash
# Purpose: 週次で /weekly-audit skill (~/.claude/skills/weekly-audit/SKILL.md, PR-B 配置)
#          を起動し、tail 50 行を agentops-watch notify --kind weekly --message に渡して
#          Discord に送信する。skill は agentops 設計思想 (Trinity / DbC / localize 4 戦略 /
#          freshness drift) ベースの多 project 中量レビューを実行。
# Trigger: crontab 例: 0 9 * * 1 (毎週月曜 9:00)、PR-D で crontab に反映予定。
# Failure mode: fail-soft (Claude CLI 不在や skill 失敗は log に残し exit 0 で抜ける、cron 連発防止)。

set -uo pipefail

# Max/Pro OAuth 経路強制 (旧 audit-weekly.sh:21 の `--bare 不使用` 注記と整合、
# API 課金経路 bypass)。cron で BASH_ENV=$HOME/.bashrc 経由で env を引き継ぐ際にも
# 副次的に ANTHROPIC_API_KEY が流入する可能性を遮断する。
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

# /weekly-audit skill 起動。auto-discover で 4 root を scan し各 project の .agentops を
# 評価する。skill 自身が agentops-watch check --auto-discover --json を呼ぶ設計。
OUTPUT=$(timeout 1800 "$CLAUDE_BIN" -p "/weekly-audit" 2>&1) || true
echo "$OUTPUT" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# critical 検出時の desktop 通知。cron 環境では DISPLAY 未設定で no-op、手動実行の fallback。
if echo "$OUTPUT" | grep -iqE "critical|high severity|重大|高リスク"; then
  if command -v notify-send >/dev/null 2>&1; then
    notify-send -u critical "週次監査: critical 検出" "$LOG_FILE を確認してください"
  fi
fi

# tail 50 行を audit log field として agentops-watch notify --kind weekly --message に渡す。
# skill は末尾 30 行に per-project verdict を集約する設計のため、tail 50 で要約を取得できる。
if [[ -s "$LOG_FILE" ]]; then
  /home/otaku/agentops/scripts/agentops-watch notify \
    --kind weekly \
    --auto-discover \
    --message "[weekly-audit] $(tail -n 50 "$LOG_FILE")" \
    >/dev/null 2>&1 || true
fi

exit 0
