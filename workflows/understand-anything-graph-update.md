# Understand-Anything graph更新workflow

## 使う場面

knowledge graphを更新するか判断する時に使います。

## 手順

1. `node scripts/ua-bootstrap.mjs --check-only` で導入状態を確認する。
2. `node scripts/ua-graph-controller.mjs --mode pr --base main` でPR中の推奨actionを確認する。
3. PR中は原則 `diff` に留める。
4. merge後に必要な範囲だけ `incremental`、`domain`、`full` を検討する。
5. 重い更新は別セッションまたは別PRに分ける。
