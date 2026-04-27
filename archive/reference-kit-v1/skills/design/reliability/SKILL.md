---
name: design-reliability
description: 可用性、冪等性、失敗時の復旧、retry、timeoutを設計する時に使う。
---

# 信頼性設計

確認すること:

- 失敗モードと復旧手順が明確か。
- retry、timeout、idempotency、fallbackが必要か。
- 部分失敗や再実行で不整合が起きないか。
