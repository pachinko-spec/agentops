---
parent-plan: 2026-04-30-applies-to-and-trinity
session-date: 2026-04-30
status: in-progress
---

# Task plan: applies-to frontmatter + 三役 + Discord 通知 docs 改修

親 plan: [`../plans/current.md`](../plans/current.md)

## 今回セッションの順序

1. **.agentops/ 起票** (本 file 含む 3 file) — 完了
2. **docs/00-glossary.md に用語追加** (applies-to spec / 三役 / shared-cli-spec パターン)
3. **AGENTS.md** 三役で位置づけ書き直し (additive)
4. **README.md** 冒頭に三役を公開向け表現で追加
5. **全 20 docs に applies-to frontmatter 追加** (分類表は task 01 参照)
6. **docs/18 に shared-cli-spec パターン適用 section 追加**
7. **docs/11 に位置付け参照節追加**
8. **検証** (frontmatter parse / pytest / link-check)
9. **agentops-reviewer subagent でレビュー** (P0/P1/P2/P3 分類)
10. **Codex cross-review** (`scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/00-glossary.md`)
11. **P0/P1 反映** (round 2 以内、3 周目必要なら user 確認)
12. **archive task → archive plan → commit → push → PR**
13. **CI green + secret 未混入確認 → auto-merge**
14. **main 同期確認 + .agentops/ クリーン状態確認 + 完了報告**

## 時間見積もり

- step 2-7 (実装): 30-45 分
- step 8 (検証): 5-10 分
- step 9-11 (レビュー): 15-30 分 (Codex 実走 + 反映)
- step 12-14 (archive / merge): 10-15 分
- 合計: 60-100 分 (半日以内)

## 進捗

- step 1: 完了
- step 2 以降: 着手中
