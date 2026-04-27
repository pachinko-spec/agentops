# 設計思想

このプロジェクトは、Claude Code と Codex が共通して参照するAIエージェント運用の設計思想を管理する。

## 中核原則

- AIエージェントは自律的に動くが、作業境界、品質ゲート、停止条件は明示する。
- 複雑な自律エージェントより、単純で合成可能なworkflowを優先する。
- 設計、実装、レビュー、検証、ドキュメント更新を1つの開発サイクルとして扱う。
- 1人開発者が日本語で開発しやすいことを最優先する。
- 複数モデルは競わせるのではなく、役割分担と相互レビューのために使う。
- 最終判断はメインエージェントが持つ。サブエージェントは調査、実装補助、レビュー、検証のために使う。
- AIの記憶を信用しすぎず、公式docs、GitHub、package registry、release notesなど一次情報を確認する。

## 採用する考え方

### DbC

各タスクには、前提条件、不変条件、完了条件、禁止事項、停止条件を持たせる。

### Agent Computer Interface

AIエージェントが使うCLI、ログ、ディレクトリ構成、状態ファイルは性能と安全性に直結する。CLI Wrapper、`.agentops/`、hooks、skills、workflowsは設計対象として扱う。

### 検証可能性

AIが自分の作業を検証できるように、テスト、lint、型チェック、E2E、スクリーンショット、CI結果、期待出力を明示する。

再現性が必要な作業では、task spec、setup、allowed commands、fixtures、oracle、artifact、replay条件を harness として明示する。詳細は [Harness Engineering](12-harness-engineering.md) を参照する。

### コンテキスト衛生

長い会話に失敗履歴を溜めすぎない。必要な状態は `.agentops/` の短い文書に残し、別セッション・別モデルが続きから読めるようにする。

### 時刻方針

ユーザーは日本語話者で、運用タイムゾーンは `Asia/Tokyo` とする。スクリプト、ログ、run id、監視レポート、handoff、PR本文、ドキュメントで時刻や日付を扱う場合は、外部仕様でUTCが必須のときを除き、日本時間を基準にする。

時刻を機械可読に保存する場合は、`2026-04-27T10:30:00+09:00` のように timezone offset つきの ISO 形式を使う。外部APIやCIがUTCを返す場合は、日本時間へ変換するか、UTCであることを明示する。

### コメント方針

コードコメントは、日本語運用のプロジェクトでは原則として日本語で書く。英語が自然な API 名、CLI 名、エラー文字列、固有名詞は英語のままでよい。

コードには、意図、前提、制約、危険な分岐、将来の保守で迷いやすい判断を説明するコメントを適切に入れる。すべての行や自明な処理にコメントする必要はない。

関数、メソッド、コマンド handler には、原則として1〜2行で役割を説明するコメントまたは docstring を置く。大きい関数、重要な関数、副作用のある関数、失敗時の扱いが重要な関数では、複数行で責務、入力の前提、副作用、停止条件を説明する。

AI向けのドキュメント、設定、プロンプト、skillには、履歴メモや「どのplanにより変更したか」のようなコンテキストを消費するだけのコメントを入れない。変更履歴はGit、PR、handoff、run logで扱う。

## 参考にする知見

- OpenAI Codex best practices: AGENTS.md、skills、automations、hooks、subagentsを活用する。
- Claude Code best practices: explore -> plan -> implement、検証可能性、コンテキスト管理、subagentsを活用する。
- Anthropic Building effective agents: 単純で合成可能なworkflow、parallelization、orchestrator-workers、evaluator-optimizerを使い分ける。
- SWE-agent: エージェント用インターフェース設計が性能に影響する。
- Harness Engineering: repository knowledge、実行環境、検証、artifact、eval harness を agent が扱いやすい形にする。
- Reflexion / Self-Refine: 反省と反復は有効だが、ループ回数と停止条件を持つ。
- Agentless: 複雑な自律性より、局所化、修正、検証の単純な手順が強い場合がある。
