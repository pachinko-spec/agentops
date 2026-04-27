# skills

グローバル化候補のskill設計を置く場所です。

`skills/` は、常時読むルールではなく、特定の観点や用途で必要になった時だけ読む再利用可能な能力です。常時適用する判断基準は `rules/`、作業手順は `workflows/` に置きます。

## 構成

- `review/`: コード、設計、PR差分をレビューする観点。
- `design/`: 設計時に見る観点。
- `docs/`: ドキュメント作成・更新の観点。
- `ops/`: 運用、委譲、handoff、freshness、Understand-Anythingの観点。

## 運用

- 各skillは `SKILL.md` を持つ。
- frontmatterの `name` は英語の識別子でよい。
- `description` と本文は日本語を基本にする。
- 複数skillで共通する常時ルールは `rules/` に寄せる。
