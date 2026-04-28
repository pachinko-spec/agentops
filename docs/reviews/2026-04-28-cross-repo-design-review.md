# agentops 横断設計レビュー 2026-04-28

> 評価日: 2026-04-28（Asia/Tokyo）
> 対象コミット: `a82fefb`（branch: main、dirty 0、構成: 16 docs / 12 rule 候補 / 31 skill 候補 / 15 workflow 候補）
> 評価者: pachinko-spec（主 orchestrator: Claude Opus 4.7 1M、cross-reviewer: Codex CLI）
> 評価軸: A 一貫性 / B 契約と停止 / C マルチモデル / D 鮮度 / E 運用負荷 / F 拡張性
> 評価方式: A–E スコア（A=業界先進 / B=妥当 / C=最低限 / D=不足 / E=欠落）。`+` / `−` は同一段の上位 / 下位四分位。点数は付けない
> last-reviewed: 2026-04-28
> next-review-by: 2026-07-31（四半期 + Claude Code / Codex / AAIF メジャー変更時）
> 言語: 日本語

---

## 0. エグゼクティブサマリ

agentops は **「Claude Code / Codex のグローバル設定を 1 人開発者が日本語で運用するための参照キット」** という珍しい立ち位置の設計思想集である。`docs/` 16 ファイル、`rules/`・`skills/`・`workflows/` の候補カタログ（rule 12 / skill 31 / workflow 15）、`config/model-catalog.yml`（model_id 意図的 null）、`templates/{claude,codex,agentops}/` 雛形、CLAUDE.md ↔ AGENTS.md 対称運用、`.agentops/` 階層運用、`scripts/agentops delegate` cross-model ラッパまでを 1 リポジトリで束ねている。

**強みは 3 点**: (1) DbC（前提・不変・完了・禁止・停止）を全タスクに適用し業界の Agent Behavioral Contracts 論文（arXiv:2602.22302, 2026-02）と並走する形式知、(2) Reviewer は所見のみ・主 orchestrator が決定する production 寄り cross-review 設計、(3) `.agentops/plans / task-plans / tasks / handoffs / archive/` の責務階層が Anthropic `claude-progress.txt` より細かく業界類例が乏しい先進性。

**弱みは 3 点**: (1) AAIF 設立（2025-12-09）以降「AGENTS.md → CLAUDE.md import」が公式推奨になったが agentops は両方併記で二重メンテ、(2) 停止条件はプロセス層（レビュー 2 周）は明確だが tool 実行層（max_tool_calls / no-progress / circuit breaker）が未規定、(3) `.github/`（CI / PR template / CODEOWNERS）が不在で品質ゲートがローカル hooks のみに依存（`.gitignore` は存在するが secret 拡張子は未列挙）。

**最重要提案 3 件**: P0-02 tool 実行層の停止条件追加（唯一の P0）、P1-07 CI 最小セット導入と `.gitignore` への secret 拡張子追加、P1-08 AGENTS.md 一本化（CLAUDE.md は `@AGENTS.md` import + 差分のみ）。詳細は §7。

総合評価: **設計思想として筋がよく、業界・学術コンセンサスと相互参照可能な水準にある**。残課題は二重メンテと自動化の薄さに集中しており、半年以内に解消可能な範囲。

---

## 1. 評価の前提とスコープ

### 1.1 対象

`/home/otaku/agentops` リポジトリ全体。`docs/`、`rules/`、`skills/`、`workflows/`、`config/`、`templates/`、`scripts/`、`tools/agentops_cli/`、ルートの `CLAUDE.md` と `AGENTS.md`、`.agentops/`（運用記録）、`decisions/`（設計判断ログ）、`archive/reference-kit-v1/`（旧版）。

### 1.2 想定読者

agentops 保守者本人（Claude Code / Codex 利用者、1 人開発者）。Web システム（Nuxt / Next.js / PHP / Go）を Cloudflare Workers・Pages、Xserver、GCP、ローカルに展開する想定。

### 1.3 非対象

- グローバル `~/.claude/CLAUDE.md` および `~/.codex/AGENTS.md` の実体への反映作業
- 個別提案の実装（別 plan）
- 機密値・本番データ・課金影響を伴う検証

### 1.4 評価方法

(a) Explore × 3 並列でリポジトリ全 docs / カタログ / メタファイルを抽出、(b) Claude Code / Codex 公式仕様を一次情報で再確認、(c) 学術・業界ブログを 2025-2026 動向中心に走査、(d) Plan agent で報告書アーキテクチャを設計、(e) 6 軸 × A-E スコアで定性評価。点数化はしない（恣意性回避）。

---

## 2. リポジトリ構造の俯瞰

```
/home/otaku/agentops
├── README.md                       # 自己定義・参照キットとしての位置づけ
├── CLAUDE.md / AGENTS.md           # プロジェクト指示（章立て対称）
├── docs/                           # 設計思想 16 ファイル（philosophy / workflow / DbC / ...）
├── rules/        catalog.md +      # rule 候補 12 件（global/project 判定列あり）
├── skills/       catalog.md +      # skill 候補 31 件（design/implementation/review/docs/ops）
├── workflows/    catalog.md +      # workflow 候補 15 件（出力先明示）
├── config/                         # model-catalog.yml / harness.yml / freshness-sources.yml
│   └── claude/CLAUDE.md, codex/AGENTS.md  # ~/.claude, ~/.codex 反映用雛形
├── templates/    {claude,codex,agentops}/  # CLI 別 skill / subagent / .agentops 雛形
├── scripts/      agentops          # delegate ラッパ
│                 agentops-watch    # 監視 CLI
│                 check-protected-branch / check-tests-before-push / install-hooks
├── tools/agentops_cli/             # delegate 実装（Python）
├── decisions/                      # 設計判断ログ（背景・代替案・採用理由）
├── archive/reference-kit-v1/       # 旧版（現役カタログと並存）
└── .agentops/                      # plans / task-plans / tasks / reviews / runs / handoffs / archive / prompts
```

### 主要メタファイル

- `CLAUDE.md` ↔ `AGENTS.md`: 章立て完全対称（Claude / Codex のパス・CLI 名差分のみ）
- `config/model-catalog.yml`: 7 ロール（orchestrator_frontier / architect_frontier / review_frontier / coding_frontier / coding_fast / research_fast / docs_agent）。**model_id は全ロール意図的に null**、使用直前に公式 docs で確認する設計
- `config/harness.yml`: agent run の検証仕様（sandbox policy / allowed_read_only / allowed_validation / require_confirmation / forbidden）
- `config/freshness-sources.yml`: 情報源の鮮度監視ポリシー
- `.agentops/`: 直近 2026-04-28 に運用ルール階層化が反映済み（未完了タスク 0、健全）

