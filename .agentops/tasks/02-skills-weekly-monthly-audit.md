---
task-id: 02-skills-weekly-monthly-audit
plan-id: 2026-04-30-discord-cron-3tier-redesign
status: pending-merge
branch: claude/discord-cron-3tier-pr-b-skills
pr-target: B
started: 2026-04-30T15:00:00+09:00
---

> **status note**: skill 配置 (`~/.claude/skills/{weekly,monthly}-audit/SKILL.md`) と DbC 完了条件は満たしているが、AGENTS.md §AI auto-merge 許諾の post-merge 必須手順「完了 task を archive へ移動」は PR-B が main へ merge された後に行う。merge 前の archive は AGENTS.md 規定違反 (PR-A 時の Codex scope 違反事例と同一)。本 PR merge 後に `status: completed` へ更新し、`scripts/agentops archive task --task-id 02-skills-weekly-monthly-audit` を別 commit で実行する。

# PR-B: weekly-audit / monthly-audit skill 新設

## 目的

`~/.claude/skills/weekly-audit/SKILL.md` `~/.claude/skills/monthly-audit/SKILL.md` を新設し、agentops 設計思想 (Trinity / DbC / localize 4 戦略 / freshness drift) ベースの多 project 監査を skill として実装する。

これにより `claude -p "/weekly-audit"` `claude -p "/monthly-audit"` が PR-C で新設する `scripts/audit-{weekly,monthly}.sh` から起動可能になり、tail 50 行が `agentops-watch notify --kind {weekly,monthly} --message ...` の audit log field として Discord に届く。

## 配置と repo 境界

- **skill 本体**: `~/.claude/skills/{weekly,monthly}-audit/SKILL.md` (Claude Code global、agentops repo 外)
- **agentops repo 側 commit**: 本 task md (PR-B trace) + archive task 01-cli-auto-discover (PR-A 完了分の archive 移動) のみ
- **~/.claude/.agentops/ 記録**: skill 配置作業の grounding として、`~/.claude/.agentops/runs/` にも作業 log を残す
- skill template の `templates/claude/skill/{weekly,monthly}-audit/` 雛形配布は別 plan で対応 (本 PR scope 外)

## DbC

### 前提条件
- PR-A merged (`agentops-watch notify --auto-discover` が main 上で動く)
- `~/.claude/skills/` directory が存在 (現状 6 skill 配置済)
- `claude` CLI が `~/.local/bin/claude` で実行可能

### 不変条件
- skill 内に webhook URL や API token を hardcode しない
- skill が `.agentops/` を変更しない (read-only)
- skill が cross-review skill を呼ばない (loop 防止)
- dotfiles 側 `monthly-audit-scope.md` 等 (project-local scope ファイル) は touch しない

### 完了条件
- `~/.claude/skills/weekly-audit/SKILL.md` 配置
- `~/.claude/skills/monthly-audit/SKILL.md` 配置
- 各 skill の frontmatter (name / description) と 4 セクション (`## Use this when` / `## Procedure` / `## Output` / `## Boundaries`) が記述済み
- 手動 dry-run (`claude -p "/weekly-audit" --output-format text` 想定で skill が呼べるか) で検出される
- agentops repo 側: archive task 01 + 02 task md 起票が commit / PR / merge 済み
- secret 値 hardcode 無し (`grep -rE 'sk-|xoxb-|ghp_|discord\.com' ~/.claude/skills/{weekly,monthly}-audit/`)

### 禁止事項
- skill 内で code 変更
- skill 内で `.agentops/` への write
- secret hardcode
- API timeout を wrapper script より大きく設定する (skill 側は記述だけで実 timeout は wrapper の `timeout 1800/2400`)

### 停止条件
- agentops-watch CLI が exit 2 を返す経路
- skill 配置で既存 6 skill との衝突
- claude CLI で skill が検出されない

## Skill 設計詳細

### `~/.claude/skills/weekly-audit/SKILL.md`

```yaml
frontmatter:
  name: weekly-audit
  description: |
    Multi-project weekly review across auto-discovered .agentops projects,
    evaluating each through agentops Trinity (catalog / shared-cli-spec /
    template-source), localize 4 strategies, and DbC drift. Cron-only via
    /home/otaku/agentops/scripts/audit-weekly.sh.
```

#### Procedure
1. `bash -lc "/home/otaku/agentops/scripts/agentops-watch check --auto-discover --json"` を実行して project list 取得
2. 各 project (`~/.claude` `~/.codex` `~/agentops` `~/dev/*/`) の `.agentops/` 構造を `Read` で確認:
   - `plans/current.md` `tasks/*.md` `handoffs/*.md` `prompts/next-session.md` `runs/*/status.json`
