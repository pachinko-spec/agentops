---
plan-id: 2026-04-29-agentops-monitor-kind-implementation
created: 2026-04-29
status: in-progress
parent-docs: docs/18-notification-strategy.md, docs/11-monitoring-cli.md
last_reviewed: 2026-04-29
---

# Plan: `agentops-watch notify` `--kind` 実装 (4 channel + ANT_TIME)

## Context

- 直前 plan (`2026-04-29-notification-strategy-and-project-localization`) で `docs/18-notification-strategy.md` と `docs/11-monitoring-cli.md` の **契約** が確定済み (PR #58、PR #59 マージ済)。
- `docs/11` の「実装ステータス注記」が単一真ソース。現状 `tools/agentops_monitor/__main__.py` は **旧 envvar `AGENTOPS_DISCORD_WEBHOOK_URL` のみ参照、`--kind` 渡すと exit 2** で停止する状態。
- 本 plan では契約 (8 kind / 4 channel mapping / embed payload / ANT_TIME rate-limit / HTTP 429-5xx 停止) を **実装本体に反映** する。
- 既存環境変数: `DISCORD_WEBHOOK_URL_DAILLY` / `WEEKLY` / `MONTHLY` / `ANT_TIME` (`~/.bashrc` で export 済)。
- 高リスク領域: secret (Webhook URL) を扱う → **`coding_frontier high` 以上**、Codex `review_frontier --effort high` cross-review 必須 (AGENTS.md auto-merge 許諾条件)。

## 親 task 一覧

- [01-notify-kind-implementation](../tasks/01-notify-kind-implementation.md) — PR-A: notify CLI 拡張本体 (argparse / webhook resolver / payload builder / rate-limit / HTTP hardening) + tests
- [02-docs-and-cron-samples](../tasks/02-docs-and-cron-samples.md) — PR-B: docs/11 実装ステータス注記の更新 + cron / hook 移行サンプル雛形 + 旧 envvar 残存確認

## スコープ外 (別 plan)

- `~/.claude/hooks/{session_start,session_end,permission_request}.py` への notify 呼び出し追加 (C: 別 plan)
- crontab 5 行整理 (B: 別 plan、本 plan 完了後)
- `agentops localize` CLI 実装 (D: 別 plan)
- 既存 `~/dev/` 5 プロジェクトのマイグレーション (E: 各個別 plan)
- 公式 Discord plugin との統合自動化

## 完了条件

- 各 task の DbC 完了条件をすべて満たす
- PR-A / PR-B ともに Codex `review_frontier --effort high` cross-review で **P0/P1 0 件** (または反映済)
- `python3 -m compileall tools/` exit 0
- `python3 -m unittest discover tools/agentops_monitor/tests` 全 pass (新規テスト含む)
- `markdown-link-check docs/11-monitoring-cli.md docs/18-notification-strategy.md` pass
- secret (Webhook URL の値) が diff / commit message / PR 本文 / log / handoff に混入していない
- `tools/agentops_monitor/__main__.py` の旧 envvar `AGENTOPS_DISCORD_WEBHOOK_URL` 参照は **deprecation 警告つきの後方互換 path** へ縮退、または完全撤去 (task 01 で判断)

## 停止条件

- レビュー修正が 2 周を超える → ユーザー確認
- Webhook URL の値が誤って diff / log / PR 本文に混入 → 即停止
- Discord 公式 docs と payload schema が食い違う → ユーザー確認
- urllib.request の 429 / 5xx ハンドリングで予期しない side effect → ユーザー確認
- 単体テスト無し / mock 不可で実 webhook へ送信が必要な状況 → 設計変更してテスト可能化、あるいはユーザー確認
- スコープ外への踏み込み (hook / cron 実反映 / localize 実装)

## DbC

- **適用前提**: docs/18 と docs/11 の契約が変更されていない、`tools/agentops_monitor/__main__.py` の `cmd_check` / 共通関数群を破壊しない、Python 3.11+ 標準ライブラリのみ (urllib / json / argparse / pathlib / zoneinfo)
- **適用不変**: secret 値を出力しない、`allowed_mentions: {"parse": []}` を全 payload に必須、test 経路で実 HTTP を発生させない (urllib.request.urlopen を mock)、`~/.cache/agentops-watch/anttime-rate.json` は host-local state でリポジトリに置かない
- **適用完了**: 上記「完了条件」全項目
- **適用禁止**: 実 webhook URL の log / commit / PR 出力、Webhook URL の値を docs / コメントに書く、`~/dotfiles/bin/notify-pending-discord.sh` への変更
- **適用停止**: 上記「停止条件」のいずれか発生

## 検証手順

1. `python3 -m compileall tools/`
2. `cd /home/otaku/agentops && python3 -m unittest discover tools/agentops_monitor/tests -v`
3. `python3 scripts/agentops-watch notify --kind daily --projects config/projects.yml --dry-run`
4. `python3 scripts/agentops-watch notify --kind alert --message "test alert" --dry-run`
5. `python3 scripts/agentops-watch notify --kind session-start --project /home/otaku/agentops --dry-run`
6. `grep -rn 'AGENTOPS_DISCORD_WEBHOOK_URL' tools/ docs/ scripts/ rules/ skills/ workflows/ templates/ config/ 2>/dev/null` で deprecated 注記つき or 後方互換 path のみ残ること
7. `markdown-link-check docs/11-monitoring-cli.md`
8. `scripts/agentops delegate --to codex --role review_frontier --effort high --input tools/agentops_monitor/__main__.py` で cross-review
9. P0/P1 反映後、reviewer 再走で 0 件確認
10. `scripts/agentops archive task --task-id <NN>-<basename> --dry-run` → 本番実行
11. commit → push → PR 作成 → AI auto-merge 許諾条件評価 → squash merge → main 同期

## branch / PR

- task 01: `claude/agentops-monitor-kind-impl-2026-04-29` (現ブランチ)
- task 02: PR-A マージ後に同ブランチを更新 or 新規ブランチ `claude/agentops-monitor-docs-2026-04-29` で開始

## 想定時間

- task 01: 120 分 (本体 + tests)
- task 02: 30 分 (docs / cron sample)
- 各 cross-review: 30 分
