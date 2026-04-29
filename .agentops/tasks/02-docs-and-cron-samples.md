---
task-id: 02-docs-and-cron-samples
parent-plan: ../plans/current.md
created: 2026-04-29
status: pending
pr-target: PR-B (docs/11 実装ステータス更新 + cron / hook サンプル雛形)
branch: claude/agentops-monitor-kind-impl-2026-04-29 (継続) または別ブランチ
blocked-by: 01-notify-kind-implementation
---

# Task 02: docs/11 実装ステータス注記 更新 + cron / hook サンプル雛形 (PR-B)

## 前提条件

- task 01 (PR-A) がマージ済 (`tools/agentops_monitor` の notify CLI 実装完了)
- docs/11 の「実装ステータス注記」が「**契約段階**」と書かれている → 「**実装済み**」へ更新する責務
- cron / hook の **実反映** は本 task のスコープ外 (B / C 別 plan)

## 不変条件

- secret 値を docs / sample に書かない (envvar 名のみ)
- cron sample / hook sample は **コメントつき雛形** であり、実反映ではない
- AGENTOPS_DISCORD_WEBHOOK_URL の deprecation 注記は維持する

## 完了条件

- `docs/11-monitoring-cli.md` 編集:
  - 「実装ステータス注記」を **task 01 マージ後の現状** に更新 (kind / 4 channel / payload / rate-limit / 429 hardening が実装済み、`--dry-run` で確認可能)
  - 旧 envvar `AGENTOPS_DISCORD_WEBHOOK_URL` の後方互換 path の説明を追加 (deprecation 警告 stderr / 撤去予定時期)
  - kind 別 dry-run 例を 1〜2 件追加 (smoke 確認手段)
- `templates/agentops/cron/notification-sample.cron` 新規作成 (コメントつき雛形):
  - DAILLY / WEEKLY / MONTHLY 起動例 (docs/18 §cron / systemd timer の起動例 と整合)
  - timezone (Asia/Tokyo) 注記
  - secret は envvar 参照のみ
- `templates/agentops/hooks/anttime-notify-sample.md` 新規作成 (仕様メモ):
  - SessionStart / SessionEnd / PermissionRequest hook が `agentops-watch notify --kind <kind>` をどう呼ぶかの **疑似コード**
  - 実 hook ファイル生成は別 plan (C) のスコープ
- `markdown-link-check docs/11-monitoring-cli.md docs/18-notification-strategy.md templates/agentops/cron/notification-sample.cron templates/agentops/hooks/anttime-notify-sample.md` pass
- Codex `review_frontier --effort high` cross-review で P0/P1 0 件
- archive 移動 + commit + push + PR-B 作成

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

1. `npx markdown-link-check docs/11-monitoring-cli.md docs/18-notification-strategy.md`
2. cron sample を `crontab -l | crontab -` 等で **反映しない** で構文だけ目視確認
3. agentops-reviewer subagent で独立レビュー
4. `scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/11-monitoring-cli.md` で cross-review
5. P0/P1 反映 → reviewer 再走 → 0 件
6. archive 移動 → commit → push → PR-B → AI auto-merge 許諾条件評価

## DbC

- **適用前提**: task 01 マージ済、docs/18 契約変更なし
- **適用不変**: secret 値非露出、cron / hook の実反映なし
- **適用完了**: 上記「完了条件」全項目
- **適用禁止**: 上記「禁止事項」記載
- **適用停止**: 上記「停止条件」のいずれか発生
