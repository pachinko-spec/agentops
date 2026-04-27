# 003 structure refactor plan

parent_plan: 2026-04-27-agentops-reference-kit-refactor
status: completed

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

## 完了時の後処理

- 完了した task は `.agentops/tasks/` 直下に残さず、対応する `.agentops/archive/<parent_plan>/tasks/` へ移す。
- 完了した `.agentops/task-plans/current.md` は `.agentops/archive/<parent_plan>/task-plans/` へ移し、次に着手する task に合わせて新しい `current.md` を作る。
- `.agentops/prompts/next-session.md` は、次に読むべき `current.md` と task を指す内容へ更新し、古い plan や完了済み task を入口にしない。
- `scripts/agentops-watch check --projects config/projects.yml` で、完了済み task が未完了件数に残っていないことを確認する。

## 停止条件

- 既存の `skills/` や `workflows/` を削ると、ユーザーが期待する参照資料が失われる。
- 移動先ディレクトリ構成に合意がない。

## 完了メモ

- `rules/`、`skills/`、`workflows/` の全ファイルを棚卸しした。
- README、docs、config、workflows、skills、`.agentops` からの参照関係を確認した。
- `docs/15-reference-kit-structure.md` に、現役参照資料、`examples/` 候補、`templates/` 候補、`checklists/` 候補、archive 候補を分類案として記録した。
- 「正本」「投影物」などの強い語彙が残る箇所を、構造整理と合わせて扱う候補として記録した。
- `rules/`、`skills/`、`workflows/` 本体の移動、削除、archive 化は実施していない。
