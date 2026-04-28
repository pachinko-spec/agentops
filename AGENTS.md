# agentops プロジェクト指示

このファイルは `/home/otaku/agentops` リポジトリで作業する Codex 向けのプロジェクト固有指示です。グローバル設定や `config/codex/AGENTS.md` より、このリポジトリ内の作業ではこのファイルを優先します。

Claude Code 向けの対応指示は同階層の `CLAUDE.md` にあります。両ファイルは章立てを揃えてあるので、片方を更新したら他方も同期してください。

## このリポジトリの位置づけ

- `agentops` は Claude Code / Codex のグローバル設定、運用思想、雛形、候補カタログを保守するリポジトリです。
- `config/codex/AGENTS.md` は `~/.codex/AGENTS.md` へ反映するための雛形です。このリポジトリを変更しただけでは Codex の実グローバル設定には反映されません。
- `rules/`、`skills/`、`workflows/` は完成品ではなく候補カタログとして扱います。実設定へ採用する場合は、Codex の現在仕様、公式 docs、実環境、既存設定を確認して調整します。

## 記録先の使い分け

- `/home/otaku/agentops` 内の設計、実装、docs、テンプレート、補助 script を触る作業は、プロジェクトローカルの `/home/otaku/agentops/.agentops/` に plan、task-plan、task、review、handoff、run log を残します。
- `~/.codex/AGENTS.md`、`~/.codex/config.toml`、`~/.codex/skills/`、`~/.codex/plugins/`、`~/.codex` 配下の hooks、MCP、subagents、その他 Codex 実グローバル設定を読む、生成する、変更する、検証する作業では、`~/.codex/.agentops/` にも記録を残します。
- 1つの作業でこのリポジトリと `~/.codex` の両方を扱う場合は、`/home/otaku/agentops/.agentops/` を主記録にし、`~/.codex/.agentops/` にはグローバル設定側の変更内容、検証結果、未解決リスク、次回ハンドオフだけを短く残します。
- project local の一時ファイルは `/home/otaku/agentops/.agentops/.tmp/` を使います。Codex global 側の一時ファイルは `~/.codex/.agentops/.tmp/` を使います。
- 機密値、認証情報、環境変数ファイル、個人情報、本番データ、巨大な依存 cache は、どちらの `.agentops/` や `.agentops/.tmp/` にも保存しません。

## `~/.codex` を触る作業

- `~/.codex` 配下の実ファイルは、このリポジトリ外のユーザーグローバル設定です。読み取り、書き込み、削除、移動、生成、MCP / plugin / hook / skill / subagent 導入、shell profile 変更、外部反映の前に、対象、非対象、リスク、検証方法を短く計画し、ユーザー承認を得ます。
- 反映前に、現在の `~/.codex/AGENTS.md`、`~/.codex/config.toml`、関連する実ファイル、`codex --help`、必要な公式 docs を確認します。
- 反映後に、実際に変更したファイル、変更しなかったファイル、読み込み確認、検証結果、残リスクを `~/.codex/.agentops/` と最終報告に残します。
- 機密値は表示、保存、ログ出力しません。MCP や shell profile を扱う場合も、環境変数名や参照方式だけを記録します。

## Git と作業ブランチ

- 作業前に `git status --short --branch` で branch と dirty worktree を確認します。
- `main` / `master` / `develop` など保護対象ブランチへ直接 commit / push しません。
- このリポジトリの変更は原則 `codex/` プレフィックスの作業ブランチで行います。
- ユーザーの未コミット変更は巻き戻しません。関係する場合は内容を読み、共存する形で作業します。

## 完了条件

- 実装または docs 更新のあと、意図した差分だけになっていることを確認します。
- 必要な検証、自己レビュー、docs 更新要否確認を行います。
- レビュー起点で修正した場合は、最後に再レビューして終えます。
- 完了済み task は `.agentops/tasks/` 直下に残さず、必要に応じて `.agentops/archive/<plan-id>/` へ移します。

## 停止条件

- 機密値、個人情報、本番データ、課金、外部公開、本番反映、破壊的操作が必要になった場合。
- `~/.codex` の実設定を変更する範囲が当初計画より広がる場合。
- 公式 docs または実 CLI 仕様と、このリポジトリの雛形が食い違う場合。
- テスト修正またはレビュー修正が 2 周を超えそうな場合。

