---
name: implementation-deployment-adapter
description: Cloudflare Workers/Pages、Xserver、GCP、ローカルサーバー向けに実装や設定を合わせる時に使う。
---

# deployment adapter実装

確認すること:

- デプロイ先の公式docsで、runtime、build output、environment variables、secret、log、rollbackを確認したか。
- Cloudflareでは Workers / Pages / bindings / edge runtime / Node.js互換性 / framework adapter の制約に合うか。
- Xserverでは PHP、静的ファイル、Cron、SSH、DB、メールで自然に運用できるか。常駐daemon前提にしていないか。
- GCPでは Cloud Run、App Engine、Cloud SQL、Secret Manager、Cloud Logging、rollbackの責務が整理されているか。
- ローカルサーバーでは systemd、reverse proxy、TLS、backup、logrotate、監視、復旧手順があるか。
- deploy前後の検証、smoke test、monitoring確認、docs/runbook更新があるか。
