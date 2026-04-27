# Codex グローバル設定雛形

このファイルは `~/.codex/AGENTS.md` に配置するための雛形です。

注意: このファイルは雛形であり、このリポジトリを変更しただけでは実際のグローバル設定に反映されない。運用反映では、配置先の実ファイル、MCP 設定、shell profile、GitHub リモート設定を確認し、読み込み状態まで検証する。

プロジェクト固有の `AGENTS.md`、`CLAUDE.md`、`.agentops/` がある場合は、それらを優先してください。

## この雛形の前提

- `agentops` 自体はグローバル設定用の設計思想保守リポジトリであり、実プロジェクトそのものではない。
- `rules/`、`skills/`、`workflows/` は、グローバル設定へ反映する参照テンプレートであり、実プロジェクトで使える粒度を保つ。
- 実プロジェクト作業では、原則として `~/dev` 配下を対象にする。dotfiles は明示依頼がない限り対象外にする。
- 主な対象は Nuxt、Next.js、PHP、Go などの Web システム。
- 主なリリース先は Cloudflare Workers / Pages、Xserver レンタルサーバー、GCP、一部ローカルサーバー。
- 実プロジェクトでは、テンプレートよりもプロジェクト固有のコマンド、デプロイ手順、secret管理、運用手順を優先する。

## 基本方針

- 応答、commit message、Issue/PR、レビューコメント、引き継ぎ文書は日本語で書く。
- 実装、削除、ファイル生成、インストール、外部反映の前に必ず計画を提示し、ユーザー承認を得る。承認済みplanをセッション跨ぎで継続する場合だけ承認を省略できるが、その場合でも今回セッションの小分け計画とtaskは必ず明示する。
- 時刻、日付、ログ、run id、監視レポート、handoff、PR本文では、外部仕様でUTCが必須のときを除き `Asia/Tokyo` の日本時間を基準にする。
- コード、API名、CLI名、パッケージ名、UIラベルなど英語が自然なものは英語のままでよい。
- 作業前に必ず `git status --short --branch` で現在ブランチと未コミット差分を確認する。
- `main` / `master` / `develop` など保護対象ブランチでは直接作業しない。必要なら `codex/` プレフィックスの作業ブランチを作る。
- バージョン管理は必ず GitHub を正とする。作業ブランチ、commit、push、GitHub上のPR作成、レビュー、GitHub上のマージの順で扱う。
- main への直 push は禁止する。GitHub が使えない場合は、ローカル作業だけで完了扱いせず停止してユーザーに確認する。
- ローカルで main へマージして完了扱いしない。履歴、レビュー、マージ判断はリモートPRに残す。
- マージ完了後は、必ず `main` に戻り、remote の `main` を取得して `git status --short --branch` で `main...origin/main` が同期していることを確認する。
- 実装後は必ず検証する。テスト未実行または失敗状態では commit / push しない。
- 実装差分が README、docs、設定、prompt、skill、workflow に影響する場合はドキュメント更新を完了条件に含める。対象はグローバル設定だけでなく、作業中プロジェクトの README、docs、運用手順、設定、prompt、skill、workflow も含める。
- DbC の考え方を使い、前提条件、不変条件、完了条件、禁止事項、停止条件を明確にする。
- ライブラリ、ランタイム、CLI、API、モデルは AI の記憶だけで判断しない。公式 docs、GitHub、package registry、release notes、security advisory を優先する。

## MCP と外部知識

- MCP 対応クライアントで Context7 と Google Stitch が未導入なら導入する。
- API key は shell profile（例: `.bashrv`）で export 済みの `CONTEXT7_API_KEY` と `STITCH_API_KEY` を使う。
- secret 値をリポジトリ、PR、ログ、handoff に書かない。MCP 設定では環境変数参照またはクライアントの secret 管理を使う。
- Context7 や Google Stitch の導入方法、transport、認証方式は変化しやすいため、導入時は公式 docs、GitHub、release notes、クライアント側 MCP docs を確認する。

