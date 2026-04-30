---
plan-id: 2026-04-30-discord-cron-3tier-redesign
session-started: 2026-04-30T17:30:00+09:00
session-target: PR-A 完了 + PR-B/C 着手
---

# 今回セッション task-plan

## フェーズ

| 順 | フェーズ | 想定時間 | 完了条件 |
|---|---|---|---|
| 1 | branch 作成 + .agentops 起票 | 10 min | `claude/discord-cron-3tier-pr-a-auto-discover` branch 上で plan/task md commit |
| 2 | PR-A 実装: `--auto-discover` flag + `discover_projects()` helper | 60 min | `tools/agentops_monitor/__main__.py` 改修 + tests 追加 |
| 3 | PR-A 検証: tests green + dry-run 確認 | 20 min | `python3 -m unittest discover` exit 0、`agentops-watch notify --kind daily --auto-discover --dry-run` で 4 root payload 確認 |
| 4 | PR-A commit + push + PR 作成 + cross-review | 30 min | PR open、Codex に delegate review 投げる |
| 5 | PR-B 実装: `~/.claude/skills/{weekly,monthly}-audit/SKILL.md` | 45 min | 2 file 起票、手動 dry-run で skill 検出確認 |
| 6 | PR-B commit + push + PR 作成 | 15 min | PR open |

## 着手順

PR-A → PR-B → PR-C → PR-D (user 確認必須) → PR-E (観察期間後)

PR-A merge 後に PR-B 着手、PR-B merge 後に PR-C 着手、と直列進行。

## 想定リスク

- `tools/agentops_monitor/__main__.py:298 load_projects()` 改修で既存 `--projects` 経路が壊れる回帰
- tests fixture で 4 root を mock する際に `HOME` patch が他 test に漏れる

## 停止条件

- tests 修正が 2 周を超える
- cross-review で P0/P1 が 2 周持ち越し
- `--projects` 既存経路の regression 検出
