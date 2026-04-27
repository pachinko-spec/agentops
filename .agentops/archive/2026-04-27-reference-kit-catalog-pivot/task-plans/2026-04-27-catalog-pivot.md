# Task Plan: reference kit catalog pivot

plan_id: 2026-04-27-reference-kit-catalog-pivot
status: completed
created_at: 2026-04-27
completed_at: 2026-04-27
timezone: Asia/Tokyo

## 今回の目的

`rules/`、`skills/`、`workflows/` を完成品集から候補カタログへ転換し、旧実体を archive へ退避したうえで、Claude Code / Codex / `.agentops` 向けテンプレート入口を作る。

## 実行順

1. 方向転換の decision log と `.agentops` plan/task を作る。
2. 旧 `rules/`、`skills/`、`workflows/` を `archive/reference-kit-v1/` へ移す。
3. 新しい `rules/`、`skills/`、`workflows/` を README と catalog で再作成する。
4. `templates/claude/`、`templates/codex/`、`templates/agentops/` を作る。
5. README、docs、config の参照と説明を新構造へ更新する。
6. 参照検索、`git diff --check`、`scripts/agentops-watch check --projects config/projects.yml` を実行する。
7. 問題なければ commit、push、PR 作成まで行う。

## 今回は行わないこと

- 実際の `~/.claude`、`~/.codex` グローバル設定へ反映すること。
- 旧実体を削除して参照不能にすること。
- 公式 docs 未確認の CLI 固有仕様を断定すること。

## 完了結果

- 1PR で catalog pivot を実施した。
- 旧実体は削除せず `archive/reference-kit-v1/` へ退避した。
- 現役入口は候補カタログと CLI 別テンプレートに整理した。
- 完了済み plan、task-plan、task は `.agentops/archive/2026-04-27-reference-kit-catalog-pivot/` へ移す。

## 停止条件

- 参照切れが広範囲に出て、1PRで安全に直せない。
- `agentops-watch` が完了済み task を未完了として数える。
- 実グローバル設定への反映が必要になる。
