# 実プロジェクトテンプレート境界

## ルール

`rules/`、`skills/`、`workflows/` は、agentops 保守のためだけでなく、実プロジェクトで使うテンプレートとして設計します。

実プロジェクト作業の既定対象は `~/dev` 配下です。dotfiles は明示依頼がない限り対象外にします。

## 優先順位

1. ユーザーの明示指示。
2. 対象プロジェクトの `AGENTS.md`、`CLAUDE.md`、README、docs、`.agentops/`、CI、deploy設定。
3. このリポジトリの template rule / skill / workflow。
4. 一般知識。

## テンプレートに入れるもの

- 設計、実装、レビュー、運用、収益化、docs更新、リリースの判断軸。
- Nuxt、Next.js、PHP、Go などの Web システムで再利用できる手順。
- Cloudflare Workers / Pages、Xserver、GCP、ローカルサーバーの選定観点。
- 公式docs確認、検証、rollback、停止条件。

## テンプレートに入れないもの

- 個別プロジェクトの secret、DB接続先、環境変数の値。
- 個別プロジェクトの deploy token、webhook URL、監視通知先。
- そのプロジェクトだけにしか通用しないビルド・デプロイコマンド。
- dotfiles 保守専用の手順。ただしユーザーが明示した場合は例外とする。
