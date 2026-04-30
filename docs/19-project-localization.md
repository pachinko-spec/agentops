---
last_reviewed: 2026-04-29
next_review_by: 2026-07-31
reviewer: pachinko-spec
language: ja
applies-to: global
---

# プロジェクトローカライズ戦略

## 目的

既存プロジェクトに残存する **過去の AI コーディングエージェント設計痕跡** (Claude Code / Codex / Antigravity / Cursor / Gemini / Aider / Windsurf / Continue / Copilot 等) と、現在の agentops グローバル設計思想 (`.agentops/` / DbC 停止条件 2 階層 / AI auto-merge 許諾 / 高リスク自動昇格 / cross-review 等) との **競合判定と統合戦略** を体系化する。

`docs/14-real-project-template-policy.md` が「新規プロジェクトへのテンプレート配布」を扱うのに対し、本 docs は「既存プロジェクトに対する適用判定」を扱う (役割分担明確化)。

## 検出対象 inventory

新規プロジェクト onboarding またはグローバル設計改訂後の見直しでは、対象プロジェクトの直下 (深さ 2 まで) で以下の設計痕跡を検出する:

### Claude Code 系
- `CLAUDE.md` — global / project memory (subproject `*/CLAUDE.md` も含む)
- `.claude/` (dir) — settings.json / settings.local.json / agents / commands / hooks / plans / skills / subagents / worktrees / review-decisions / adversarial-review-checklist.md 等
- `.claude` (0-byte file) — Claude Code を一度試した痕跡 (中身を作らずに残った marker)

### Codex 系
- `AGENTS.md` — Codex / 共通指示 (AAIF 仕様で Claude Code も import 可)。subproject `*/AGENTS.md` も含む
- `.codex/` (dir) — config.toml / agents / hooks / skills / plugins
- `.codex` (0-byte file) — Codex を一度試した痕跡 (中身を作らずに残った marker)
- `AGENTS.override.md` — agentops 内のように共通 AGENTS.md を Codex 固有差分で上書きする場合

### Gemini 系
- `GEMINI.md` (root or subdir) — Gemini Code memory file
- `.gemini/` (dir)
- `.agent/` (dir) — Gemini / 汎用 AI 設計 dir (memory / personas / rules / skills / workflows / tmp 等のサブを持つ)

### Antigravity / Cursor / その他
- `.antigravity/`
- `.cursorrules` (古い形式) / `.cursor/` (新形式)
- `.aider*` (`.aider.conf.yml` / `.aider.chat.history.md` 等) / `.windsurfrules` / `.continue/` / `.copilot/`

### 本人標準 / 共通
- `.ai/` (dir) — 本人が標準化した AI 設計 dir (`contracts` / `decisions` / `gates` / `memory` / `reviews` / `tasks` 等の構造、`.agentops/` と responsibility 重複候補)
- `.agentops/` — 本リポジトリの運用形式

### 除外対象 dot dir / dot file

以下は AI 設計痕跡ではないため検出対象外 (実プロジェクトでよく見られる generic 痕跡):

- VCS / CI: `.git/` / `.github/` / `.gitlab/` / `.gitignore` / `.gitattributes`
- ランタイム / build / cache: `.tmp/` / `.cache/` / `.next/` / `.nuxt/` / `.svelte-kit/` / `.vite/` / `.turbo/` / `.parcel-cache/` / `node_modules/.cache/`
- デプロイ系: `.wrangler/` / `.vercel/` / `.netlify/` / `.firebase/` / `.gcloud/`
- IDE / editor: `.vscode/` / `.idea/` / `.zed/` / `.fleet/`
- 環境 / Python: `.venv/` / `.python-version` / `.tool-versions` / `.nvmrc`
- テスト / MCP server 自動生成: `.playwright-mcp/` / `.playwright/` (browser test artifact、MCP server local state)

### 検出網羅性