### 不在 / 未拡充

- `.github/`（GitHub Actions / PR template / CODEOWNERS）が無い
- `.gitignore` は存在（`.tmp/`、`.agentops/runs/*`、`__pycache__/`、`.pytest_cache/` 等 22 行）するが、secret 拡張子（`.env*`、`*.key`、`credentials*.json` 等）の明示列挙が未実施
- `LICENSE` / `CHANGELOG` の有無は本評価ではスコープ外

---

## 3. 設計思想の評価（軸別）

### 3.A 設計思想の一貫性 (Coherence) — スコア B

**定義**: philosophy（最上位思想）と下位 doc / rule / skill / workflow / template / config が論理整合し、用語・参照・例示が統一されているか。

**観察事実**: docs/01-philosophy.md の中核原則（DbC、ACI、検証可能性、コンテキスト衛生、時刻方針、コメント方針）は下位 doc から相互参照されており骨格は強い。CLAUDE.md ↔ AGENTS.md の章立て対称性は CLI agnostic な作業フローを支えている。一方、用語ゆれが複数箇所に残る: "orchestrator" vs "orchestrator_frontier"（context 文と model-catalog.yml ロール名で混在）、"cross-review" vs "cross-model-delegate"（skills/catalog.md L41 と L55、config/claude/CLAUDE.md L99）、"harness" vs "harness spec"（docs/12-harness-engineering.md 文脈依存）。DbC の記述は docs/01・03・09・12 に重複し DRY 違反気味。philosophy.md L14「単純で合成可能な workflow を優先」と docs/02-workflow.md L27-53 の 24 ステップ標準サイクルにはトーンの食い違いがある。

**業界比較**: agents.md 公式（AAIF 配下）は「短く、機械可読、相互参照可」を推奨。Claude Code 公式は CLAUDE.md 200 行未満を推奨。agentops の docs は個別ファイルが平均 80–150 行で読みやすい範囲だが、相互参照の双方向性が弱い。

**B（妥当）の理由**: 骨格は強く致命的矛盾は無いが、用語ゆれと DbC 重複が複数箇所に残るため A までは行かない。P1 で用語統一表を追加し、DbC 記述を philosophy.md に集約 + 他からは参照のみとすれば A に届く（philosophy.md L14 と docs/02-workflow.md の 24 ステップ標準サイクルのトーン差も併せて整理）。

### 3.B 契約と停止条件 (Contract & Termination) — スコア B+

**定義**: DbC（前提・不変・完了・禁止・停止）が運用可能粒度で定義され、レビュー粒度・修正ループ上限・tool 実行層循環防止が機能するか。

**観察事実**: docs/03-dbc-and-quality-gates.md は前提・不変・完了・禁止・停止の 5 条件を全タスクに適用するテンプレートを提供。レビュー修正は最大 2 周、3 周目は統合判断またはユーザー確認、P0/P1 必修・P2 判断・P3 単独継続禁止という分類が CLAUDE.md / docs/05-review-policy.md に明記。一方、tool 実行層（個別ツール呼び出しの循環、no-progress、cost cap）への停止条件は未規定。「修正後は必ず再レビュー」が typo / リンク修正にも適用されうる粒度問題が残る。停止条件「レビュー修正 2 周」の単位（task / セッション / 指摘 count）が CLAUDE.md L47 で曖昧。

**業界比較**: Bhardwaj "Agent Behavioral Contracts"（arXiv:2602.22302, 2026-02-25）は 6-tuple（P / Hard Invariants / Soft Invariants / Hard Governance / Soft Governance / Recovery）と (p, δ, k)-satisfaction を提案。agentops の 5 条件と直接対応可能で、「禁止」が Hard Governance に、「停止」が Recovery + (p, δ, k) bound に対応。Cordum / Meganova の業界記事は max_steps、no-progress rule、circuit breaker、cost cap を layered defense として推奨。Anthropic Managed Agents（2026-04-08）は session を append-only event log として定義し replay-driven で停止判定可能にしている。

**B+ の理由**: プロセス層は学術と並走する先進性があり、ABC 論文より「停止」を独立カテゴリ化している点で運用しやすい。tool 実行層の停止規定欠落で A に届かないが、追加すれば確実に A 帯へ。

### 3.C マルチモデル運用 (Multi-Model Orchestration) — スコア A−

**定義**: model-routing / cross-review / handoff / cross-model-delegate が ACI として再現性を持ち、決定権の所在が明示されているか。

**観察事実**: docs/04-model-routing.md は 7 論理ロール × target_cli（codex / claude）で実モデルを使用直前に決定する設計。docs/05-review-policy.md と CLAUDE.md は「reviewer は所見のみ、最終判断は主 orchestrator」を明文化。cross-review トリガ・preferred_reviewer_difference・decision_owner・escalation_rules が config/model-catalog.yml に列挙。`scripts/agentops delegate` ラッパは request / status / stdout / stderr / result を `.agentops/runs/<timestamp>/` に残し再現可能。dry-run / timeout / command_template / security 配慮も P2 hardening 済み。CLAUDE.md ↔ AGENTS.md 対称性で CLI agnostic な実行が可能。

**業界比較**: MAJ-EVAL（arXiv:2507.21028）や Meta-Judges（arXiv:2504.17087）は judge 融合の最適化が研究主流だが、agentops の「決定権 orchestrator 専任」は production 寄りの合理的選択で、コストと再現性の両立に優れる。OpenHands SDK（arXiv:2511.03690, 2025-11）の 4 層（agent IF / security / multi-interface / sandboxed multi-LLM routing）と構造的に重なる。

**A− の理由**: 設計が業界先進と並走しており、cross-review / handoff / decision-owner の三点セットは学術コンセンサスと整合。reviewer に persona（security / API / DX）を割り当てる発展余地（P2 提案へ）を残して A−。

### 3.D 鮮度と出典管理 (Freshness & Provenance) — スコア B−

**定義**: docs / model_id / 外部 URL の鮮度監査が仕組み化され、AI 記憶ではなく一次情報を優先する運用が機能しているか。

