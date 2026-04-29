---
task-id: 02-docs-and-cron-samples
parent-plan: ../plans/current.md
created: 2026-04-29
updated: 2026-04-30
status: in-progress
pr-target: PR-B (cron sample + hook stub 拡張 + docs/11 smoke 例)
branch: claude/agentops-monitor-docs-cron-2026-04-30
blocked-by: (PR-A merged in c94547d / squash merged in d39c4cb)
---

# Task 02: cron sample + hook stub 拡張 + docs/11 smoke 例 (PR-B)

## 前提条件

- task 01 (PR-A) は **2026-04-30 にマージ済** (`tools/agentops_monitor` の notify CLI 実装完了 / docs/11 実装ステータス注記更新済)
- 既存 `templates/claude/hooks/session-notify-stub.md` は SessionStart / Stop / PermissionRequest 例を持つ。本 task ではこれに `alert` / `stop-failure` を追加する
- 既存 `config/hooks.env.example` がある → cron sample は `config/cron.example` で同じパターン
- cron / hook の **実反映** は本 task のスコープ外 (B 別 plan: crontab 5 行整理、C 別 plan: hooks 通知連携)

## 不変条件

- secret 値を docs / sample に書かない (envvar 名のみ)
- cron sample / hook sample は **コメントつき雛形** であり、実反映ではない
- AGENTOPS_DISCORD_WEBHOOK_URL の deprecation 注記は維持する

## 完了条件 (本 task で扱う残スコープ)

- `config/cron.example` 新規作成 (コメントつき雛形):
  - DAILLY / WEEKLY / MONTHLY 起動例 (docs/18 §cron / systemd timer の起動例 と整合)
  - timezone (Asia/Tokyo) 注記
  - secret は envvar 参照のみ
- `templates/claude/hooks/session-notify-stub.md` 編集:
  - `alert` / `stop-failure` 用呼び出し例を追加 (現状は session-start / session-end / permission-wait のみ)
  - `--bypass-rate-limit` の使用条件 (`--kind alert --priority high` 限定) を注記
- `docs/11-monitoring-cli.md` 編集:
  - kind 別 dry-run 例を 2 件程度追加 (`alert` / `session-start`)。PR-A で更新済の実装ステータス注記とは独立に追加
- `markdown-link-check docs/11-monitoring-cli.md docs/18-notification-strategy.md templates/claude/hooks/session-notify-stub.md` pass
- Codex `review_frontier --effort high` cross-review で P0/P1 0 件 (scope 小なので 1 round 想定)
- archive 移動 + commit + push + PR-B 作成

## 完了条件 (PR-A で先行反映済)

- ~~`docs/11-monitoring-cli.md` 「実装ステータス注記」更新~~ → PR-A で実施済 (P2-3 反映)
- ~~旧 envvar `AGENTOPS_DISCORD_WEBHOOK_URL` の後方互換 path 説明~~ → docs/06 / docs/11 / docs/18 に既存の deprecation 注記で十分

## 禁止事項

- `tools/agentops_monitor` の実装本体を編集 (本 task は docs / template のみ)
- 実 cron / 実 hook を反映
- secret 値 (実 webhook URL) を sample / docs に値として書く
- `~/dotfiles/bin/notify-pending-discord.sh` の中身を変更

## 停止条件

- レビュー修正 2 周超過
- task 01 で実装した CLI と docs/11 記載が食い違う (実装が docs に追従できていない)
- secret 混入

## 検証手順

1. `npx markdown-link-check docs/11-monitoring-cli.md docs/18-notification-strategy.md templates/claude/hooks/session-notify-stub.md`
2. cron sample (`config/cron.example`) を `crontab -l | crontab -` 等で **反映しない** で構文だけ目視確認
3. cron sample に書かれている `agentops-watch notify` invocation を `--dry-run` 付きで手動 smoke (実通知させない)
4. agentops-reviewer subagent で独立レビュー
5. `scripts/agentops delegate --to codex --role review_frontier --effort high --input config/cron.example` で cross-review
6. P0/P1 反映 → reviewer 再走 → 0 件
7. archive 移動 → commit → push → PR-B → AI auto-merge 許諾条件評価

## DbC

- **適用前提**: task 01 マージ済、docs/18 契約変更なし
- **適用不変**: secret 値非露出、cron / hook の実反映なし
- **適用完了**: 上記「完了条件」全項目
- **適用禁止**: 上記「禁止事項」記載
- **適用停止**: 上記「停止条件」のいずれか発生
