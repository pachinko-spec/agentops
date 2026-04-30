#!/usr/bin/env bash
# Purpose: 日次で agentops-watch notify --kind daily を起動し、auto-discover で
#          ~/.claude / ~/.codex / ~/agentops / ~/dev/*/ の .agentops 持ち project を
#          digest として Discord に送信する。Claude CLI は起動しない (軽量集計のみ)。
# Trigger: crontab 例: 10 9 * * * (毎日 9:10)、PR-D で crontab に反映予定。
# Failure mode: fail-soft (env 不足や CLI エラーは log に残し exit 0 で抜ける、cron 連発防止)。

set -uo pipefail

# Max/Pro OAuth 経路強制 (将来 weekly/monthly wrapper との統一、本 wrapper では Claude CLI を
# 起動しないため必須ではないが、誤って ANTHROPIC_API_KEY が cron env に流入したケースで API
# 課金経路へ落ちないよう先に unset する)。
unset ANTHROPIC_API_KEY

LOG_DIR="${HOME}/.cache/agentops-watch/logs"
LOG_FILE="${LOG_DIR}/audit-daily-$(date +%Y%m%d).log"
mkdir -p "$LOG_DIR"

{
  echo "=== Daily digest: $(date -Iseconds) ==="
} >> "$LOG_FILE"

# CLI 内 build_digest_embed が project field に集約するため --message は付与しない。
# 失敗 (env 未設定 / network) は CLI 側で stderr に出すが wrapper は exit 0 で抜ける。
/home/otaku/agentops/scripts/agentops-watch notify \
  --kind daily \
  --auto-discover \
  >> "$LOG_FILE" 2>&1 || true

exit 0