**観察事実**: docs/06-freshness-and-monitoring.md と config/freshness-sources.yml で監視対象（CLI / model id / MCP / フレームワーク LTS）を列挙し、Context7 / 公式 docs / GitHub release notes / package registry / security advisory を一次情報として優先する原則を明文化。`agentops-watch` 監視 CLI は dirty files / stuck run / 未完了 task / freshness 確認 / Discord 通知をスコープに置く設計。一方、(a) docs/01–15 の多くに last-reviewed 日が無い、(b) freshness-sources.yml の `max_age_days` 実装が monitoring-cli の「今後の拡張」のまま、(c) docs/04-model-routing.md L62-67 の 2026-04-28 採用例は時点固定で更新スキームが不明、(d) `code.claude.com/docs` への URL 移行（旧 docs.anthropic.com からの 301）に追随できているか不明。

**業界比較**: AAIF / agents.md 公式は AGENTS.md に updated 日付を入れることを推奨。Anthropic Managed Agents は session の append-only event log で "確認時点" を記録する設計を提示。

**B− の理由**: 思想は明確だが実装が追いついていない。last-reviewed 導入と freshness-sources.yml の max_age_days 実装で B+〜A− に上がる。

### 3.E 運用負荷と自動化 (Operability) — スコア B−

**定義**: 設定適用・hook 実行・監視・PR ガードが手動 / 自動どちら寄りで、コストに見合うか。

**観察事実**: グローバル設定 `~/.claude/CLAUDE.md` への自動反映なし。docs/16-global-settings-application-checklist.md は反映前→ MCP → hooks → skills/subagents → permissions → 反映後の 6 段チェックリストだが、毎回手動実行が必要で重い。`.github/`（GitHub Actions / PR template / CODEOWNERS）不在で PR 強制ガードが無い。`.gitignore` は存在し `.tmp/` / `.agentops/runs/*` / `__pycache__/` 等を除外しているが、secret 拡張子（`.env*` / `*.key` / `credentials*.json` 等）が明示列挙されておらず、誤 commit 防止としてはあと一歩。Git hooks（`scripts/check-protected-branch` / `check-tests-before-push`）は提供されているが install は手動（`scripts/install-hooks --target . --mode copy`）。`agentops-watch` は監視 CLI として設計されているが Discord 通知などは「今後の拡張」段階。archive インデックス（`.agentops/archive/README.md`）は手動更新。`prompts/next-session.md` の動的判定（tasks / handoffs / 削除）も手動。

**業界比較**: Anthropic Managed Agents は session / harness / sandbox を decouple して replay-driven。Cursor blog はサンドボックス API 抽象化（macOS Seatbelt + Linux Landlock+seccomp + WSL2）を統一。OpenHands SDK は production-ready harness を 4 層に再構成。

**B− の理由**: `.gitignore` ベースは整っており Git hooks も用意されているが、CI 強制ガードと secret 拡張子の明示が欠けるため B+ には届かない。最小 CI（lint / docs link check / freshness check）+ `.gitignore` 拡充 + archive 自動更新 hook の 3 点で B+ 帯へ進む。

### 3.F 拡張性と再利用 (Extensibility) — スコア B

**定義**: rule / skill / workflow の追加・archive 廃止・他プロジェクト派生が低コストで、規約とテンプレートが揃っているか。

**観察事実**: rules / skills / workflows カタログは Markdown 表形式で統一フォーマット。rule には「global 候補 / project 候補」の採用判断列が明記されている（rules/catalog.md L7-L18 に候補 12 件）。docs/14-real-project-template-policy.md と docs/15-reference-kit-structure.md で `~/dev` 配下 Web システムへの持ち出し方針を提示。templates/{claude,codex,agentops}/ に skill / subagent / .agentops 雛形あり。一方、(a) skill / workflow には「採用判断・見送り条件」列がない（rule のみ）、(b) skill frontmatter の具体例が SKILL.md 雛形に無い（agentskills.io 標準キーの例示が必要）、(c) rule ↔ skill ↔ workflow の逆参照・マッピングが無い（rule → どの skill / hook で実装するか不明）、(d) `archive/reference-kit-v1/` 旧版が deprecation マーカー無しで現役カタログと並存し混乱の余地。

**業界比較**: Claude Code 公式は SKILL.md frontmatter に `name / description / when_to_use / argument-hint / arguments / disable-model-invocation / user-invocable / allowed-tools / model / effort / context: fork|agent / hooks / paths / shell` を提示。AAIF / agents.md 公式は monorepo の各 package に AGENTS.md を置く拡張パターンを示す。

**B の理由**: 候補カタログ思想は妥当だが、frontmatter 例示・逆参照・deprecation マーカーで具体性が不足。3 点を補えば A− へ。

---

## 4. 業界・学術ベンチマークとのギャップ

### 4.1 Claude Code 公式仕様（2026-04 時点）

公式 docs URL は `docs.anthropic.com` から `code.claude.com/docs` へ 301 移行済み。**Slash commands は Skills に統合**され、`.claude/commands/*.md` は skills の入口扱いとなった。**Skills は 2025-12 に open standard 化**（agentskills.io）し、frontmatter キーが大幅に拡張された（`disable-model-invocation`、`user-invocable`、`allowed-tools`、`model`、`effort`、`context: fork|agent`、`hooks`、`paths`、`shell`）。**Plugins / marketplace が GA** となり `extraKnownMarketplaces`、`enabledPlugins`、`/plugin install` が利用可能。**Auto memory**（v2.1.59〜）で Claude が `MEMORY.md` を自分で書く機能が標準化された。Hooks イベントは `SessionStart/End`、`Stop/StopFailure`、`PreToolUse / PermissionRequest / PostToolUse / PostToolUseFailure / PostToolBatch`、`Notification`、`SubagentStart/Stop`、`TaskCreated/Completed`、`CwdChanged / FileChanged / ConfigChange / InstructionsLoaded`、`PreCompact / PostCompact`、`Elicitation / WorktreeCreate/Remove` まで拡大。Hook type は `command / http / mcp_tool / prompt / agent`。MCP は `http` 推奨で `sse` deprecated。

agentops 側の追随状況: 公式 docs URL の参照は docs/16 などで部分的に更新が必要。Skills frontmatter の拡張キーは templates/claude/skill/SKILL.md には未反映。Plugins / marketplace への対応方針は docs に記述が薄い。Auto memory の存在は user グローバル CLAUDE.md（`~/.claude/CLAUDE.md`）の `# auto memory` 節で確認できるが、agentops 側の docs では未触れ。

### 4.2 Codex CLI 公式仕様

