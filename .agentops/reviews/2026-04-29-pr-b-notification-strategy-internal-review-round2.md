---
review-id: 2026-04-29-pr-b-notification-strategy-internal-review-round2
date: 2026-04-29
reviewer: claude-code (independent subagent, round 2)
target-pr: PR-B
target-branch: claude/notification-strategy-2026-04-29
target-task: .agentops/tasks/01-notification-strategy-docs.md
predecessor-review: .agentops/reviews/2026-04-29-pr-b-notification-strategy-internal-review.md
review-axes: correctness / security / tests / docs / maintainability
verdict: passed (minor optional cleanup; no blocking findings)
---

# PR-B independent internal review — round 2

P0: 0 / P1: 0 / P2: 0 (1 optional nit) / P3: 0 (deferred per request).
全 P1 / P2 指摘が反映済みであることを確認。新規 P0 / P1 なし。

## 反映確認 (resolved)

- **P1-1 (resolved)**: `scripts/README.md:21` を `--kind daily --dry-run` 必須形式に修正済み。docs/11-monitoring-cli.md:23-27 の Synopsis (`--kind daily|weekly|monthly --projects ...`) と整合。
- **P1-2 (resolved)**: `docs/17-cross-reference.md:42` の `notification-policy` hook 列が em dash (`—`) に戻っており、`rules/catalog.md:21` の hook 列 (em dash) と方向が一致。docs/17:50-56 の補完経路節に notification-policy が明記され、`templates/claude/hooks/session-notify-stub.md` への相対リンクも到達可能 (実ファイル存在を確認)。
- **P2-1 / P2-3 (resolved)**: `docs/18-notification-strategy.md:147` の DbC「適用前提」が kind 別に分岐 (`digest 系では --projects YAML / それ以外では --project <path>`) され、CLI 自前ガード超過と外部 HTTP 429/5xx の扱いが「適用不変」(:148) と「適用停止」(:150) で明確に区別された。停止条件節は外部側 429/5xx を明示し、自前ガードは warning + skip 継続として CLI 全体停止と切り分け。
- **P2-2 (resolved)**: `docs/18-notification-strategy.md:86` が「実装 plan で `tools/agentops_monitor/notifiers/discord.py` 等に近接配置する想定 (本 PR は未生成、フィールド契約のみ規定)」と将来形に変更され、スコープ外節 (:160) にも `tools/agentops_monitor/notifiers/discord.py` 等の実体生成が追加。docs と現状ファイルツリーの非整合が解消。

## 新規所見

P0: なし
P1: なし
P2 (任意・本 PR で見送り可): 1 件
P3: ユーザー指示により deferral 判定済み、本ラウンドで指摘しない。

### P2 (任意・nit)

- **P2-NEW-1 (任意)**: docs/18-notification-strategy.md:148 の「適用不変」に追加した CLI 自前ガード文 (`...skip して継続し、本 DbC 停止条件としては扱わない`) と :150 末尾の補足文 (`CLI 自前の頻度上限ガードによる skip は本停止条件と区別する`) は意味として重複。読み手の混乱はないが、:150 末尾を「上記『適用不変』参照」に短縮するか :148 末尾を削るかで 1-2 行短縮可能。本 PR スコープでは見送り可。

## 整合性チェック (新たな矛盾なし)

- docs/11-monitoring-cli.md:23-27 の `--kind` 必須仕様と scripts/README.md:21 の例が一致。
- docs/17:42 hook 列 (`—`) と rules/catalog.md:21 hook 列 (`—`) が同方向。
- docs/18:147 の `--projects` / `--project` 分岐と docs/11:23-27 の Synopsis (digest 系のみ `--projects`、その他は `--project`) が一致。
- docs/18:160 のスコープ外宣言 (`tools/agentops_monitor/notifiers/discord.py` 等の実体生成) と :86 の将来形参照が整合。
- templates/claude/hooks/session-notify-stub.md は実在し、docs/17:56 と docs/18:174 の相対リンクが解決可能。
- secret 値・Webhook URL 値は本 PR の diff・log・stub.md・docs に出ていない (env 変数名のみ)。
- AI auto-merge 許諾 §6 (secret 未混入) を満たす。

## 残リスク (read-only review で除外しきれないもの)

- `tools/agentops_monitor/notifiers/discord.py` の実体は未生成。本 PR は契約のみで整合するが、実装 plan 着手時に payload field と本 docs のテーブル (docs/18:88-95) に乖離が起きないか継続監視が必要。
- markdown-link-check / actionlint / yamllint 等の CI job 結果は read-only では未検証。CI 通過は orchestrator 側で確認のこと。
- ユーザー env の `ANT_TIME` typo (`ANY_TIME` 本来) は docs/18:39 の運用観察ノートで尊重済みだが、将来 typo 修正パスを別 plan で扱う必要あり (P3 deferral 範囲)。
- 公式 Claude Code hooks docs (https://code.claude.com/docs/en/hooks) との event 名 / schema 突合は別 plan で実施前提 (stub.md:11-17 で明示済み)。

## 総合判定

**passed** — 修正は指摘内容を正確に反映し、新規矛盾なし。本ラウンドで blocking findings ゼロ。P2-NEW-1 は任意の nit で本 PR 見送り可。**再レビューパス不要**。orchestrator は AI auto-merge 許諾条件 (DbC 完了 / cross-review P0/P1 反映済み / CI green / scope 単一 / secret 未混入) の残項目 (CI green と cross-review run 記録) を確認した上で squash-merge へ進めて良い。

