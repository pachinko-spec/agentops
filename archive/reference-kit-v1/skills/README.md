> DEPRECATED — see /archive/reference-kit-v1/DEPRECATED.md

# skills

グローバル化候補のskill設計を置く場所です。

`skills/` は、常時読むルールではなく、特定の観点や用途で必要になった時だけ読む再利用可能な能力です。常時適用する判断基準は `rules/`、作業手順は `workflows/` に置きます。

このディレクトリのskillは、agentops保守だけでなく、`~/dev` 配下の実プロジェクトで設計、実装、レビュー、運用、収益化、docs更新、リリースに使うテンプレートとして設計します。

## 構成

- `design/`: 設計時に見る観点。要件、ドメイン、API、DB、security、privacy、cost、profitabilityなど。
- `implementation/`: 実装時に使う観点。Nuxt/Next frontend、PHP/Go backend、deployment adapter、test automationなど。
- `review/`: コード、設計、PR差分をレビューする観点。
- `docs/`: ドキュメント作成・更新の観点。
- `ops/`: 本番運用、委譲、handoff、freshness、Understand-Anythingの観点。

## 使い分け

- 作業開始時は `workflows/project-intake.md` で対象プロジェクト、スタック、デプロイ先を確認する。
- 設計時は `design/`、実装時は `implementation/`、レビュー時は `review/` を必要な分だけ読む。
- docs更新、runbook、release notesは `docs/` を使う。
- セッション継続、freshness、委譲、運用補助は `ops/` を使う。

## 運用

- 各skillは `SKILL.md` を持つ。
- frontmatterの `name` は英語の識別子でよい。
- `description` と本文は日本語を基本にする。
- 複数skillで共通する常時ルールは `rules/` に寄せる。
- プロジェクト固有のコマンド、secret、環境名、デプロイ設定はskillへ固定せず、プロジェクト側docsや `.agentops/` に置く。
