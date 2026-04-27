# 004 skills/workflows拡張

親plan: `.agentops/plans/current.md`
状態: done

## 実行内容

- `skills/` をreview/design/docs/opsの観点で拡張する。
- `workflows/` にplan承認、レビュー、docs更新、依存導入、freshness、handoff、Understand-Anythingを追加する。

## 検証

- `find skills workflows -maxdepth 4 -type f` で配置を確認する。

## 停止条件

- skillが過剰に詳細化し、汎用雛形として読みにくい場合は粒度を調整する。
