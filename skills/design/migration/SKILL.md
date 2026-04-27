---
name: design-migration
description: migration、rollout、rollback、backfill、互換期間を設計する時に使う。
---

# migration設計

確認すること:

- expand/contractや段階移行が必要か。
- rollbackと再実行が安全か。
- 旧client、旧schema、旧workerとの互換期間があるか。
