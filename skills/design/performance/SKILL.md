---
name: design-performance
description: performance budget、query、cache、batch、rendering、scalingを設計する時に使う。
---

# パフォーマンス設計

確認すること:

- 目標レイテンシ、入力規模、負荷パターンがあるか。
- cache、pagination、index、batch、非同期化が必要か。
- 計測方法と劣化検知があるか。
