# Understand-Anything導入workflow

## 使う場面

Understand-Anythingを使う前、またはプロジェクトに導入する時に使います。

## 手順

1. `node scripts/ua-bootstrap.mjs --check-only` で導入状態を確認する。
2. 未導入なら `node scripts/ua-bootstrap.mjs --platform codex` を実行する。
3. OpenCodeやGemini CLIの配置が必要ならplatformを切り替える。
4. Claude Code native pluginは公式marketplace commandを優先する。
5. 導入後もsecretや不要な生成物をcommitしない。
