---
plan-id: 2026-05-01-claude-codex-orchestrator-rules
session-date: 2026-05-01
session-status: discussion-completed
next-action: implementation-next-session
---

# task-plan: Claude orchestrator + Codex 体制 実装

## 今回セッション (2026-05-01) の作業

- 議論で役割分担 / 修正ループ運用 / kind ラベル運用を確定
- parent plan file 作成: `~/.claude/plans/gpt5-5-opus4-7-codex-pc-tranquil-quilt.md`
- `.agentops/plans/current.md` / `.agentops/task-plans/current.md` / `.agentops/tasks/01-04` / `.agentops/prompts/next-session.md` 整備
- 実装着手は次セッションへ持ち越し (user 指示「議論であって実装は行わない」を尊重)

## 次セッション予定フェーズ

| phase | 内容 | 予測時間 |
|---|---|---|
| 1 | `claude/` branch 作成 (`claude/codex-orchestrator-rules-01` 等)、task 01 着手 | 5 min |
| 2 | task 01 (PR-01) 実装 → cross-review (Codex review run B) → PR → CI green → auto-merge | 60-90 min |
| 3 | task 02 (PR-02) 実装 → cross-review → PR → auto-merge、`~/.claude/` 反映側手動同期 | 45-60 min |
| 4 | task 03 (PR-03) 実装 → cross-review → PR → auto-merge、`~/.claude/` 反映側手動同期 | 30-45 min |
| 5 | task 04 (PR-04) 実装 → cross-review → PR → auto-merge、`~/.claude/` 反映側手動同期 | 30-45 min |
| 6 | main 同期確認、`~/.claude/.agentops/handoffs/` に反映メモ、archive 移動 | 15 min |

合計予測: 半日 〜 1 日 (4 PR + cross-review + 反映側同期)

## 注意点

- 各 PR は単一 task スコープ厳守 (auto-merge 許諾条件 5)
- cross-review は Codex (run_id B) を別 session で fire、同一 Codex 内で実装 run A と review run B が context 共有しないこと
- `~/.claude/` 配下変更は repo 管理外なので PR には含めず、別途 `~/.claude/.agentops/handoffs/` にメモ
- secret 値 (API key / token / Webhook URL) を diff / log / PR / handoff に出さない、env 名のみ参照

## 現セッション残作業

なし。次セッションが `.agentops/prompts/next-session.md` の `entry_point` から開始。
