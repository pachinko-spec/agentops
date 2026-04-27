---
name: review-cost
description: インフラ、LLM/API、storage、egress、運用コストの観点でレビューする時に使う。
---

# コストレビュー

確認すること:

- 呼び出し回数、payload量、保存量、再計算量が増えすぎないか。
- LLM/API利用にrate limit、budget、cache、fallbackがあるか。
- free tierやtrialで赤字化または悪用されないか。
