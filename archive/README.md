# archive

参照キット本体の旧構造や、現役入口から外した見本を置く場所です。

`.agentops/archive/` は plan、task、run などの作業履歴専用です。この `archive/` はリポジトリ本体の資料を退避する場所として使います。

## 現在の内容

- `reference-kit-v1/`: `rules/`、`skills/`、`workflows/` を具体ファイル群として管理していた旧構造。

## 方針

- 旧資料は削除せず、必要に応じて参照できる形で残す。
- 現役の `rules/`、`skills/`、`workflows/` からは、完成品ではなく候補カタログとして参照する。
- 旧資料を復活させる場合は、公式 docs と実環境を確認し、現役カタログまたは `templates/` へ取り込む。
