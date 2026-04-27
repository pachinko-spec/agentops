# 運用workflow

## 使う場面

本番運用、障害対応、監視追加、backup、cron、定期作業、運用手順の整備に使います。

## 手順

1. 対象環境、デプロイ先、影響ユーザー、権限、secret、production data の扱いを確認する。
2. 現在の状態、ログ、metrics、alert、recent deploy、外部サービス状態を確認する。
3. 手順を plan と runbook に分け、実行前に停止条件とrollbackを明示する。
4. Cloudflare、Xserver、GCP、ローカルサーバーごとの運用制約を確認する。
5. 作業後に検証、監視確認、docs/runbook更新、handoffを行う。

## 停止条件

- 本番secretや個人情報を安全に扱えない。
- rollbackできない変更を外部公開環境へ直接行う必要がある。
- 影響範囲、権限、監視方法が不明。
