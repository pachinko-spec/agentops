# task 01 — P0-02: tool 実行層停止条件を docs/03 + harness.yml に追加

> 親 plan: `2026-04-28-design-review-p0-p1` (`.agentops/plans/current.md`)  
> 提案 ID: P0-02  
> 優先度: P0（即時対応）  
> 状態: 未着手  
> 想定コスト: M（1 日）  
> 想定 PR ブランチ: `claude/design-review-impl-p0-02`  
> 依存: なし

---

## 前提条件

- 触ってよい範囲: `docs/03-dbc-and-quality-gates.md`、`config/harness.yml`、`docs/12-harness-engineering.md`（相互リンク追加のみ）。
- 触らない範囲: `docs/01-philosophy.md` の本文、`docs/05-review-policy.md`、報告書本体。
- 事前確認: `config/harness.yml` の `schema_version: 1` を維持。`agentops-watch` の現在仕様（`scripts/agentops-watch`）。
- 業界出典: cordum.io / blog.meganova.ai の circuit breaker 記事（runaway agent の代表事例として参照、一次性は弱いため具体額を計画値に固定しない）、ABC 論文 (arXiv:2602.22302) の (p, δ, k)-satisfaction、Anthropic Managed Agents の event log。

## 不変条件

- 既存の DbC 5 条件（前提・不変・完了・禁止・停止）テンプレートは保持。
- `harness.yml` の既存セクション（placement_policy、usage_policy、defaults、task_template）の構造を壊さない。
- secret / 本番値を harness.yml に書かない。

本 task のスコープは **「機械可読な停止条件 spec の導入」** に限定する。`agentops-watch` 等の監視側で実際にこの spec を読んで警告する実装は、次 plan の handoff 対象とする（本 task 範囲外）。

1. `docs/03-dbc-and-quality-gates.md` の「停止条件」を **プロセス層** + **tool 実行層** の 2 階層に再整理する。
   - プロセス層（既存）: テスト失敗 2 周、レビュー修正 2 周、仕様判断、セキュリティリスク。
   - tool 実行層（新規）: max_tool_calls / no_progress_steps / circuit_breaker_cycle_threshold / cost_cap_usd_per_session の 4 種を spec として導入。業界出典は「runaway agent の代表事例（cordum.io / meganova.ai）」として 1 行で言及（具体額は引用しない）。
2. `config/harness.yml` の `defaults` 配下に `stop_conditions:` セクションを追加し、tool_layer の閾値を機械可読に書く。
   ```yaml
   stop_conditions:
     tool_layer:
       max_tool_calls: 200          # 後段の監視 CLI が読む spec。閾値は plan で再評価
       no_progress_steps: 10        # N steps 進捗無しで halt
       circuit_breaker_cycle_threshold: 3  # 同一 cycle 3 回検知で halt
       cost_cap_usd_per_session: 20 # 通貨単位は USD、プロジェクト側で上書き可
   ```
   既定値の根拠を行末コメントで残す（具体額の固定は避ける）。
3. `docs/12-harness-engineering.md` の harness 仕様参照に `docs/03` の停止条件 2 階層へのリンクを追加。
4. 既存の単一停止条件のみの記述があれば 2 階層方式に揃える（grep で確認）。
5. 監視側実装は本 task 範囲外。次 plan へ持ち越す旨を `次セッションへ残すこと` に記録する。

## 完了条件

- `docs/03` の停止条件節が 2 階層構造になっている。
- `config/harness.yml` に上記 4 種の閾値が機械可読で入っている（spec として導入。監視実装は別 plan）。
- `docs/12` から `docs/03` の停止条件節への相互リンクがある。
- `python3 -m compileall tools` が exit 0。
- `scripts/agentops-watch check --projects config/projects.yml`（存在時）が exit 0。
- 自己レビューで「停止条件を増やしすぎて運用コストが上がっていない」ことを確認。
- 監視 CLI 側の実装拡張（spec を読んで警告する処理）は本 task 範囲外で、`次セッションへ残すこと` に handoff 候補として記録されている。
- Codex cross-review 完了、P0/P1 所見を反映済み。
- PR が main にマージされ、ローカル main が origin/main と同期。

## 検証

- `git status --short --branch`
- `python3 -m compileall tools`
- `rg -n "停止条件" docs/03-dbc-and-quality-gates.md`（2 階層の見出しが出ること）
- `rg -n "max_tool_calls|no_progress_steps|circuit_breaker_cycle_threshold|cost_cap_usd_per_session" config/harness.yml`
- `scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/03-dbc-and-quality-gates.md`
- 同様に `--input config/harness.yml` でも委譲（または diff を 1 ファイルにまとめて 1 回）。
- 結果を `.agentops/runs/<timestamp>-p0-02/` に保存、所見を `.agentops/reviews/p0-02.md` に転記。

## 禁止事項

- main 直 push。
- secret 値（cost_cap の通貨単位以外）を harness.yml に書く。
- `schema_version` を上げる（破壊的変更）。
- 報告書本体を編集する。
- 関連しない docs / config をついでに変更する（スコープ外リファクタ禁止）。

## 完了時の後処理

- 本ファイルを `.agentops/archive/2026-04-28-design-review-p0-p1/tasks/01-p0-02-tool-stop-conditions.md` に移す（**commit 前**）。
- 次 task（`02-p1-01-glossary.md`）に着手するため `prompts/next-session.md` を更新。
- PR マージ後、`git fetch && git status` で `main...origin/main` 同期確認。

## 停止条件

- harness.yml の `schema_version` を上げざるを得ない構造変更が必要になった場合 → plan に戻り再設計を提案。
- 4 種の閾値の根拠が公式 docs / 一次情報から確認できない場合 → 値を保留にして user 確認。
- 既存の `agentops-watch` 仕様と新規 stop_conditions の整合が崩れる場合 → user 確認。
- レビュー修正 2 周超え。

## 次セッションへ残すこと

- 本 task のマージ後、**監視 CLI 側で stop_conditions spec を実際に読んで警告する実装** を `handoffs/2026-MM-DD-tool-stop-monitoring.md` として残す（`agentops-watch` の拡張、Discord 通知、no_progress 検知ロジック等）。次 plan の検討対象。
- 途中で持ち越す場合は本ファイルに進捗を追記し、`prompts/next-session.md` で本ファイルを指す。
