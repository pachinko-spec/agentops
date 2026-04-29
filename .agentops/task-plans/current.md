# task-plan: task 09 (P1-08) — AGENTS.md 一本化、CLAUDE.md は @AGENTS.md import + 差分のみ

> 親 plan: `2026-04-28-design-review-p0-p1`
> 親 task: `.agentops/tasks/09-p1-08-agents-md-unify.md`
> session: 2026-04-29
> branch: `claude/design-review-impl-p1-08`
> 想定 PR 構成: 実装 PR + archive ドッグフード PR の 2 PR (本 task は plan 完了 task のため archive ドッグフード PR で plan archive を実行)

---

## 着手前の仕様確認 (task 09 §実行内容 1 必須)

### Claude Code: `@AGENTS.md` import 仕様 (`code.claude.com/docs/en/memory`)

公式 docs `### AGENTS.md` セクションより:

> Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses `AGENTS.md` for other coding agents, create a `CLAUDE.md` that imports it so both tools read the same instructions without duplicating them. You can also add Claude-specific instructions below the import. Claude loads the imported file at session start, then appends the rest:
>
> ```markdown CLAUDE.md
> @AGENTS.md
>
> ## Claude Code
>
> Use plan mode for changes under `src/billing/`.
> ```

import 仕様 (`### Import additional files`):

- `@path/to/import` 構文。相対パスは「import を含むファイル基準」(working directory ではない)
- 再帰的 import 可、最大 5 hops
- 初回 import 時に approval dialog (decline すると永続的に disable)

→ **本 task のパターン (CLAUDE.md = `@AGENTS.md` + Claude 固有差分) は公式推奨そのもの**。互換性問題なし。

### Codex CLI: `AGENTS.md` 連結読込仕様 (`developers.openai.com/codex/guides/agents-md`)

3 スコープ:

1. **Global**: `~/.codex/AGENTS.md` (または `AGENTS.override.md`、`CODEX_HOME` 環境変数優先)
2. **Project**: project root から cwd まで walk down、各 directory で `AGENTS.override.md` → `AGENTS.md` → `project_doc_fallback_filenames` の順
3. **Current/nested**: 各 directory の AGENTS.md/AGENTS.override.md を確認

挙動:

- root 側から順に concat、blank line で join
- `Files closer to your current directory override earlier guidance because they appear later in the combined prompt.`
- 各 directory 1 ファイルのみ
- `project_doc_max_bytes` (default 32 KiB) で停止
- 空ファイルはスキップ、cwd で停止

→ 本 task のパターン (project root に `AGENTS.md` 真ソース) は仕様通り。`AGENTS.override.md` は本 task で導入しない（必要時に user 個別運用）。

### 互換性結論

両 CLI で `AGENTS.md` 真ソース化 + `CLAUDE.md` の `@AGENTS.md` import + Claude 固有差分 のパターンが成立。**本 task を保留する理由なし**。

---

## フェーズ別実行計画

### Phase 1: 着手前確認の記録

| step | 内容 | 状態 |
|---|---|---|
| 1.1 | `.agentops/reviews/p1-08.md` 新規（着手前仕様確認結果） | ✅ 完了 (本 task-plan §着手前の仕様確認 と整合) |
| 1.2 | `.agentops/task-plans/current.md` 新規（本ファイル） | ✅ 完了 |

### Phase 2: AGENTS.md 真ソース化（≤ 200 行）

