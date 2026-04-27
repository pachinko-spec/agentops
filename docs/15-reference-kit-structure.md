# reference kit structure

## 位置づけ

この文書は、`rules/`、`skills/`、`workflows/` を今後どの置き場へ整理するかの分類案と、005 で決めた移行方針です。005 では対象ファイルの大きな移動や削除は行わず、移行候補、archive 方針、参照切れ確認方法を記録します。

分類は次の意味で使います。

- 現役参照資料: グローバル設定見直し時や実プロジェクト作業時に、引き続き参照候補として残すもの。
- `examples/` 候補: 特定ツールや過去の実装例として、最小見本に寄せるもの。
- `templates/` 候補: Claude Code / Codex などへ採否を判断して取り込む、CLI 用テンプレートに寄せるもの。
- `checklists/` 候補: skill や workflow 形式より、確認項目として読む方が自然なもの。
- archive 候補: 重複、古い前提、特定ツール依存が強く、現役参照から外す可能性があるもの。

## 棚卸しサマリー

- `rules/`: README を含め 12 ファイル。
- `workflows/`: README を含め 16 ファイル。
- `skills/`: README と 53 個の `SKILL.md`。
- 直接参照は README、docs、config、workflows、skills README、`.agentops` に広く存在する。
- `config/claude/CLAUDE.md` と `config/codex/AGENTS.md` は、`workflows/project-intake.md`、`workflows/web-system-design.md`、`workflows/deployment-target-selection.md` を具体名で参照している。
- `workflows/code-review.md` は `skills/review/*`、`workflows/design-review.md` は `skills/design/*`、`workflows/feature-delivery.md` は `skills/review/*` を参照している。
- `config/understand-anything-policy.json` は `rules/**`、`skills/**`、`workflows/**` を対象 glob として含む。

## 005 での移行方針

005 では、過剰な見本群をすぐに削除せず、次の方針で扱う。

- `rules/`: 現時点では全体を現役参照資料として残す。表現が強い箇所は、構造移動より先に語彙を弱める候補として扱う。
- `workflows/`: 実プロジェクト作業の入口や中核手順は現役参照資料として残す。確認項目型は `checklists/` 候補、CLI へ取り込む手順型は `templates/workflows/` 候補、Understand-Anything 固有手順は `examples/` または archive 候補として扱う。
- `skills/`: `SKILL.md` 形式のまま使う場合は `templates/skills/` 候補、観点だけを残す場合は `checklists/` 候補として扱う。Understand-Anything 固有 skill は `examples/` または archive 候補とする。
- `examples/`: 特定ツール、特定スクリプト、過去の実装に依存するが、見本として価値があるものを置く候補にする。
- `templates/`: Claude Code / Codex などへ採否を判断して取り込む、CLI 用または実プロジェクト用の雛形を置く候補にする。
- `checklists/`: workflow や skill として常時入口に置くより、確認項目として読む方が自然なものを置く候補にする。
- `.agentops/archive/`: 完了した plan、task-plan、task、review、run の運用履歴だけを置く。参照キット本体の見本ファイルは、`.agentops/archive/` へ混ぜない。
- repository-level archive: 参照キット本体のファイルを archive する必要が出た場合だけ、ユーザー承認後に置き場を決める。既存の `.agentops/archive/` とは役割を分ける。

大きな移動や削除に入る前には、次をユーザーへ提示して承認を得る。

- 移動、削除、archive 対象の正確なファイル一覧。
- 移動先を `examples/`、`templates/`、`checklists/`、archive のどれにするか。
- README、docs、config、workflows、skills、scripts、`.agentops` からの参照更新対象。
- `config/understand-anything-policy.json` の glob 変更要否。
- 検証コマンドと、参照切れが見つかった場合の戻し方。

## rules 分類案

`rules/` は常時適用に近い短い判断基準が中心のため、現時点では全体を現役参照資料として残す。ただし、README、DRY、責務分離まわりの語彙は、後続作業で弱める候補とする。

