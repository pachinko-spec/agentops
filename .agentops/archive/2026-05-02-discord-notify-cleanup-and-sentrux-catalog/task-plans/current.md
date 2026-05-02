# task-plan: discord-notify-cleanup-and-sentrux-catalog (再々設計版)

> parent_plan: `2026-05-02-discord-notify-cleanup-and-sentrux-catalog`
> session_started: 2026-05-02T17:30:00+09:00
> last_updated: 2026-05-02T20:00:00+09:00 (Phase 4 2 周目反映後、Phase 1-2 finalize 確認済み + handoff 整合)

## フェーズ (担当列必須、Phase 着手前 1 行宣言)

| Phase | work area | 担当 | 状況 |
|---|---|---|---|
| Phase 1-1 | 設計段階 cross-review (初回 + 反映) | Codex review_frontier (effort high) | 完了 (2 周、`runs/20260502T034048+0900` / `runs/20260502T034550+0900`) |
| Phase 1-2 | plan 再々設計後 cross-review | Codex review_frontier (effort high) | 完了 (`runs/20260502T051610+0900-codex-review_frontier` で新規 P0/P1/P2/P3 なし、finalize 可) |
| Phase 2-revert | Claude 違反実装の revert (modified + untracked file 削除) | Codex coding_frontier (effort high) | 実施済み (`runs/20260502T052743+0900-codex-coding_frontier`、git restore は sandbox 制約で `apply_patch` で代替。グローバル 3 ファイルは P1#1 例外受け入れで Codex 判定「target 形」のため revert 不要) |
| Phase 2-impl | agentops repo 4 ファイル + グローバル 5 ファイル を fresh 実装 | Codex coding_frontier (effort high) | 実施済み (agentops repo 4 ファイルは Codex 直接 write、グローバル skill 2 ファイルは Codex snippet を Claude orchestrator が Apply、グローバル 3 ファイルは Codex 判定で「target 形」のため Apply 不要 = sandbox 制約による不可避、user 承認 a) |
| Phase 2.5 | memory feedback 保存 + handoff 追記 (命令形化) | Claude orchestrator_frontier | 完了 (`feedback_phase_owner_declaration.md` 新規保存、MEMORY.md 追記、handoff 命令形化) |
| Phase 3 | 静的検証 + replayable 検証 (sample payload で additionalContext JSON 確認) | Claude orchestrator_frontier | 完了 (`compileall` exit 0、sample payload で運用ルール再掲 5 行消失 + 動的情報残存確認) |
| Phase 4 | 実装後 cross-review | Codex review_frontier (effort high) | 1 周目 (`runs/20260502T053705+0900` で P1=2 検出 → 例外受け入れ + 状態同期で反映)、2 周目 (`runs/20260502T054434+0900` で P1=2 検出 → 網羅修正反映、user 承認 a)、3 周目で finalize 確認待ち |
| Phase 4.5 | merge 前 archive (`scripts/agentops archive task` / `archive plan`) | Claude orchestrator_frontier | 1 PR scope 完結原則 |
| Phase 5 | merge (`gh pr merge --squash --delete-branch`) | Claude orchestrator_frontier | auto-merge 許諾条件 6 全クリア時のみ |
| Phase 6 | post-merge 確認 (main 同期 + 動作確認) | Claude orchestrator_frontier | 報告まで責務 |

## 時間予測 (残作業)

- Phase 4 2 周目 cross-review (反映確認): 5-10 min
- Phase 4.5 + Phase 5 + Phase 6: 15-20 min

合計 0.5-1 hour 残予測。

## 注意点

- **次の違反は一切認めない** (user 強い指示)
- 各 Phase 着手前に担当宣言を必ず発する
- Codex coding_frontier 担当 (Phase 2) なら Edit / Write を直接呼ばず delegate 経由のみ使う
- Phase 2-revert 手順は untracked file (`docs/20-tooling-candidates.md` / `templates/projects/sentrux/`) 明示削除を含める (`git restore` だけでは消えない)
- `.agentops/` 配下 (plans / tasks / handoffs / task-plans / runs) は revert 対象外、本セッション設計記録として残す
- secret 値 (Webhook URL / API key / token / credential) を diff / log / PR / handoff に出さない (env 名のみ参照)
- review-policy 解釈: 修正最大 2 周 + 3 周目で統合判断 / user 確認 (現行 rule 準拠、4 分岐は中期 plan D で実装)
