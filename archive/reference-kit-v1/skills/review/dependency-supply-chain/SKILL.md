---
name: review-dependency-supply-chain
description: 依存関係、package、license、脆弱性、lockfile、supply chain riskをレビューする時に使う。
---

# 依存関係レビュー

確認すること:

- 新規依存の必要性、保守状況、license、脆弱性を確認したか。
- lockfile、pinning、transitive dependencyの影響が妥当か。
- 実装で代替できる小さな依存を増やしていないか。