## AI auto-merge 許諾（durable instructions）

このリポジトリでは、以下の **AI auto-merge 許諾条件をすべて満たした PR に限り**、主 orchestrator（Codex / Claude Code いずれの場合も）が `gh pr merge --squash --delete-branch` でマージしてよいものとします。docs/03 のマージ条件節「ユーザーまたはルール上許可された AI がマージしてよい状態」の「ルール上許可された AI」をここで定義します。

### 許諾条件（全て AND）

1. **DbC 完了**: 該当 PR がカバーする `.agentops/tasks/<NN>-*.md` の DbC 完了条件をすべて満たしている。
2. **cross-review 通過**: 別系列 frontier reviewer（主 orchestrator が Codex の場合は Claude Code、主 orchestrator が Claude Code の場合は Codex）で `scripts/agentops delegate --to <別系列> --role review_frontier --effort high --input <該当ファイル>` を実施済み、所見に **P0 / P1 が 0 件、または反映済み**。run 記録が `.agentops/runs/<timestamp>-<task-id>/` に残っている。
3. **CI green**: GitHub Actions の fail 系 job（actionlint / yamllint / markdown-link-check が導入済みなら全 job、未導入なら自己検証で `python3 -m compileall tools` 等が exit 0）。
4. **観察事実食い違いなし**: 着手時に裏取りした観察事実と現状に食い違いが新たに発生していない。
5. **PR スコープ単一**: 該当 task が要求する変更だけを含み、スコープ外リファクタを含まない。
6. **secret 未混入**: diff、commit message、PR 本文、run log に secret 値（API key、token、credential、本番 URL の認証情報）が混入していない。

### 停止条件（auto-merge せず必ず user 確認）

- レビュー修正が 2 周を超えそう、または 3 周目に入った。
- `main pull --ff-only origin main` が失敗した、または CI fail / 同期不整合が発生。
- 公式仕様確認が必要（例: AAIF `@AGENTS.md` import、GitHub Actions 課金、MCP transport の deprecation）。
- 観察事実と現状の食い違い、L コスト超過、半日 → 1 日見積もりを大幅超過。
- secret / 本番 / 課金 / 外部公開 / 破壊的操作。
- task の `停止条件` 節に該当する事象が発生。
- cross-review 所見に P0 / P1 が残っている、または採否判断が分かれた。

### auto-merge 後の必須手順

1. `git checkout main && git fetch origin && git pull --ff-only origin main` で main 同期確認。
2. `scripts/agentops archive task --task-id <basename> --dry-run` で内容を確認した上で、`--dry-run` 無しで本番実行する。これにより完了 task ファイルが `.agentops/archive/<plan-id>/tasks/` へ移動し、`.agentops/prompts/next-session.md` の `entry_point` と `completed_tasks` が一括更新される。`<basename>` は task md ファイル名から `.md` を除いたもの（例: `07-p1-06-archive-auto-update`）。
3. `tasks/` が残ゼロなら `prompts/next-session.md` を削除するか保持するかを user に確認する（本コマンドは entry_point を完了マーカー文字列 `(none — all tasks archived; consider removing this file)` に書き換えるが、ファイル自体は削除しない）。
4. plan 全体完了時のみ `scripts/agentops archive plan --plan-id <id> --summary <text> [--date <YYYY-MM-DD>]` を実行し、残った plans/task-plans/tasks/reviews を archive へ一括移動 + `archive/README.md` の table に新規 row を挿入する。
5. 上記が完了するまで次 task に着手しない。

### 適用範囲

- 本許諾は agentops リポジトリ（`/home/otaku/agentops`）でのみ有効。他プロジェクトに派生する場合は、各プロジェクトの `CLAUDE.md` / `AGENTS.md` で明示的に許諾を再宣言します。
- 本許諾は `main` への squash merge のみ対象。force push、`git reset`、ブランチ削除（PR マージ時の自動削除は許諾範囲）以外の破壊的操作は対象外。
- 1 セッション内で連続 auto-merge する場合も、各 PR ごとに上記許諾条件を独立に評価します。

### 取消条件

- ユーザーが「auto-merge 停止」「全件 user 確認に戻す」等を明示した場合、即時取消し。
- 直近の auto-merge で問題が発覚した場合（事故、誤マージ、回帰）は次セッション以降を user 確認に戻します。
