# cross-review design self review

plan_id: 2026-04-28-cross-review-design
reviewed_at: 2026-04-28
timezone: Asia/Tokyo
review_type: self-review

## 結果

- P0: なし
- P1: なし
- P2: なし
- P3: なし

## 確認したこと

- cross-review を特定 model id 固定として扱っていない。
- Codex 主体と Claude Code 主体の候補 reviewer が対称に表現されている。
- 高リスク設計以外の検討条件を追加しつつ、全変更で必須化していない。
- reviewer の所見を最終判断にせず、採否と統合判断を主 orchestrator に残している。
- `rules/`、`skills/`、`workflows/` を完成品ではなく候補カタログとして扱う既存方針と矛盾していない。
- `/home/otaku/.codex`、`/home/otaku/.claude`、shell profile、MCP 実設定へ触れていない。

## 検証

- `rg -n "cross-review|cross-model|クロスモデル|review_frontier|別系列|別 CLI|別モデル|model_id:" README.md docs rules skills workflows templates config .agentops`
- `rg -n "gpt-[0-9]|claude-[0-9]|sonnet|opus|haiku|o[0-9]" docs skills workflows templates config .agentops`
- `git diff --check`
- `rg -n "[ \t]+$" ...`
- `scripts/agentops-watch check --projects config/projects.yml`
- `python3 -c 'import pathlib, yaml; yaml.safe_load(pathlib.Path("config/model-catalog.yml").read_text())'`

## 残リスク

- 実運用で cross-review を実行する場合は、使用直前に対象 CLI の公式 docs と現在の model id を確認する必要がある。
- 今回は文書とカタログの更新であり、外部 CLI を実行した cross-review は行っていない。
