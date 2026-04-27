---
name: production-operations
description: 本番運用、障害対応、監視、backup、cron、手動復旧を扱う時に使う。
---

# production operations

確認すること:

- 対象環境、デプロイ先、影響ユーザー、権限、production data、secretの扱いが明確か。
- Cloudflare、Xserver、GCP、ローカルサーバーごとのログ、監視、rollback、backupの方法を確認したか。
- cron、queue、background job、証明書更新、DB backup、storage backup、mail送信の失敗時挙動があるか。
- runbook、復旧手順、手動介入の停止条件、作業後の確認項目があるか。
- 1人開発者が継続できる運用負荷、通知頻度、費用になっているか。