AGENTS.md は `~/.codex/AGENTS.md`（global）+ project root → cwd の連結読込で、`AGENTS.override.md` 優先。`project_doc_max_bytes`（既定 32 KiB）超過でスキップ。**Hooks** は `features.codex_hooks = true` の feature flag 付きで利用可能となり（developers.openai.com/codex/hooks）、project-local hooks / exec policies は trusted `.codex/` 配下でのみ読み込まれる。`sandbox_mode` は `read-only / workspace-write / danger-full-access`、`approval_policy` は `untrusted / on-request / never` + granular policy オブジェクト。`[profiles.<name>]` で名前付き設定を切替。Enterprise 向け `requirements.toml` で禁止構成を強制可能（managed configuration）。

agentops 側: AGENTS.md / config/codex/AGENTS.md は対称運用が確立済みだが、`AGENTS.override.md` や `project_doc_fallback_filenames` の活用は未提示。`requirements.toml` の存在は本リポジトリのスコープでは扱う必要が薄いが、enterprise 派生時の参照点として記述があると親切。

### 4.3 AAIF / AGENTS.md 標準化動向

**2025-12-09**、OpenAI と Anthropic が **AGENTS.md を Linux Foundation に寄贈し、Agentic AI Foundation (AAIF) を共同設立**。AGENTS.md は 20,000+ リポジトリで採用され、Claude Code / Cursor / Codex / Gemini CLI / Windsurf / Replit / Amp / Firebase Studio が parsing 対応。**Skills も同時期に open standard 化**。Anthropic 公式の現在推奨は「**AGENTS.md を真実とし、CLAUDE.md からは `@AGENTS.md` で import + Claude 固有差分のみ追記**」（code.claude.com/docs/en/memory）。

agentops 側: CLAUDE.md ↔ AGENTS.md の章立て対称運用は CLI agnostic 観点で良い設計だが、AAIF 公式推奨に対して **二重メンテのコスト** が発生する状態。AGENTS.md → CLAUDE.md import 一本化への再編が今後の標準動線。

### 4.4 ACI と harness（SWE-agent / OpenHands / Managed Agents）

**ACI（Agent-Computer Interface）の発祥**は SWE-agent（Yang et al., NeurIPS 2024, arXiv:2405.15793）。エージェント側に最適化した CLI / 編集 / 検索 tool 群が成功率を大幅に上げる、を初めて体系化した foundational paper。**OpenHands SDK**（arXiv:2511.03690, 2025-11; v2 2026-04-22）は production-ready agent harness を 4 層（flexible agent IF / security & reliability / multi-interface / sandboxed multi-LLM routing）に再構成。**Anthropic "Effective harnesses for long-running agents"**（2025-11-26）は initializer + coding agent の二段 harness、`claude-progress.txt` による進捗ファイル、JSON feature list を契約に近い停止条件として運用。**Anthropic Managed Agents**（2026-04-08）は session（append-only event log）/ harness / sandbox を decouple、`wake / getSession / emitEvent / execute / provision / getEvents` というライフサイクル IF を定義し replay-driven durable execution を実現。

agentops 側: docs/12-harness-engineering.md の 8 領域（task spec / setup / oracle / artifact / replay / sandbox + α）は OpenHands SDK 4 層と awesome-harness-engineering 8 ドメインに整合的。`scripts/agentops delegate` の run 記録は Managed Agents の event log に近い構造で、replay 可能性は持っている。**業界用語との対応表があれば相互参照しやすい**。

### 4.5 DbC for AI（ABC 論文）

**Leoveanu-Condrei "A DbC Inspired Neurosymbolic Layer for Trustworthy Agent Design"**（arXiv:2508.03665, 2025-08 preprint）は古典 Hoare logic {P}C{Q} を確率的 LLM call に拡張し、input type validation → precondition check → LLM 生成 → postcondition validation → remediation の 5 段を提示。**Bhardwaj "Agent Behavioral Contracts (ABC)"**（arXiv:2602.22302, 2026-02 preprint、査読・採録状況は §10.4 参照）は契約を 6-tuple（P / Hard Invariants / Soft Invariants / Hard Governance / Soft Governance / Recovery）で形式化し、(p, δ, k)-satisfaction という確率的満足を定義。

agentops 側: 5 条件（前提・不変・完了・禁止・停止）は ABC 6-tuple と直接マッピング可能。「禁止」= Hard Governance、「停止」= Recovery + (p, δ, k) bound。「不変」を Hard Invariants と Soft Invariants に分割すれば ABC 互換。**「停止条件」を独立カテゴリ化している点は agentops の運用しやすさの源で、ABC 論文より粒度は粗いが実用的**。学術と並走しているという観点では先進的。

### 4.6 multi-agent judge

**MAJ-EVAL**（arXiv:2507.21028, 2025-07）は persona 別 evaluator を自動生成し人間評価との一致を改善。**Meta-Judges**（arXiv:2504.17087）は rubric → 三 LLM 採点 → threshold の三段 meta-judge pipeline。**Multi-Agent Debate for LLM Judges**（OpenReview, 2025-2026）は debate が static ensemble より correctness を増幅することを形式的に分析。

agentops 側: cross-review は「reviewer は所見のみ、決定は主 orchestrator」を採用しており、judge 融合の最適化は研究主流とは別路線。**production 寄りの責任分離としては合理的**。reviewer に persona（security / API contract / DX）を割り当てる発展余地は残る（P2 提案）。

### 4.7 停止条件と circuit breaker

業界記事（Cordum 2026 / Meganova 2025 ほか）は layered defense として `max_steps`、`timeout`、`max_tool_calls`、`max_tokens`、de-duplication、no-progress rule（N steps 進捗なしで停止）、**circuit breaker**（cycle 検知で halt）、cost circuit breaker（cordum.io / meganova.ai が引用する $47k / 11 日 loss 事例）、validation error 区別（401/403 等は retry しない）を共通項として挙げる。学術側では ABC 論文の (p, δ, k)-satisfaction が "soft invariant 違反は k steps 以内に recover" を formal に定義。

agentops 側: 「レビュー修正 2 周上限、3 周目はユーザー確認」は **retry budget の高位プロセス版**として優れる。一方、tool 呼び出しレベル（max_tool_calls / no-progress / circuit breaker / cost cap）への mapping は未整備。**P0-02 として `max_tool_calls` と no-progress rule の追加を提案**。

---

## 5. 強みの言語化（保存すべき設計資産）