| ファイル | 主分類 | 補助候補 | 理由と影響 |
| --- | --- | --- | --- |
| `rules/README.md` | 現役参照資料 | `templates/` の索引候補 | `rules/` の入口。現在は「実行時の正本」「投影」という強い語彙が残るため表現更新候補。 |
| `rules/planning-approval.md` | 現役参照資料 | `checklists/` 候補 | 計画承認と `.agentops` の基本運用。作業安全性に直結する。 |
| `rules/project-template-scope.md` | 現役参照資料 | なし | 実プロジェクトへ持ち出す条件を定義する中核資料。 |
| `rules/deployment-target-policy.md` | 現役参照資料 | `checklists/` 候補 | Cloudflare、Xserver、GCP、ローカルサーバーの選定軸。実プロジェクトでも再利用できる。 |
| `rules/dry-principle.md` | 現役参照資料 | 語彙更新候補 | 「正本」「投影物」が複数残る。概念は必要だが「中心資料」「設定雛形」へ寄せる候補。 |
| `rules/source-of-truth.md` | 現役参照資料 | 語彙更新候補 | 責務分離の中核だが、タイトルと本文に「正本」が残る。`reference-boundaries.md` のような名称変更候補。 |
| `rules/language-policy.md` | 現役参照資料 | なし | 日本語運用の基本。移動不要。 |
| `rules/review-policy.md` | 現役参照資料 | `checklists/` 候補 | レビュー優先度の短い基準。現役でよい。 |
| `rules/design-policy.md` | 現役参照資料 | `checklists/` 候補 | 設計時の基本質問。現役でよいが checklist 化も可能。 |
| `rules/git-and-branch-policy.md` | 現役参照資料 | なし | GitHub PR 運用の中核。移動不要。 |
| `rules/documentation-policy.md` | 現役参照資料 | `checklists/` 候補 | docs 更新の完了条件。現役でよい。 |
| `rules/freshness-policy.md` | 現役参照資料 | なし | 最新性確認の基本。移動不要。 |

## workflows 分類案

`workflows/` は「作業手順」と「確認チェックリスト」と「特定ツール手順」が混在している。後続作業では、入口と実プロジェクト向けの少数を現役参照として残し、確認項目型は `checklists/`、CLI へ取り込む手順型は `templates/workflows/`、Understand-Anything 固有手順は `examples/` または archive 候補へ分けるのが自然。

| ファイル | 主分類 | 補助候補 | 理由と影響 |
| --- | --- | --- | --- |
| `workflows/README.md` | 現役参照資料 | 語彙更新候補 | 入口として残す。現在は「作業手順の正本」が残るため表現更新候補。 |
| `workflows/project-intake.md` | 現役参照資料 | `templates/` 候補 | 実プロジェクト開始時の入口。README、skills README、docs、config から参照されるため移動時の影響が大きい。 |
| `workflows/feature-delivery.md` | 現役参照資料 | `templates/` 候補 | 実装から検証、docs、レビューまでの基本流れ。実プロジェクト向けの中核。 |
| `workflows/web-system-design.md` | 現役参照資料 | `templates/` 候補 | config から具体名で参照される。Web システム設計の中核。 |
| `workflows/deployment-target-selection.md` | 現役参照資料 | `templates/` または `checklists/` 候補 | config から具体名で参照される。デプロイ選定の詳細確認に使う。 |
| `workflows/release-readiness.md` | `checklists/` 候補 | `templates/` 候補 | リリース前確認の項目性が強い。移動時は docs/14 の参照更新が必要。 |
| `workflows/production-operations.md` | `templates/` 候補 | `checklists/` 候補 | 運用作業の手順テンプレート。実プロジェクト向けだが常時入口ではない。 |
| `workflows/plan-approval.md` | `templates/` 候補 | `checklists/` 候補 | `.agentops` 運用込みの手順。CLI 設定テンプレートへ寄せる候補。 |
| `workflows/design-review.md` | `checklists/` 候補 | `templates/` 候補 | `skills/design/*` を選ぶ入口。レビュー観点として checklist 化しやすい。 |
| `workflows/code-review.md` | `checklists/` 候補 | `templates/` 候補 | `skills/review/*` を選ぶ入口。レビュー checklist と相性がよい。 |
| `workflows/docs-update.md` | `checklists/` 候補 | 語彙更新候補 | 「正本」「投影物」が残る。docs 更新チェックリストへ移す候補。 |
| `workflows/dependency-introduction.md` | `checklists/` 候補 | なし | 新規依存導入時の確認項目。チェックリスト化が自然。 |
| `workflows/freshness-audit.md` | `checklists/` 候補 | `templates/` 候補 | 最新性監査の確認項目。`config/freshness-sources.yml` と合わせる必要がある。 |
| `workflows/session-handoff.md` | `templates/` 候補 | `checklists/` 候補 | セッション復帰用の手順。CLI 反映テンプレートとして使える。 |
| `workflows/understand-anything-bootstrap.md` | `examples/` 候補 | archive 候補 | 特定ツールとスクリプトに依存するため、最小見本または別 docs に寄せる候補。 |
| `workflows/understand-anything-graph-update.md` | `examples/` 候補 | archive 候補 | 特定ツールの PR/merge 後手順。現役に残すなら補助ツール docs へ移す候補。 |

