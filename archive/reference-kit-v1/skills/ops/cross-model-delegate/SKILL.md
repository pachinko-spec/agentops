---
name: cross-model-delegate
description: Claude CodeとCodex間、またはsubagentへ作業委譲する時に使う。
---

# cross-model delegate

確認すること:

- 委譲する範囲が具体的で、main agentの判断責任が残っているか。
- `.agentops/runs/` にrequest、status、stdout、resultを残すか。
- 委譲結果を鵜呑みにせず統合判断するか。