1. **DbC を全タスクに適用する形式知**: 前提・不変・完了・禁止・停止の 5 条件をテンプレ化し、`.agentops/plans/`・`task-plans/`・`tasks/` に組み込んでいる。ABC 論文の学術形式化（2026-02）と並走しており、業界・学術コンセンサスと相互参照可能。

2. **Reviewer は所見のみ・主 orchestrator が決定する production 寄り cross-review**: judge 融合の最適化を追わず、責任分離と再現性を優先する設計。`scripts/agentops delegate` ラッパで run 記録を `.agentops/runs/<timestamp>/` に残す replay 可能性も併せ持つ。

3. **`.agentops/` 階層運用の先進性**: plans（最大 1）/ task-plans（セッション）/ tasks（PR 単位）/ handoffs（plan を跨ぐ）/ archive（plan-id 別）/ prompts（動的判定で削除可）の責務分離は、Anthropic `claude-progress.txt` + JSON feature list より粒度が細かく、業界類例が乏しい。

4. **CLI agnostic な CLAUDE.md ↔ AGENTS.md 対称運用**: 2026 時点で AAIF 寄贈後の標準は「AGENTS.md 一本化 + CLAUDE.md import」だが、対称運用そのものは Claude Code / Codex / Gemini CLI など複数 CLI を切り替える 1 人開発者にとって読み手の切替コストを下げる利点がある。

5. **freshness-first の運用ルール**: 公式 docs / GitHub / release notes / package registry / security advisory を AI の記憶より優先する明文ルール。Context7 MCP との組み合わせで RAG-for-docs を運用に組み込んでいる点は最新ベストプラクティスと整合。

6. **日本語運用と Asia/Tokyo 基準の徹底**: 1 人開発者の作業履歴と判断記録を残しやすい統一基盤。応答・commit・PR・レビュー・handoff の言語と時刻方針が CLAUDE.md / AGENTS.md / docs 全体で一貫。

7. **停止条件の独立カテゴリ化**: ABC 論文 6-tuple では Recovery に統合されている "stop" を agentops は独立条件として扱う。レビュー修正 2 周・P3 単独継続禁止という具体ルールが運用上機能している。

---

## 6. 弱み・リスクの分類

### 6.1 運用負荷

- グローバル `~/.claude/CLAUDE.md` への自動反映なし。docs/16 の反映チェックリストが 6 段で重く、毎回手動実行が必要。
- archive インデックス（`.agentops/archive/README.md`）の手動更新。
- `prompts/next-session.md` の動的判定（tasks → handoffs → 削除）が手動。
- Git hooks の install が手動（`scripts/install-hooks --target . --mode copy`）。

### 6.2 一貫性

- 用語ゆれ: "orchestrator" vs "orchestrator_frontier"、"cross-review" vs "cross-model-delegate"、"harness" vs "harness spec"。
- DbC 記述の重複（docs/01-philosophy.md、03-dbc-and-quality-gates.md、09-hooks-quality-gates.md、12-harness-engineering.md）。
- philosophy.md L14 の「単純で合成可能な workflow を優先」と docs/02-workflow.md の 24 ステップ標準サイクルにトーン差。

### 6.3 鮮度

- docs/01–15 の多くに last-reviewed 日や changelog が無い。
- model-catalog.yml の model_id 全 null は意図的だが、「使用直前確認」を 3 回繰り返すテンプレートそのものが運用負担。
- freshness-sources.yml の `max_age_days` 実装が monitoring-cli の「今後の拡張」のまま。
- Claude Code 公式 docs URL の `code.claude.com/docs` 移行に追随できているか未検証。

### 6.4 拡張性

- skill / workflow に「採用判断・見送り条件」列が無い（rule のみ提示）。
- skill frontmatter の具体例が SKILL.md 雛形に無い（agentskills.io 標準キーの例示が必要）。
- rule ↔ skill ↔ workflow の逆参照・マッピングが無い。
- `archive/reference-kit-v1/` が deprecation マーカー無しで現役カタログと並存。

### 6.5 観測性 / セキュリティ

- `.gitignore` は存在するが、secret 拡張子（`.env*` / `*.key` / `credentials*.json` / cloudflare の `wrangler` secret 等）の明示列挙が無く、誤 commit 防止としてはあと一歩。
- `.github/` 不在（GitHub Actions / PR template / CODEOWNERS）で PR 強制ガード無し。
- `agentops-watch` の Discord 通知などが「今後の拡張」段階で実装未完。
- tool 実行層の停止条件（max_tool_calls / no-progress / circuit breaker / cost cap）が未規定。

---

## 7. 改善提案（P0–P3）

各提案: `ID / タイトル / 根拠 / 想定影響（軸 A-F のどれを何段階）/ 実装コスト / 依存先 docs / 業界出典 / 再評価条件`

### P0（即時対応・運用害が顕在化）

| ID | タイトル | 根拠 | 影響 | コスト | 依存 | 出典 | 再評価条件 |
|---|---|---|---|---|---|---|---|
| **P0-02** | tool 実行層の停止条件を docs/03 + config/harness.yml に追加（max_tool_calls / no-progress rule / circuit breaker / cost cap） | プロセス層は 2 周上限あるが tool 層は未規定。$47k / 11 日 loss 事例（cordum.io 引用） | B: B+→A | M（1 日） | docs/03-dbc-and-quality-gates.md、config/harness.yml | cordum.io / meganova.ai circuit breaker、ABC (p,δ,k) | 4 種すべて harness.yml に閾値が入り `agentops-watch` で監視 |

補足:
- **P0-02**: docs/03-dbc-and-quality-gates.md に「停止条件 = プロセス層 + tool 実行層」の 2 階層を導入し、tool 実行層は config/harness.yml に閾値を持たせる。`max_tool_calls=200`、`no_progress_steps=10`、`circuit_breaker_cycle_threshold=3`、`cost_cap_usd_per_session=20` のような既定値。
- 注: AGENTS.md 一本化は当初 P0-01 と分類したが、Codex 側 cross-review で「Claude Code 公式の推奨ではあるが即時の運用害や安全性欠陥を起こしているわけではない」との指摘を受け、**P1-08 へ降格**して再分類した。

### P1（1 ヶ月以内に解消すべき構造課題）

