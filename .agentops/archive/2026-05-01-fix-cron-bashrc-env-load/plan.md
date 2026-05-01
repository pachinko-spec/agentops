# plan: 2026-05-01-fix-cron-bashrc-env-load

> plan-id: `2026-05-01-fix-cron-bashrc-env-load`

## 背景

2026-05-01 09:10 の daily cron (`scripts/audit-daily.sh`) が
`error: DISCORD_WEBHOOK_URL_DAILLY is not set` で失敗していることを確認した
(`~/.cache/agentops-watch/logs/audit-daily-20260501.log`)。

原因は `~/.bashrc` の non-interactive 早期 return ガード
(`case $- in *i*) ;; *) return;; esac`) よりも後ろに
`export DISCORD_WEBHOOK_URL_*` 系 4 行が置かれているため、
crontab 冒頭の `BASH_ENV=$HOME/.bashrc` が non-interactive bash で
発火しても export 行へ到達しない。手動 (interactive) 実行時は
ガードを通過するため成功してしまい問題が露見しにくかった。

weekly (月曜 09:00) / monthly (1日 11:00) も同じ env を使うため、
次回 cron 実行で同じ理由で失敗する見込み。

## 目的

cron 経由 (non-interactive bash) で `audit-daily.sh` /
`audit-weekly.sh` / `audit-monthly.sh` を起動した際に、Discord
webhook URL 4 種が確実に export されている状態にする。

## 非目的

- bashrc 全体の整理、別 secret 管理基盤への移行
- audit スクリプト本体や agentops-watch CLI の挙動変更
- 既存 Discord webhook URL の rotate / 再発行

## 採用方針

A 案: `~/.bashrc` の 4 行 (DISCORD_WEBHOOK_URL_ANT_TIME /
DAILLY / WEEKLY / MONTHLY の export) を non-interactive 早期
return ガードより前へ移動する。export はそもそも non-interactive
shell でも必要であり、ガード前に置くのは意味的にも正しい。

B (env file 分離) / C (cron スクリプト側で source) と比較し、
変更量・副作用が最小なため採用。

## 完了条件

- `~/.bashrc` で 4 つの `DISCORD_WEBHOOK_URL_*` export 行が
  non-interactive ガードよりも前に位置している
- non-interactive bash (`bash -c '...'` 相当) で `BASH_ENV=$HOME/.bashrc`
  経由で起動したとき、4 env がいずれも非空で export されている
- `scripts/audit-daily.sh` を cron と同等条件 (env を inherit させない
  起動方法) で 1 回手動 fire し、`audit-daily-YYYYMMDD.log` に
  `discord notification sent: HTTP 204` が記録される
- `tasks/01-fix-bashrc-cron-env-load.md` の DbC 完了条件をすべて満たす

## 停止条件

- bashrc を編集した結果、interactive shell の起動が壊れる
  (PS1 / alias / PATH 等が想定外に変わる)
- webhook URL の値が diff / log / commit message / PR / handoff に
  混入した場合は即座に切り戻して rotate を user に提案
- bashrc 編集後の検証で webhook が依然 not set / HTTP 4xx を返す

## 親 task 一覧

- `tasks/01-fix-bashrc-cron-env-load.md` — bashrc の export 移動と
  cron 経路の動作確認