上記に列挙のない `.<vendor>/` / `.<vendor>rules` / `<VENDOR>.md` ファイルを発見したら **未列挙痕跡として user 確認に escalate** する (新興 AI ツールの追加に追従する)。除外対象 dot dir / dot file は escalate 不要 (AI 設計痕跡ではないため)。

### 補助情報
- `package.json` / `go.mod` / `composer.json` / `Cargo.toml` / `Gemfile` 等 (技術スタック判定)
- `wrangler.toml` / `vercel.json` / `Dockerfile` / `.github/workflows/` (デプロイ先判定)
- `git log -1 --format=%cI -- CLAUDE.md AGENTS.md GEMINI.md` と痕跡 dir の `stat -c %Y` (痕跡の鮮度判定)

## 競合判定マトリクス

旧設計が新グローバル方針と衝突する典型パターン:

| 旧設計の特徴 | 新グローバル方針との競合度 | 主な衝突箇所 |
| --- | --- | --- |
| `CLAUDE.md` に独自運用ルール (lint コマンド・テスト方針・branch 命名) を多数記述 | 低〜中 | プロジェクト固有ルールは尊重、グローバル本文に置きすぎないもの方針と整合判定 |
| `.codex/` に subagent 定義あり、グローバル subagent と被る | 中 | role 重複、cross-review 系の責務分離が崩れる |
| `.cursorrules` に lint / format ルール | 低 | 新グローバルは独立、共存可能 |
| `.claude/hooks/` に SECRET ガード以外の独自 hook | 中〜高 | グローバル hook (`agentops_guard.py` 系) と event 競合の恐れ |
| `.claude/plans/` で独自 plan 運用 (`.agentops/plans/` と二重) | 高 | plan 単一真ソース原則に反する |
| `.agentops/` 既存 + `.claude/plans/` 既存 = 二重 | 高 | 統合しないと next-session の参照先が分裂 |
| `.ai/` 既存 + `.agentops/` 未追加 = 本人標準と新グローバルの重複候補 | 高 | `.ai/{contracts,decisions,gates,memory,reviews,tasks}` と `.agentops/{plans,task-plans,tasks,handoffs,reviews,runs,archive}` の責務重複。片方を真ソース化するか、共存しつつ役割を分けるか判定要 |
| `.agent/` 既存 (Gemini 系汎用 dir) + 新グローバル設計 = 過去 Gemini 運用残存 | 中〜高 | memory / personas / rules / skills / workflows の責務が新カタログと重複。残置物として archive 化するか、新方針に組み替えるか判定要 |
| `0-byte の .codex / .claude` ファイル | 低 | 試行痕跡だけで実運用なし。削除または無視 |
| `AGENTS.md` に `auto-merge 許諾` と書かれていない | 中 | グローバル既定で許諾するか、project 側で明示拒否するか判断必要 |
| 旧 `archive/reference-kit-v1/` 由来の rule / skill / workflow を直コピー | 中 | 新カタログとの差分追従が止まっている可能性 |
| 過去の `decisions/` (ADR) | 低 | 履歴として尊重、新方針と齟齬は note 扱い |

## 4 戦略の意思決定木

判定軸:
1. **設計痕跡の有無**: CLAUDE.md / AGENTS.md / .codex / .claude / .cursorrules 等の存在
2. **技術スタック**: Nuxt / Next / PHP / Go / Rust / Python など (本人開発スタックは Nuxt / Next / PHP / Go)
3. **デプロイ先**: Cloudflare Workers/Pages / Xserver / GCP / ローカルサーバー / 未稼働
4. **痕跡の鮮度**: 最終 commit から 30 日以内 / 31-180 日 / 180 日以上 / 不明
5. **既存運用の重要度**: 本番運用中 / ステージング / プロトタイプ / 凍結
6. **ユーザー作業頻度**: 週次以上 / 月次 / 散発 / 休止中

