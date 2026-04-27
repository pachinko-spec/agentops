# Plan: cross-review design policy

plan_id: 2026-04-28-cross-review-design
status: completed
created_at: 2026-04-28
completed_at: 2026-04-28
timezone: Asia/Tokyo

## 背景

Codex 側のグローバル設定後、初めてこのリポジトリの運用ルールを適用する作業として、cross-review / cross-model review の設計思想を現行 docs、catalog、config template へ反映した。

agentops は実設定ではなく、Claude Code / Codex のグローバル設定を設計・見直すための参照キットである。そのため、実 model id や dotfiles へ直接反映せず、設計思想、候補カタログ、テンプレート方針として整理した。

## 目的

- cross-review が特定モデル固定ではないことを明示する。
- 主エージェントとは別系列、別 CLI、別モデルファミリーの frontier reviewer を入れる思想として整理する。
- Codex 主体なら Claude Code / Anthropic 系、Claude Code 主体なら Codex / OpenAI 系が候補になりうることを対称に整理する。
- 高リスク設計だけでなく、新規機能追加、リファクタリング、依存追加、API 契約変更、デプロイ影響、レビュー修正後にも cross-review を検討する方針を追加する。
- 採否と統合判断は主 orchestrator が持つことを再確認する。

## 非目的

- 実 model id を固定しない。
- `/home/otaku/.codex` や `/home/otaku/.claude` を変更しない。
- shell profile、MCP、hooks、permission、sandbox の実設定を変更しない。
- cross-review を全変更で必須化しない。
- `archive/reference-kit-v1` の旧具体 Skill / workflow を現役入口へ丸ごと復活させない。

## 影響範囲

- `docs/02-workflow.md`
- `docs/04-model-routing.md`
- `docs/05-review-policy.md`
- `skills/catalog.md`
- `workflows/catalog.md`
- `config/model-catalog.yml`
- `config/codex/AGENTS.md`
- `config/claude/CLAUDE.md`
- 必要最小限の `templates/`
- 今回作業用の `.agentops/`

## DbC

### 前提条件

- 現在の作業対象は `/home/otaku/agentops`。
- この repo は実設定ではなく、設計思想、候補カタログ、テンプレート、補助ツールの管理リポジトリである。
- 作業は `codex/` prefix の作業ブランチで行う。
- 変更前に README、docs、rules、skills、workflows、templates、config、既存 `.agentops/` を確認済み。

### 不変条件

- secret、token、`.env`、本番個人情報を diff、ログ、PR、handoff に出さない。
- 実 model id を未確認のまま固定しない。
- Claude Code / Codex の実設定へ直接コピーする表現にしない。
- main / master / develop へ直接 commit / push しない。
- 採否と統合判断を reviewer へ委ねない。

### 完了条件

- cross-review 設計思想が docs、catalog、config template に過不足なく反映されている。
- `.agentops/plans/current.md`、`.agentops/task-plans/current.md`、必要な `.agentops/tasks/*.md` が作成または更新されている。
- `git diff --check` が成功する。
- `scripts/agentops-watch check --projects config/projects.yml` が成功する。
- diff 自己レビューと最終レビューを行い、未解決の P0/P1 がないことを確認する。
- PR を GitHub 上で merge し、main と origin/main を同期する。
- 完了済み plan / task-plan / task / review を `.agentops/archive/2026-04-28-cross-review-design/` へ移す。

### 禁止事項

- main 直 push。
- 無断の破壊的操作。
- scope 外 refactor。
- 実 model id の固定反映。
- `/home/otaku/.codex` や `/home/otaku/.claude` の変更。

### 停止条件

- 実設定反映が必要になった。
- 現在の公式 docs 確認なしに model id を選ぶ必要が出た。
- セキュリティ、secret、データ損失リスクが出た。
- テスト修正またはレビュー修正が2周を超えた。
- P0/P1 指摘を解消できない。

## 検証方針

- `rg` で cross-review / cross-model / review frontier まわりの参照整合性を確認する。
- `git diff --check`
- `scripts/agentops-watch check --projects config/projects.yml`
- 差分自己レビューと最終レビューを行う。
