---
last_reviewed: 2026-04-28
next_review_by: 2026-07-31
reviewer: pachinko-spec
language: ja
---

# 設計思想

> 用語は [docs/00-glossary.md](./00-glossary.md) を参照。

このプロジェクトは、Claude Code / Codex のグローバル設定を設計・見直すときに参照する、AIエージェント運用の設計思想と判断材料を管理する。

agentops 自体は、グローバル設定時の参照キットである。ここに置く `rules/`、`skills/`、`workflows/` は完成品集ではなく、各 CLI の実仕様とユーザー環境を確認したうえで採否を判断する候補カタログである。実際の Claude Code / Codex 用設定、Skill、subagent、workflow は、`templates/` と公式 docs を入力にして生成する。

## 中核原則

- AIエージェントは自律的に動くが、作業境界、品質ゲート、停止条件は明示する。
- 実装前には必ず計画を提示し、ユーザー承認を得る。承認済みplanをセッション跨ぎで継続する場合でも、今回セッションの小分け計画とtaskは明示する。
- DRY原則を守り、常時適用ルール候補は `rules/`、作業手順候補は `workflows/`、観点別能力候補は `skills/`、CLI 別の生成雛形は `templates/`、現役の設計思想と参照資料は `docs/`、実設定へ取り込む候補となる雛形は `config/` に置く。
- グローバル設定は雛形であり、実設定ファイルや MCP 設定へ採否を判断して取り込んで初めて効く。反映確認を完了条件に含める。
- `rules/`、`skills/`、`workflows/` は、グローバル設定保守だけに閉じず、`~/dev` 配下の実プロジェクトへ持ち出して使える候補カタログにする。
- 複雑な自律エージェントより、単純で合成可能なworkflowを優先する。
- 設計、実装、レビュー、検証、ドキュメント更新を1つの開発サイクルとして扱う。
- レビュー後に修正した場合は必ず再レビューし、修正で終わらせない。
- 1人開発者が日本語で開発しやすいことを最優先する。
- 複数モデルは競わせるのではなく、役割分担と相互レビューのために使う。
- 最終判断は主 orchestrator が持つ。サブエージェントは調査、実装補助、レビュー、検証のために使う。
- AIの記憶を信用しすぎず、公式docs、GitHub、package registry、release notesなど一次情報を確認する。
- ユーザーの指示は、曖昧、断片的、急なアイデアを含む前提で扱う。
- 不明点、懸念点、代替提案がある場合は、思い込みで進めずユーザーへ確認する。
- ユーザーの指示をそのまま実行するだけでなく、より良い方法、より良い実装、より良いロジックがあるなら提案する。
- 低リスクで、不明点が結果に大きく影響しない場合だけ、合理的な仮定を明示して完遂してよい。
- ユーザーの指示が大きなリスクを抱えると判断した場合は、必ずエスカレーションし、ユーザー判断を仰ぐ。

## 実プロジェクト前提

実プロジェクト作業の既定対象は `~/dev` 配下とする。dotfiles は明示依頼がない限り対象外にする。

主な対象は Nuxt、Next.js、PHP、Go などの Web システムである。主なリリース先は Cloudflare Workers / Pages、Xserver レンタルサーバー、GCP、一部ローカルサーバーを想定する。

ただし、このリポジトリにはプロジェクト固有のビルドコマンド、デプロイコマンド、secret、環境変数、DB接続先、監視先を固定しない。実プロジェクトでは、そのプロジェクトの README、docs、`AGENTS.md`、`CLAUDE.md`、`.agentops/`、CI、deploy設定を優先する。

## グローバル設定見直しの考え方

このリポジトリの変更は、グローバル設定へ自動的に反映されない。運用へ取り込むには、`~/.claude/CLAUDE.md`、`~/.codex/AGENTS.md`、各クライアントの MCP 設定、shell profile、GitHub remote/branch protection を確認し、採用する内容、調整する内容、見送る内容を判断する。反映した場合は、設定が読み込まれていることを検証する。

プロジェクト固有の `AGENTS.md`、`CLAUDE.md`、docs、`.agentops/` がある場合は、グローバル思想を下敷きにしながらプロジェクト側の具体条件を優先する。ドキュメント更新も同様に、グローバル設定だけでなく作業中プロジェクトの README、docs、運用手順、設定、prompt、skill、workflow を対象にする。旧 `rules/`、`skills/`、`workflows/` 実体は `archive/reference-kit-v1/` に残し、現役の候補カタログと混同しない。

実プロジェクトへテンプレートを持ち出す時の詳しい方針は [実プロジェクト向けテンプレート方針](14-real-project-template-policy.md) を参照する。設計判断の履歴や採用理由の確認が必要な場合は `decisions/` を参照するが、`decisions/` はグローバル設定時に毎回読む現役 docs ではない。

## 採用する考え方

### DbC

各タスクには、前提条件、不変条件、完了条件、禁止事項、停止条件を持たせる。5 条件の詳細と品質ゲートとの接続は [DbCと品質ゲート](03-dbc-and-quality-gates.md) を参照する。

### Agent Computer Interface

AIエージェントが使うCLI、ログ、ディレクトリ構成、状態ファイルは性能と安全性に直結する。CLI Wrapper、`.agentops/`、hooks、skills、workflowsは設計対象として扱う。

### 検証可能性

AIが自分の作業を検証できるように、テスト、lint、型チェック、E2E、スクリーンショット、CI結果、期待出力を明示する。

再現性が必要な作業では、task spec、setup、allowed commands、fixtures、oracle、artifact、replay条件を harness として明示する。詳細は [Harness Engineering](12-harness-engineering.md) を参照する。

### コンテキスト衛生

長い会話に失敗履歴を溜めすぎない。必要な状態は `.agentops/` の短い文書に残し、別セッション・別モデルが続きから読めるようにする。

`.agentops/plans/current.md` は大きい承認済みplan、`.agentops/task-plans/current.md` は今回セッションの実行計画、`.agentops/tasks/*.md` は未完了または進行中の子taskとする。完了したplan/task/task-planは `.agentops/archive/<plan-id>/` へ移す。詳細責務（親 task 一覧必須、PR 単位、`handoffs/` の限定運用、`prompts/next-session.md` の動的判定など）は [docs/02-workflow.md](02-workflow.md) の責務テーブルを参照する。

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
