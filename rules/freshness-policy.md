# 最新性確認ルール

## ルール

ライブラリ、ランタイム、CLI、API、モデル、料金、制限、MCP仕様はAIの記憶だけで判断しません。

導入、更新、設計判断では、公式docs、GitHub、package registry、release notes、security advisoryを優先します。

## 外部知識取得

Context7などの知識取得ツールは使ってよいですが、更新遅延を前提に一次情報も確認します。

## secret

API keyやtokenはリポジトリ、PR、ログ、handoffへ書きません。環境変数またはクライアント側secret管理を使います。
