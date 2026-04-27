---
name: review-performance
description: レイテンシ、メモリ、DB負荷、描画コスト、ネットワーク量、スケールリスクをレビューする時に使う。
---

# パフォーマンスレビュー

確認すること:

- N+1 query、全件取得、巨大payload、不要な同期処理がないか。
- cache、pagination、batch、timeout、retryが妥当か。
- 通常ケースとworst caseの入力規模が想定されているか。
