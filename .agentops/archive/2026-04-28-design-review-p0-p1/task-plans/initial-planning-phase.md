# task-plan: 横断設計レビュー P0+P1 実装フェーズ雛形

> 親 plan: `2026-04-28-design-review-p0-p1` (`.agentops/plans/current.md`)  
> 現在の状態: **計画立案フェーズ完了 / 実装フェーズ未開始**  
> 起票: 2026-04-28 (Asia/Tokyo)

---

## 1. 今セッションのスコープ（2026-04-28）

- ブランチ `claude/design-review-2026-04-28` で計画立案のみ実施。
- 実装ファイルは一切変更しない。`docs/reviews/2026-04-28-cross-repo-design-review.md` と `docs/01–16` も読み取り専用。
- 出力:
  - `~/.claude/plans/2026-04-28-design-review-p0-p1.md`（Plan agent の詳細計画）
  - `.agentops/plans/current.md`（親 plan）
  - `.agentops/task-plans/current.md`（このファイル）
  - `.agentops/tasks/01-09-*.md`（DbC 入りの task ファイル 9 件）
- 計画全体を Codex に cross-review 委譲し、所見を反映してユーザーへ提示。承認後に実装フェーズへ移行。

## 2. 次セッション（実装フェーズ）の起動手順

1. `git checkout main && git pull --ff-only origin main` で main を最新化。
2. `git checkout -b claude/design-review-impl-p0-p1` で実装ブランチを切る。
3. `.agentops/tasks/` 配下の最小番号 task（`01-p0-02-*.md`）から着手。
4. task ごとに以下のフェーズを 1 PR で完結させる。
   - 実装 → 自己レビュー → `python3 -m compileall tools` 等の検証 → Codex cross-review (`scripts/agentops delegate --to codex --role review_frontier --effort high --input <ファイル>`) → 所見を P0/P1/P2/P3 で分類して P0/P1 を反映 → PR 作成 → main マージ。
   - PR タイトルは `<task-id>: <短縮タイトル>` 形式（例: `P0-02: tool 実行層停止条件を docs/03 + harness.yml に追加`）。
   - PR 本文に DbC（前提・不変・完了・禁止・停止）、検証コマンド、未解決リスクを記載。
5. PR が main に取り込まれたら、**commit 前**（次 PR 作業開始時）に当該 task ファイルを `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/` へ移し、`prompts/next-session.md` を最新化。
6. 9 task すべてマージ後、plan / task-plan / tasks / reviews / runs を `.agentops/archive/2026-04-28-design-review-p0-p1/` 配下へまとめて移し、`.agentops/archive/README.md` にサマリ行を追記。

## 3. PR 単位の実行順（依存順）

| 順 | task | ブランチ案 | 想定コスト | 依存 |
|---|---|---|---|---|
| 1 | `01-p0-02-tool-stop-conditions.md` | `claude/design-review-impl-p0-02` | M（1 日） | なし |
| 2 | `02-p1-01-glossary.md` | `claude/design-review-impl-p1-01` | S（2h） | 01 |
| 3 | `03-p1-02-deprecation-marker.md` | `claude/design-review-impl-p1-02` | S（30m） | なし（02 / 07 と並行 PR 可） |
| 4 | `04-p1-04-last-reviewed.md` | `claude/design-review-impl-p1-04` | S（1h） | 02 |
| 5 | `05-p1-05-dbc-consolidation.md` | `claude/design-review-impl-p1-05` | S（1h） | 02 |
| 6 | `06-p1-03-cross-reference.md` | `claude/design-review-impl-p1-03` | M（半日） | 02 |
| 7 | `07-p1-06-archive-auto-update.md` | `claude/design-review-impl-p1-06` | M（半日） | なし（03 と並行 PR 可） |
| 8 | `08-p1-07-ci-and-gitignore.md` | `claude/design-review-impl-p1-07` | S–M（半日） | 04 |
| 9 | `09-p1-08-agents-md-unify.md` | `claude/design-review-impl-p1-08` | M（半日） | 02, 04, 05, 06 |

合計 9 PR、4–5 日想定。

**並行 PR 候補**（依存なし、別ブランチで並走可）:
- task 03 (P1-02) ↔ task 07 (P1-06): 完全独立。
- task 03 (P1-02) は task 02 とも依存無しのため並行可（ただし PR レビューを 1 名で回すなら逐次でもよい）。

実装フェーズで並行する場合も、各 PR は単独でマージ可能な完結状態を保つこと（共通ファイルへの編集は最小化）。

## 4. クロスレビュー運用（毎 task 共通）

- `scripts/agentops delegate --to codex --role review_frontier --effort high --input <該当ファイル>` を実行。
- 結果は `.agentops/runs/<timestamp>-<task-id>/{request.md,status.json,result.md,stdout.log,stderr.log}` に保存（secret は記録禁止）。
- Codex 所見を `.agentops/reviews/<task-id>.md` に書き出し、P0/P1/P2/P3 分類。P0/P1 は必修反映、P2 は採否判断、P3 は単独でループ継続しない。
- レビュー修正は最大 2 周。3 周目が必要なら統合判断またはユーザー確認。

## 5. 共通停止条件

- 観察事実と現状に新たな食い違いが見つかった。
- レビュー修正 2 周超え。
- secret / 本番 / 課金 / 外部公開 / 破壊的操作が必要。
- task の所要時間が想定の 2 倍を超える。
- AAIF / Claude Code / Codex の公式仕様変更が plan 前提を覆す。

## 6. 本セッションの最後にユーザーへ提示する内容

1. PR #27 マージ確認結果（済み）。
2. 報告書観察事実と現状の整合確認結果（済み・全件一致）。
3. 計画全体の構造（plan / task-plans / tasks ファイル一覧）。
4. Codex cross-review の所見と反映内容。
5. 次セッションでの実装フェーズ起動手順。
6. ユーザー承認待ちであること。
