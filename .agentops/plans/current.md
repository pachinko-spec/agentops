# Plan: agentops reference kit refactor

plan_id: 2026-04-27-agentops-reference-kit-refactor
status: approved
created_at: 2026-04-27
timezone: Asia/Tokyo

## 背景

agentops は Claude Code / Codex のグローバル設定時に参照する設計思想管理リポジトリである。一方で、`rules/`、`skills/`、`workflows/`、`config/` が増え、汎用 AI 運用フレームワークや実プロジェクト向けテンプレート集のように読める状態になっている。

今後は、各 CLI のエージェントがこのリポジトリを読み、現在の CLI 仕様、実環境、既存設定、MCP、plugin/skill/subagent/hook、shell profile、GitHub 設定を調査したうえで、何を採用し、何を編集し、何を見送るかを判断する形に寄せる。

## 目的

- agentops を Claude Code / Codex のグローバル設定時に参照する設計思想、判断材料、テンプレート、チェックリスト、補助ツールの管理リポジトリとして再定義する。
- 「正本」「投影物」という強い語彙を弱め、各 CLI エージェントが採否を判断する参照資料群として整理する。
- `docs/` は現役の設計思想・参照資料、`decisions/` は設計判断ログ、`.agentops/` は作業計画・タスク管理として分ける。
- `rules/`、`skills/`、`workflows/` の見本群を、必要に応じて `examples/`、`templates/`、`checklists/`、archive へ再編する。

## 非目的

- すぐに大量のファイルを削除すること。
- Claude Code / Codex の現在仕様をこのリポジトリ側で固定しきること。
- `rules/`、`skills/`、`workflows/` を機械的に各 CLI へ反映する運用を続けること。
- 実プロジェクト用の包括的な AI 運用フレームワークを作ること。

## 影響範囲

- `README.md`
- `docs/`
- `rules/`
- `skills/`
- `workflows/`
- `config/`
- `decisions/`
- `.agentops/`
- 補助スクリプトの説明文書

## 完了条件

- `decisions/` に設計判断ログ置き場と今回の判断ログがある。
- `.agentops/plans/current.md`、`.agentops/task-plans/current.md`、`.agentops/tasks/*.md` に今回の大きな計画と子タスクがある。
- README と主要 docs の位置づけが「参照キット」に寄っている。
- `rules/`、`skills/`、`workflows/` の扱いについて、残す、移す、縮小する、archive する方針が決まっている。
- Claude Code / Codex 用のベストプラクティスとテンプレートに集中する次フェーズの作業単位が明確になっている。

## 停止条件

- `rules/`、`skills/`、`workflows/` の移動や削除が、既存の参照関係を大きく壊す可能性がある。
- Claude Code / Codex の現在仕様確認が必要だが、公式情報にアクセスできない。
- どのファイルを現役参照資料として残すか判断できない。
- ユーザーの意図と、リポジトリ整理方針に矛盾が出た。

## 検証方針

- `rg "正本|投影物"` で強すぎる語彙を確認する。
- `git diff --check`
- `scripts/agentops-watch check --projects config/projects.yml`
- README のグローバル設定反映プロンプトが、調査、差分整理、計画提示、承認後反映に集中していることを確認する。
