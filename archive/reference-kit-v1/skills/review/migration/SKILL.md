---
name: review-migration
description: migration、rollout、rollback、backfill、互換期間の観点でレビューする時に使う。
---

# migrationレビュー

確認すること:

- rolloutとrollbackの順序が安全か。
- 旧データ、旧client、旧workerとの互換期間が考慮されているか。
- backfillや再実行が冪等か。
