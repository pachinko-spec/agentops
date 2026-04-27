---
name: review-data-integrity
description: データ整合性、transaction、migration、重複、欠損、順序の観点でレビューする時に使う。
---

# データ整合性レビュー

確認すること:

- transaction境界とrollback条件が明確か。
- migration、backfill、削除、再実行でデータが壊れないか。
- unique制約、外部キー、並行更新、順序依存が扱われているか。
