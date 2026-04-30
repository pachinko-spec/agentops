# Discord 通知 cron の 3-tier 再編と agentops 集約

date: 2026-04-30
status: accepted
plan: 2026-04-30-discord-cron-3tier-redesign

## 背景

`crontab -l` を確認した結果、Discord 通知系 cron は 2 系統が混在していた:

- `~/dotfiles/bin/notify-pending-discord.sh --kind {daily,weekly}` (dotfiles wrapper) — 内部参照する `discord-notify.sh` が dotfiles working tree から削除済のため壊れた状態 (silent skip、配信されていない)
- `/home/otaku/bin/audit-{weekly,monthly,quarterly}.sh` (host-local wrapper) — agentops-watch notify 経由で動作していたが dotfiles 単一プロジェクト対象のみ

`config/projects.yml` も agentops 1 行のみで、`~/.claude` / `~/.codex` / `~/dev/*` 配下の `.agentops/` は通知対象外。`docs/18-notification-strategy.md:78-84` で多プロジェクト走査ルールを契約済だったが、CLI 実装 (`tools/agentops_monitor/__main__.py`) が追従していない gap があった。

## 決定

Discord 通知 cron を **3-tier 構成** へ再編し、wrapper script を `/home/otaku/agentops/scripts/` に集約する:

- **daily** (毎日 9:10): `agentops/scripts/audit-daily.sh` → `agentops-watch notify --kind daily --auto-discover` のみ呼ぶ軽量 wrapper (Claude 起動なし)
- **weekly** (毎週月曜 9:00): `agentops/scripts/audit-weekly.sh` → `claude -p /weekly-audit` を timeout 1800s で起動、tail 50 を `--message` の `audit log` field として WEEKLY channel へ送信
- **monthly** (毎月 1 日 11:00): `agentops/scripts/audit-monthly.sh` → `claude -p /monthly-audit` を timeout 2400s で起動 (旧 quarterly review を吸収)、tail 50 を `--message` field として MONTHLY channel へ送信

通知対象は `agentops-watch notify --auto-discover` で **4 root を浅く scan** (`~/.claude` / `~/.codex` / `~/agentops` / `~/dev/*`)。`.agentops/` directory が存在する全 project が対象 (空の `.agentops/` も含む — ユーザー方針)。

## 採用しないこと

- 旧 `notify-pending-discord.sh` (dotfiles wrapper) を crontab から呼び続ける運用
- quarterly 専用 cron 行 + skill (monthly に吸収済)
- `config/projects.yml` を hardcode して project 列挙する運用 (CI / 単体動作確認時の fallback として残置)
- 同名 skill (`/sanity-check` / `/quarterly-review` / dotfiles 由来 `/monthly-audit`) との衝突: global skill は `/weekly-audit` / `/monthly-audit` を新規定義し、dotfiles 側 `*-scope.md` は touch しない (user 認識「もう読み込まれていない」前提)

## 影響範囲

### agentops repo (本 plan で実装)

- `tools/agentops_monitor/__main__.py`: `--auto-discover` flag + `discover_projects()` helper + 非 git fall-through (PR-A #66)
- `scripts/audit-{daily,weekly,monthly}.sh`: 新規 wrapper (PR-C #68)
- `docs/{11,18,19}-*.md` + `config/cron.example`: 3-tier 構成への docs 同期 (PR-D #69)
- `tools/agentops_monitor/__main__.py`: send_webhook の HTTP header baseline 強化 (Cloudflare bot block 回避、PR #70 + #71)
- `tools/agentops_monitor/__main__.py`: digest を embed.description ベースに、signal-only filter + emoji 装飾 (PR #70)

### グローバル設定 (`~/.claude/`)

- `~/.claude/skills/weekly-audit/SKILL.md` 新規 (PR-B #67)
- `~/.claude/skills/monthly-audit/SKILL.md` 新規 (PR-B #67、quarterly 吸収)

### host-local (`crontab` / `/home/otaku/bin/`)

- crontab: 5 行削除 + 3 行追加 + `BASH_ENV=$HOME/.bashrc` 追加 (PR-D #69 後に user 手動)
- `/home/otaku/bin/audit-weekly.sh` → `agentops/scripts/audit-weekly.sh` への symlink (PR-E)
- `/home/otaku/bin/audit-monthly.sh` → 同上 (PR-E)
- `/home/otaku/bin/audit-quarterly.sh` 削除 (PR-E)

### dotfiles repo (本 plan scope 外、別 PR で対応推奨)

- `~/dotfiles/bin/notify-pending-discord.sh` は cron から外れた後 dead code 状態。dotfiles 側で deprecation guard (`echo "deprecated..." >&2; exit 1`) を追加 + 将来削除を recommend。本 plan では touch しない。
- `~/dotfiles/.claude/{sanity-check,monthly-audit,quarterly-review}-scope.md` は project-local scope file として残置 (skill 本体ではないため global skill と衝突しない)。

## 教訓

### Cross-review reviewer の scope 越境

PR-A の cross-review delegate (Codex) で reviewer が `scripts/agentops archive task` を勝手に実行する事象が発生した (PR-A merge 前なので AGENTS.md post-merge archive 規定違反)。

教訓: cross-reviewer は **所見を出すだけ** で archive / commit / file move 等の作業を行わない。これは AGENTS.md / CLAUDE.md の cross-review skill 仕様にも明記済 (「reviewer の所見は参考情報。採否、修正範囲、延期、統合判断はメインエージェントが持つ」) だが、Codex 側 hook (Stop hook での「completed task を archive」誘導) が reviewer に同じ判断を促してしまうため、hook 設定で reviewer の archive 操作を抑制する追加対策が望ましい。

### Cloudflare bot block の段階的発覚

実環境で Discord 配信を試した結果、urllib default header (Content-Type + User-Agent) の minimum 性が Cloudflare bot heuristics で断続的に block (HTTP 403 + error code 1010) されることが判明した。

- 第 1 回 hotfix (PR #70): User-Agent を独自値に明示
- 第 2 回 hotfix (PR #71): Accept / Accept-Language / Connection も baseline として明示

教訓: 実環境テスト無しに mock test だけで検証完了とせず、本番 webhook で 5 回以上の連続送信を試すことを動作確認 DbC の必須項目とする。

### PR scope と運用上の依存

PR-E (cleanup) を main に追随させない (rebase しない) 運用判断は、cleanup task 内容が hotfix に依存しないため成り立つが、PR-E branch 上で wrapper 動作確認を行うと hotfix 未適用状態でテストすることになり HTTP 403 が再現する。動作確認は **main branch 上で** 行うのが正解。

## ロールバック

各 layer ごとの rollback path:

- crontab 編集: `~/.claude/.agentops/runs/<ts>-pr-d-crontab-snapshot/crontab.before` で復元 (`crontab - < snapshot`)
- agentops repo の各 PR: 通常の `git revert <hash>` (PR-A〜#71)
- skill 配置取消: `rm -rf ~/.claude/skills/{weekly,monthly}-audit`
- symlink 取消: `rm /home/otaku/bin/audit-{weekly,monthly}.sh`
- 旧 `audit-quarterly.sh` 復元: PR-D 反映前の状態 (本 plan で削除済) を git 履歴から取得不可 (host-local script、未 commit)。再実装が必要なら旧 logic を `~/dotfiles/bin/notify-pending-discord.sh` 周辺の git history から復元する。
