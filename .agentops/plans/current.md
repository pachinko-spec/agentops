---
plan-id: 2026-04-30-discord-cron-3tier-redesign
status: in-progress
started: 2026-04-30T17:30:00+09:00
owner: claude
---

# Discord 通知 cron 3-tier 再設計 (auto-discovery + agentops 集約)

## 背景

`crontab -l` を確認した結果、Discord 通知系 cron は以下のように二系統が混在していた:

- `notify-pending-discord.sh --kind {daily,weekly}` (dotfiles wrapper) — 内部参照する `discord-notify.sh` が dotfiles working tree から削除済のため壊れている (silent skip)。
- `audit-{weekly,monthly,quarterly}.sh` (host `/home/otaku/bin/`) — agentops-watch notify 経由で生きているが dotfiles 単一プロジェクト対象のみ。

`config/projects.yml` も agentops 1 行のみで、~/.claude / ~/.codex / ~/dev 配下の `.agentops/` は通知対象外。`docs/18-notification-strategy.md:78-84` で多プロジェクト走査ルールを契約済だが、CLI 実装 (`tools/agentops_monitor/__main__.py`) が追従していない gap がある。

## 目的

1. 壊れた cron 2 行 (notify-pending-discord daily / weekly) を解消する。
2. 通知対象を `~/.claude/.agentops` `~/.codex/.agentops` `~/agentops/.agentops` `~/dev/*/.agentops` の 4 root へ拡張 (auto-discovery)。
3. daily=CLI 軽量集計 / weekly=Claude `/weekly-audit` / monthly=Claude `/monthly-audit` (quarterly 吸収) の 3-tier 設計に再編する。
4. wrapper script を agentops repo 配下 (`scripts/audit-*.sh`) に集約し、Trinity (b) shared-cli-spec の責務範囲を明確化する。
5. `~/.claude/skills/{weekly,monthly}-audit/SKILL.md` を新設し、agentops 設計思想 (Trinity / DbC / localize 4 戦略 / freshness) ベースの多 project 監査を実装する。

## 非目的 (out of scope)

- Codex 側 ANT_TIME hook 対応 (別 plan)
- Codex 側 skill (`~/.codex/skills/`) 新設 (別 plan)
- `~/dotfiles/` repo 内 deprecation guard 追加 (dotfiles 側別 PR)
- `~/dev/` 各 project への `.agentops/` 配備 (将来 user 個別)

## PR 分割

- **PR-A**: agentops-watch CLI に `--auto-discover` flag 追加、`discover_projects()` helper 実装、tests 追加。`tools/agentops_monitor/__main__.py:265,298,872`。
- **PR-B**: `~/.claude/skills/weekly-audit/SKILL.md` `monthly-audit/SKILL.md` 新設。
- **PR-C**: `scripts/audit-{daily,weekly,monthly}.sh` 新設 (旧 `/home/otaku/bin/audit-*.sh` 由来、`unset ANTHROPIC_API_KEY` で OAuth 経路強制、log を `~/.cache/agentops-watch/logs/` に統一)。
- **PR-D**: crontab 切替 (5 行削除 + 3 行追加 + `BASH_ENV=$HOME/.bashrc`)、docs 更新 (`docs/11` `docs/18` `docs/19` `config/cron.example`)。
- **PR-E**: 旧 `/home/otaku/bin/audit-{weekly,monthly}.sh` を symlink 化、`audit-quarterly.sh` 削除、ADR 起票 + plan archive。

## 完了条件

- 全 PR が main へ merge 済み。
- DAILLY / WEEKLY / MONTHLY 3 channel に各 1 通の digest が観察期間内に届くこと。
- secret 値 (URL / token) が embed / log / commit history に出ていない。
- `tools/agentops_monitor/tests/` の全 test green。
- `crontab -l` の diff が plan の after 表と一致。
- 旧 cron 行 (notify-pending-discord daily/weekly + audit-quarterly) が完全に消えている。

## 停止条件

- レビュー修正が 2 周を超える。
- crontab 切替後に Discord 受信失敗が発生 → 即 rollback。
- `notify-pending-discord.sh` の dotfiles 側変更が必要になる (本 plan は dotfiles touch しない)。
- ANT_TIME Codex hook を触る必要が生じる (本 plan scope 外)。

## 参考

- 詳細プラン: `~/.claude/plans/discord-cron-sharded-tarjan.md`
- 関連 docs: `docs/11-monitoring-cli.md` `docs/18-notification-strategy.md` `docs/19-project-localization.md`