```text
┌─ 痕跡なし or AGENTS.md のみ最小 ─→ greenfield (完全新規)
│
├─ 痕跡あり、痕跡 180 日以上前 + 休止中 ─→ freeze (凍結、override notice のみ)
│
├─ 痕跡あり、(痕跡 1 ヶ月以内 OR 31-180 日 + substantial な .agent/.ai/.claude 運用あり) + 週次以上稼働 + 競合度「中〜高」─→ inventory-rebuild (棚卸しマイグレーション)
│
├─ 痕跡あり、競合度「低〜中」+ 短命/プロトタイプ ─→ coexistence (共存、新 .agentops/ のみ追加)
│
└─ 上記いずれにも該当しない ─→ user 確認後に再判定
```

意思決定木の鮮度条件は「概ね 1 ヶ月以内 (`stat -c %Y` の差分で 31 日内外も許容)」を基準とする。1-6 ヶ月の痕跡でも `.agent/` / `.ai/` / `.claude/` に substantial な運用構造 (subdir 複数 + ファイル多数) が残っている場合は休止扱いせず inventory-rebuild に乗せる (実観察で 31 日前の `.agent/` / 1.5 ヶ月前の subproject CLAUDE.md でも実運用継続のケースがあるため)。

### greenfield (完全新規)

設計痕跡なし、または `AGENTS.md` だけで他は空。グローバル雛形 (`templates/claude/CLAUDE.md` / `templates/codex/AGENTS.md` / `.agentops/` 雛形) を新規適用する。

**チェックリスト**:
- [ ] グローバル `~/.claude/CLAUDE.md` / `~/.codex/AGENTS.md` を import する `CLAUDE.md` / `AGENTS.md` を作成
- [ ] `.agentops/{plans,task-plans,tasks,handoffs,reviews,runs,archive,prompts}/` 構造を生成
- [ ] `.agentops/archive/README.md` の table header を初期化
- [ ] 技術スタック固有の lint / test / build / deploy コマンドを project 側 docs に明記
- [ ] AI auto-merge 許諾を project でも適用するか拒否するか CLAUDE.md / AGENTS.md に記載

### inventory-rebuild (棚卸しマイグレーション)

旧 `CLAUDE.md` / `AGENTS.md` / `.claude/` / `.codex/` から **再利用可能な要素を抽出して新方針へ組み替える**。

**抽出ターゲット**:
- 旧 CLAUDE.md の「プロジェクト固有 lint / test / build コマンド」→ 新 CLAUDE.md (project 固有節)
- 旧 `.claude/agents/` の role 定義 → グローバル subagent と重複していないか判定 → 残すなら project subagent として継続
- 旧 `.claude/hooks/` の独自 hook → グローバル `agentops_guard.py` 系と event 衝突しないか確認 → 残すなら project hook として継続
- 旧 `.claude/plans/` の進行中 plan → `.agentops/plans/current.md` へ移行 (古い plan は `.agentops/archive/` へ)
- 旧 `.codex/` の subagent / hook → グローバル `~/.codex/` と responsibility 重複ないか
- 旧 `.cursorrules` → そのまま温存 (Cursor 利用者向け、新グローバルと独立)

**チェックリスト**:
- [ ] 旧設計痕跡の inventory を `~/.claude/.agentops/runs/<run-id>/inventory.md` または対象 project の `.agentops/runs/` に書き出す
- [ ] 各要素を「移行」「廃棄」「温存」「保留」のいずれかに分類
- [ ] 移行: 新方針へ組み替え + diff レビュー
- [ ] 廃棄: 削除または `archive/` へ退避
- [ ] 温存: 新グローバルと共存できる根拠を docs に書く
- [ ] 保留: 次セッションへ handoff
- [ ] グローバル設計改訂後の追従可能性を確保 (project 固有差分は `AGENTS.override.md` 等に集約)

### coexistence (共存)

