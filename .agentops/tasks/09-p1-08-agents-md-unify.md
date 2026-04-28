# task 09 — P1-08: AGENTS.md 一本化、CLAUDE.md は @AGENTS.md import + 差分のみ

> 親 plan: `2026-04-28-design-review-p0-p1`  
> 提案 ID: P1-08  
> 優先度: P1  
> 状態: 未着手  
> 想定コスト: M（半日）  
> 想定 PR ブランチ: `claude/design-review-impl-p1-08`  
> 依存: task 02（glossary）/ 04（フロントマター）/ 05（DbC 集約）/ 06（逆参照）すべて完了後（最終仕上げ）

---

## 前提条件

- 触ってよい範囲: ルート `CLAUDE.md`、`AGENTS.md`、`config/claude/CLAUDE.md`、`config/codex/AGENTS.md`、`README.md`（CLAUDE.md / AGENTS.md の関係を更新する場合）。
- 触らない範囲: docs 本文、`scripts/`、`tools/`、`templates/` の本文、`archive/`。
- 事前確認:
  - `code.claude.com/docs/en/memory` で `@AGENTS.md` import 構文の現在仕様を Context7 / WebFetch で再確認。
  - Codex CLI の `~/.codex/AGENTS.md` 連結読込仕様、`AGENTS.override.md` 優先動作を `developers.openai.com/codex/guides/agents-md` で再確認。
  - 既存 47 行 / 47 行の章立て対称運用を base に、Claude 固有差分を抽出。
- 業界出典: AAIF agents.md、`code.claude.com/docs/en/memory`、code.claude.com / developers.openai.com の最新 docs。

## 不変条件

- AGENTS.md / CLAUDE.md の意味（プロジェクト指示の責務）を変えない。
- Claude Code でも Codex でも読み込めること（両 CLI の動作確認必須）。
- `~/.claude/CLAUDE.md` への影響は config/claude/CLAUDE.md 雛形までで、本 plan では実反映しない（user グローバルは別 plan）。
- **AGENTS.md ≤ 200 行 / CLAUDE.md ≤ 50 行を目安とする**。Claude の `@AGENTS.md` import は context 共有なので CLAUDE.md だけ短縮しても context 削減にならない点に留意（Codex cross-review P2-4 反映）。

## 実行内容

1. **着手前の仕様確認**（着手日に必ず実施、結果を `.agentops/reviews/p1-08.md` に記録）:
   - Claude Code: `@AGENTS.md` import が CLAUDE.md で機能するか公式 docs 再確認。
   - Codex: `~/.codex/AGENTS.md` の global → project root → cwd 連結読込、`AGENTS.override.md` 優先の現在仕様再確認。
   - 互換問題があれば本 task を保留し、user に対称運用維持の妥当性を確認。
2. `AGENTS.md` を真ソース化。
   - 現状の章立てを基本維持。
   - Codex 固有差分（`~/.codex` パス、Codex CLI 名、`AGENTS.override.md`、sandbox_mode、approval_policy 等）は別セクション「Codex 固有」に分離。
   - 共通章（agentops の位置づけ、記録先、`~/.claude` を触る作業の方針、Git 運用、完了/停止条件）はそのまま。
3. `CLAUDE.md` を短縮版にする。
   ```md
   # agentops プロジェクト指示 (Claude Code 向け)

   このファイルは AGENTS.md を真ソースとして読み込む。

   @AGENTS.md

   ## Claude Code 固有差分
   - パス: `~/.claude/CLAUDE.md`、`~/.claude/skills/`、`~/.claude/agents/`、`~/.claude/plugins/`
   - CLI 名: `claude`
   - Auto memory: `~/.claude/projects/<project-id>/memory/`
   - Skills / Plugins / marketplace: code.claude.com/docs/en/skills, plugins
   ```
   目標は < 50 行。
4. `config/claude/CLAUDE.md` テンプレも同方針で短縮版にする。`config/codex/AGENTS.md` テンプレを真ソース化。
5. `README.md` で CLAUDE.md / AGENTS.md の関係を解説している箇所があれば更新。

## 完了条件

- `AGENTS.md` が真ソースとして十分（Codex 単独で読んで作業できる）、≤ 200 行。
- `CLAUDE.md` が `@AGENTS.md` import + Claude 固有差分のみ、≤ 50 行。
- 両 CLI で実際に読み込めることを動作確認（Claude Code は `/memory` で確認、Codex は `codex` 起動時に AGENTS.md がロードされる確認）。
- `config/claude/CLAUDE.md` / `config/codex/AGENTS.md` テンプレも整合。
- Codex cross-review 完了、所見反映済み。
- PR が main にマージされ、ローカル main が同期。
- 本 task のマージで本 plan の親 task 9 件すべてが完了する。

## 検証

- `wc -l CLAUDE.md AGENTS.md`（CLAUDE.md ≤ 50 行、AGENTS.md ≤ 200 行）
- Claude Code で `/memory` を実行し、AGENTS.md の内容が import されて読まれていることを確認（ユーザーに依頼）
- Codex CLI で起動し、AGENTS.md が読まれていることを確認
- `rg -n "^@AGENTS.md" CLAUDE.md`
- `scripts/agentops delegate --to codex --role review_frontier --effort high --input AGENTS.md`
- 結果を `.agentops/runs/<timestamp>-p1-08/` に保存、所見を `.agentops/reviews/p1-08.md` に転記。

## 禁止事項

- main 直 push。
- AGENTS.md / CLAUDE.md の意味変更。
- `~/.claude/CLAUDE.md` への実反映（本 task 範囲外）。
- 章立てを大きく変えるリファクタ（共通章維持）。

## 完了時の後処理

- 本ファイルを `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/09-p1-08-agents-md-unify.md` へ移す（task 07 で完成した `agentops archive` 経由）。
- 本 task のマージ後、plan / task-plan / tasks / reviews / runs を `.agentops/archive/2026-04-28-design-review-p0-p1/` 配下へまとめて移動（`scripts/agentops archive --plan-id 2026-04-28-design-review-p0-p1 --summary "P0+P1 改善 9 件マージ完了"`）。
- `.agentops/archive/README.md` への追記が自動で行われていることを確認。
- `prompts/next-session.md` を削除（残作業なし）。
- 主 orchestrator が plan 全体の最終レビューも Codex に委譲し、所見反映後に plan 完了宣言。
- PR マージ後 main 同期確認。

## 停止条件

- `@AGENTS.md` import が Claude Code 公式仕様で機能しないことが判明した場合 → import せず symlink / include script の代替を検討。それでも不可なら本 task を見送り、対称運用を維持して plan の他 8 件で完了とする（user 確認）。
- AGENTS.md 真ソース化で Codex 側の動作が破壊される場合 → 直前状態へロールバックし user 確認。
- レビュー修正 2 周超え。

## 次セッションへ残すこと

- `~/.claude/CLAUDE.md` への実反映（user グローバル更新）は別 plan で扱う。本 task のマージ後 `handoffs/` に新規ファイル `2026-MM-DD-global-claude-md-sync.md` を残す。
- P2 / P3 提案 9 件は次の plan で扱う。本 plan 完了時に handoff を残すかは plan 全体最終レビュー時に判断。
