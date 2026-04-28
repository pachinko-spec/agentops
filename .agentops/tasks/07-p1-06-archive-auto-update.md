# task 07 — P1-06: archive 自動更新 hook

> 親 plan: `2026-04-28-design-review-p0-p1`  
> 提案 ID: P1-06  
> 優先度: P1  
> 状態: 未着手  
> 想定コスト: M（半日）  
> 想定 PR ブランチ: `claude/design-review-impl-p1-06`  
> 依存: なし

---

## 前提条件

- 触ってよい範囲: `scripts/agentops`（CLI）、`tools/agentops_cli/`（Python 実装）、`scripts/hooks/`（必要に応じ）、`docs/11-monitoring-cli.md`、`config/harness.yml`（必要に応じ）。
- 触らない範囲: 既存 hook 仕様の破壊的変更、`.agentops/archive/README.md` の既存行（新規 row 挿入のみ）。
- 事前確認: `tools/agentops_cli/` の現状サブコマンド、`.agentops/archive/README.md` は **Markdown table 形式**（列: `完了日 | plan-id | サマリ`、新しい順で先頭に追加）。各 plan archive の plan-id と日付。
- 業界出典: Anthropic Managed Agents の event log（append-only）。

## 不変条件

- `scripts/agentops` の既存サブコマンドを破壊しない。
- secret / 本番値を hook に書かない。
- archive README の既存 table 行を改変しない（新規 row の挿入のみ）。table 列構造（`完了日 | plan-id | サマリ`）を変えない。

## 実行内容

1. `scripts/agentops archive` サブコマンドを新設（または既存サブコマンドを拡張）。引数: `--plan-id <id>` / `--summary <text>` / `--date <YYYY-MM-DD>`（既定は今日）。
2. 動作:
   - `.agentops/plans/current.md` を `.agentops/archive/<plan-id>/plan.md` へ移動。
   - `.agentops/task-plans/current.md` を `.agentops/archive/<plan-id>/task-plan.md` へ移動。
   - `.agentops/tasks/*.md`（README.md 除く）を `.agentops/archive/<plan-id>/tasks/` へ移動。
   - `.agentops/reviews/*` と該当 `runs/*` も `.agentops/archive/<plan-id>/` 配下へ移動。
   - `.agentops/archive/README.md` の table（列 `| 完了日 | plan-id | サマリ |`）に、`| YYYY-MM-DD | [<plan-id>](<plan-id>/plan.md) | <summary> |` の row を **新しい順を維持して先頭（既存 row の上）に挿入**する。`<plan-id>` は existing entry のリンク慣行（plan.md がある場合は plan.md、無い場合は plan-id ディレクトリ）に合わせる。
3. `--dry-run` を実装し、移動内容と挿入する table row を報告のみで実行しない。
4. `docs/11-monitoring-cli.md` に新サブコマンドの使い方を追記。
5. `tools/agentops_cli/` 配下の既存テストがあれば追加。なければ最低限の smoke test（`python3 -m compileall tools`）。

## 完了条件

- `scripts/agentops archive --plan-id <id> --summary <text> --dry-run` が成功し、移動予定とインデックスへ挿入する table row をレポートする。
- `--dry-run` 無しで実行した時、archive ディレクトリへの移動と README.md table への row 挿入（先頭 = 新しい順）が両方完了する。既存 row は不変。
- 既存の plan archive を破壊しない（ロールバック手順を docs/11 に記載）。
- Codex cross-review 完了、所見反映済み。
- PR が main にマージされ、ローカル main が同期。

## 検証

- `python3 -m compileall tools`
- `scripts/agentops archive --help` が新サブコマンドを表示する
- `scripts/agentops archive --plan-id test --summary test --dry-run` が想定動作（実移動なし）
- 仮の plan-id で `--dry-run` 無し実行 → archive 配下に移動 → 元に戻して plan を保つ（または別ブランチで実行確認）
- `scripts/agentops delegate --to codex --role review_frontier --effort high --input scripts/agentops`（または該当 Python ファイル）
- 結果を `.agentops/runs/<timestamp>-p1-06/` に保存、所見を `.agentops/reviews/p1-06.md` に転記。

## 禁止事項

- main 直 push。
- 既存サブコマンドの破壊的変更。
- secret / 本番値を hook / docs に書く。
- archive README の既存行改変。

## 完了時の後処理

- 本ファイルを `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/07-p1-06-archive-auto-update.md` へ移す（commit 前）。実移動には新コマンド `scripts/agentops archive` を使ってドッグフードする（plan 全体 archive 時は本コマンドが完成しているのでそれを使う）。
- `prompts/next-session.md` を次 task（08）に更新。
- PR マージ後 main 同期確認。

## 停止条件

- archive ディレクトリ構造が想定と異なる場合 → 構造を docs/11 に記載してから実装を続ける。
- 既存 hook（pre-commit / pre-push）と新サブコマンドの責務分担で混乱する場合 → docs/09 と docs/11 を整理してから実装。
- レビュー修正 2 周超え。

## 次セッションへ残すこと

- pre-archive hook で「未完了 task が残っていないか」を検知する fail-safe は次 plan のスコープにするか本 plan で実装するか、レビュー時に判断。
