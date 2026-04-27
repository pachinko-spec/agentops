---
name: review-security
description: 認証、認可、secret、injection、データ露出、悪用経路の観点でレビューする時に使う。
---

# セキュリティレビュー

確認すること:

- 認証と認可がサーバー側で強制されているか。
- ユーザー入力、外部入力、LLM出力を信頼していないか。
- secret、token、個人情報がログやレスポンスに出ないか。
- injection、path traversal、prompt injection、replay、abuseの経路がないか。
