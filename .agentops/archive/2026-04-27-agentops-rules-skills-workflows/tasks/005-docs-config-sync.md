# 005 docs/config反映

親plan: `.agentops/plans/current.md`
状態: done

## 実行内容

- `README.md`、`docs/`、`config/claude/CLAUDE.md`、`config/codex/AGENTS.md` に新ルールを反映する。
- グローバル設定は雛形であり、実設定への反映確認が必要であることを維持する。

## 検証

- `rg` で古い `/ai` 参照と反映漏れを確認する。

## 停止条件

- READMEとconfigに同じ長文を重複させすぎる場合は、正本と投影物の分離を優先する。
