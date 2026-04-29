---
plan-id: 2026-04-30-agentops-monitor-digest-message
created: 2026-04-30
status: in-progress
parent-docs: docs/18-notification-strategy.md, docs/11-monitoring-cli.md
last_reviewed: 2026-04-30
---

# Plan: digest kind に `--message` 拡張 + audit-*.sh 切替

## Context

- 直前 plan (`2026-04-29-agentops-monitor-kind-implementation`) で `agentops-watch notify --kind` 8 種実装完了 (PR #60 / #61 マージ済)
- B (crontab 5 行整理) を進める過程で、Discord 通知経路が壊れていることが判明:
  - `discord-notify.sh` が dotfiles の git HEAD に存在するが working tree から削除済
  - audit-*.sh × 3 と notify-pending-discord.sh が `|| true` で silent fail
  - audit-*.sh が使う独自 kind (`sanity-check` / `quarterly-review` / `monthly-audit`) は agentops-watch 8 標準 kind に存在しない
- 解決策: agentops-watch を拡張し digest kind (daily/weekly/monthly) で `--message` 受付 → audit log を embed field として乗せる
- 同 plan で Phase B (audit-*.sh 修正、host-local commit なし) と Phase C (notify-pending-discord 報告のみ) も扱う

## 親 task 一覧

- [01-digest-kind-message](../tasks/01-digest-kind-message.md) — Phase A: agentops-watch digest kind に --message 統合 (impl + tests + docs)
- [02-audit-scripts-migration](../tasks/02-audit-scripts-migration.md) — Phase B: /home/otaku/bin/audit-*.sh × 3 修正トラッキング (host-local、commit なし)

## スコープ外

- notify-pending-discord.sh (1397 行 / 9 責務、置換不能、別 plan で C-A or C-B 検討)
- crontab 行そのもの (cmdline 不変なので編集不要)
- dotfiles repo 全体 (Phase C は報告のみ)
- audit-*.sh の skill 実行ロジック (`claude /sanity-check` 等は touch しない)
- `metrics-collect.sh` / `server-report.sh` (user 明示)

## 完了条件

- task 01 (PR-C) の DbC 完了条件すべて
- task 02 の DbC 完了条件すべて
- Codex `review_frontier --effort high` cross-review で P0/P1 0 件
- 既存 60 系単体テストすべて pass + 新規 5 件以上 pass
- secret 値 (Webhook URL) が diff / commit / PR 本文 / log / docs に混入していない
- archive 移動 + commit + push + PR 作成 + user 手動マージ + main 同期

## 停止条件

- レビュー修正 2 周超過 → user 確認
- Webhook URL 値が誤って混入 → 即停止
- agentops-watch の既存 cmd_check 挙動を破壊 (regression) → ロールバック
- audit-*.sh の skill 実行ロジックを破壊 → 元に戻す
- crontab を user 同意なく編集 → 即停止
- dotfiles repo を編集 (scope 違反) → 即停止

## 想定時間

- task 01 実装 + テスト: 90 分
- task 01 cross-review + 反映: 30〜60 分
- task 01 archive + commit + push + PR + 手動マージ: 15 分
- task 02 (host-local edit + smoke): 30 分
