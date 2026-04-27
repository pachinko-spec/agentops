# agentops reference kit refactor

date: 2026-04-27
status: proposed

## 背景

agentops は Claude Code / Codex のグローバル設定時に参照する設計思想管理リポジトリとして始まった。一方で、`rules/`、`skills/`、`workflows/`、`config/` が増え、汎用 AI 運用フレームワークや実プロジェクト向けテンプレート集のように読める状態になっている。

このままでは、各 CLI のエージェントが「このリポジトリの内容を正本として機械的にグローバル設定へ投影する」と誤解しやすい。また、グローバル設定時に不要な見本や履歴まで読み込み、判断材料が膨らみすぎる。

## 決定

agentops は、Claude Code / Codex のグローバル設定時に参照する設計思想、判断材料、設定テンプレート、チェックリスト、補助ツールの管理リポジトリとして再定義する。

各 CLI のエージェントは、このリポジトリを読んだうえで、現在の CLI 仕様、実環境、既存グローバル設定、MCP、plugin/skill/subagent/hook、shell profile、GitHub 設定を調査し、何を採用し、何を編集し、何を見送るかを計画する。

## 採用しないこと

- このリポジトリの `rules/`、`skills/`、`workflows/` を正本として、Claude Code / Codex へ機械的に投影する運用。
- グローバル設定時に、履歴ログや大量の見本を常に読み込ませる運用。
- CLI ごとの差分をこのリポジトリ側で過度に固定する運用。

## 影響範囲

- README の位置づけとグローバル設定反映プロンプト。
- `docs/` の語彙と読み込み対象の整理。
- `rules/`、`skills/`、`workflows/` の扱い。
- `config/` の位置づけ。
- 見本群の `examples/`、`templates/`、`checklists/`、`archive/` への再編案。
- 補助スクリプトの役割説明。

## 移行方針

1. まず `.agentops` に大きな計画、task-plan、子タスクを作る。
2. 設計判断ログは `docs/` 直下ではなく `decisions/` に置く。
3. README と docs の語彙を「正本」「投影物」から「参照資料」「判断材料」「反映候補」へ寄せる。
4. `rules/`、`skills/`、`workflows/` の必要性と配置を見直す。
5. Claude Code / Codex 用の書き方ベストプラクティス、テンプレート、チェックリストへ主軸を移す。
6. 不要な見本群は削除を急がず、必要に応じて `examples/` や archive に移す。

## `.agentops` と `decisions/` の役割分担

- `.agentops/`: 作業計画、今回セッションの実行順、未完了タスク、レビュー、run log を管理する。
- `decisions/`: 設計思想やリポジトリ構造に関わる重要判断の背景、代替案、採用理由、影響範囲を記録する。
