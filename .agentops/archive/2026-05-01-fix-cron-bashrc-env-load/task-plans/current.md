# task-plan: 2026-05-01-fix-cron-bashrc-env-load (session 1)

親 plan: `plans/current.md` (2026-05-01-fix-cron-bashrc-env-load)
作業ブランチ: `claude/fix-cron-bashrc-env-load`

## フェーズ

| # | フェーズ | 想定時間 | 主作業 |
|---|---|---|---|
| 1 | 現状確認 | 5 分 | crontab / bashrc 構造 / 直近 cron log 把握済み |
| 2 | 修正 | 5 分 | bashrc の export 4 行を non-interactive ガード前へ移動 |
| 3 | 検証 | 10 分 | non-interactive bash で env 解決確認 + audit-daily.sh 実発火 1 回 |
| 4 | 記録 | 10 分 | task / plan / archive 移動、handoff 不要 |
| 5 | PR | 10 分 | commit / push / PR 作成 / cross-review 要否判定 |

## 残懸念

- weekly / monthly は次回 cron 発火 (来週月曜 / 来月 1 日) まで
  実環境での確認ができない。本 PR では non-interactive bash での
  env 解決確認をもって fix 妥当性とし、週次/月次の実 cron 確認は
  次回発火時の通常監視 (digest 受信) に委ねる。
- bashrc は git 管理外であるため diff として残らない。修正の
  事実は task md / handoff (本 task では不要) に記述する。