| ID | タイトル | 根拠 | 影響 | コスト | 依存 | 出典 | 再評価条件 |
|---|---|---|---|---|---|---|---|
| **P1-01** | 用語統一表を docs/00-glossary.md として追加 | "orchestrator" vs "orchestrator_frontier" 等の用語ゆれが複数箇所 | A: B→A | S（2 時間） | docs/、config/、skills/、rules/、workflows/ | Claude Code public docs の用語慣用 | grep で旧用語が 0 件 |
| **P1-02** | `archive/reference-kit-v1/` に deprecation マーカー（`DEPRECATED.md` + 各 catalog 先頭注記） | 現役カタログと並存して混乱を生む | A: B→A、F: B→B+ | S（30 分） | archive/reference-kit-v1/、各 catalog.md 先頭 | 一般的 deprecation 慣行 | 新規参照者が現役と誤認しない |
| **P1-03** | rule ↔ skill ↔ workflow ↔ hook の逆参照テーブルを docs/17-cross-reference.md に追加 | rule → どの skill / hook で実装するかが不明 | F: B→A− | M（半日） | rules/catalog.md、skills/catalog.md、workflows/catalog.md | agents.md monorepo パターン | 各 rule に「関連 skill / hook」列が入る |
| **P1-04** | docs/01–16 全ファイルに `last-reviewed` / `next-review-by` フロントマター追加 | 鮮度監査が docs 個別で機能しない | D: B−→B+ | S（1 時間） | docs/01–16 | AAIF agents.md 推奨慣行 | freshness check CI が経過日を検出 |
| **P1-05** | DbC 記述を docs/03-dbc-and-quality-gates.md に集約、他 docs（01 / 09 / 12）は参照のみに | DRY 違反 | A: B→A | S（1 時間） | docs/01, 03, 09, 12 | 一般的 DRY 原則 | DbC の本文が 1 箇所のみ |
| **P1-06** | `.agentops/archive/README.md` 自動更新 hook（plan archive 時に行追加） | 手動更新で漏れリスク | E: B−→B | M（半日） | scripts/agentops、scripts/hooks/ | Anthropic Managed Agents event log | plan archive 時に自動でインデックスに追加される |
| **P1-07** | 最小 CI（actionlint / yamllint / markdown-link-check / freshness check）導入 + `.gitignore` への secret 拡張子追加（`.env*` / `*.key` / `credentials*.json` 等） | `.github/` 不在で PR 強制ガード無し。`.gitignore` は存在するが secret 拡張子未列挙 | E: B−→B+ | S–M（半日） | リポジトリルート、`.github/workflows/`、`.gitignore` | GitHub Actions docs、一般的 secret hygiene 慣行 | secret 拡張子・docs link 切れが CI で reject される |
| **P1-08** | AGENTS.md 一本化、CLAUDE.md は `@AGENTS.md` import + Claude 固有差分のみ | AAIF 設立（2025-12-09）以降の公式推奨。agentops の対称運用は二重メンテ。即時の運用害は無いが構造課題（Codex cross-review 所見） | A: B→A、C: A−→A | M（半日） | CLAUDE.md / AGENTS.md / config/{claude,codex}/ | code.claude.com/docs/en/memory、agents.md | CLAUDE.md が AGENTS.md import + 差分 < 50 行になる |

### P2（価値高いが緊急でない）

| ID | タイトル | 根拠 | 影響 | コスト | 依存 | 出典 | 再評価条件 |
|---|---|---|---|---|---|---|---|
| **P2-01** | skill frontmatter の具体例を SKILL.md 雛形に追加（agentskills.io 標準キー網羅） | Claude Code 公式キーが templates/claude/skill/SKILL.md に未反映 | F: B→A− | S（1 時間） | templates/claude/skill/SKILL.md、templates/codex/skill/SKILL.md | code.claude.com/docs/en/skills、agentskills.io | 新規 skill 作成時にコピペで動く |
| **P2-02** | レビュー粒度の例外条件（typo / リンク修正 / docs 整形のみは self-merge OK）を docs/05 に追加 | 「修正後は必ず再レビュー」が軽微修正にも適用 | B: B+→A− | S（1 時間） | docs/05-review-policy.md | 一般的 PR 慣行 | small-PR フィルタが運用で有効 |
| **P2-03** | reviewer に persona 割当（security / API contract / DX）を model-catalog.yml に追加 | judge 多様性が研究で有効 | C: A−→A | S（1 時間） | config/model-catalog.yml、skills/cross-review.md | MAJ-EVAL、Meta-Judges | persona 別所見が runs/ に出る |
| **P2-04** | harness 用語統一（"harness" / "harness spec" / "harness engineering"）と docs/12 の用語表 | 文脈依存で混在 | A: B→B+ | S（30 分） | docs/12-harness-engineering.md | OpenHands SDK 用語 | grep で表記ゆれ 0 件 |
| **P2-05** | `agents-watch` Discord 通知の実装 | 設計済み・実装未完 | E: B+→A− | M（半日） | scripts/agentops-watch、docs/11 | 一般的監視慣行 | dirty / stuck / freshness alert が届く |
| **P2-06** | Codex の `AGENTS.override.md` 活用方針を docs/16 に追記 | 公式仕様だが未提示 | F: B→B+ | S（30 分） | docs/16-global-settings-application-checklist.md | developers.openai.com/codex/guides/agents-md | docs/16 に override の使い分けが明記 |

### P3（検討価値あり・将来オプション）

| ID | タイトル | 根拠 | 影響 | コスト | 依存 | 出典 | 再評価条件 |
|---|---|---|---|---|---|---|---|
| **P3-01** | replay-driven テスト harness を `.agentops/runs/` から構築 | Anthropic Managed Agents の replay 思想 | C: A−→A | L（1 週） | scripts/agentops、tools/agentops_cli/ | anthropic.com/engineering/managed-agents | 過去 run の決定論的再現が可能 |
| **P3-02** | agentops 用 plugin（`/agentops-*` slash commands）を marketplace 公開 | Claude Code plugins GA、参照キット価値共有 | F: B→A | L（1 週+） | templates/、skills/、`.claude-plugin/` | code.claude.com/docs/en/plugins | marketplace に公開され install 可能 |
| **P3-03** | (p, δ, k)-satisfaction を `.agentops/reviews/` の評価メトリクスに導入 | ABC 論文の確率的満足を運用へ | B: A→A+ | L（実験的） | docs/03、`.agentops/reviews/` | arXiv:2602.22302 | 評価レポートに p / δ / k が記録される |

### 再提案しないリスト（既解決）

