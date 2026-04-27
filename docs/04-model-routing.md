# モデルルーティング

モデル名は変化しやすいため、グローバル指示には固定モデル名を大量に埋め込まない。通常は論理ロールで指定し、実際のモデル名は定期更新されるカタログで管理する。

## 論理ロール

| ロール | 用途 | 推論レベル |
| --- | --- | --- |
| `orchestrator_frontier` | 複雑タスクの分解、委譲計画、統合判断、停止条件判断 | xhigh |
| `architect_frontier` | 複雑な設計、アーキテクチャ判断、ハイリスク実装方針 | high / xhigh |
| `review_frontier` | 設計レビュー、コードレビュー、セキュリティ観点、cross-review | high / xhigh |
| `coding_frontier` | 通常実装、難所の修正 | high / xhigh |
| `coding_fast` | typo、軽微修正、レビュー後の小修正 | medium / high |
| `research_fast` | コード調査、docs調査、差分整理 | medium / high |
| `docs_agent` | docs更新、PR本文、引き継ぎ整備 | medium / high |

## モデルカタログ

`config/model-catalog.yml` は、このリポジトリ専用の固定表ではなく、グローバル運用または各プロジェクトの `.agentops/` へコピーして使う雛形である。

カタログは次の二段階で読む。

1. `role` で用途を選ぶ。
2. `target_cli` が `codex` か `claude` かで、実際に使う provider / model id を選ぶ。

そのため、`architect_frontier` を特定の GPT 系列へ固定しない。Codex CLI で動かす場合は OpenAI 側の現在の model id、Claude Code CLI で動かす場合は Anthropic 側の現在の model id を、使用前に公式 docs で確認して設定する。

`model_id: null` は「未確認なのでこのまま実行に使わない」という意味である。確認済みのプロジェクトでは、プロジェクト側の `.agentops/model-catalog.yml` で上書きする。

## cross-review の選び方

cross-review は、現在の主エージェントと同じ model id をもう一度呼ぶことではない。可能なら、別 CLI、別 provider、別モデルファミリーの `review_frontier` を使う。

- 主エージェントが Codex / OpenAI 系なら、Claude Code / Anthropic 系の `review_frontier` を候補にする。
- 主エージェントが Claude Code / Anthropic 系なら、Codex / OpenAI 系の `review_frontier` を候補にする。
- 片方の CLI が使えない場合は、同一 CLI 内でも別モデルファミリー、別ロール、別コンテキストの reviewer を候補にする。
- いずれの場合も、実 model id は使用直前に公式 docs と CLI の現在仕様で確認する。

cross-review の採否、委譲範囲、指摘の採用可否はオーケストレーターが判断する。reviewer の出力は品質ゲートの入力であり、最終判断そのものではない。

## リスクによる昇格

モデルカタログは固定配車表ではなく、オーケストレーターが判断するための候補表と最低ラインである。オーケストレーターは、ユーザー指示、プロジェクトローカルの catalog、公式 docs で確認した現在の CLI 対応状況、コンテキスト量、コスト、レイテンシを見てモデルを選び直してよい。

ただし、次の領域は実装担当であっても高推論モデルへ昇格する。

- 認証、認可、セッション管理
- secret、credential、暗号化
- 決済、課金、個人情報、プライバシー
- public API 契約、互換性、データ移行、データ損失リスク
- デプロイ、インフラ、incident response
- セキュリティ修正

高リスク設計は `architect_frontier` 以上、高リスク実装は `coding_frontier` の high 以上を最低ラインにし、セキュリティ修正は xhigh と `review_frontier` による独立レビューを基本にする。`coding_fast` は typo、docs、局所的なリネームなど低リスクの機械的変更に限定する。

新規機能追加、リファクタリング、依存追加、API 契約変更、デプロイ影響、レビュー修正後は、リスクが中程度でも cross-review を検討する。採用しない場合は、既存テスト、変更範囲、コスト、時間制約などの理由を run log / PR / handoff に短く残す。

このルールは柔軟性を奪うものではなく、下限を定めるためのものとする。オーケストレーターは必要に応じて上位モデルへ上げてよい。高リスク領域を下げる場合は、ユーザー明示指示または明確な理由を run log / PR / handoff に残す。

## 運用ルール

- 設計とレビューは高推論モデルを惜しまず使う。
- 調査は軽量モデルでよいが、重要判断は公式docsまたは高推論モデルで確認する。
- 複雑な設計・実装・レビューでは、別系列、別 CLI、別モデルファミリーの frontier reviewer による cross-review を検討する。
- モデル名エラー、品質低下、公式更新を検知したら `model-catalog` を更新する。
- オーケストレーター、設計、レビュー、実装、調査、docs を同じモデルに固定しない。
- モデルカタログは短い表にし、毎回全文を読み込ませない。
