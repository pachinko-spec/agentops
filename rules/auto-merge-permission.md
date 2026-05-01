---
name: auto-merge-permission
description: AI auto-merge 許諾条件 6 個 (全 AND)、停止条件、必須手順 (agentops repo / 他プロジェクト分岐)、適用範囲、取消条件、post-merge 1 PR scope 完結原則と例外条項。グローバル既定として全プロジェクト適用。
applies-to: global
---

# AI auto-merge 許諾（durable instructions）

以下の **許諾条件をすべて満たした PR に限り**、主 orchestrator（Claude Code / Codex いずれの場合も）が `gh pr merge --squash --delete-branch` で自動マージしてよい。これは [`docs/03`](file:///home/otaku/agentops/docs/03-dbc-and-quality-gates.md) §マージ条件の「ルール上許可された AI がマージしてよい状態」をグローバル既定として定義するもの。

## 許諾条件（全て AND）

1. **DbC 完了**: 該当 PR がカバーする `.agentops/tasks/<NN>-*.md` の DbC 完了条件をすべて満たしている。
2. **別系列 frontier cross-review 通過**: 主 orchestrator とは異なる系列の frontier reviewer で `scripts/agentops delegate --to <reviewer> --role review_frontier --effort high --input <該当ファイル>` を実施済み、所見に **P0 / P1 が 0 件、または反映済み**。run 記録が `.agentops/runs/<run_id>/` に残っている。reviewer 選定は主 orchestrator と別系列（Anthropic ↔ OpenAI）。
   - reviewer は修正指摘ごとに `kind: mechanical | design` ラベルを付与する。`kind: mechanical` (patch / 行番号 / 具体書き換え提示) は Claude が直接 patch、`kind: design` (抽象指摘) は Codex (run A) に再委譲。修正したらループ +1、修正者問わず。3 周目到達 → kind 不問で user 確認 (本許諾発動せず)。kind ラベル無し → 保守的に `design` 扱い。詳細は `rules/model-routing.md` (雛形) / `~/.claude/rules/model-routing.md` (反映) の「## 設計 → 設計レビュー → 実装 → 実装レビュー → 最終判断 (5 工程フロー)」節。
3. **CI green**: GitHub Actions の fail 系 job が全 green（actionlint / yamllint / markdown-link-check 等が導入済みなら全 job、未導入なら自己検証で `python3 -m compileall` 等が exit 0）。
4. **観察事実食い違いなし**: 着手時に裏取りした観察事実と現状に新たな食い違いが発生していない。
5. **PR スコープ単一**: 該当 task が要求する変更だけを含み、スコープ外リファクタを含まない。
6. **secret 未混入**: diff、commit message、PR 本文、run log に secret 値（API key、token、credential、本番 URL の認証情報）が混入していない。

## 停止条件（auto-merge せず必ず user 確認）

- レビュー修正が 2 周を超えそう、または 3 周目に入った。
- `git pull --ff-only origin main` 失敗、または CI fail / 同期不整合が発生。
- 公式仕様確認が必要（例: AAIF `@AGENTS.md` import、GitHub Actions 課金、MCP transport の deprecation）。
- 観察事実と現状の食い違い、L コスト超過、半日 → 1 日見積もりを大幅超過。
- secret / 本番 / 課金 / 外部公開 / 破壊的操作。
- task の `停止条件` 節に該当する事象が発生。
- cross-review reviewer の所見に P0 / P1 が残っている、または採否判断が分かれた。

## auto-merge 後の必須手順

**1 PR scope 完結原則**: post-merge 整理 (archive 移動 / `plans/current.md` 更新 / `task-plans/current.md` archive / `prompts/next-session.md` 更新) は **merge 対象 PR の scope 内で完結** させる。merge 前 commit に含めるのが原則。

- 同セッション内整理は `~/.claude/hooks/_common.py` の `inspect_agentops` block (Stop 時に completed task 残存を検知して `"before finalizing"` block message を emit) と整合する設計。別 chore PR への分離は hook 意図と逆向きとなる。
- 別 chore PR への分離は **user 明示許可がある場合のみ** 許容。
- **「user 明示許可」の構成要件 (全て AND)**:
  1. 同セッション内で user に scope 分離理由を提示し、明示的な口頭承認を得る
  2. run log / handoff / 元 PR 本文に分離理由と user 承認 (日時 / 理由 / 想定影響) を残す
  3. 別 chore PR の commit message と PR 本文にも分離理由と元 PR への参照を記載
- 例外発動の典型例: archive 規模が大きすぎて diff が読めない (例: 10 task 以上の同時 archive)、scope 違いの整理を一括で行う、merge 後に判明した観察事実で追加整理が必要になった等

merge 完了直後の必須手順は **「main 同期確認」と「archive 状態の read-only 確認」のみ** とし、archive 移動 / plans 更新 / next-session.md 更新の **実装変更そのもの** は merge 前 commit に含めること:

1. `git checkout main && git fetch origin && git pull --ff-only origin main` で main 同期確認。
2. **archive 状態の read-only 確認** (実装は merge 前 commit に含めること):
   - **agentops repo（`/home/otaku/agentops`）の場合**: `scripts/agentops archive task --task-id <basename> --dry-run` で内容を確認した上で本番実行 → **これらは Phase 4.5 (merge 前) で実施済み**。merge 後は `ls .agentops/archive/<plan-id>/tasks/` と `cat .agentops/prompts/next-session.md` で結果確認のみ。
   - **他プロジェクトの場合**: 同様に `git mv` を merge 前 commit に含める。merge 後は移動済み確認のみ。
3. `git status --short` で merge 後 dirty diff が無いこと確認。
4. **plan 全体完了時のみ**:
   - agentops repo: `scripts/agentops archive plan --plan-id <id> --summary <text>` も Phase 4.5 (merge 前) で実施済み。merge 後は `archive/README.md` と `archive/<plan-id>/` の存在確認のみ。
   - 他プロジェクト: 同様に手動移動を merge 前 commit に含める。
5. 上記が完了するまで次 task に着手しない。

## 適用範囲

- 本許諾は **全プロジェクトで有効**（グローバル既定）。
- ただし **プロジェクト固有の `CLAUDE.md` / `AGENTS.md` / `.agentops/` で `auto-merge 不可` を明示している場合**は、そちらを優先し本許諾を発動しない。
- 本許諾は `main` への squash merge のみ対象。force push、`git reset`、ブランチ削除（PR マージ時の自動削除は許諾範囲）以外の破壊的操作は対象外。
- 1 セッション内で連続 auto-merge する場合も、各 PR ごとに上記許諾条件を独立に評価する。

## 取消条件

- ユーザーが「auto-merge 停止」「全件 user 確認に戻す」等を明示した場合、即時取消し。
- 直近の auto-merge で問題が発覚した場合（事故、誤マージ、回帰）は次セッション以降を user 確認に戻す。