旧設計を温存しつつ `.agentops/` のみ追加する。低リスクプロジェクト・短命プロトタイプ・本人作業頻度が低いプロジェクト向け。

**チェックリスト**:
- [ ] `.agentops/` 構造のみ追加 (旧 CLAUDE.md / AGENTS.md / GEMINI.md / `.codex` / `.claude/` / `.agent/` / `.ai/` / `.cursorrules` / `.cursor/` 等には触れない)
- [ ] `.agentops/plans/current.md` の Context に「既存設計と共存しており、見直しは inventory-rebuild に切り替える時に再評価」と記載
- [ ] グローバル設計改訂時の追従が薄くなる旨を CLAUDE.md / AGENTS.md に注記

### freeze (凍結)

既に運用安定 + 新規変更なし。設計痕跡 180 日以上前 + 休止中など。

**チェックリスト**:
- [ ] 既存ファイルに override notice (1-3 行) のみ追記:「本プロジェクトは凍結状態。グローバル設計改訂を反映する場合は本プロジェクトを `inventory-rebuild` で再起動する」
- [ ] `.agentops/` は **追加しない** (休止プロジェクトに新規 dir を生やすと管理対象が増える)
- [ ] 次回再起動時に本 docs を再評価する旨を `~/.claude/.agentops/handoffs/` に残すかは ad-hoc 判断

## 主要 5 プロジェクトへの dry-run 適用例

`~/dev/` 配下には観察時点で 30 directory 存在するが、本人が能動的に保守している主要 5 プロジェクト (ai-engine / ai-keiba / ai-utg / pachi-studio / ai-content-engine) に絞って dry-run する。残り 25 directory (休眠系 / template / 試作 / `dotfiles`) は本表の対象外で、`freeze` / `coexistence` 判定の素材として別途見直す。

実マイグレーションは各プロジェクト個別に user 承認を取って別 plan で実施する。観察日: 2026-04-29。

| プロジェクト | 痕跡 (root) | サブ痕跡 | スタック | 痕跡鮮度 | 競合度 | 推奨戦略 | 主な根拠 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ai-engine | CLAUDE.md / AGENTS.md / `.claude/` (dir) | `.claude/{settings.json,settings.local.json,agents,commands,hooks,worktrees,adversarial-review-checklist.md}` | Go | 4/4 (25 日前) | 中 | inventory-rebuild | `.claude/` 配下に複数 subdir (agents / commands / hooks / worktrees) と独自 adversarial-review-checklist。グローバル subagent / hook と二重化候補で抽出組み替えが必要 |
| ai-keiba | CLAUDE.md / AGENTS.md / `.codex` (0-byte file) / `.claude/` (dir) / `.ai/` (dir) | `.claude/{settings.json,settings.local.json,agents,commands,hooks,plans,adversarial-review-checklist.md}` / `.ai/{contracts,decisions,gates,memory,reviews,tasks}` / subproject `engine/{CLAUDE.md, .claude/{settings.json,agents,commands,hooks,adversarial-review-checklist.md}}` | Node | 4/11-4/25 (very new) | 高 | inventory-rebuild | `.codex` 0-byte (試行痕跡)、`.claude/plans/` と `.ai/` で plan 二重運用、subproject `engine/` にも独立した CLAUDE.md + `.claude/` 構造あり。最大規模の棚卸し対象 |
| ai-utg | CLAUDE.md / AGENTS.md / `.claude/` (dir) / `.ai/` (dir) | `.claude/{settings.json,settings.local.json,adversarial-review-checklist.md}` / `.ai/{contracts,decisions,gates,memory,reviews,tasks}` | Node | 4/11-4/25 | 中〜高 | inventory-rebuild | `.claude/` は最小だが `.ai/` フル構造あり。`.ai/` ↔ `.agentops/` 重複の判定が必要 |
| pachi-studio | CLAUDE.md / AGENTS.md / `.codex` (0-byte file) / `.claude/` (dir) / `.ai/` (dir) | `.claude/{plans,review-decisions}` / `.ai/{contracts,decisions,gates,memory,reviews,tasks}` | Go | 4/24-4/25 (very new) | 高 | inventory-rebuild | `.codex` 0-byte + `.claude/plans/` + `.claude/review-decisions/` + `.ai/` で独自運用が分厚い。plan 単一真ソース化が必要 |
| ai-content-engine | AGENTS.md / GEMINI.md / `.agent/` (dir) | `.agent/{GEMINI.md,memory,personas,rules,skills,workflows,tmp}` / `agent-templates/{GEMINI.md,AGENTS.md}` 等 | Node | 3/29 (1 ヶ月前) | 中 | inventory-rebuild | CLAUDE.md なしだが GEMINI.md + `.agent/` が substantial に存在し過去 Gemini 系運用の残存。greenfield ではなく Gemini 設計を新方針に棚卸しマイグレーションする対象 |

