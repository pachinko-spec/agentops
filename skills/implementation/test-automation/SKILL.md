---
name: implementation-test-automation
description: Webシステムのunit、integration、E2E、ブラウザ確認、migration検証を設計・実装する時に使う。
---

# test automation実装

確認すること:

- 変更リスクに対して、unit、integration、contract、E2E、visual、manual smoke のどれが必要か。
- 認証、権限、課金、DB migration、external API、file upload、cron の回帰を検出できるか。
- fixture、seed、mock、test database、secretの扱いが安全か。
- Nuxt / Next.js では hydration、routing、form、API連携、browser-specific挙動を確認する必要があるか。
- PHP / Go では request handler、service、repository、transaction、migration の境界で検証できるか。
- CIまたはpre-pushで現実的な時間で実行でき、重い検証はrelease readinessへ分けているか。
