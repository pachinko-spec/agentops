# task-plan: task 08 (P1-07) — 最小 CI + .gitignore secret 拡張子追加

> 親 plan: `2026-04-28-design-review-p0-p1`
> 親 task: `.agentops/tasks/08-p1-07-ci-and-gitignore.md`
> session: 2026-04-29
> branch: `claude/design-review-impl-p1-07`
> 想定 PR 構成: 実装 PR + archive ドッグフード PR の 2 PR

---

## フェーズ別実行計画

### Phase 1: 実装（着手済）

| step | 内容 | 状態 |
|---|---|---|
| 1.1 | `.gitignore` 末尾に secret 拡張子 6 行 + コメント追記 | ✅ 完了 |
| 1.2 | `.github/workflows/ci.yml` 新規（actionlint / yamllint / markdown-link-check / freshness-check の 4 job） | ✅ 完了 |
| 1.3 | `.github/markdown-link-check.json` 新規（rate limit 対策） | ✅ 完了 |
| 1.4 | `.github/PULL_REQUEST_TEMPLATE.md` 新規（DbC 5 条件 + auto-merge 6 件 checklist） | ✅ 完了 |
| 1.5 | `.agentops/task-plans/current.md` 新規（本ファイル） | ✅ 完了 |
| 1.6 | `.agentops/reviews/p1-07.md` 新規 | ✅ 完了 (Round 1 投入前は枠のみ、各 Round 後に転記) |

### Phase 2: ローカル smoke

| step | 内容 | 状態 |
|---|---|---|
| 2.1 | `python3 -c "import yaml; yaml.safe_load(...)"` で workflow YAML 構文検証 | ✅ pass |
| 2.2 | `json.load` で markdown-link-check.json 検証 | ✅ pass |
| 2.3 | freshness-check Python 等価実装で `docs/[0-9]*.md` 18 件 stale=0 / missing=0 確認 | ✅ pass |
| 2.4 | `python3 -m compileall tools` exit 0 | ✅ pass |
| 2.5 | `python3 -m unittest discover -s tests` 12/12 pass | ✅ pass |
| 2.6 | actionlint binary ローカル実行 | ❌ permission denied、CI 側で確認 |
| 2.7 | yamllint ローカル実行 | ❌ pip 不可、CI 側で確認 |
| 2.8 | markdown-link-check ローカル実行 | ❌ npm install スキップ、CI 側で確認 |

> note: ローカル env 制約により actionlint / yamllint / markdown-link-check の手元実行は不可。
> CI 自体が初回 PR で 4 job を回すため、push 直後の Actions 結果で fail を検知して修正する方針へ切替。

### Phase 3: PR #1 push & GitHub Actions green 確認

| step | 内容 |
|---|---|
| 3.1 | commit (.gitignore / workflow / config / template / task-plan / review skeleton) |
| 3.2 | push → PR 作成（auto-merge 6 件 checklist を本文に含める） |
| 3.3 | Actions tab で 4 job の結果確認。fail なら修正 commit を push |
| 3.4 | freshness-check job summary が `All docs are fresh` を出すことを確認 |

### Phase 4: Codex cross-review（3 Round）

| step | 内容 |
|---|---|
| 4.1 | Round 1: `scripts/agentops delegate --to codex --role review_frontier --effort high --input .github/workflows/ci.yml --run-id <ts>+0900-p1-07-r1 --message <観点 9 件>` |
| 4.2 | 所見を `.agentops/reviews/p1-07.md` Round 1 セクションに転記、P0/P1 反映 |
| 4.3 | Round 2: 修正後の clean 確認 |
| 4.4 | Round 3: 確認専用、`no further P0/P1` |

### Phase 5: AI auto-merge 6 件評価 → squash merge

CLAUDE.md §許諾条件 6 件を独立評価。全 OK なら `gh pr merge --squash --delete-branch`。

### Phase 6: main 同期 & PR #2 (archive ドッグフード)

| step | 内容 |
|---|---|
| 6.1 | `git checkout main && git fetch origin && git pull --ff-only origin main` |
| 6.2 | `git checkout -b claude/archive-task-08-p1-07-ci-and-gitignore-dogfood` |
| 6.3 | `scripts/agentops archive task --task-id 08-p1-07-ci-and-gitignore --dry-run` → 本番 |
| 6.4 | `git add .agentops/prompts/next-session.md`（PR #32 既知制約） |
| 6.5 | `next-session.md` 本文を task 08 セッション内容で書き直し（手動） |
| 6.6 | PR #2 作成 → self-merge → main 同期確認 |

---

## 過去 task 04 Round 1 P3 申し送りの反映確認

- ✅ freshness-check の grep を `^next_review_by:` に絞り、blockquote 形式 (`^> next-review-by`) を OR で許容しない（ci.yml L97 のコメントで明示）
- ✅ 検証スクリプト側では `rg --files-without-match` を使う方針（`rg -L` は `--follow` のため未一致列挙には使わない）

## 想定リスクと縮退（plan/risks より）

| ID | 状態 |
|---|---|
| R1: yamllint で既存 config fail | inline config に `comments-indentation: disable` 追加で予防的対応 |
| R2: markdown-link-check 外部 false positive | `.github/markdown-link-check.json` で retry / aliveStatusCodes / ignorePatterns 設定済み |
| R3: 無料枠超過 | public repo 想定（無料無制限）、コスト試算は p1-07.md に記録 |
| R4: PR #1 自身の CI 初回 fail | ローカル smoke で YAML/JSON/freshness-check ロジックを事前確認、push 直後に green 確認 |
| R5: Round 2 で P0/P1 新規発生 | 3 周目修正に入らず統合判断 / user 確認 |
| R6: archive CLI の next-session.md unstaged | PR #2 で `git add` 明示 |
| R7: `.dev.vars` 衝突 | コメントで「Wrangler local dev secrets」と用途明示済み |

## 停止条件

- レビュー修正 2 周超え
- public/private 課金発生確認時
- markdown-link-check が外部 URL の rate limit で繰り返し false positive
- secret 値混入の疑い
