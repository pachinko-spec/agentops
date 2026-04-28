# Next session プロンプト（2026-04-28 設計レビュー後の実装フェーズ）

parent_plan: 2026-04-28-cross-repo-design-review（archive 済み、報告書 `docs/reviews/2026-04-28-cross-repo-design-review.md`）
status: pending
created_at: 2026-04-28
timezone: Asia/Tokyo

---

## このセッションの位置づけ

直前 plan で作成した横断設計レビュー報告書（PR #27）を入力に、**改善提案 18 件（P0=1 / P1=8 / P2=6 / P3=3）の実装計画を立てる**ためのセッション。

実装はまだしない。本セッションのゴールは「Plan ファイル + 親 task ファイル群」を作成し、ユーザー承認を得ることまで。

---

## 投入プロンプト（次セッションのユーザー指示として、そのまま貼ってよい）

> agentops の横断設計レビュー報告書 `docs/reviews/2026-04-28-cross-repo-design-review.md` を全文読み込み、§7 の改善提案 18 件（P0=1 / P1=8 / P2=6 / P3=3）の実装計画を立ててください。
>
> 計画の作り方:
>
> 1. **Planner ロールは Opus 4.7（あなた自身の Plan agent / Plan mode）** が担当。報告書を入力に、依存関係・実装コスト・影響軸（A-F）を踏まえて、CLAUDE.md の `.agentops/` 運用ルールに沿った形で計画を組む。
> 2. **粒度方針**:
>    - `.agentops/plans/current.md` は **最大 1 つ**（CLAUDE.md ルール）。最初は **P0 + P1（計 9 件）** を一括対象にする plan「`2026-MM-DD-design-review-p0-p1`」を起こす。P2 / P3 は次以降の plan として後回し（理由: 提案数が多く、依存関係を見ながら段階的に潰す方が安全）。
>    - 各提案を **1 PR 単位の task** として `.agentops/tasks/NN-<提案 ID>.md` に展開。task ファイルには CLAUDE.md の task 雛形（実行内容 / 完了条件 / 検証 / 完了時の後処理 / 停止条件）を必ず埋める。
>    - 依存がある提案は task 順序で表現（例: P1-01 用語統一表 → P1-05 DbC 集約は順序依存）。
>    - 1 PR ≒ 半日〜1 日コスト。S/M で収まらない L 提案（P3-01 replay-driven テスト等）は分割せず本 plan には入れない。
> 3. **クロスレビュー方針**:
>    - 各 task の実装完了後、`scripts/agentops delegate --to codex --role review_frontier --effort high --input <該当ファイル>` で **GPT-5.5（Codex CLI）** に cross-review を委譲する旨を、task の「検証」に明記。
>    - 主 orchestrator（Opus 4.7）が最終判断権を保持し、Codex は所見のみ。これは agentops の `docs/04-model-routing.md` / `docs/05-review-policy.md` の規約と一致。
>    - Plan 全体の最終レビューも Codex に委譲し、所見を反映してマージ判断。
> 4. **計画立案中の停止条件**:
>    - 報告書の観察事実と現リポジトリ状態が一致しない箇所（例: 既に部分対応済み）が見つかったら停止してユーザー確認。
>    - 提案間に大きな依存があり 1 plan に収まらないと判断した場合は、plan 分割案を提示してユーザー判断を仰ぐ。
>    - L コスト提案を本 plan に含めるか別 plan にするかで揺れたら、保守的に別 plan へ寄せる。
>
> 出力（このセッション内で作るファイル）:
>
> - `/home/otaku/.claude/plans/<topic>.md` — Plan mode の plan ファイル（Plan agent が書き出す詳細計画）
> - `.agentops/plans/current.md` — 親 plan（plan-id、背景、目的、非目的、影響範囲、完了条件、停止条件、検証方針、親 task 一覧）
> - `.agentops/task-plans/current.md` — 今セッションは「計画立案のみ」。次セッション以降の実装着手フェーズで使う雛形を準備
> - `.agentops/tasks/NN-<提案 ID>.md` — P0 / P1 提案ごとの task ファイル（最大 9 件、依存順に並べる）
>
> 制約:
>
> - 本セッションでは実装ファイルには触らない。`docs/reviews/` の報告書本体や `docs/01–16` も読み取り専用。
> - 計画提示後、ユーザー承認を得てから実装フェーズへ進む（CLAUDE.md「実装、削除、ファイル生成、インストール、外部反映の前に計画を提示し承認を得る」）。
> - `claude/design-review-2026-04-28` は本 PR 用ブランチ。実装フェーズは別ブランチ `claude/design-review-impl-p0-p1` などを切り直す。
> - PR #27 が main にマージ済みかどうかを冒頭で確認し、未マージなら本 plan の起票はマージ後に持ち越す。

---

## 触らないこと（参考）

- 報告書 `docs/reviews/2026-04-28-cross-repo-design-review.md` は cross-review 反映済みの最終版。本セッションで内容修正しない。
- `archive/reference-kit-v1/` は P1-02 で deprecation マーカーを付ける対象だが、本セッションでは設計のみで実ファイルは触らない。

## 副次的な持ち越し

- PR #27 のレビュー結果対応はこの実装計画とは独立。指摘があれば別途 hot-fix で対応してから本実装フェーズへ進む。
- `.claude/scheduled_tasks.lock` は本 PR の `.gitignore` 修正で commit 対象外化済み（commit `854d7da`）。
