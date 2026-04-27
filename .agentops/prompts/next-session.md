# 次セッション用プロンプト

このプロジェクトは、Claude Code と Codex が参照するAIエージェント用グローバル設定の設計思想リポジトリです。

前回セッションでは、READMEにClaude Code / Codex用のグローバル設定プロンプトを追加し、`docs/` に設計思想、workflow、DbC、モデルルーティング、レビュー方針、最新性と監視、グローバル設定とプロジェクト設定の分離方針を作成しました。

次セッションの責務は、設計思想を実際の設定・ツール雛形に落とし込むことです。

必ず守ること:
- 日本語で応答する。
- 作業前に現在ブランチを確認し、main直作業はしない。
- 必ず作業ブランチを切る。
- 既存docsを読んでから設計する。
- 実装後は実行可能な範囲でテストまたは構文チェックを行う。
- docs更新も完了条件に含める。
- commit/push/PRは、ユーザーが求めた場合のみ行う。

やること:
1. `docs/` と `.agentops/plans/2026-04-27-design-foundation.md` を読み、設計思想を把握する。
2. Claude Code / Codex の最新公式docsを確認し、設定ファイル、hooks、subagents、skills、plugins、MCPの現在仕様を確認する。
3. `templates/` または適切なディレクトリに、Claude Code / Codex のグローバル設定雛形を作成する。
4. 共通CLI Wrapper `agentops` の最小仕様を設計する。
5. 可能であれば `scripts/agentops` または `tools/agentops_cli/` にMVPを作る。
6. `.agentops/runs/{run_id}/request.md/status.json/stdout.log/result.md` 形式で委譲ログを残す仕様を作る。
7. hooksで強制する品質ゲートの雛形を作る。
8. 監視CLIのMVPを設計し、Discord webhook通知の安全な設定方法をdocs化する。
9. `skills/` と `workflows/` に初期スキル候補を追加する。

優先順:
1. 設定雛形
2. hooks品質ゲート
3. CLI Wrapper仕様
4. 監視CLI仕様
5. skills/workflows雛形

成果物:
- 更新されたREADMEまたはdocs
- Claude Code / Codex設定雛形
- CLI Wrapper仕様またはMVP
- hooks仕様またはMVP
- 監視CLI設計
- 次セッションが必要な場合は新しい引き継ぎプロンプト
