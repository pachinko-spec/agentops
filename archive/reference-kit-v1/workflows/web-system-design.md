# Webシステム設計workflow

## 使う場面

Nuxt、Next.js、PHP、Go を中心とした Web システムの新規設計、機能追加、アーキテクチャ変更で使います。

## 手順

1. 利用者、業務目的、収益目的、非目的を整理する。
2. frontend、backend、DB、外部API、auth、file upload、mail、cron、queue、admin機能を分解する。
3. rendering方式を確認する。static、SSG、SSR、edge runtime、serverless API、常駐サーバーのどれかを明示する。
4. デプロイ先候補を `deployment-target-selection.md` で比較する。
5. データモデル、API契約、認可境界、監査、個人情報、課金、migration、rollbackを確認する。
6. 実装しやすさだけでなく、運用、費用、監視、support負荷、将来変更のしやすさを評価する。
7. 必要な design skill を選び、代替案を少なくとも1つ検討する。

## 完了条件

- 主要な設計判断と採用理由、代替案、リスク、検証方法が明確である。
- デプロイ先とruntime制約が設計に反映されている。
- プロジェクト側docsへ残すべき内容が洗い出されている。
