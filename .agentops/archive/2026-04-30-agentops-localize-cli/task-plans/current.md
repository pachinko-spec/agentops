---
session: 2026-04-30
parent-plan: ../plans/current.md
status: in-progress
---

# Task Plan: agentops localize CLI 実装

## 今回セッションの実行順

1. **localize 実装** (`tools/agentops_cli/__main__.py` に追加):
   - 痕跡検出 (depth-2 scan、検出対象 / 除外対象は docs/19 §検出対象 inventory に従う)
   - 鮮度判定 (各痕跡の `stat -c %Y` + `git log -1` 補助)
   - 技術スタック推定 (`package.json` / `go.mod` / `composer.json` / `Cargo.toml` / `Gemfile` / `pyproject.toml`)
   - git activity 推定 (last commit / 30 日コミット数)
   - 4 戦略意思決定 (greenfield / inventory-rebuild / coexistence / freeze / user 確認 escalate)
   - report 出力 (stdout + run log)
2. **単体テスト追加** (`tools/agentops_cli/tests/`):
   - 痕跡検出 (各カテゴリ + 除外対象)
   - 鮮度バケット
   - 戦略判定 (4 戦略 + escalate)
   - report 出力 / run log 保存
3. **docs 更新**:
   - `docs/10-cli-wrapper.md`: 実装ステータス注記 (`localize` 実装済)
   - `docs/19-project-localization.md`: §CLI 仕様 を実装済表記に更新
4. **検証 + cross-review**: dry-run smoke / Codex `review_frontier --effort high`
5. **archive + commit + push + PR + auto-merge**

## 想定時間

- 実装: 90 分
- テスト: 60 分
- docs: 15 分
- cross-review + 反映: 30〜60 分

## branch / PR

- `claude/agentops-localize-cli-2026-04-30` (現ブランチ)

## 検証コマンド

```sh
python3 -m compileall tools/
python3 -m unittest discover tools/agentops_cli/tests -v

# dry-run smoke (主要 5 プロジェクトの 1 つで動作確認)
scripts/agentops localize --project /home/otaku/agentops --dry-run    # agentops 自身
scripts/agentops localize --project /home/otaku/dev/ai-engine --dry-run  # 過去 inventory 例

# secret 漏洩確認
grep -rn "discord.com/api/webhooks/[0-9]" tools/ docs/ scripts/ 2>/dev/null

# cross-review
scripts/agentops delegate --to codex --role review_frontier --effort high \
  --input tools/agentops_cli/__main__.py
```

## 機微情報の取り扱い

- 単体テストでは fixture project を tempdir に作成し、実 `~/dev/` を使わない
- 既存 project (~/dev/*) の実 dry-run は smoke 確認のみ、log には **パス・存在・サイズ・鮮度のみ** で痕跡内容の長文は転載しない (docs/19 §不変条件 と整合)
- 環境変数や secret 値を inventory に書かない
