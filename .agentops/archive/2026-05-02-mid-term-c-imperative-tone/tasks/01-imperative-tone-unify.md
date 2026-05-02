# Task 01: 文末曖昧表現の命令形化 + Phase 4 役割分離 (4-α 同系列独立 + 4-β cross-review)

task-id: 01-imperative-tone-unify
status: approved
created_at: 2026-05-02
approved_at: 2026-05-02T14:53:00+09:00
timezone: Asia/Tokyo
parent_plan: 2026-05-02-mid-term-c-imperative-tone

- 親 plan: `.agentops/plans/current.md` (`2026-05-02-mid-term-c-imperative-tone`)
- 状態: 進行中 (Phase 0/1/1.5/2 完了、Phase 3 実装完了、Phase 4 review 待ち)
- 担当: orchestrator (Claude) + research_fast + Codex (review_frontier / coding_frontier) + Claude (review_frontier internal)
- スコープ: Phase 1〜5 完結 (Phase 6 は別作業)
- user 承認: 2026-05-02 ExitPlanMode で承認済

## 実行内容

### A-1: 文末曖昧表現の命令形化 (採用候補 ~9 件)

`/home/otaku/agentops/AGENTS.md` / `CLAUDE.md` / `docs/10-cli-wrapper.md` / `docs/11-monitoring-cli.md` / `docs/12-harness-engineering.md` / `docs/13-design-evaluation.md` / `docs/18-notification-strategy.md` / `templates/claude/CLAUDE.md` / `templates/codex/AGENTS.md` の対応行を断定形 / 命令形に書き換える。

置換規則 (詳細は `~/.claude/plans/plan-c-cryptic-pixel.md` Phase 3 §作業 参照):
- `〜してください` → `〜する` / `〜せよ`
- `〜することがある` (命令文脈) → 削除 / 「〜する」「〜する場合は次の挙動になる」
- `〜してもよい` → 「〜する」「〜してはならない」、または許可ニュアンス維持
- `〜推奨する` → 規範強度を変えない範囲で書き換え

**規範強度変更ガード**: 「推奨」「望ましい」「のがよい」を命令形に強度を上げる置換は **しない** (意味変更非混入)。

### A-2: 5 工程フロー Phase 4 役割分離 (4-α 同系列独立実装レビュー + 4-β cross-review 別系列)

以下のファイルで「Phase 4 担当 = Codex review_frontier 単独」記述を **「4-α: 同系列独立実装レビュー (cross-review ではない) + 4-β: cross-review (別系列、本来の cross 観点)」** に修正:
- `rules/model-routing.md` (5 工程フロー表 Phase 4 行)
- `rules/auto-merge-permission.md` (許諾条件 §2、4-α / 4-β 両者通過の明示)
- `AGENTS.md` (AI auto-merge 許諾節 / 設計段階 cross-review)
- `CLAUDE.md` (Claude 固有メモ)
- `docs/03-dbc-and-quality-gates.md`
- `docs/04-model-routing.md`
- `docs/05-review-policy.md` (Phase 4 役割分離定義の集約先)

**注**: `rules/review-policy.md` は agentops repo に **存在しない** ため対象外。新規 rule 追加は本 plan の非目的。Phase 4 の役割分離定義は `docs/05-review-policy.md` に集約する。4-α (cross-review **ではない** 同系列独立検証) と 4-β (cross-review = 別系列) を明確に分離する。

各ファイルで触る範囲は **Phase 4 役割分離記述のみ** に限定 (中期 D scope を侵食しない、kind 分岐や他構造に踏み込まない)。

## 検証

### A-1 検証 (grep)
```sh
cd /home/otaku/agentops
grep -nE '(してください|下さい|してもよい|してもいい|しても良い|することがある|場合がある|推奨する|推奨される|望ましい|べきです|べきだ|したほうが|のが良い|のがよい|かもしれない|でしょう|だろう|ましょう|ことができる|可能性がある|と良い|と思う|考えられる)' \
  AGENTS.md CLAUDE.md rules/*.md docs/*.md templates/claude/CLAUDE.md templates/codex/AGENTS.md templates/claude/skill/agentops-localize/SKILL.md skills/catalog.md
```
→ 採用リスト分が消滅、除外リスト分のみ残る。

### A-2 検証 (grep)
```sh
cd /home/otaku/agentops
grep -nE '(Phase 4|工程 4|実装レビュー)' rules/model-routing.md docs/04-model-routing.md docs/05-review-policy.md
grep -nE 'cross-review' rules/model-routing.md rules/auto-merge-permission.md AGENTS.md CLAUDE.md docs/*.md
```
→ Phase 4 が 4-α / 4-β の役割分離構成として一貫記述、cross-review 定義が「実装担当と別系列の review_frontier」を明示。

### CI green
- `python3 -m compileall tools` 等の自己検証
- markdown-link-check / yamllint 等の CI が導入済なら全 job

### 4-α / 4-β 両レビュー通過
- Phase 4-α (Codex review_frontier) + Phase 4-β (Claude review_frontier internal) の双方で P0 / P1 = 0 件、または反映済

## 停止条件

- レビュー修正 2 周超 → user 確認
- 採用判断で意味変更を伴う候補が 3 件以上発見 → user 確認
- 中期 D 想定範囲との conflict 発見 → user 確認
- secret / 本番 / 課金 / 外部公開 / 破壊的操作 → user 確認
- 観察事実と現状の食い違い発見 → user 確認

## 次セッションへ残すこと

本 task が 1 セッションで完了しなかった場合、未完了 Phase と残作業を明示し、`.agentops/prompts/next-session.md` で次番号 task を指す。Phase 6 は本 task の完了条件に含めない (別作業として `prompts/next-session.md` で別 plan 化を案内する)。

## 参照

- 真ソース plan: `~/.claude/plans/plan-c-cryptic-pixel.md`
- 親 handoff: `~/.claude/.agentops/handoffs/2026-05-02-mid-term-cde-plan-followup.md`
- 関連 rule: `~/.claude/rules/model-routing.md` / `auto-merge-permission.md` / `review-policy.md`
