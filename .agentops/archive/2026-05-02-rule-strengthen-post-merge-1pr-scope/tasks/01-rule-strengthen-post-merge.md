# task: 01 — agentops 雛形リポの post-merge 1 PR scope 完結原則 + cross-review タイミング整理

親 plan: `plans/current.md` (2026-05-02-rule-strengthen-post-merge-1pr-scope)

## 観察事実 (着手時)

- `~/.claude/rules/auto-merge-permission.md` / `~/.claude/rules/session-record-and-handoff.md`
  は agentops repo 内に **実体なし** (catalog 未掲載 = 漏れた雛形)
- `/home/otaku/agentops/rules/model-routing.md` は template-source として存在
- `/home/otaku/agentops/docs/03-dbc-and-quality-gates.md` L83-90 にマージ条件節、
  post-merge 手順専用節なし、frontmatter `applies-to: global`
- `/home/otaku/agentops/docs/04-model-routing.md` L80-95 に 5 工程フロー節 (L92 で
  「工程 2 設計段階の `kind: design` → user 確認再取得」)
- `/home/otaku/agentops/AGENTS.md` に「設計段階 cross-review (高リスク plan で必須)」
  記述 (「実装着手前」の解釈が曖昧)
- `~/.claude/hooks/_common.py` L226-227 の `inspect_agentops` が `"before finalizing"`
  block message を emit (同セッション内整理意図)
- `~/.claude/hooks/stop.py` L65 で `"decision": "block"` を emit
- 設計段階 cross-review (Codex review_frontier) 実施済、run-id `20260502T023326+0900-codex-review_frontier`、
  P0=0 / P1=3 (F1 archive timing / F2 Phase 4 縮退 / F3 特殊運用判定基準衝突) を反映済

## 前提条件

- 作業ブランチ `claude/rule-strengthen-post-merge-1pr-scope` で作業中
- 親 plan は user 承認済 (auto mode)
- 設計段階 cross-review (Phase 1.5) 通過済 (P0/P1=0)

## 不変条件

- `~/.claude/*` (グローバル設定) は本 PR で **触らない** (PR scope 外、別作業)
- secret 値は diff / log / commit / PR / handoff に書かない
- 既存 `rules/model-routing.md` L43-67 (5 工程フロー表 / kind 分岐) は **触らない**、
  新節として後ろに追加する (Plan agent P1-2 反映)
- `~/.claude/hooks/*` は触らない (rule 側で hook 整合説明を追記するのみ)

## 完了条件 (DbC)

1. `/home/otaku/agentops/rules/auto-merge-permission.md` を新規作成、frontmatter
   (`name` / `description` / `applies-to: global`) + 1 PR scope 完結原則 + 例外条項
   3 要件 を含む
2. `/home/otaku/agentops/rules/session-record-and-handoff.md` を新規作成、frontmatter
   + next-session.md 同セッション内更新原則 + hook 整合説明 を含む
3. `/home/otaku/agentops/docs/03-dbc-and-quality-gates.md` ファイル末尾に新節
   `## post-merge 手順 (1 PR scope 完結原則)` を append
4. `/home/otaku/agentops/rules/catalog.md` に新規 2 entry (auto-merge-permission /
   session-record-and-handoff) を既存列構成に揃えて追加
5. `/home/otaku/agentops/rules/model-routing.md` の既存 5 工程フロー節の後に
   新節 3 つ (`## Plan agent と cross-review の区別` / `## 工程 2 のタイミング` /
   `## plan mode 制約`) を追加。既存節 (L43-67) は触らない
6. `/home/otaku/agentops/docs/04-model-routing.md` L92 「工程 2 設計段階の
   `kind: design`」記述を「大幅乖離時のみ user 確認再取得、軽微変更は orchestrator
   判断」に明確化、L95 後に通常運用 / 特殊運用判定基準への参照追加
7. `/home/otaku/agentops/AGENTS.md` の「設計段階 cross-review (高リスク plan で
   必須)」記述に通常運用 (user 承認後) と特殊運用 (user 提示前) の境界を明記、
   「実装着手前」を「user 承認後 / 実装着手前」と明示化
8. Phase 4.5 で `scripts/agentops archive task --task-id 01-rule-strengthen-post-merge --dry-run`
   実行 → 確認後本番実行、`scripts/agentops archive plan --plan-id 2026-05-02-rule-strengthen-post-merge-1pr-scope --summary <text>` 実行
9. 上記 7 ファイル + Phase 4.5 archive 結果を 1 commit にまとめ、PR 作成
10. 実装後 cross-review (Phase 6、Codex review_frontier) で P0/P1=0
11. CI green、AI auto-merge 許諾条件 6 を全て満たす

## 禁止事項

- `~/.claude/*` の編集 (PR scope 外)
- `~/.claude/hooks/*` の編集
- 既存 `rules/model-routing.md` L43-67 の改変 (新節追加のみ)
- `archive task` を merge 後 (Phase 8) に実施すること (Codex F1 反映: 1 PR scope 違反になる)
- secret 値の diff / log / commit / PR / handoff への混入

## 停止条件

- cross-review 所見に P0/P1 が反映困難 (3 周目到達 → user 確認)
- 既存 `rules/catalog.md` 列構成が Plan agent / Codex 報告と異なり追記不能
- 新規 frontmatter 形式が既存 `rules/model-routing.md` と整合しない
- archive 実行で merge 後 dirty diff が残る (= 1 PR scope 違反、Codex F1 該当)
- hook 仕様 (L226-227) と新規 rule 記述が齟齬する

## 検証手順

1. `git diff --stat main..HEAD` で変更ファイル数 = 修正対象 7 + Phase 4.5 archive 関連
2. `find /home/otaku/agentops/rules /home/otaku/agentops/docs -name '*.md'` で新規ファイル確認
3. 各新規 / 編集ファイルの frontmatter / link 整合性を Read で目視確認
4. `python3 -m compileall /home/otaku/agentops/tools` (Codex F1 で archive スクリプトに変更ないことの間接確認、本 task では tools/ を触らない想定)
5. `markdown-link-check` 等の CI 通過確認 (PR 作成後)
6. Phase 6 cross-review run log で P0/P1=0 確認
