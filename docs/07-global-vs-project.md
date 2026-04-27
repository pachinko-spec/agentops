# グローバル設定とプロジェクト設定

## グローバル設定に置くもの

- 日本語運用ルール
- グローバル設定は雛形であり、実設定へ反映して初めて効くという前提
- GitHub を正とするバージョン管理
- main直push禁止
- 作業前ブランチ作成
- DbCテンプレート
- レビュー優先度とループ上限
- 最新LTS・公式docs確認ポリシー
- Context7 / Google Stitch など汎用 MCP の導入確認方針
- クロスモデル委譲の基本方針
- ドキュメント更新必須ルール
- 曖昧な指示の扱いと、修正後に最終レビューで終える方針
- 汎用skills、workflow、hooks
- harness の考え方と共通テンプレート

## プロジェクト設定に置くもの

- プロジェクト固有のビルド・テストコマンド
- 使用スタックとバージョン
- デプロイ手順
- プロジェクト固有の禁止事項
- プロジェクト固有の harness spec、fixture、oracle、sandbox/network allowlist
- `.agentops/tasks/`、`.agentops/plans/`、`.agentops/runs/`
- `.agentops/harness.yml`、`.agentops/harnesses/`、`.agentops/evals/`
- PRテンプレート、Issueテンプレート
- プロジェクト固有のhooks、skills、MCP設定
- プロジェクト固有の README、docs、運用手順、prompt、workflow の更新条件

## 優先順位

1. ユーザーの明示指示
2. プロジェクト固有のAGENTS.md / CLAUDE.md / docs
3. このリポジトリの設計思想
4. AIエージェントの一般知識

## 拡張用スキル

必要なrule、workflow、skillを発見した場合は、次の流れで管理する。

1. まずプロジェクトローカルで小さく試す。
2. 複数プロジェクトで再利用できると判断したらグローバル化する。
3. スキル化できるものは `skills/` に設計を書く。
4. 安定したら Claude Code / Codex の実際のグローバル設定へ反映する。
5. 反映後に、対象クライアントが設定と MCP を読み込んでいることを確認する。

実設定雛形は `config/claude/CLAUDE.md` と `config/codex/AGENTS.md` に置く。
詳細は [実設定雛形](08-config-templates.md) を参照する。

Harness の共通方針は [Harness Engineering](12-harness-engineering.md)、コピー元の雛形は `config/harness.yml` を参照する。
