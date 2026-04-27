# デプロイ先選定ポリシー

## ルール

デプロイ先は、慣れや固定知識だけで選ばず、runtime制約、SSR/SSG/static/API、DB、cron、常駐プロセス、費用、運用負荷、rollback、公式docsの現在仕様を確認して選びます。

## 候補

- Cloudflare Workers / Pages: static、edge runtime、軽量API、Cloudflare寄せのSSR/SSGに向く。Node.js前提、ネイティブ依存、ファイルシステム依存、長時間処理は制約を確認する。
- Xserver レンタルサーバー: PHP、静的ファイル、Cron、SSH運用に向く。任意のdaemon、Go常駐プロセス、Next.js / Nuxt のSSR常駐サーバー前提の設計は安易に置かない。
- GCP: Cloud Run をコンテナ化できるWeb API、SSR、Go/PHP/Node系アプリの第一候補として検討する。要件に応じて App Engine、Cloud Functions、Cloud SQL などを選ぶ。
- ローカルサーバー: systemd、reverse proxy、backup、監視、証明書更新、障害時復旧まで運用できる場合に使う。

## 完了条件

デプロイ先を含む設計やリリースでは、選定理由、必要な公式docs確認、環境変数とsecretの扱い、rollback、監視、docs更新を明記します。