## 曖昧な指示の扱い

- ユーザーの指示が曖昧な場合は、目的、非目的、完了条件、リスクを短く言語化してから進める。
- 低リスクで局所的な作業は合理的な仮定で完遂する。
- 高リスク、破壊的操作、課金、外部公開、secret、広範囲変更を伴う場合は、作業前にユーザーへ確認する。
- 明示された作業だけでなく、検証、ドキュメント更新、レビューまでを完了条件に含める。ただし勝手に無関係なスコープへ広げない。

## 作業サイクル

1. ブランチと作業ツリーを確認する。
2. README、docs、プロジェクト固有設定を読む。実プロジェクトでは `~/dev` 配下、dotfiles除外、スタック、デプロイ先、検証コマンドを確認する。
3. 影響範囲、完了条件、停止条件を短く設計する。必要なら `workflows/project-intake.md`、`web-system-design.md`、`deployment-target-selection.md` を使う。
4. 計画をユーザーへ提示し、承認を得る。承認省略条件を満たす場合でも、今回セッションの小分け計画を明示する。
5. 必要に応じて `.agentops/plans/current.md`、`.agentops/task-plans/current.md`、`.agentops/tasks/*.md` を更新する。
6. 高リスクなら別モデルまたはサブエージェントで設計レビューを行う。
7. 実装する。
8. lint、型チェック、テスト、必要なら E2E / ブラウザ確認を行う。
9. ドキュメントを更新する。API、環境変数、deploy、rollback、runbook、release notesへの影響も確認する。
10. 差分、検証結果、ドキュメント更新を自己レビューする。外部公開や本番反映がある場合は release readiness も確認する。
11. 必要な修正を行った場合は、修正後に必ず再レビューする。
12. 完了したtaskは `.agentops/archive/<plan-id>/tasks/` へ移す。
13. commit / push / GitHub PR 作成へ進む。
14. PR レビュー後、修正した場合は最終レビューを再実行する。
15. GitHub上でマージする。ローカル main への merge だけで完了扱いしない。
16. マージ後は main に戻り、remote の main を取得して同期確認まで行う。

## レビュー修正ループ

- レビュー指摘は P0 / P1 / P2 / P3 で分類する。
- P0 / P1 は必ず修正する。修正不能なら停止してユーザーに確認する。
- P2 は修正するか、理由つきで次セッションへ延期する。
- P3 だけで修正ループを続けない。
- レビュー修正は最大 2 周までにする。3 周目が必要なら統合判断を行い、ユーザー確認または次セッション分割を行う。
- レビュー後に修正した場合は、必ず再レビューする。作業の最後は修正ではなく、最終レビュー結果の確認で終える。

## クロスモデル委譲

- Claude Code へ委譲する場合は、原則として共通 CLI Wrapper を使う。
- 委譲依頼、進捗、stdout/stderr、結果は `.agentops/runs/` に残す。
- 委譲先の所見は参考情報であり、採否と統合判断はメインエージェントが持つ。

例:

```text
agentops delegate --to claude --role architect_frontier --model <claude-model-id> --effort xhigh --input .agentops/plans/current.md
```

## セッション引き継ぎ

1 セッションで終わらない場合は、次を `.agentops/handoffs/` または `.agentops/prompts/` に残す。

- 今回完了したこと
- 未完了のこと
- 現在のブランチ
- 変更ファイル
- 実行した検証
- 未解決リスク
- 次セッションに投入するプロンプト
- リモート反映と同期確認が完了しているか
- 残タスクが本当にないか、または運用反映・実環境導入・実モデルID確認などが残っているか

## 参照優先順位

1. ユーザーの明示指示
2. プロジェクト固有の `AGENTS.md` / `CLAUDE.md` / docs / `.agentops/`
3. この `agentops` リポジトリの `rules/`、`skills/`、`workflows/`、`docs/`
4. 一般的なベストプラクティス
