---
name: understand-anything-bootstrap
description: Understand-Anythingを未導入なら導入し、導入済みならskipする時に使う。
---

# Understand-Anything bootstrap

使うコマンド:

```bash
node scripts/ua-bootstrap.mjs --check-only
node scripts/ua-bootstrap.mjs --platform codex
```

導入済みなら既存plugin rootとskill symlinkを優先します。
