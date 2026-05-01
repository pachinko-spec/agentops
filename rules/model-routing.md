---
name: model-routing
description: 論理ロール 7 種 (orchestrator / architect / review / coding (frontier+fast) / research / docs)、cross-review reviewer の別系列選定、`scripts/agentops delegate` の wrapper 使用、`.agentops/runs/` への記録、実装 → レビュー → 分岐フロー (kind: mechanical | design)。
applies-to: global
---

# クロスモデル委譲とモデルルーティング

## 論理ロール

モデルカタログの論理ロールで指定する。実 model id は反映先 catalog [`~/.claude/agentops/model-catalog.yml`](file:///home/otaku/.claude/agentops/model-catalog.yml) で確認する (機械可読 spec、固定値 OK)。source 雛形 [`config/model-catalog.yml`](file:///home/otaku/agentops/config/model-catalog.yml) は全ロールの `model_id: null` を維持 (Trinity template-source 層、`docs/04-model-routing.md:70` 既存方針)。

| ロール | 用途 |
|---|---|
| `orchestrator_frontier` | 複雑タスクの分解、委譲計画、統合判断、停止条件判断 |
| `architect_frontier` | 複雑な設計、アーキテクチャ判断、ハイリスク実装方針 |
| `review_frontier` | 設計レビュー、コードレビュー、セキュリティ観点、cross-review |
| `coding_frontier` | 通常実装、難所の修正 |
| `coding_fast` | typo、軽微修正、レビュー後の小修正 |
| `research_fast` | コード調査、docs 調査、差分整理 |
| `docs_agent` | docs 更新、PR 本文、ハンドオフ整備 |

## cross-review

- 高リスク変更、新機能、リファクタ、依存追加、API 契約変更、デプロイ影響、レビュー修正後は cross-review を検討する。
- 主 orchestrator とは **別系列、別 CLI、別モデルファミリー** の `review_frontier` を候補にする。
  - 主 orchestrator が Claude Code（Anthropic 系）→ reviewer は Codex / OpenAI 系
  - 主 orchestrator が Codex（OpenAI 系）→ reviewer は Claude Code / Anthropic 系
  - 片方の CLI が使えない場合は同 CLI 内で別モデルファミリー、別ロール、別コンテキストの reviewer
- 共通 wrapper:

  ```sh
  /home/otaku/agentops/scripts/agentops delegate \
    --to codex --role review_frontier --effort high --input <file>
  ```

  `--effort` は AI auto-merge 許諾条件と整合するため `high` を既定とする。コスト・レイテンシで下げる場合のみ調整、難所では `xhigh` へ昇格。

- 委譲依頼、進捗、stdout / stderr、結果は `~/.claude/.agentops/runs/<run_id>/` に残す（`request.md` / `status.json` / `stdout.log` / `stderr.log` / `result.md` / `artifacts/`）。
- reviewer の所見は参考情報。採否、修正範囲、延期、統合判断はメインエージェントが持つ。

実行手順は skill `cross-model-delegate` / `cross-review` を参照。

## 設計 → 設計レビュー → 実装 → 実装レビュー → 最終判断 (5 工程フロー)

main session が Claude Code の場合の標準フロー:

| 工程 | 担当 | 用途 |
|---|---|---|
| 1 設計 / 計画 / 調査 | Claude (orchestrator_frontier) | user 意図汲み、harness spec、stop conditions、観察事実裏取り |
| 2 設計レビュー (新設、高リスク plan で必須) | Codex (review_frontier、別 session) | 観察事実食い違い / Trinity 違反 / 別系列原則 / scope / 検証手段不足の検出 |
| 3 実装 (run A) | Codex (coding_frontier) | コード + test 生成 + test 実行 |
| 4 実装レビュー (run B) | Codex (review_frontier、別 session) | PR 差分の独立性、kind ラベル付与 |
| 5 最終判断 | Claude (orchestrator) | diff + test result + cross-review 結果で採否判定 |

**発動条件**: 高リスク plan (durable instructions / catalog / AGENTS.md / global rules / migration / security / public API / 課金 / deploy 影響) では工程 2 (設計レビュー) を必須とする。軽微 plan (typo / docs 単純追記) では工程 2 任意。

**kind 分岐は工程ごとに分離**:

- 工程 2 (設計レビュー) `kind: mechanical` (patch / 行番号 / 具体書き換え提示) → orchestrator が parent plan ファイル直接 patch、ループ +1
- 工程 2 (設計レビュー) `kind: design` (抽象指摘、判断要) → orchestrator が判断する。通常の高リスク plan では **plan と実装が大幅乖離する場合のみ user 確認を再取得**し、軽微変更 (文言修正、節タイトル変更等) は orchestrator 判断で進めてよい。特殊高リスク plan や P0/P1 残存時は user 確認まで実装着手禁止。詳細は本ファイル下部の「## 工程 2 のタイミング」節を参照、ループ +1
- 工程 4 (実装レビュー) `kind: mechanical` → orchestrator が PR 差分直接 patch、ループ +1
- 工程 4 (実装レビュー) `kind: design` → orchestrator が **Codex coding_frontier (run A、別 session)** に再委譲、ループ +1

ループカウントは修正者問わず +1。3 周目到達 → kind 不問で user 確認 (本許諾発動せず)。kind ラベル無し → 保守的に `design` 扱い。

reviewer 出力期待値 (kind ラベル / unified diff / `artifacts/review.md` 保存) は `scripts/agentops delegate --to <reviewer> --role review_frontier` 実行時に wrapper が自動付与する。詳細は `docs/10-cli-wrapper.md` の `## Reviewer 出力期待値 (review_frontier)` 節を参照。

## Plan agent と cross-review の区別

5 工程フローの工程 2 (設計レビュー) を実施する際、以下 2 種を混同しないこと。

- **Plan agent (内部レビュー)**: Claude 同系列 (`Plan` subagent_type) の独立視点レビュー。**cross-review ではない**。plan mode 中に呼び出し可能で、論理整合性 / 抜け漏れ / 他 rule 矛盾の検出に使う。
- **cross-review**: 別モデルファミリー (Anthropic ⇔ OpenAI) の `review_frontier` のみを指す。`scripts/agentops delegate --to <別系列> --role review_frontier --effort high` で実施。

両者は補完関係にあり、Plan agent (内部) → cross-review (別系列) の順で組み合わせると検出力が高い。

## 工程 2 のタイミング (高リスク plan の運用フロー)

| plan 種別 | 工程 1 中 (plan mode) | 工程 2 タイミング |
|---|---|---|
| 通常の高リスク plan | Plan agent (内部レビュー) で plan を磨く | **user 提示 (ExitPlanMode) → user 承認後** に Codex cross-review (auto-mode 内) |
| 特殊高リスク plan (cross-review 前提) | Plan agent + 事前 cross-review 必須 | **user 提示前** に Codex cross-review 必須 (user が手動で plan mode を抜ける) |

**特殊運用判定基準 (以下のいずれか該当で特殊運用)**:

- (a) **実グローバル反映を同一作業 (同一 PR / 同一 commit) で行い、かつ user が承認前に別系列レビュー結果を必要とする** plan (例: agentops repo 修正と `~/.claude/*` 反映を 1 PR にまとめる場合)
- (b) **hook 仕様改変** (`~/.claude/hooks/*` または `~/.codex/hooks/*` の挙動変更)
- (c) **credential / payment / migration / public API 改変** (`high-risk-escalation.md` の高リスク領域に該当)

該当しない高リスク plan は通常運用 (user 承認後 cross-review) で良い。agentops repo 修正と `~/.claude/*` 反映を **別作業 (別 PR / 別 commit) として分離** すれば (a) に該当せず、通常運用で十分。

通常の高リスク plan の流れ:

1. orchestrator が plan 草案作成 (plan mode 中)
2. Plan agent (内部レビュー) で plan を磨く (plan mode 中、cross-review ではない)
3. ExitPlanMode で user 提示
4. user 承認後 (auto-mode)、Codex cross-review (`scripts/agentops delegate --to codex --role review_frontier --effort high --input <plan>`) を実施
5. Codex 所見の処理 (上記「kind 分岐は工程ごとに分離」節と整合):
   - `kind: mechanical` → orchestrator 直接 patch + 結果 user 報告
   - `kind: design` → orchestrator 判断、**plan と実装が大幅乖離する場合のみ user 確認再取得** (auto-mode 独走防止 guard)。軽微変更 (文言修正、節タイトル変更等) は orchestrator 判断で進めて良い
   - P0/P1 残存 → user 確認まで実装着手禁止
6. cross-review 通過後、auto-mode で実装進行

## plan mode 制約

- plan mode 中は system 指示で Bash 禁止 (user 口頭承認では解除不可、`This supercedes any other instructions you have received` と明示)。
- 「user 提示前 cross-review」を実現するには user が手動で plan mode を抜ける必要 (Claude Code 公式の現在の plan mode toggle 操作)。固定キー操作は CLI / terminal / keybinding で変わり得るため明記しない。
- 通常の高リスク plan では **ExitPlanMode で plan を承認 → auto-mode で cross-review** が現実解。