| step | 内容 | 状態 |
|---|---|---|
| 2.1 | `AGENTS.md` 1 行目 / intro を中立化（Claude Code / Codex 並列） | ⏳ |
| 2.2 | §記録先: `~/.claude/` / `~/.codex/` を並列記述 | ⏳ |
| 2.3 | §global 設定を触る作業: 章名を中立化 (`~/.codex` を触る作業` → `global 設定 (~/.claude/ / ~/.codex/) を触る作業`)、CLI specific 確認方法を並列記述 | ⏳ |
| 2.4 | §Git と作業ブランチ: branch prefix を「使用中 CLI: Claude `claude/`、Codex `codex/`」と並列記述 | ⏳ |
| 2.5 | §AI auto-merge: 主 orchestrator を「Claude Code / Codex いずれの場合も」 | ⏳ |

### Phase 3: CLAUDE.md 短縮版（≤ 50 行）

| step | 内容 | 状態 |
|---|---|---|
| 3.1 | 1 行目に `@AGENTS.md` を配置（公式推奨）| ⏳ |
| 3.2 | Claude Code 固有差分セクション (パス・確認コマンド・branch prefix のみ) を追記 | ⏳ |
| 3.3 | 行数確認 ≤ 50 | ⏳ |

### Phase 4: ローカル smoke

| step | 内容 |
|---|---|
| 4.1 | `wc -l AGENTS.md CLAUDE.md` で行数 ≤ 200 / ≤ 50 確認 |
| 4.2 | `python3 -m compileall tools` exit 0 |
| 4.3 | `python3 -m unittest discover -s tests` 12/12 pass |
| 4.4 | `git diff --check` clean |
| 4.5 | `grep -c "^## " AGENTS.md` で章数確認、CLAUDE.md は import + 1-2 章のみ |

### Phase 5: PR 作成 → CI green 確認

GitHub Actions の 4 job (actionlint / yamllint / markdown-link-check / freshness-check) が全 pass。markdown-link-check は AGENTS.md / CLAUDE.md 内の link を検証。

### Phase 6: Codex cross-review 3 Round

`scripts/agentops delegate --to codex --role review_frontier --effort high --input AGENTS.md --run-id <ts>+0900-p1-08-r1` で Round 1。観点:

1. AGENTS.md が Codex 真ソースとして必要十分（≤ 200 行、≤ 32 KiB project_doc_max_bytes）
2. CLAUDE.md の `@AGENTS.md` import + Claude 固有差分が公式 docs パターンに整合
3. 共通章を AGENTS.md に集約、CLI 固有名詞を中立化（並列記述または使用中 CLI 表記）
4. AI auto-merge 主 orchestrator が「Claude Code / Codex いずれの場合も」になっているか
5. config/claude/CLAUDE.md / config/codex/AGENTS.md の対称運用維持（本 task では touch しない）が DbC §触ってよい範囲 から逸脱しないか
6. CLAUDE.md ≤ 50 行 / AGENTS.md ≤ 200 行 目安遵守
7. 既存の章立て（位置づけ / 記録先 / global / Git / 完了 / 停止 / auto-merge）が両 CLI で意味的に同等か
8. branch prefix 「Claude: `claude/`、Codex: `codex/`」記述で本 task の implementation branch (`claude/design-review-impl-p1-08`) と整合

Round 2 で clean 確認、Round 3 で `no further P0/P1`。

### Phase 7: AI auto-merge 6 件評価 → squash merge

CLAUDE.md / AGENTS.md §許諾条件を独立評価。全 OK なら `gh pr merge 50+1 --squash --delete-branch`。

### Phase 8: main 同期 + archive ドッグフード PR (plan 全体 archive)

| step | 内容 |
|---|---|
| 8.1 | `git checkout main && git fetch origin && git pull --ff-only origin main` |
| 8.2 | `git checkout -b claude/archive-task-09-p1-08-agents-md-unify-dogfood` |
| 8.3 | `scripts/agentops archive task --task-id 09-p1-08-agents-md-unify --dry-run` → 本番 |
| 8.4 | tasks/ 残ゼロ → user 確認: prompts/next-session.md 削除？ |
| 8.5 | **plan 全体完了** → `scripts/agentops archive plan --plan-id 2026-04-28-design-review-p0-p1 --summary "<text>"` で plan 全体 archive + archive/README.md table 挿入 |
| 8.6 | PR #2 作成 → self-merge → main 同期確認 |

---

## 不変条件 (task 09 §不変条件)

- AGENTS.md / CLAUDE.md の意味（プロジェクト指示の責務）を変えない
- Claude Code でも Codex でも読み込めること（両 CLI の動作確認必須 → 着手前確認で完了、Round 1 でも再確認）
- `~/.claude/CLAUDE.md` への影響は config/claude/CLAUDE.md 雛形までで、本 plan では実反映しない
- AGENTS.md ≤ 200 行 / CLAUDE.md ≤ 50 行を目安

## 触ってよい範囲

- ルート `CLAUDE.md`、`AGENTS.md`
- `.agentops/reviews/p1-08.md` 新規
- `.agentops/task-plans/current.md` 新規 (本ファイル)

## 触らない範囲（本 task でスコープ外）

- `config/claude/CLAUDE.md` / `config/codex/AGENTS.md`: グローバル雛形は `~/` から見て `@AGENTS.md` import が解決できないため、本 task の戦略 (import + 差分) が適用不可。**対称運用維持**で次 plan 検討。Codex Round で意見もらう
- `docs/00-17` 本文と既存 frontmatter
- `scripts/`、`tools/`、`templates/` 本文
- `archive/`

## 想定リスクと縮退

| ID | リスク | 縮退案 |
|---|---|---|
| R1 | `@AGENTS.md` import が初回承認 dialog で user 拒否される | この repo を新規開く ./ run で初回 dialog が出る想定。手動で承認、または事前に user に告知 |
| R2 | AGENTS.md が 200 行を超える | 中立化で実質 89 行から大きく増えないはず。並列記述で増えても ≤ 120 行想定 |
| R3 | 共通章の中立化で意味が曖昧になる | 並列記述 (Claude: X、Codex: Y) または「使用中 CLI に応じて」の 2 表現を併用 |
| R4 | config/ 雛形と root AGENTS.md の整合性 drift | 本 task ではスコープ外、handoff として記録 |
| R5 | Round 2 で P0/P1 新規発生 | 3 周目修正に入らず統合判断 / user 確認 (CLAUDE.md §停止条件) |
| R6 | archive plan CLI で archive/README.md table 挿入が手動補完必要 | task 07 (P1-06) 既知制約。CLI 出力を確認して必要なら手動補完 |

## 停止条件

- レビュー修正 2 周超え
- `@AGENTS.md` import が両 CLI で動作しない（仕様変更が判明）
- secret 値混入の疑い
- config/ 雛形変更が必要と判明（scope 拡張で user 確認）
