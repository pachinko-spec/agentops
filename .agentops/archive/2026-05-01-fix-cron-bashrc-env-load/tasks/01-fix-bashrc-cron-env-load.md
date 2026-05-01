# task: 01 — bashrc の DISCORD webhook export を non-interactive ガード前へ移動

親 plan: `plans/current.md` (2026-05-01-fix-cron-bashrc-env-load)

## 観察事実 (着手時)

- 2026-05-01 09:10 daily cron 失敗ログ: `error: DISCORD_WEBHOOK_URL_DAILLY is not set`
  (`~/.cache/agentops-watch/logs/audit-daily-20260501.log`)
- crontab 冒頭に `BASH_ENV=$HOME/.bashrc` が指定済み
  (`crontab -l` で確認、agentops 3-tier cron section)
- `~/.bashrc` 5-9 行目に non-interactive 早期 return ガード
- `~/.bashrc` 201-204 行目に `DISCORD_WEBHOOK_URL_{ANT_TIME,DAILLY,WEEKLY,MONTHLY}`
  の export 4 行 (ガードより後ろのため non-interactive で読まれない)

## 前提条件

- 作業ブランチ `claude/fix-cron-bashrc-env-load` で作業中
- bashrc 編集は user 承認済 (auto mode + 明示承認)
- bashrc は git 管理外、commit 対象外

## 不変条件

- secret 値 (webhook URL) は diff / log / commit / PR / handoff に
  記述しない (env 名のみ参照)
- bashrc の interactive shell 動作 (PS1 / alias / PATH / completion 等)
  に副作用を持ち込まない (移動するのは export 4 行のみ、内容変更なし)

## 完了条件 (DbC)

1. `~/.bashrc` で 4 つの export 行が `case $-` ガード (5-9 行目相当) より
   前 (ファイル先頭コメント直後) に移動している
2. 元の 201-204 行目相当の位置から該当 export 行が消えている
   (重複定義が残らない)
3. non-interactive 起動 `env -i HOME=$HOME PATH=/usr/bin:/bin BASH_ENV=$HOME/.bashrc bash -c '[ -n "$DISCORD_WEBHOOK_URL_DAILLY" ] && echo OK'`
   で `OK` が出力される (値そのものは出力しない)
4. `scripts/audit-daily.sh` を cron と同等条件で 1 回手動 fire し、
   `audit-daily-20260501.log` に `discord notification sent: HTTP 204`
   が追記される
5. interactive shell (新規 terminal 等で `echo $PS1`, `alias`, `which claude`)
   の挙動に変化がない (smoke 確認)

## 禁止事項

- webhook URL を tool result / PR / commit / log / handoff に転記すること
- bashrc 全体の整理 / refactor (今回スコープ外)
- agentops repo 側 audit スクリプトや CLI の編集 (今回スコープ外)

## 停止条件

- 検証で env 4 種のいずれかが空のまま
- 修正後の cron 経路で再び HTTP 4xx (Discord 側 block) を観測
- bashrc 編集後 `bash -i` 起動で error 出力

## 検証手順

1. `~/.bashrc` 編集前後の構造差分を `wc -l` 行数で記録 (内容差分は git 管理外)
2. non-interactive 起動で 4 env が非空であることを確認 (値は echo しない、
   `${VAR:+OK}` パターンで存在確認)
3. `bash -lc 'true'` で startup error が出ないこと
4. `scripts/audit-daily.sh` 手動実行 → `audit-daily-YYYYMMDD.log` 末尾確認
   (Discord 側 channel #日報 にも 1 件追加発火する点は許容)
