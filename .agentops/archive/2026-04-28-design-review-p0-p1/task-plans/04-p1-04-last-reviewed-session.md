# Task-plan: task 04-p1-04-last-reviewed セッション

> 親 plan: `2026-04-28-design-review-p0-p1`  
> task: `.agentops/tasks/04-p1-04-last-reviewed.md`  
> セッション開始: 2026-04-28 (Asia/Tokyo)  
> 主 orchestrator: Claude Opus 4.7 (1M)  
> Reviewer (cross-model): Codex CLI (review_frontier)  
> 想定コスト: S（1h）  
> 実装ブランチ: `claude/design-review-impl-p1-04`  
> 後処理ブランチ: `claude/archive-task-04-p1-04-last-reviewed-dogfood`

---

## 親 plan からの参照

- 残 3 task のうち 1 件目を本セッションで実装。task 02/03/05/06/07 完了済み、本 task 04 完了後は task 08 → 09 の順。
- 採用方針: YAML frontmatter（`---`）4 共通キー + docs/00 のみ scope: glossary 保持で 5 キー（user 確認済み）。

## セッション フェーズ

| Phase | 内容 | 想定時間 |
|---|---|---|
| 0 | git 同期 + branch 作成 + task-plan 作成 | 完了 |
| 1 | docs/01–17 (17 件) に YAML frontmatter 追加 | 10 分 |
| 2 | docs/00 frontmatter 差分整理（5 キー） | 2 分 |
| 3 | docs/06 に `## last_reviewed フロントマター形式` セクション + 自身 frontmatter 追加 | 5 分 |
| 4 | 検証コマンド一式実行 | 3 分 |
| 5 | Codex cross-review Round 1 → 修正 → Round 2 → Round 3 確認専用 | 30 分 |
| 6 | PR 作成 + auto-merge 6 件評価 + squash merge | 5 分 |
| 7 | main 同期 + archive task ドッグフード（別 PR） | 10 分 |

合計目安: 約 1 時間

## DbC（task 04 完了条件、再掲）

- [ ] `docs/` 直下番号付き Markdown 全 18 件にフロントマター
- [ ] `rg -L "^last_reviewed|^> last-reviewed" docs/[0-9]*.md` 空
- [ ] `rg "^last_reviewed: 2026-04-28" docs/[0-9]*.md` 件数 18
- [ ] 形式選択根拠が docs/06 に記録
- [ ] Codex cross-review 完了、所見反映済み
- [ ] PR が main にマージ、ローカル main 同期
- [ ] `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/04-*.md` に移動済み

## 検証コマンド

```bash
python3 -m compileall tools                                      # exit 0
rg -L "^last_reviewed|^> last-reviewed" docs/[0-9]*.md           # 空
rg "^last_reviewed: 2026-04-28" docs/[0-9]*.md | wc -l           # 18
rg "^scope: glossary" docs/[0-9]*.md | wc -l                     # 1 (docs/00)
rg "^## last_reviewed" docs/06-freshness-and-monitoring.md       # 1
python3 -m unittest discover -s tests                            # all pass
```

## 停止条件

- frontmatter 形式選択で markdown link check / docs ビルドツール破損 → blockquote 互換に切替
- レビュー修正 2 周超え（3 周目で修正必要） → 統合判断 / user 確認
- AI auto-merge 6 件いずれか NG → user 確認
- 観察事実食い違い → user 確認

## 完了後の archive 後処理

1. PR マージ後 `git checkout main && git pull --ff-only origin main`
2. `claude/archive-task-04-p1-04-last-reviewed-dogfood` 切り出し
3. `scripts/agentops archive task --task-id 04-p1-04-last-reviewed --dry-run` → 本番実行
4. `git add .agentops/prompts/next-session.md`（CLI 既知問題、PR #32 で発覚）
5. next-session.md 本文を手動書き直し（次 task 08 への申し送り）
6. 別小 PR 作成 → self-merge → main 同期

## 関連ファイル

- 親 plan: `.agentops/plans/current.md`
- task: `.agentops/tasks/04-p1-04-last-reviewed.md`
- Plan agent ファイル: `~/.claude/plans/task-04-p1-04-last-reviewed-archive-ticklish-church.md`
- review (作成予定): `.agentops/reviews/p1-04.md`
