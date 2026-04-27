---
name: understand-anything-update
description: Understand-Anythingのgraph更新範囲をdiff/incremental/domain/full/skipから選ぶ時に使う。
---

# Understand-Anything update

使うコマンド:

```bash
node scripts/ua-graph-controller.mjs --mode pr --base main
node scripts/ua-graph-controller.mjs --mode post-merge --base HEAD~1 --write-log
```

PR中は軽く、merge後に必要な範囲だけ更新します。