意思決定木の枝で **1 プロジェクトに 1 戦略が一意に決まる** ことを 5 件で確認した (各行の「主な根拠」がどの判定軸を満たすかは個別 inventory で書き出す)。

`freeze` と `coexistence` は主要 5 件には該当なし (全件稼働中、痕跡 1 ヶ月以内)。`~/dev/` 配下の休眠系 (`dotfiles` / `antigravity-boost` / `old_yomiroru` / `pinfo` / `nekos-hp` 等) は本表対象外で、これらに対する `freeze` / `coexistence` 適用は別 plan で扱う。

## ローカライズ workflow との連携

`workflows/catalog.md` の `project-localize` workflow が本 docs を実装する手順を定義する。`project-intake` の前段に置き、痕跡検出 → 戦略決定 → intake の順に進める。

```text
[新規 onboarding or グローバル設計改訂後見直し]
    ↓
[project-localize workflow] ← 本 docs と意思決定木で戦略決定
    ↓
[project-intake workflow] ← 対象パス・スタック・デプロイ先・検証コマンドを確認
    ↓
[plan-approval workflow] ← 計画承認
    ↓
[feature-delivery workflow] ← 実装着手
```

## CLI 仕様 (実装済 / dry-run only、`--apply` は将来仕様)

`agentops localize` サブコマンドは `tools/agentops_cli/__main__.py` に **実装済** ([docs/10-cli-wrapper.md](10-cli-wrapper.md))。本 docs の検出対象 / 4 戦略意思決定木 / DbC を機械適用する。

```text
scripts/agentops localize --project <path> [--dry-run] [--strategy auto|greenfield|inventory-rebuild|coexistence|freeze|needs-user-confirmation] [--run-id <id>] [--runs-root <path>]
```

- `--dry-run` (既定、唯一の動作モード): 痕跡 inventory + 推奨戦略 + 戦略チェックリストを report 出力
- `--strategy auto` (既定) で意思決定木により自動判定
- `--strategy <name>` で戦略を強制指定 (緊急対応用)
- 4 戦略どれにも明確に該当しない判定不能ケースは `needs-user-confirmation` で escalate (auto 推奨を強制しない)
- 出力 (mode 別):
  - `--dry-run` (既定): 対象 project には書き込まず、stdout に痕跡 inventory + 推奨戦略 + 戦略チェックリストを report 出力 + Claude Code 側グローバル `~/.claude/.agentops/runs/<run-id>/inventory.md` に保存 (`--runs-root` で test 等のために上書き可)
  - 承認後の本反映 (`--apply` 等、将来仕様): 対象 project の `.agentops/plans/current.md` 雛形を書き出し + グローバル run log 保存。dry-run と本反映の境界を CLI で明示し、誤って既存 project を書き換えない。

skill `/agentops:localize` 経由で対話的に呼ぶ用途も想定 ([templates/claude/skill/agentops-localize/SKILL.md](../templates/claude/skill/agentops-localize/SKILL.md))。skill の実体 (`~/.claude/skills/agentops-localize/`) は別 plan で生成。