3. agentops 設計思想観点で評価:
   - Trinity 分類 (`docs/00-glossary.md` の `applies-to` 用語、`AGENTS.md` の三役宣言)
   - DbC 5 条件 (前提 / 不変 / 完了 / 禁止 / 停止) の記述有無
4. localize 4 戦略 (greenfield / inventory-rebuild / coexistence / freeze) で各 project を分類 (`docs/19`)
5. `freshness-sources.yml` の stale 行を flag (skill 単体では context7 を呼ばず、明らかな drift のみ)
6. markdown レポート出力 (末尾 30 行に per-project 1 行 verdict、1024 文字 truncate 想定)

#### Output
```text
# weekly-audit 2026-MM-DD

## per-project verdict (末尾 30 行)
- ~/.claude (.agentops): OK — plans 0, tasks 0, handoffs 0
- ~/.codex (.agentops): OK — empty .agentops/.tmp only
- ~/agentops (.agentops): OK — branch claude/<...>, PR-B in progress
- ~/dev/<...>: ...
```

#### Boundaries
- code 変更しない
- cross-review skill 呼ばない (cross-review は orchestrator の責務、reviewer は所見のみ)
- `.agentops/` を write しない
- API timeout は wrapper `audit-weekly.sh` 側で 1800s

### `~/.claude/skills/monthly-audit/SKILL.md`

```yaml
frontmatter:
  name: monthly-audit
  description: |
    Heavy structural audit across auto-discovered .agentops projects, absorbing
    former quarterly review. Inspects docs drift, dependency staleness via
    context7 / WebFetch, and global vs project boundary adherence. Cron-only
    via /home/otaku/agentops/scripts/audit-monthly.sh.
```

#### Procedure
1. weekly と同じ project list 取得
2. 各 project `docs/` の `last_reviewed` / `next_review_by` frontmatter を check (`docs/16-global-settings-application-checklist.md` 等の date frontmatter)
3. context7 / WebFetch 経由で `freshness-sources.yml` 全 source の staleness check (`freshness-audit` skill を内部から呼んで良い)
4. Trinity 境界違反列挙:
   - host-side script の重複実装
   - shared-cli (`agentops-watch notify`) を bypass している箇所
   - template-source (`templates/claude/skill/`) と実体 (`~/.claude/skills/`) の drift
5. archive 候補 (90 日以上 update 無い `plans/current.md`) を warning
6. 末尾 30 行に critical / deprecated / drift / archive 候補の numeric summary

#### Output
```text
# monthly-audit 2026-MM

## summary (末尾 30 行)
- critical: 0
- deprecated: 0
- drift: 2 (project / global)
- archive 候補: 1 (~/dev/<...> 90+ days)
- freshness stale: 1 / 12
- ...
```

#### Boundaries
- read-only (各 project の file を read のみ、`agentops archive` を skill 内から実行しない)
- API timeout は wrapper `audit-monthly.sh` 側で 2400s
- quarterly skill (`/quarterly-review`) は呼ばない (本 skill が吸収)

## 検証手順

```bash
# 1. skill 配置確認
ls ~/.claude/skills/weekly-audit/SKILL.md ~/.claude/skills/monthly-audit/SKILL.md

# 2. secret hardcode 検出 (出力 0 行が期待)
grep -rE 'sk-|xoxb-|ghp_|discord\.com/api/webhooks' ~/.claude/skills/{weekly,monthly}-audit/ || echo "no secrets"

# 3. 既存 skill との衝突確認
ls ~/.claude/skills/ | grep -E 'weekly|monthly'

# 4. 手動 dry-run (実 cron 連携は PR-C 以降、ここでは skill が claude 側で読まれることを確認)
# 実際の起動は PR-C の wrapper script で行うため、本 PR では skill md の構文整合と存在のみ確認
```

## auto-merge 許諾条件

- DbC 完了 (上記)
- agentops repo 側 commit に secret 未混入
- scope 単一 (PR-B 範囲内、CLI / wrapper / docs / crontab には触らない)
- skill md 配置は ~/.claude/skills/ (agentops repo 外、git 管理外)、agentops repo の commit 自体は task md 起票 + archive 移動のみ

## ロールバック path

- skill 配置取消: `rm -rf ~/.claude/skills/weekly-audit ~/.claude/skills/monthly-audit`
- 既存 6 skill には影響しない
- agentops repo の commit は revert 可能 (task md だけ)
