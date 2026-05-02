# agentops プロジェクト指示

このファイルは `/home/otaku/agentops` リポジトリで作業するコーディングエージェント (Claude Code / Codex CLI) 向けのプロジェクト固有指示です。グローバル設定 (`~/.claude/CLAUDE.md` / `~/.codex/AGENTS.md`) より、このリポジトリ内の作業ではこのファイルを優先します。

Claude Code 固有の補足は同階層の `CLAUDE.md` にあります。`CLAUDE.md` は `@AGENTS.md` で本ファイルを import し、Claude Code 固有のパス・確認コマンド・branch prefix のみを差分として追記しています。両ファイルの章立ては本ファイルを基準にする。

## このリポジトリの位置づけ — 三役 (Trinity)

`agentops` は Claude Code / Codex のグローバル設定と関連運用を支えるため、同時に **3 つの役割** を担います。各 docs / config / scripts / tools がどの役割に属するかは、`docs/*.md` の `applies-to` frontmatter で機械可読に分類しています（用語定義は [docs/00-glossary.md §docs 分類 / リポジトリ責務](docs/00-glossary.md#docs-分類--リポジトリ責務) を参照）。

### (a) 設計思想カタログ (catalog) — `applies-to: global` / `template-source`

- 対象: `docs/` (`applies-to: global` の docs) / `rules/` / `skills/` / `workflows/` / `templates/`
- 役割: Claude Code / Codex のグローバル設定や他プロジェクトへ反映する候補として、思想・rule・workflow・skill を提示する
- 別 AI への指針: 候補カタログとして読み、使用中 CLI の現在仕様・公式 docs・実環境・既存設定を確認した上で採用 / 調整 / 見送りを判断する。完成品集ではない

### (b) 共有 CLI / ライブラリ (shared CLI) — `applies-to: shared-cli-spec`

- 対象: `tools/agentops_cli` (`scripts/agentops`) / `tools/agentops_monitor` (`scripts/agentops-watch`) / 関連 docs (`docs/10-cli-wrapper.md` / `docs/11-monitoring-cli.md`)
- 役割: cron / hook / shell scripts / 他 repo から呼ばれる **集約点** として、Discord 通知 / archive 後処理 / monitoring 集計 / cross-model 委譲 / project localization 等を提供する
- 別 AI への指針: **実装本体は touch せず、共有 CLI を呼ぶだけ**。`applies-to: shared-cli-spec` の docs は agentops が他層へ提供する CLI 契約として読み、host や他 repo の運用に組み込む。詳細は [docs/00-glossary.md](docs/00-glossary.md) §shared-cli-spec パターン 参照

### (c) 雛形配布元 (template source) — `applies-to: agentops-internal` (反映用 source)

- 対象: `config/claude/CLAUDE.md` (→ `~/.claude/CLAUDE.md` 反映用) / `config/codex/AGENTS.md` (→ `~/.codex/AGENTS.md` 反映用) / `config/harness.yml` / `config/cron.example` 等
- 役割: グローバル設定や cron / hook 雛形の配布 source として機能する
- 別 AI への指針: これらを変更しただけでは実グローバル設定には反映されません。明示反映が必要であり、反映時は対象 CLI の現在仕様・公式 docs・実環境・既存設定を確認して調整する

### docs 区分の早見表

| `applies-to` | 意味 | 例 |
| --- | --- | --- |
| `global` | 全 project / 全 CLI に適用される設計思想 (グローバル設定 反映候補) | `01-philosophy` / `02-workflow` / `18-notification-strategy` / `19-project-localization` |
| `shared-cli-spec` | agentops repo 内 CLI の仕様 (host / 他 repo から呼ばれる) | `10-cli-wrapper` / `11-monitoring-cli` |
| `agentops-internal` | agentops repo 自身の内部運用 docs (反映対象外) | `08-config-templates` / `13-design-evaluation` / `15-reference-kit-structure` / `16-global-settings-application-checklist` |
| `template-source` | 雛形・候補カタログの md ファイル自体 (`templates/<...>.md` / `rules/catalog.md` 等) への予約値 | (`docs/` に該当無し。雛形・カタログ運用について書いた meta docs (例: `docs/14` / `docs/15`) は `agentops-internal`) |

## 記録先の使い分け

- agentops repo 内の設計、実装、docs、テンプレート、補助 script を触る作業は、プロジェクトローカルの `/home/otaku/agentops/.agentops/` に plan、task-plan、task、review、handoff、run log を残します。
- 各 CLI のグローバル設定（Claude Code: `~/.claude/CLAUDE.md`、`~/.claude/settings.json`、`~/.claude/skills/`、`~/.claude/agents/`、`~/.claude/plugins/`、`~/.claude` 配下の hooks、MCP 設定、permission / Codex: `~/.codex/AGENTS.md`、`~/.codex/config.toml`、`~/.codex/skills/`、`~/.codex/plugins/`、`~/.codex` 配下の hooks、MCP 設定、subagents）を読む、生成する、変更する、検証する作業では、それぞれ `~/.claude/.agentops/` または `~/.codex/.agentops/` にも記録を残します。
- 1 つの作業でこのリポジトリとグローバル設定の両方を扱う場合は、`/home/otaku/agentops/.agentops/` を主記録にし、グローバル側 `.agentops/` には変更内容、検証結果、未解決リスク、次回ハンドオフだけを短く残します。
- project local の一時ファイルは `/home/otaku/agentops/.agentops/.tmp/` を使います。グローバル側の一時ファイルは `~/.claude/.agentops/.tmp/` または `~/.codex/.agentops/.tmp/` を使います。
- 機密値、認証情報、環境変数ファイル、個人情報、本番データ、巨大な依存 cache は、どちらの `.agentops/` や `.agentops/.tmp/` にも保存しません。

## グローバル設定 (`~/.claude/` / `~/.codex/`) を触る作業

- これらの実ファイルは agentops repo 外のユーザーグローバル設定です。読み取り、書き込み、削除、移動、生成、MCP / plugin / hook / skill / subagent / permission 設定の導入、shell profile 変更、外部反映の前に、対象、非対象、リスク、検証方法を短く計画し、ユーザー承認を得ます。
- 反映前に、現在のグローバル実ファイル（Claude Code: `~/.claude/CLAUDE.md` / `~/.claude/settings.json`、Codex: `~/.codex/AGENTS.md` / `~/.codex/config.toml`）、CLI version (`claude --version` / `codex --version`)、`--help`、必要な公式 docs を確認します。
- 反映後に、実際に変更したファイル、変更しなかったファイル、読み込み確認、検証結果、残リスクをグローバル側 `.agentops/` と最終報告に残します。読み込み確認には CLI が提供する確認方法（Claude Code: `/memory`、`/config`、`/mcp`、Codex: 該当 CLI の確認コマンド）を使います。
- 機密値は表示、保存、ログ出力しません。MCP や shell profile を扱う場合も、環境変数名や参照方式だけを記録します。

## Git と作業ブランチ

- 作業前に `git status --short --branch` で branch と dirty worktree を確認します。
- `main` / `master` / `develop` など保護対象ブランチへ直接 commit / push しません。
- このリポジトリの変更は使用中 CLI に応じた branch prefix で行います（Claude Code: `claude/`、Codex: `codex/`）。
- ユーザーの未コミット変更は巻き戻しません。関係する場合は内容を読み、共存する形で作業します。

## 完了条件

- 実装または docs 更新のあと、意図した差分だけになっていることを確認します。
- 必要な検証、自己レビュー、docs 更新要否確認を行います。
- レビュー起点で修正した場合は、最後に再レビューして終えます。
- 完了済み task は `.agentops/tasks/` 直下に残さず、必要に応じて `.agentops/archive/<plan-id>/` へ移します。

## 停止条件

- 機密値、個人情報、本番データ、課金、外部公開、本番反映、破壊的操作が必要になった場合。
- グローバル設定 (`~/.claude/` / `~/.codex/`) の実設定を変更する範囲が当初計画より広がる場合。
- 公式 docs または実 CLI 仕様と、このリポジトリの雛形が食い違う場合。
- テスト修正またはレビュー修正が 2 周を超えそうな場合。

## AI auto-merge 許諾（durable instructions）

このリポジトリでは、以下の **AI auto-merge 許諾条件をすべて満たした PR に限り**、主 orchestrator（Claude Code / Codex いずれの場合も）が `gh pr merge --squash --delete-branch` でマージしてよいものとします。docs/03 のマージ条件節「ユーザーまたはルール上許可された AI がマージしてよい状態」の「ルール上許可された AI」をここで定義します。

**設計段階 cross-review (高リスク plan で必須)**: durable instructions / catalog / AGENTS.md / global rules / migration / security / public API / 課金 / deploy 影響を持つ plan は、**user 承認後 / 実装着手前**に主 orchestrator と別系列の frontier reviewer (主 Claude → Codex、主 Codex → Claude) に設計レビューを委譲し、P0/P1=0 を確認する。

**Phase ownership lint (全 plan で実施)**: plan 作成直後、plan 提示前に、Phase 詳細表の担当列と Phase 担当宣言欄の存在だけを軽量モデルまたは Plan agent で確認する。cross-review とは分離し、記載漏れがあれば orchestrator が補完してから次工程へ進む。

**通常運用** (大半の高リスク plan):

1. orchestrator が plan 作成 (plan mode 中、Plan agent 内部レビューで磨く)
2. ExitPlanMode で user 提示 → user 承認
3. auto-mode で Codex cross-review 実施 (`scripts/agentops delegate --to codex --role review_frontier --effort high --input <plan>`)
4. P0/P1=0 を確認、cross-review 通過後 auto-mode で実装進行 (`kind: design` 大幅乖離時のみ user 再確認、軽微変更は orchestrator 判断)

**特殊運用** (cross-review 前提の特殊高リスク plan): user 提示前に Codex cross-review 必須。判定基準は `rules/model-routing.md` の「## 工程 2 のタイミング」節 (a)〜(c) を参照 ((a) 実グローバル反映を同一作業で行い user が承認前に別系列レビュー結果を必要とする / (b) hook 仕様改変 / (c) credential / payment / migration / public API 改変)。plan mode 制約 (Bash 禁止、user 口頭承認では解除不可) のため user が手動で plan mode を抜ける必要 (Claude Code 公式の現在の plan mode toggle 操作)。

実施手順は `rules/model-routing.md` (雛形) / `~/.claude/rules/model-routing.md` (反映) の 5 工程フロー節と「Plan agent と cross-review の区別」「工程 2 のタイミング」「plan mode 制約」節を参照。kind 分岐は工程 2 (設計レビュー) と工程 4 (実装レビュー) で異なる (前者は orchestrator 判断 + 大幅乖離時 user 確認再取得、後者は Codex run A 再委譲)。工程 4 は 4-α 同系列独立実装レビューと 4-β cross-review を分けて実施する。

### 許諾条件（全て AND）

1. **DbC 完了**: 該当 PR がカバーする `.agentops/tasks/<NN>-*.md` の DbC 完了条件をすべて満たしている。
2. **frontier review 通過**: 設計段階では主 orchestrator と別系列の frontier reviewer、実装段階では 4-α 同系列独立実装レビューと 4-β 実装担当と別系列の frontier reviewer を実施済み。`scripts/agentops delegate --to <reviewer> --role review_frontier --effort high --input <該当ファイル>` または対応する内部 `review_frontier` で実施し、所見に **P0 / P1 が 0 件、または反映済み**。run 記録が `.agentops/runs/<timestamp>-<task-id>/` に残っている。4-β の reviewer 選定は **実装担当と別系列（Anthropic ↔ OpenAI）** とする。
   - 設計段階: 主 orchestrator が Claude Code (Anthropic 系) → reviewer は **Codex / OpenAI 系** (`--to codex`)
   - 設計段階: 主 orchestrator が Codex (OpenAI 系) → reviewer は **Claude / Anthropic 系** (`--to claude`)
   - 実装段階 4-β: 実装担当が Codex (OpenAI 系) → reviewer は **Claude / Anthropic 系** (`--to claude`)
   - 実装段階 4-β: 実装担当が Claude Code (Anthropic 系) → reviewer は **Codex / OpenAI 系** (`--to codex`)
   - reviewer は修正指摘ごとに `kind: mechanical | design` ラベルを付与する。`kind: mechanical` (patch / 行番号 / 具体書き換え提示) は Claude が直接 patch、`kind: design` (抽象指摘) は Codex (run A) に再委譲。修正したらループ +1、修正者問わず。3 周目到達 → kind 不問で user 確認 (本許諾発動せず)。kind ラベル無し → 保守的に `design` 扱い。詳細は `rules/model-routing.md` (雛形) / `~/.claude/rules/model-routing.md` (反映) の 5 工程フロー節。
3. **CI green**: GitHub Actions の fail 系 job（actionlint / yamllint / markdown-link-check が導入済みなら全 job、未導入なら自己検証で `python3 -m compileall tools` 等が exit 0）。
4. **観察事実食い違いなし**: 着手時に裏取りした観察事実と現状に食い違いが新たに発生していない。
5. **PR スコープ単一**: 該当 task が要求する変更だけを含み、スコープ外リファクタを含まない。
6. **secret 未混入**: diff、commit message、PR 本文、run log に secret 値（API key、token、credential、本番 URL の認証情報）が混入していない。

### 停止条件（auto-merge せず必ず user 確認）

- レビュー修正が 2 周を超えそう、または 3 周目に入った。
- `git pull --ff-only origin main` が失敗した、または CI fail / 同期不整合が発生。
- 公式仕様確認が必要（例: AAIF `@AGENTS.md` import、GitHub Actions 課金、MCP transport の deprecation）。
- 観察事実と現状の食い違い、L コスト超過、半日 → 1 日見積もりを大幅超過。
- secret / 本番 / 課金 / 外部公開 / 破壊的操作。
- task の `停止条件` 節に該当する事象が発生。
- Codex 所見に P0 / P1 が残っている、または採否判断が分かれた。

### auto-merge 後の必須手順 (1 PR scope 完結原則)

post-merge 整理 (archive 移動 / `plans/current.md` 更新 / `task-plans/current.md` archive / `prompts/next-session.md` 更新) は **merge 前 commit に含める** ことを原則とする。merge 後に別 chore PR で実施するのは **user 明示許可がある場合のみ** 許容 (詳細な「user 明示許可」3 要件は `~/.claude/rules/auto-merge-permission.md` § auto-merge 後の必須手順を参照)。

1. `git checkout main && git fetch origin && git pull --ff-only origin main` で main 同期確認。
2. `scripts/agentops archive task --task-id <basename> --dry-run` での確認と本番実行 (`--dry-run` 無し) は **merge 前 commit に含める**。本コマンドは完了 task ファイルを `.agentops/archive/<plan-id>/tasks/` へ移動し、`.agentops/prompts/next-session.md` の `entry_point` と `completed_tasks` を一括更新する。`<basename>` は task md ファイル名から `.md` を除いたもの (例: `07-p1-06-archive-auto-update`)。merge 後は `ls .agentops/archive/<plan-id>/tasks/` と `cat .agentops/prompts/next-session.md` で結果を read-only 確認する。
3. `git status --short` で merge 後 dirty diff が無いことを確認する (本コマンドが entry_point を完了マーカー文字列 `(none — all tasks archived; consider removing this file)` に書き換えるが、ファイル自体は削除しない仕様も merge 前 commit で吸収済)。
4. plan 全体完了時のみ `scripts/agentops archive plan --plan-id <id> --summary <text> [--date <YYYY-MM-DD>]` も **merge 前 commit に含める**。本コマンドは残った plans/task-plans/tasks/reviews を archive へ一括移動し、`archive/README.md` の table に新規 row を挿入する。merge 後は `archive/README.md` と `.agentops/archive/<plan-id>/` の存在確認のみ行う。
5. 上記が完了するまで次 task に着手しない。

### 適用範囲

- 本許諾は agentops リポジトリ（`/home/otaku/agentops`）でのみ有効。他プロジェクトに派生する場合は、各プロジェクトの `CLAUDE.md` / `AGENTS.md` で明示的に許諾を再宣言します。
- 本許諾は `main` への squash merge のみ対象。force push、`git reset`、ブランチ削除（PR マージ時の自動削除は許諾範囲）以外の破壊的操作は対象外。
- 1 セッション内で連続 auto-merge する場合も、各 PR ごとに上記許諾条件を独立に評価します。

### 取消条件

- ユーザーが「auto-merge 停止」「全件 user 確認に戻す」等を明示した場合、即時取消し。
- 直近の auto-merge で問題が発覚した場合（事故、誤マージ、回帰）は次セッション以降を user 確認に戻します。