- `.agentops/` 階層責務（plans / task-plans / tasks / handoffs / next-session.md）→ 2026-04-28 反映済み
- archive 時系列インデックス + plan-id 別ディレクトリ → 運用済み
- delegate CLI の P2 hardening（command template / security / timeout）→ PR #20 で完了済み
- CLAUDE.md ↔ AGENTS.md 章立て対称性 → 既に確立（ただし P1-08 で AAIF 推奨形へ再編予定）

---

## 8. 他プロジェクト派生可能性

agentops は `~/dev` 配下の Web システム開発（Nuxt / Next.js / PHP / Go）と Cloudflare Workers・Pages、Xserver、GCP、ローカルへの展開を想定している（docs/14-real-project-template-policy.md）。実プロジェクトへ派生する際の適合性を、デプロイ先別に短く評価する。

**Cloudflare Workers / Pages**: skills/freshness-audit と Context7 で Wrangler / Hono / D1 / KV / R2 の最新仕様を一次情報で確認する運用が有効。`scripts/agentops delegate` での Codex 委譲は Workers 実装の review_frontier 用途に向く。注意: `.gitignore` に `.dev.vars` / `wrangler.toml` の secret 部分を含める運用が必要（P1-07 で対応）。

**Next.js / Nuxt**: AGENTS.md 一本化（P1-08）後は monorepo 各 package に AGENTS.md を置く AAIF パターンが適用しやすい。Skills の `paths` 自動アクティベートで `app/` `pages/` `components/` 別の振る舞い切替も可能。

**PHP（Xserver）**: harness.yml の sandbox policy を `read-only` 寄りに、deploy commands を `require_confirmation` 必須に設定する運用が必要。`.htaccess` / `php.ini` / cron 等は project 側 AGENTS.md で具体化（agentops は雛形のみ）。

**Go / GCP**: model-routing の coding_frontier ロールで Go 標準ライブラリ・公式 Go module proxy を一次情報優先。GCP 系は IAM / KMS / Secret Manager 周りで `forbidden` リストの厳格化が必要。

**ローカルサーバー / dotfiles 除外**: 現状の「dotfiles は明示依頼ない限り対象外」（user グローバル CLAUDE.md）は適切。ローカル DB / docker-compose は project 側で扱う。

**テンプレートのギャップ**: `templates/agentops/` には .agentops 雛形があるが、`templates/{nuxt,nextjs,php,go}/` のような stack 別 AGENTS.md / harness.yml サンプルは無い。**P3 として stack 別 starter を 1〜2 個追加する余地**（例: Nuxt + Cloudflare Workers の AGENTS.md + harness.yml + skills セット）。ただし docs/14 が「プロジェクト固有のビルド・デプロイ・secret は固定しない」方針を明示しているので、stack 別 starter も「候補カタログ」のスタンスを崩さないこと。

---

## 9. ロードマップ素案

| 時期 | 解消対象 | 完了の合図 |
|---|---|---|
| **1–2 週**（P0） | P0-02 tool 層停止条件 | harness.yml に max_tool_calls 等の閾値、`agentops-watch` で監視 |
| **1 ヶ月**（P1） | P1-01 用語統一表 / P1-02 deprecation マーカー / P1-03 逆参照テーブル / P1-04 last-reviewed / P1-05 DbC 集約 / P1-06 archive 自動更新 / P1-07 最小 CI + .gitignore 拡充 / P1-08 AGENTS.md 一本化 | docs/00-glossary.md 公開、archive/reference-kit-v1 に DEPRECATED.md、freshness check CI が pass、archive インデックス自動追記、secret 拡張子が CI で reject、CLAUDE.md が AGENTS.md import + 差分 < 50 行 |
| **四半期**（P2） | P2-01 skill frontmatter 例示 / P2-02 レビュー粒度例外 / P2-03 reviewer persona / P2-04 harness 用語統一 / P2-05 Discord 通知 / P2-06 Codex override 方針 | 新規 skill のコピペ可、small-PR self-merge 運用、persona 別所見、Discord 通知稼働 |
| **バックログ**（P3） | P3-01 replay-driven テスト / P3-02 plugin 公開 / P3-03 (p,δ,k) メトリクス | `.agentops/runs/` から決定論的再現、marketplace に plugin、評価レポートに確率的満足 |

四半期レビュー時は本報告書を `docs/reviews/YYYY-MM-DD-cross-repo-design-review.md` で再発行し、当該 P0/P1 解消状況を確認する。

---

## 10. 検証・更新運用

### 10.1 本報告書の検証

- 出典 URL: Appendix A の URL を `curl -sIL` で 200 / 3xx 確認、取得日併記。
- リポジトリ内引用パス: `ls` / `test -e` で全件存在確認。
- 業界比較: freshness audit で 2025-2026 動向の固有名詞（AAIF、ABC 論文、SWE-agent、Managed Agents）を再確認。
- 第三者視点: Codex 側 cross-review（`scripts/agentops delegate --to codex --role review_frontier`）。orchestrator が最終決定権を保持。

### 10.2 再評価サイクル

- **四半期ごと**: 本報告書を新規日付で再発行。前回報告書を Appendix で参照。
- **メジャー公式変更時**: Claude Code / Codex / AAIF agents.md の仕様改訂、ABC 論文・OpenHands SDK・Managed Agents の続編、用語標準化があれば臨時レビュー。
- **本リポジトリ大規模変更時**: docs / カタログを 30% 以上書き換える plan の終了時。

### 10.3 last-reviewed / next-review-by

- 本報告書: last-reviewed=2026-04-28、next-review-by=2026-07-31
- docs/01–16: P1-04 で各ファイルに導入予定

### 10.4 残存不確実性

本報告書では以下を未検証または推定値のまま採用しており、Codex 側 cross-review で再点検する:

- 学術論文 arXiv:2602.22302（ABC）/ arXiv:2511.03690（OpenHands SDK）/ arXiv:2508.03665（DbC neurosymbolic）/ arXiv:2507.21028（MAJ-EVAL）/ arXiv:2504.17087（Meta-Judges）は HEAD 200 と HTML プレビューを確認済みだが、採録会議・査読状況・引用件数までは未検証。
- AAIF charter の Linux Foundation 配下の正式文書は未取得。複数報道（agents.md / sdtimes.com / venturebeat.com）が 2025-12-09 を寄贈日として一致している点までで採用。
- Codex CLI の "Skills in Codex" が Anthropic Agent Skills（agentskills.io）と完全互換かは公式 docs で明示確認できず、構造的同一とまでに留めている。
- `config/model-catalog.yml` の model_id 採用例（gpt-5.5 / claude-sonnet-4-6 系の表記）は 2026-04-28 時点 advisory であり、本報告書では固定モデル ID として採用しない。
- 一部 GitHub `docs/*.md`（特に Codex 側）は外部 docs へのリダイレクトスタブで、真ソースは `developers.openai.com/codex/*`。本報告書は真ソース基準で記述。

