# 001 positioning and decision log

parent_plan: 2026-04-27-agentops-reference-kit-refactor
status: pending

## 実行内容

- agentops の位置づけを「Claude Code / Codex グローバル設定時の参照キット」へ再定義する。
- 設計判断ログの置き場所として `decisions/` を導入する。
- `decisions/README.md` と `decisions/2026-04-27-agentops-reference-kit-refactor.md` を作る。

## 完了条件

- `decisions/README.md` に、ここが毎回読む現役 docs ではなく判断履歴であることが書かれている。
- `decisions/2026-04-27-agentops-reference-kit-refactor.md` に、背景、決定、採用しないこと、影響範囲、移行方針、`.agentops` との役割分担が書かれている。

## 検証

- `rg "decisions" README.md docs .agentops decisions` で参照関係を確認する。
- 判断ログが `docs/` 直下に置かれていないことを確認する。

## 停止条件

- `decisions/` が現役 docs として誤読される構成になっている。
- 設計判断ログにユーザー未承認の方針が含まれる。