## skills 分類案

`skills/` の各 `SKILL.md` は Claude Code / Codex へ取り込む候補としての形式を持つため、主分類は `templates/skills/` 候補とする。本文は短い「確認すること」が中心なので、将来的に `checklists/` へ内容を抽出することもできる。

### skills root

| ファイル | 主分類 | 補助候補 | 理由と影響 |
| --- | --- | --- | --- |
| `skills/README.md` | 現役参照資料 | `templates/skills/README.md` 候補 | skill 群の入口。グローバル化候補と実プロジェクト向けテンプレートの説明を持つ。 |

### design skills

| ファイル | 主分類 | 補助候補 |
| --- | --- | --- |
| `skills/design/accessibility/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/api-contract/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/architecture-boundary/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/business-logic/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/cost/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/data-model/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/domain-model/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/experimentation/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/migration/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/observability/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/operability/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/performance/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/privacy/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/profitability/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/reliability/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/requirements/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/security/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |
| `skills/design/ux/SKILL.md` | `templates/skills/` 候補 | `checklists/design/` 候補 |

### implementation skills

| ファイル | 主分類 | 補助候補 |
| --- | --- | --- |
| `skills/implementation/deployment-adapter/SKILL.md` | `templates/skills/` 候補 | `checklists/implementation/` 候補 |
| `skills/implementation/test-automation/SKILL.md` | `templates/skills/` 候補 | `checklists/implementation/` 候補 |
| `skills/implementation/web-backend/SKILL.md` | `templates/skills/` 候補 | `checklists/implementation/` 候補 |
| `skills/implementation/web-frontend/SKILL.md` | `templates/skills/` 候補 | `checklists/implementation/` 候補 |

### review skills

| ファイル | 主分類 | 補助候補 |
| --- | --- | --- |
| `skills/review/accessibility/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |
| `skills/review/api-compatibility/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |
| `skills/review/correctness/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |
| `skills/review/cost/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |
| `skills/review/data-integrity/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |
| `skills/review/dependency-supply-chain/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |
| `skills/review/docs/SKILL.md` | `templates/skills/` 候補 | 語彙更新候補 |
| `skills/review/maintainability/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |
| `skills/review/migration/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |
| `skills/review/observability/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |
| `skills/review/performance/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |
| `skills/review/privacy/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |
| `skills/review/release-readiness/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |
| `skills/review/reliability/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |
| `skills/review/security/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |
| `skills/review/testability/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |
| `skills/review/ux/SKILL.md` | `templates/skills/` 候補 | `checklists/review/` 候補 |

### docs skills

| ファイル | 主分類 | 補助候補 |
| --- | --- | --- |
| `skills/docs/api-docs-writer/SKILL.md` | `templates/skills/` 候補 | `checklists/docs/` 候補 |
| `skills/docs/changelog-release-notes/SKILL.md` | `templates/skills/` 候補 | `checklists/docs/` 候補 |
| `skills/docs/decision-log-writer/SKILL.md` | `templates/skills/` 候補 | `checklists/docs/` 候補 |
| `skills/docs/docs-maintainer/SKILL.md` | `templates/skills/` 候補 | 語彙更新候補 |
| `skills/docs/onboarding-writer/SKILL.md` | `templates/skills/` 候補 | `checklists/docs/` 候補 |
| `skills/docs/prompt-skill-authoring/SKILL.md` | `templates/skills/` 候補 | 語彙更新候補 |
| `skills/docs/runbook-writer/SKILL.md` | `templates/skills/` 候補 | `checklists/docs/` 候補 |

