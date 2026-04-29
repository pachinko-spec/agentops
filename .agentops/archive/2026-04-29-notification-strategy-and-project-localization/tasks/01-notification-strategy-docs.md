---
task-id: 01-notification-strategy-docs
parent-plan: ../plans/current.md
created: 2026-04-29
status: in-progress
pr-target: PR-B (Discord 通知戦略 docs / catalog / templates)
branch: claude/notification-strategy-discord-2026-04-29
---

# Task 01: Discord 通知戦略 docs / catalog / templates 整備 (PR-B B-1)

## 前提条件

- 既存 export envvar: `DISCORD_WEBHOOK_URL_DAILLY` / `WEEKLY` / `MONTHLY` / `ANT_TIME`
- 既存 docs: `docs/06-freshness-and-monitoring.md` (notify 設計言及)、`docs/11-monitoring-cli.md` (`agentops-watch notify` + 旧 envvar `AGENTOPS_DISCORD_WEBHOOK_URL`)
- 既存実体: `scripts/agentops-watch` → `tools.agentops_monitor`、`~/dotfiles/bin/notify-pending-discord.sh` (先行実装、本 task は触らない)
- 公式 Discord plugin (`~/.claude/plugins/.../discord/`) は MCP server 双方向、本 task は一方向 webhook digest 設計
- agentops は実フックを持たない方針 (AGENTS.md)、templates は雛形/仕様メモのみ

## 不変条件

- agentops 参照キット は「設計思想 / 雛形 / 候補カタログ」管理。CLI 実装本体は別 plan
- Webhook URL / SECRET 値を diff / commit / log / PR に出さない
- 既存 envvar `AGENTOPS_DISCORD_WEBHOOK_URL` は deprecated 注記つきで残す (壊さない)
- `~/.claude/CLAUDE.md` 増分 +5 行以内
- `~/dotfiles/bin/notify-pending-discord.sh` の中身を変更しない (read-only)

## 完了条件

- `/home/otaku/agentops/docs/18-notification-strategy.md` 新規作成 (last_reviewed frontmatter 含む)
- `/home/otaku/agentops/docs/11-monitoring-cli.md` 編集 (4 channel / kind→envvar マッピング表 / deprecated 注記)
- `/home/otaku/agentops/docs/06-freshness-and-monitoring.md` 編集 (docs/18 リンク + envvar 追従)
- `/home/otaku/agentops/docs/17-cross-reference.md` 編集 (新規 rule/skill/workflow の逆参照)
- `/home/otaku/agentops/templates/claude/hooks/session-notify-stub.md` 新規作成 (仕様メモ、コード雛形ではない)
- `/home/otaku/agentops/rules/catalog.md` 編集 (`notification-policy` 行追加)
- `/home/otaku/agentops/skills/catalog.md` 編集 (`notification-digest-writer` 行追加)
- `/home/otaku/agentops/workflows/catalog.md` 編集 (`notification-cron-setup` 行追加)
- `~/.claude/CLAUDE.md` 編集 (「通知方針」短い節 +5 行以内)
- markdown-link-check pass
- `grep -rn AGENTOPS_DISCORD_WEBHOOK_URL docs/ rules/ skills/ workflows/ templates/ scripts/ config/` の残存に未注記参照ゼロ
- `tools/agentops_monitor/__main__.py` の旧 envvar 実参照は **本 task スコープ外** (実装本体は別 plan で 4 channel 対応する)。docs/11 の「実装ステータス注記」が単一真ソース。
- Codex `review_frontier --effort high` cross-review で P0/P1 0 件 (または反映済)
- agentops repo の archive ルールで commit 前に本 task ファイル + plan / task-plan を archive へ移動

## 禁止事項

- `agentops-watch` 本体 (`tools/agentops_monitor`) の実装を変更すること
- `~/.claude/hooks/` 配下の実 hook ファイル追加・編集
- crontab の実反映 (B-2 は別 task)
- `~/dotfiles/bin/notify-pending-discord.sh` の中身改修
- 公式 Discord plugin のセットアップ自動化に踏み込むこと

## 停止条件

- envvar 仕様や channel 区分が user 申告と食い違う
- `~/.claude/CLAUDE.md` 増分が +5 行を超える
- レビュー修正が 2 周を超える
- Webhook URL の SECRET が誤って混入
- envvar 旧名 deprecated 周知が docs 間で整合しない

## 検証手順

1. `markdown-link-check docs/18-notification-strategy.md docs/11-monitoring-cli.md docs/06-freshness-and-monitoring.md docs/17-cross-reference.md templates/claude/hooks/session-notify-stub.md`
2. `grep -rn 'AGENTOPS_DISCORD_WEBHOOK_URL' docs/ rules/ skills/ workflows/ templates/ scripts/ config/` で deprecated 注記つきの参照のみ残ること (`tools/` は実装本体 plan のスコープ、本 task では検査外。grep 範囲は line 40 の完了条件と同期)
3. `wc -l ~/.claude/CLAUDE.md` で増分確認
4. agentops-reviewer subagent で独立レビュー
5. `scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/18-notification-strategy.md` で cross-review
6. P0/P1 反映後、reviewer 再走で 0 件確認
7. `scripts/agentops archive task --task-id 01-notification-strategy-docs --dry-run` で確認 → 本番実行
8. commit → push → PR 作成 → AI auto-merge 許諾条件評価 → squash merge → main 同期