## `project-localize` の DbC 適用

`project-localize` は [DbCと品質ゲート](03-dbc-and-quality-gates.md) を **既存プロジェクト評価の文脈に適用したもの**。標準 5 項目で展開する。

- **前提条件**: 対象 project path が読める、`git log -1 --format=%cI -- CLAUDE.md AGENTS.md GEMINI.md` が動く、技術スタック判定の補助情報 (`package.json` / `go.mod` 等) が読める、観察日時が `Asia/Tokyo` で記録される。
- **不変条件**: 既存 project ファイルを書き換えない (`--dry-run` モードのみ)。secret / 認証情報 / 個人データ / Webhook URL の値を inventory に書かない。痕跡内容の長文をそのまま転載しない (パス・存在・サイズ・鮮度のみ)。
- **完了条件**: inventory.md と推奨戦略 + 戦略チェックリストを report 出力するまで。docs/19 の検出対象 inventory に列挙されない痕跡が見つかった場合は user 確認に escalate して結果を inventory に追記。
- **禁止事項**: 既存 CLAUDE.md / AGENTS.md / GEMINI.md / `.codex/` / `.claude/` / `.agent/` / `.ai/` の中身を勝手に書き換えること、痕跡ファイルを delete / move すること、`agentops localize` 実装本体に触れること、5 件の主要プロジェクト以外で勝手に dry-run を広げること (各プロジェクト user 承認が必要)。
- **停止条件**: 2 階層構成。
  - **プロセス層**: project path が不在 / 4 戦略すべてが該当 (判定軸が不十分) / SECRET 検出 / 痕跡が `.git/` 内など除外パスにのみ存在 / 未列挙の AI 痕跡を発見し user 判断が必要 — いずれも skip せず作業を停止し DbC 停止条件として扱う。
  - **tool 実行層**: 将来 `agentops localize` 実装時に [`config/harness.yml`](../config/harness.yml) `defaults.stop_conditions.tool_layer` (max_tool_calls / no_progress_steps / circuit_breaker_cycle / cost_cap_usd_per_session) を継承する。本 docs では契約のみ規定し、実値は実装 plan で決める。

## スコープ外 (別 plan)

- `agentops localize` CLI 実装本体
- 既存 `~/dev/` 5 プロジェクトの実マイグレーション (各プロジェクト別 plan で user 承認後に着手)
- グローバル雛形 (`templates/claude/CLAUDE.md` / `templates/codex/AGENTS.md` / `.agentops/` 雛形) のローカライズ用変種追加
- 旧 `.cursorrules` / `.aider*` / `.windsurfrules` 等の自動マイグレーション (本 docs は判定基準のみ提供)

## 関連リンク

- [docs/14-real-project-template-policy.md](14-real-project-template-policy.md) — 新規プロジェクトへのテンプレート配布 (役割分担)
- [docs/02-workflow.md](02-workflow.md) — 標準ワークフロー (project-intake / plan-approval 連携)
- [docs/10-cli-wrapper.md](10-cli-wrapper.md) — `agentops localize` サブコマンド仕様 (将来実装)
- [docs/15-reference-kit-structure.md](15-reference-kit-structure.md) — 参照キット構造
- [docs/17-cross-reference.md](17-cross-reference.md) — rule ↔ skill ↔ workflow ↔ hook 逆参照表
- [templates/claude/skill/agentops-localize/SKILL.md](../templates/claude/skill/agentops-localize/SKILL.md) — Claude Code skill 雛形
- [rules/catalog.md](../rules/catalog.md) — `project-integration-policy` 候補
- [skills/catalog.md](../skills/catalog.md) — `project-localize-inventory` 候補
- [workflows/catalog.md](../workflows/catalog.md) — `project-localize` 候補
