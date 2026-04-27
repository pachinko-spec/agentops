---
name: implementation-web-backend
description: PHP、Go、API、DB、認証、バッチ、cronを実装する時に使う。
---

# Web backend実装

確認すること:

- PHP / Go / framework / runtime の現在仕様と対象環境を公式docsで確認したか。
- request validation、認証、認可、CSRF、rate limit、error response、loggingが適切か。
- DB transaction、index、migration、rollback、backfill、data integrityを確認したか。
- Xserver、GCP、Cloudflare、ローカルサーバーのruntime制約に合う実装か。
- cron、queue、background job、file upload、mail、external API の失敗時挙動があるか。
- unit、integration、contract、migration dry-run、load check の必要性を判断したか。
