# プロジェクト開始workflow

## 使う場面

`~/dev` 配下の実プロジェクトで作業を始める時に使います。agentops 自体の保守ではなく、テンプレートを実プロジェクトへ持ち出す入口です。

## 手順

1. 対象パスが `~/dev` 配下か確認する。dotfiles は明示依頼がない限り対象外にする。
2. `git status --short --branch` でブランチと未コミット差分を確認する。
3. プロジェクト固有の `AGENTS.md`、`CLAUDE.md`、README、docs、`.agentops/`、CI、deploy設定を読む。
4. スタックを確認する。Nuxt、Next.js、PHP、Go、DB、認証、外部API、background job、cron の有無を見る。
5. 想定デプロイ先を確認する。Cloudflare Workers / Pages、Xserver、GCP、ローカルサーバーのどれか、または未定かを明示する。
6. 実行可能な検証コマンド、E2E、ブラウザ確認、lint、型チェック、migration手順を確認する。
7. 必要な `rules/`、`skills/`、`workflows/` を選び、目的、非目的、完了条件、停止条件を短く整理する。

## 停止条件

- 対象が `~/dev` 外、または dotfiles で、ユーザー明示許可がない。
- secret、production data、外部公開、課金、破壊的操作の扱いが不明。
- プロジェクト固有ルールとグローバルテンプレートが矛盾し、合理的に解決できない。