---

## Appendix A. 参考文献・出典一覧

すべて取得日 2026-04-28（Asia/Tokyo）。生存確認は §10.1 の手順で別途実施。

### Claude Code 公式

- code.claude.com/docs/en/memory（CLAUDE.md / imports / auto memory）
- code.claude.com/docs/en/sub-agents
- code.claude.com/docs/en/skills（agentskills.io 標準準拠）
- code.claude.com/docs/en/slash-commands（skills 統合の説明）
- code.claude.com/docs/en/hooks（イベント / 入出力 / type）
- code.claude.com/docs/en/settings
- code.claude.com/docs/en/mcp（http 推奨 / sse deprecated / channels）
- code.claude.com/docs/en/plugins（GA / marketplace）
- code.claude.com/docs/en/output-styles
- code.claude.com/docs/en/changelog
- github.com/anthropics/claude-code/blob/main/CHANGELOG.md

### Codex CLI 公式

- developers.openai.com/codex/cli
- developers.openai.com/codex/cli/features
- developers.openai.com/codex/cli/reference
- developers.openai.com/codex/config-reference
- developers.openai.com/codex/config-basic
- developers.openai.com/codex/config-advanced
- developers.openai.com/codex/security
- developers.openai.com/codex/guides/agents-md
- developers.openai.com/codex/changelog
- developers.openai.com/codex/enterprise/managed-configuration
- github.com/openai/codex
- github.com/openai/codex/blob/main/CHANGELOG.md

### AAIF / 標準化

- agents.md（AAIF 配下、Linux Foundation 寄贈後の正規ホーム）
- github.blog（"How to write a great agents.md", 2,500 リポジトリ調査）
- infoq.com/news/2025/08/agents-md/（標準化動向）
- sdtimes.com（"Anthropic makes Skills an open standard", 2025-12-19）

### 学術論文（arXiv）

- arXiv:2405.15793 — SWE-agent: Agent-Computer Interfaces（Yang et al., NeurIPS 2024）
- arXiv:2511.03690 — The OpenHands Software Agent SDK（Wang et al., 2025-11）
- arXiv:2508.03665 — A DbC Inspired Neurosymbolic Layer（Leoveanu-Condrei, 2025-08）
- arXiv:2602.22302 — Agent Behavioral Contracts（Bhardwaj, 2026-02）
- arXiv:2507.21028 — MAJ-EVAL: Multi-Agent-as-Judge
- arXiv:2504.17087 — Meta-Judges multi-agent framework

### Anthropic 公式技術ブログ

- anthropic.com/engineering/effective-harnesses-for-long-running-agents（2025-11-26）
- anthropic.com/engineering/effective-context-engineering-for-ai-agents（2025-09-29）
- anthropic.com/engineering/managed-agents（2026-04-08）
- platform.claude.com/cookbook/tool-use-automatic-context-compaction
- platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool

### 業界記事・補助

- cordum.io/blog/ai-agent-circuit-breaker-pattern（2026）
- blog.meganova.ai/circuit-breakers-in-ai-agent-systems-reliability-at-scale/
- cursor.com/blog/agent-sandboxing
- thoughts.jock.pl/p/ai-coding-harness-agents-2026
- infoq.com/news/2026/04/cursor-3-agent-first-interface/
- venturebeat.com/ai/anthropic-launches-enterprise-agent-skills-and-opens-the-standard
- github.com/walkinglabs/awesome-harness-engineering

### 補足: agentops 内根拠

- docs/01-philosophy.md, 02-workflow.md, 03-dbc-and-quality-gates.md, 04-model-routing.md, 05-review-policy.md, 06-freshness-and-monitoring.md, 09-hooks-quality-gates.md, 12-harness-engineering.md, 13-design-evaluation.md, 14-real-project-template-policy.md, 15-reference-kit-structure.md, 16-global-settings-application-checklist.md
- CLAUDE.md, AGENTS.md（ルート）
- config/model-catalog.yml, config/harness.yml, config/freshness-sources.yml
- rules/catalog.md, skills/catalog.md, workflows/catalog.md
- templates/{claude,codex,agentops}/
- scripts/agentops, scripts/agentops-watch, scripts/install-hooks
- .agentops/archive/（plan-id 別履歴、2026-04-27〜2026-04-28）

---

## Appendix B. 用語集

- **ACI (Agent-Computer Interface)**: AI エージェントが触る CLI / ファイル / 状態を設計対象とする概念。SWE-agent（NeurIPS 2024）が発祥。
- **AAIF (Agentic AI Foundation)**: 2025-12-09 に OpenAI / Anthropic が AGENTS.md を寄贈して設立した Linux Foundation 配下の組織。
- **ABC (Agent Behavioral Contracts)**: arXiv:2602.22302 で提案された AI エージェント契約形式（6-tuple + (p,δ,k)-satisfaction）。
- **DbC (Design by Contract)**: Bertrand Meyer 由来。agentops では前提・不変・完了・禁止・停止の 5 条件として運用。
- **freshness audit**: 公式 docs / GitHub / release notes / package registry / security advisory を AI 記憶より優先する確認運用。
- **harness**: agent run の実行環境（task spec / setup / oracle / artifact / replay / sandbox）。
- **orchestrator**: 主モデル（決定権を持つ）。agentops では Claude Code が想定既定。`orchestrator_frontier` は config/model-catalog.yml のロール名。
- **cross-review / cross-model-delegate**: 別系列 frontier reviewer に所見だけ求め、決定は主 orchestrator が持つレビュー方式。`scripts/agentops delegate` がラッパ。
- **MCP (Model Context Protocol)**: Anthropic 主導の tool / context 連携プロトコル。`http` 推奨、`sse` deprecated。
- **Skills**: 2025-12 に open standard 化された agent capability 単位。`SKILL.md` + frontmatter で定義。

---

> 本報告書は agentops リポジトリ自身の DbC・cross-review・freshness 運用に従って作成された。Codex 側 cross-review は完成直後に `scripts/agentops delegate --to codex --role review_frontier --input docs/reviews/2026-04-28-cross-repo-design-review.md` で実施し、所見を反映した最終版を main にマージする。
