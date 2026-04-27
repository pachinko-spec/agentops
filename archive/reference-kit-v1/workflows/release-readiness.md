# リリース準備workflow

## 使う場面

実プロジェクトの変更を本番または外部公開環境へ出す前に使います。

## 手順

1. 差分、対象環境、デプロイ先、release window、影響ユーザーを確認する。
2. lint、型チェック、unit、integration、E2E、ブラウザ確認、migration dry-run など必要な検証を確認する。
3. 環境変数、secret、DB migration、cache、file storage、cron、queue、external API の変更を確認する。
4. rollback、feature flag、maintenance mode、backup、監視、alert、ログ確認手順を確認する。
5. README、docs、API docs、runbook、changelog、release notes、顧客向け説明の更新漏れを確認する。
6. 未解決P0/P1がないこと、P2の延期理由があることを確認する。

## 完了条件

- リリース条件、検証結果、rollback手順、監視確認、docs更新が明示されている。
- デプロイ先固有の制約と公式docs確認が必要な範囲で完了している。
