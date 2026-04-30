---
task-id: 01-applies-to-and-trinity
parent-plan: 2026-04-30-applies-to-and-trinity
status: in-progress
created: 2026-04-30
---

# Task 01: applies-to frontmatter + 三役宣言 + Discord 通知 docs 改修

親 plan: [`../plans/current.md`](../plans/current.md)

## 現在状態

- 着手前 commit: `3063630` (PR #64)
- branch: `claude/agentops-applies-to-frontmatter-2026-04-30`
- 全 20 docs frontmatter 4 フィールド (`last_reviewed` / `next_review_by` / `reviewer` / `language`) は完備、`applies-to` は不在
- `docs/00-glossary.md` のみ既存 5 番目 field `scope: glossary` を持つ

## 実行内容

### A. docs/00-glossary.md に用語追加 (additive)

`## 役割・運用名` の後または `## ツール / プロトコル` の前あたりに新セクションを追加:

- **applies-to frontmatter** field の正式定義 (4 値: `global` / `shared-cli-spec` / `agentops-internal` / `template-source` の語義 + grep 検証コマンド)
- **三役 (Trinity)** 用語 ((a) 設計思想カタログ / (b) 共有 CLI / ライブラリ / (c) 雛形配布元)
- **shared-cli-spec パターン** 用語 (思想は global / 実装は agentops 共有 CLI / 各層から呼ぶ)

### B. AGENTS.md 三役で書き直し

「このリポジトリの位置づけ」セクションを三役で系統化 (additive、§記録先以降は保つ)。

### C. README.md 冒頭に三役 (公開向け)

L3 直後に三役を公開向け表現で追加。

### D. 全 20 docs に `applies-to` frontmatter 追加

分類表:

| docs | applies-to |
|---|---|
| `00-glossary` | `global` |
| `01-philosophy` | `global` |
| `02-workflow` | `global` |
| `03-dbc-and-quality-gates` | `global` |
| `04-model-routing` | `global` |
| `05-review-policy` | `global` |
| `06-freshness-and-monitoring` | `global` |
| `07-global-vs-project` | `global` |
| `08-config-templates` | `agentops-internal` |
| `09-hooks-quality-gates` | `global` |
| `10-cli-wrapper` | `shared-cli-spec` |
| `11-monitoring-cli` | `shared-cli-spec` |
| `12-harness-engineering` | `global` |
| `13-design-evaluation` | `agentops-internal` |
| `14-real-project-template-policy` | `agentops-internal` |
| `15-reference-kit-structure` | `agentops-internal` |
| `16-global-settings-application-checklist` | `agentops-internal` |
| `17-cross-reference` | `agentops-internal` |
| `18-notification-strategy` | `global` |
| `19-project-localization` | `global` |

各 docs frontmatter で `language: ja` 行の直後に `applies-to: <value>` を追加 (既存 4 フィールドの値は変えない)。`docs/00` の場合は既存 `scope: glossary` の前後どちらでもよい。

### E. docs/18 に shared-cli-spec パターン適用 section 追加

L11 `## 目的` の後に新節「## shared-cli-spec パターンの適用」を追加 (additive):

- 思想 (kind / channel mapping / DbC / rate-limit) は `applies-to: global` で全 host 共通
- 実装本体は `agentops-watch notify --kind <kind>` 共有 CLI (`applies-to: shared-cli-spec`)
- 各層 (cron / Claude Code hook / Codex hook / shell scripts) は本 CLI を呼ぶだけ
- 別 AI が読むときの指針表

### F. docs/11 に位置付け参照節追加

`## 目的` の段落直下に短い shared-cli-spec パターン参照節を追加: 「本 CLI は `applies-to: shared-cli-spec` であり、cron / hook / shell scripts から呼ばれる集約点。思想本体は docs/18 (`applies-to: global`) を参照」。

## DbC 5 条件

### 適用前提

- git status clean、branch `claude/agentops-applies-to-frontmatter-2026-04-30`
- 全 20 docs frontmatter 4 フィールド完備
- `tools/agentops_cli` `doctor` 実装済 (本 task では拡張しない、optional は別 plan)

### 適用不変

- 既存 frontmatter 4 フィールド (`last_reviewed` / `next_review_by` / `reviewer` / `language`) の値を変更しない
- secret 値 (Webhook URL / API key / 個人 data) を frontmatter / docs / commit / PR 本文に書かない
- 既存 docs の本文意味を変更しない (additive 変更のみ)
- グローバル設定 (`~/.claude/` / `~/.codex/`) を touch しない
- dotfiles を touch しない
- 「applies-to: shared-cli-spec」の docs (docs/10 / docs/11) は本 plan 後も agentops repo 内部にあるが、別 AI が「これは agentops が他層に提供する CLI の仕様」と読める位置付けを明示する

### 適用完了

- 全 20 docs に `applies-to` frontmatter が機械可読で付与済
- AGENTS.md + README.md に三役宣言が追加済
- docs/18 + docs/11 に shared-cli-spec パターン明示済
- Codex `review_frontier --effort high` cross-review で P0/P1 = 0 件 (or 反映済)
- `python3 -m compileall tools` exit 0
- `python3 -m pytest tools/agentops_cli/tests tools/agentops_monitor/tests -q` regression なし
- `markdown-link-check docs/*.md README.md AGENTS.md CLAUDE.md` 全 pass
- secret 未混入
- AI auto-merge 許諾条件をすべて満たして main マージ完了
- main 同期確認 + `.agentops/` クリーン

### 禁止事項

- グローバル設定 (`~/.claude/` / `~/.codex/`) touch
- dotfiles repo touch
- 既存 docs 本文の意味的書き換え
- 既存 frontmatter 4 フィールドの値変更
- 主要 5 プロジェクト (`~/dev/{ai-engine,ai-keiba,ai-utg,pachi-studio,ai-content-engine}`) への動作変更
- doctor リント必須実装 (optional は別 plan へ)

### 停止条件

- レビュー修正が 2 周を超える → user 確認
- secret 値が誤って混入 → 即停止
- frontmatter parse 不能 (構文エラー)
- 既存 markdown-link-check / 既存テストの regression
- 既存 docs に applies-to を付与しようとして本文の意味が変わる
- 別 AI が誤判定する余地が残ると判明 → 分類見直しを別 plan に escalate
- スコープが `~/.claude/` / `~/.codex/` / dotfiles に広がる兆候

## 検証

```sh
cd /home/otaku/agentops

# frontmatter parse OK + applies-to 値の妥当性
python3 - <<'PY'
import pathlib, sys, yaml
ALLOWED = {'global', 'shared-cli-spec', 'agentops-internal', 'template-source'}
ok = True
counts = {}
for p in sorted(pathlib.Path('docs').glob('*.md')):
    txt = p.read_text()
    parts = txt.split('---\n', 2)
    if len(parts) < 3 or parts[0].strip():
        print(f'BROKEN-FRONTMATTER: {p}'); ok = False; continue
    fm = yaml.safe_load(parts[1]) or {}
    if 'applies-to' not in fm:
        print(f'MISSING-APPLIES-TO: {p}'); ok = False; continue
    val = fm['applies-to']
    if val not in ALLOWED:
        print(f'INVALID-APPLIES-TO: {p}: {val}'); ok = False; continue
    counts[val] = counts.get(val, 0) + 1
print('counts:', counts)
sys.exit(0 if ok else 1)
PY

# regression なし
python3 -m compileall tools
python3 -m pytest tools/agentops_cli/tests tools/agentops_monitor/tests -q

# link check
npx --yes markdown-link-check docs/*.md README.md AGENTS.md CLAUDE.md

# cross-review
scripts/agentops delegate --to codex --role review_frontier --effort high --input docs/00-glossary.md
```

## 次セッションへ残すこと

本 task が 1 セッションで完了する想定。完了後は plan 全体 archive で `.agentops/archive/2026-04-30-applies-to-and-trinity/` へ移動し、`prompts/next-session.md` は生成しない (残作業なし)。

未完了の場合のみ:

- 残作業の概要
- 直前停止時のコミット / branch
- 次回 entry point (該当 step 番号)
