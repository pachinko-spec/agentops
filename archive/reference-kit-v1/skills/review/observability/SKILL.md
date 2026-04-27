---
name: review-observability
description: ログ、metrics、trace、alert、debuggabilityの観点でレビューする時に使う。
---

# 監視性レビュー

確認すること:

- 重要操作、失敗、権限変更、課金、外部連携に観測点があるか。
- ログにsecretや個人情報が出ないか。
- 障害時に原因、影響範囲、復旧状況を追えるか。
