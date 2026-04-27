---
name: review-api-compatibility
description: API互換性、公開契約、schema、versioning、client影響の観点でレビューする時に使う。
---

# API互換性レビュー

確認すること:

- response schema、error code、field名、nullableの変更が互換か。
- 既存clientや外部連携に破壊的影響がないか。
- versioning、deprecation、migration pathが必要か。
