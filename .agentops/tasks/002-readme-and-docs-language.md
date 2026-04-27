# 002 readme and docs language

parent_plan: 2026-04-27-agentops-reference-kit-refactor
status: pending

## 実行内容

- README と主要 docs の語彙を見直す。
- 「正本」「投影物」「機械的に反映」という印象を弱める。
- 「参照資料」「判断材料」「反映候補」「各 CLI エージェントが採否を判断する」という表現へ寄せる。
- `docs/` は現役参照資料、`decisions/` は判断履歴として分ける。

## 完了条件

- README の位置づけが「設計思想・判断材料・テンプレート・補助ツールの管理リポジトリ」になっている。
- グローバル設定反映プロンプトが、調査、差分整理、計画提示、承認後反映に集中している。
- 主要 docs から強すぎる「正本」「投影物」表現が整理されている。

## 検証

- `rg "正本|投影物|機械的" README.md docs rules workflows config` を確認する。
- `git diff --check`

## 停止条件

- 語彙変更だけでなく構造変更が必要になり、ユーザー判断が必要になる。
- 既存スクリプトや docs 参照と矛盾する。
