# 01 Phase ownership rule 実装 + 雛形担当列追加 + catalog 登録

parent_plan: 2026-05-02-phase-ownership-rule
status: approved
phase: 3b
担当: Codex coding_frontier (effort high)

## 実行内容

### 既存ファイル修正

1. **`rules/model-routing.md`**: 新節 2 つ追加
   - `## 実装着手前チェックポイント (Phase 担当宣言)` : plan ファイル Phase 詳細表の担当列必須化、Phase 着手前の "Phase X — 担当: <model> (役割)" 1 行宣言、宣言なしで Edit/Write 呼ばないこと、各 Phase 着手時の **1 行宣言記録先 = `.agentops/task-plans/current.md` の Phase 着手記録欄、または `.agentops/runs/<run_id>/request.md` 冒頭** を明示
   - `## Phase ownership lint (記載漏れ専用 check)` : 観点 (担当列の有無 + 宣言欄の有無の存在確認のみ、設計の良し悪し不対象、将来の 1 行宣言遵守は対象外で hook 強化に依存)、担当 (軽量モデル: docs_agent / coding_fast / research_fast / Plan agent 内部のいずれか)、実施タイミング (plan ファイル作成直後、全 plan 共通)、結果処理 (欠落あり → orchestrator 差し戻し)、cross-review との関係 (重複させない)
   - 既存「Plan agent と cross-review の区別」節は **変更しない**

2. **`rules/catalog.md`**: 新 rule entry `phase-owner-declaration` 登録 (description / 適用範囲 / 関連 skill `phase-ownership-lint` 参照)

3. **`skills/catalog.md`**: 新 skill entry `phase-ownership-lint` 登録 (軽量モデル前提、catalog 登録のみ; 実 SKILL.md 配置は別 plan で扱う旨注記)

4. **`templates/agentops/plans/current.md`**: Phase 詳細表に **担当列を追加** (sample 値を `Codex coding_frontier (effort high)` 等で記入)

5. **`templates/agentops/tasks/task.md`**: Phase 列または Phase 担当宣言節を追加 (task 単位でも担当が分かる形)

6. **`AGENTS.md`**: 「設計段階 cross-review」記述は **変更せず**、別段落として「Phase ownership lint を全 plan で実施」を 1〜2 行追記 (両 CLI 共通記述として AGENTS.md 単独完結)

7. **`CLAUDE.md`**: 編集しない (CLAUDE.md:22 責務分離)

## 完了条件 (DbC)

- 上記 6 ファイル (rules/model-routing.md / rules/catalog.md / skills/catalog.md / templates/agentops/plans/current.md / templates/agentops/tasks/task.md / AGENTS.md) が編集済
- `python3 -m compileall tools` exit 0
- `AGENTS.md` 追記が既存「設計段階 cross-review」記述を変更していないこと
- `CLAUDE.md` に差分がないこと
- `rules/model-routing.md` 既存「Plan agent と cross-review の区別」節が変更されていないこと
- `rules/catalog.md` / `skills/catalog.md` 新 entry が他 entry の format と一致
- `templates/agentops/plans/current.md` の column 追加が markdown 構文を壊していないこと
- markdown lint / link check (CI 導入済 job が green)
- diff に secret 値が含まれていないこと

## 検証

- `python3 -m compileall tools` (exit 0)
- `git diff main...HEAD --stat` で変更ファイル一覧確認
- `grep -n "Plan agent と cross-review の区別" rules/model-routing.md` で既存節が残存
- `git diff main...HEAD -- CLAUDE.md` が空 (差分なし)

## 完了時の後処理 (Phase 4.5、merge 前 commit に含める = 1 PR scope 完結原則)

- 本 task ファイルを `.agentops/archive/2026-05-02-phase-ownership-rule/tasks/` へ `git mv`
- `.agentops/plans/current.md` と `.agentops/task-plans/current.md` も同タイミングで `archive/2026-05-02-phase-ownership-rule/` へ `git mv`
- `.agentops/archive/README.md` 時系列インデックスに本 plan-id 行を追加 (新しい順)
- `.agentops/prompts/next-session.md` を更新 (Phase 6/7/8 を指す) または不要なら削除
- 上記は **`scripts/agentops archive task --task-id 01-phase-ownership-rule-impl --dry-run` で確認後、本番実行 (`--dry-run` 無し)** で一括処理
- plan 全体完了時 (Phase 8 後) は別途 `scripts/agentops archive plan --plan-id 2026-05-02-phase-ownership-rule --summary "Phase ownership rule + 雛形担当列 + catalog 登録"` を実行

## 停止条件

- Codex 実装レビュー (Phase 4) で P0/P1 残存 (3 周目 = user 確認)
- 既存「Plan agent と cross-review の区別」節を誤って変更
- `CLAUDE.md` を誤って編集
- secret 値の混入
- markdown lint / compileall 失敗