### ops skills

| ファイル | 主分類 | 補助候補 |
| --- | --- | --- |
| `skills/ops/cross-model-delegate/SKILL.md` | `templates/skills/` 候補 | `checklists/ops/` 候補 |
| `skills/ops/freshness-audit/SKILL.md` | `templates/skills/` 候補 | `checklists/ops/` 候補 |
| `skills/ops/production-operations/SKILL.md` | `templates/skills/` 候補 | `checklists/ops/` 候補 |
| `skills/ops/review-loop-guard/SKILL.md` | `templates/skills/` 候補 | `checklists/ops/` 候補 |
| `skills/ops/session-handoff/SKILL.md` | `templates/skills/` 候補 | `checklists/ops/` 候補 |
| `skills/ops/understand-anything-bootstrap/SKILL.md` | `examples/` 候補 | archive 候補 |
| `skills/ops/understand-anything-update/SKILL.md` | `examples/` 候補 | archive 候補 |

## 強い語彙の扱い候補

次の箇所は「正本」「投影物」などの強い語彙が残る。005 では記録に留め、構造整理や CLI テンプレート整理と合わせて、後続作業で置換する。

| ファイル | 残る語彙 | 扱い候補 |
| --- | --- | --- |
| `rules/README.md` | `実行時の正本`、`投影` | `参照候補`、`設定雛形へ要約・調整` へ寄せる。 |
| `rules/dry-principle.md` | `正本`、`投影物` | `中心資料`、`反映候補`、`設定雛形` へ寄せる。 |
| `rules/source-of-truth.md` | `正本分離`、`正として読む` | `責務分離`、`優先して確認する資料` へ寄せる。 |
| `workflows/README.md` | `作業手順の正本` | `作業手順の参照資料` へ寄せる。 |
| `workflows/docs-update.md` | `正本`、`投影物` | docs 更新時の `中心資料` と `設定雛形` の関係へ言い換える。 |
| `skills/review/docs/SKILL.md` | `正本と投影物` | `中心資料と反映候補` へ寄せる。 |
| `skills/docs/docs-maintainer/SKILL.md` | `正本と投影物` | `中心資料と反映候補` へ寄せる。 |
| `skills/docs/prompt-skill-authoring/SKILL.md` | `正本と投影物` | `常時参照資料と設定雛形` へ寄せる。 |

`decisions/2026-04-27-agentops-reference-kit-refactor.md` と archive 内のタスクには、避けたい語彙を説明する文脈として同じ語が残る。これは判断履歴として残してよい。

## 影響範囲

構造変更を実施する場合、次の参照更新が必要になる。

- README の docs 一覧と `rules/README.md`、`skills/README.md`、`workflows/README.md` へのリンク。
- `docs/01-philosophy.md`、`docs/07-global-vs-project.md`、`docs/14-real-project-template-policy.md` にある `rules/`、`skills/`、`workflows/` の位置づけ説明。
- `config/claude/CLAUDE.md` と `config/codex/AGENTS.md` の具体パス参照。
- `config/understand-anything-policy.json` の対象 glob。
- `workflows/code-review.md`、`workflows/design-review.md`、`workflows/feature-delivery.md` から `skills/*` への参照。
- `skills/README.md` から `workflows/project-intake.md` への参照。
- `.agentops/prompts/next-session.md` や task-plan に残る旧タスク参照。

移動を実施する前には、少なくとも次を確認する。

```sh
rg -n "rules/|skills/|workflows/" README.md docs config workflows skills scripts .agentops
rg -n "正本|投影物" README.md docs rules workflows skills config scripts .agentops
git diff --check
scripts/agentops-watch check --projects config/projects.yml
```

## 後続作業への提案

- Claude Code / Codex 用テンプレートの観点で `templates/skills/`、`templates/workflows/`、`checklists/` の最小構成を決める。
- 実際の移動を行う場合は、この分類案と 005 の移行方針を元に、README/docs/config/workflows/skills/scripts の参照更新案をユーザー承認後に実施する。
- Understand-Anything 関連は、補助ツール docs、`examples/`、archive のどこへ置くかを個別判断する。
