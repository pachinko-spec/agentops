---
name: review-reliability
description: 障害、retry、timeout、冪等性、復旧性、部分失敗の観点でレビューする時に使う。
---

# 信頼性レビュー

確認すること:

- timeout、retry、backoff、circuit breakerが必要な箇所にあるか。
- 冪等性が必要な操作で二重実行に耐えるか。
- 部分失敗、外部API失敗、再実行時の整合性が保たれるか。
