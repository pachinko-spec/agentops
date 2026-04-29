---
last_reviewed: 2026-04-28
next_review_by: 2026-07-31
reviewer: pachinko-spec
language: ja
---

# 実プロジェクト向けテンプレート方針

## 位置づけ

agentops は、Claude Code / Codex のグローバル設定を設計・見直すときに使う設計思想、判断材料、参照テンプレートを保守するリポジトリである。

このリポジトリ自体が日々のアプリケーション開発対象ではない。ただし `rules/`、`skills/`、`workflows/` は、各 CLI エージェントが採否を判断する候補カタログであり、採用された場合は `~/dev` 配下の実プロジェクトでも使えることを前提に設計する。

> **役割分担**: 本 docs は **新規プロジェクトへのテンプレート配布** を扱う。**既存プロジェクトに過去の設計痕跡 (CLAUDE.md / AGENTS.md / .codex / .cursorrules / .claude 等) が残っている場合の競合判定と統合戦略** は [プロジェクトローカライズ戦略](19-project-localization.md) を参照する。

## 対象プロジェクト

- 実作業対象は原則 `~/dev` 配下のプロジェクト。
- dotfiles は明示依頼がない限り対象外。
- 主な対象は Nuxt、Next.js、PHP、Go などの Web システム。
- プロジェクト固有の `AGENTS.md`、`CLAUDE.md`、README、docs、`.agentops/`、CI、デプロイ手順がある場合はそれを優先する。

## テンプレートの条件

`rules/`、`skills/`、`workflows/` の候補は次の条件を満たす。

- agentops 保守専用の手順に閉じない。
- 実プロジェクトで、設計、実装、レビュー、運用、収益化、docs更新、リリースの判断に使える。
- 具体コマンド、secret、デプロイ設定、監視先、DB接続先はプロジェクトローカルへ逃がす。
- 公式docs確認、停止条件、検証条件、rollback、ドキュメント更新を含める。
- 1人開発者が過剰な儀式に潰されないよう、低リスク作業では軽量に使える。

## デプロイ先の考え方

### Cloudflare Workers / Pages

静的サイト、edge runtime、軽量API、Cloudflareに寄せたSSR/SSGに向く。Node.js前提の処理、長時間処理、ネイティブ依存、ファイルシステム依存は制約を確認する。

### Xserver レンタルサーバー

PHP、静的ファイル、Cron、SSHを使う一般的なレンタルサーバー運用に向く。Goの常駐プロセス、Next.js / Nuxt のSSR常駐サーバー、任意のdaemon前提の構成は安易に置かない。

### GCP

Cloud Run を、コンテナ化できるWeb API、SSR、Go/PHP/Node系アプリの第一候補として検討する。要件によって App Engine、Cloud Functions、Cloud Storage、Cloud SQL などを組み合わせる。

### ローカルサーバー

常駐プロセス、systemd、reverse proxy、backup、監視、証明書更新、障害時復旧を明文化できる場合に使う。個人運用でも、secret、ログ、backup、rollback を省略しない。

## 使い方

実プロジェクトで作業を始める時は、まず `workflows/catalog.md` の `project-intake` 候補と `templates/agentops/` を使い、対象パス、スタック、デプロイ先、検証コマンド、プロジェクト固有ルールを確認する workflow を生成する。

新機能や修正では `feature-delivery`、Web設計では `web-system-design`、リリース前には `release-readiness`、運用変更では `production-operations` の候補を、対象 CLI とプロジェクトに合わせて生成する。
