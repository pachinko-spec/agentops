# デプロイ先選定workflow

## 使う場面

Cloudflare Workers / Pages、Xserver レンタルサーバー、GCP、ローカルサーバーのどこへ出すかを選ぶ時、または既存デプロイ先の妥当性を見直す時に使います。

## 手順

1. アプリの形を確認する。static、SSG、SSR、API、background job、cron、file upload、DB接続、長時間処理の有無を見る。
2. Cloudflare Workers / Pages では、edge runtime、framework対応、bindings、build/deploy手順、Node.js互換性、長時間処理制約を公式docsで確認する。
3. Xserver では、PHP、静的ファイル、Cron、SSH、DB、メールなどレンタルサーバーとして自然な機能に収まるか確認する。任意daemonや常駐SSR前提なら別候補を検討する。
4. GCP では、Cloud Run を第一候補にし、container、HTTP service、scaling、secret、Cloud SQL、logging、費用、rollbackを確認する。必要なら App Engine などを比較する。
5. ローカルサーバーでは、systemd、reverse proxy、TLS、backup、監視、ログローテーション、障害時復旧、物理運用負荷を確認する。
6. 選定理由、非採用理由、費用、運用負荷、rollback、docs更新先をまとめる。

## 停止条件

- 公式docsで現在仕様を確認できない。
- secret、production data、課金、外部公開の扱いが不明。
- rollbackまたは復旧手順を説明できない。
