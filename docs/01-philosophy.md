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

### コンテキスト衛生

長い会話に失敗履歴を溜めすぎない。必要な状態は `.agentops/` の短い文書に残し、別セッション・別モデルが続きから読めるようにする。

## 参考にする知見

- OpenAI Codex best practices: AGENTS.md、skills、automations、hooks、subagentsを活用する。
- Claude Code best practices: explore -> plan -> implement、検証可能性、コンテキスト管理、subagentsを活用する。
- Anthropic Building effective agents: 単純で合成可能なworkflow、parallelization、orchestrator-workers、evaluator-optimizerを使い分ける。
- SWE-agent: エージェント用インターフェース設計が性能に影響する。
- Reflexion / Self-Refine: 反省と反復は有効だが、ループ回数と停止条件を持つ。
- Agentless: 複雑な自律性より、局所化、修正、検証の単純な手順が強い場合がある。
