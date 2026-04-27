# freshness監査workflow

## 使う場面

モデル、CLI、MCP、LTS、公式docs、依存関係の陳腐化を確認する時に使います。

## 手順

1. `config/freshness-sources.yml` を確認する。
2. 一次情報を確認する。
3. 変更が必要なrule、workflow、skill、configを洗い出す。
4. `last_checked` を更新する。
5. 設計思想が変わる場合はdocsへ反映する。
