# 設計思想の評価

## 総評

このプロジェクトの設計思想は、AIエージェント用のグローバル設定として妥当性が高い。特に、グローバル設定とプロジェクト固有設定を分け、DbC、GitHub PR、レビュー、検証、ドキュメント更新、handoff を1つの運用サイクルとして扱っている点が強い。

一方で、グローバル設定は肥大化しやすく、MCP やモデル名のように変化が速いものを固定しすぎると陳腐化する。グローバルには原則と確認方針を置き、具体コマンド、allowlist、secret、プロジェクト固有の禁止事項はプロジェクト側へ寄せる設計を維持するのがよい。

加えて、`rules/`、`skills/`、`workflows/` は agentops 保守専用に寄りすぎると、実プロジェクトのコード開発で使いにくくなる。現役の置き場は完成品集ではなく候補カタログとし、`~/dev` 配下の Web システム開発、Cloudflare / Xserver / GCP / ローカルサーバーへのリリース、運用と収益化まで扱える候補を、対象 CLI の公式 docs と `templates/` に基づいて生成できる粒度に保つ必要がある。

## 強い点

- 日本語運用、時刻方針、GitHub PR、レビュー、handoff が明文化されており、1人開発者の作業履歴と判断を残しやすい。
- DbC により、AI が自律的に動く範囲と停止条件を扱いやすい。
- Context7 などの外部知識と一次情報確認を組み合わせており、古い記憶で実装するリスクを下げている。
- レビュー修正ループに上限があり、無限修正や P3 だけの過剰対応を防げる。
- `.agentops/`、CLI Wrapper、harness、monitoring を設計対象として扱っており、Agent Computer Interface として筋がよい。

## 注意点

- グローバル設定を変更しても実設定へ自動反映されないため、反映手順と反映確認を運用タスクとして扱う必要がある。
- Context7 と Google Stitch の MCP 導入は有用だが、transport、認証方式、クライアントごとの設定が変わりやすい。グローバルには「未導入なら導入し、一次情報で確認する」までを置き、詳細はクライアント/プロジェクト側へ逃がすのが安全。
- 「必ず GitHub」を強くするほど、ローカル実験やネットワーク障害時の摩擦は増える。完了扱いに GitHub を必須化し、作業途中のローカル検証は許す、という現在の分け方が現実的。
- 強いモデルは曖昧な指示も完遂しがちなので、目的、非目的、完了条件、リスクを先に短く定義するルールは重要。
- 「最後はレビュー」は安全性を上げるが、軽微な修正でもコストは増える。レビュー粒度は変更リスクに応じて調整し、少なくとも差分確認と未解決 P0/P1 なしの確認で終える。

## 改善方針

- グローバル設定は、原則、判断基準、停止条件、反映確認、実プロジェクトで再利用できるテンプレートに集中させる。
- プロジェクト側には、実コマンド、テスト条件、デプロイ条件、MCP allowlist、secret 管理、harness spec を置く。
- agentops保守専用のskill/workflowは、実プロジェクト向けテンプレートと混同しないよう分類する。
- 最新性が重要な項目は `config/freshness-sources.yml` に登録し、最終確認日を運用で更新する。
- レビュー後の修正は必ず再レビューし、最終応答では最後に確認したレビュー結果を明示する。

## 調査メモ

- [Context7 公式 README](https://github.com/upstash/context7#installation) は、MCP モードと CLI + Skills モードを案内し、`CONTEXT7_API_KEY` による手動設定や `npx ctx7 setup` を案内している。
- [Context7 developer guide](https://context7.com/docs/resources/developer) は、`CONTEXT7_API_KEY` 環境変数を `--api-key` の代わりに使えることを示している。
- Google は [2026-03-18 の公式ブログ](https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-ai-ui-design/) で、Stitch の MCP server と SDK に触れている。Stitch は UI 生成・デザイン連携用途の外部ツールとして扱うのが自然。
