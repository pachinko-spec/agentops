# 003 structure refactor plan

parent_plan: 2026-04-27-agentops-reference-kit-refactor
status: pending

## 実行内容

- `rules/`、`skills/`、`workflows/` を残す、縮小する、移す、archive する方針を決める。
- `examples/`、`templates/`、`checklists/` への再編案を作る。
- 大量の見本がグローバル設定時のノイズにならない構成を設計する。

## 完了条件

- `rules/`、`skills/`、`workflows/` の扱いについて、少なくとも次の分類が決まっている。
  - 現役参照資料として残すもの。
  - 最小見本として `examples/` に移すもの。
  - CLI 用テンプレートとして `templates/` に移すもの。
  - チェックリストとして `checklists/` に移すもの。
  - archive 候補。

## 検証

- 既存ファイル一覧と参照関係を `rg` で確認する。
- 移動や削除前に、影響範囲を計画として提示する。

## 停止条件

- 既存の `skills/` や `workflows/` を削ると、ユーザーが期待する参照資料が失われる。
- 移動先ディレクトリ構成に合意がない。
