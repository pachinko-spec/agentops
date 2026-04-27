---
name: review-release-readiness
description: release前の検証、feature flag、rollback、monitoring、docs、support readinessをレビューする時に使う。
---

# release readinessレビュー

確認すること:

- release条件、検証結果、rollback手順が明確か。
- Cloudflare、Xserver、GCP、ローカルサーバーのデプロイ先制約を確認したか。
- feature flag、monitoring、alert、support導線があるか。
- docs、changelog、migration guide、runbook、環境変数説明が必要か。
