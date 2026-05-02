---
last_reviewed: 2026-05-02
next_review_by: 2026-08-02
reviewer: pachinko-spec
language: ja
applies-to: global
---

# 通知戦略

## 目的

複数プロジェクトの作業状況・セッションのライフサイクル・任意のアラートを、外部 cron / hook / 手動実行から **一方向の Discord webhook digest** として届けるための設計思想。実体 CLI は [agentops-watch notify](11-monitoring-cli.md)、上位の最新性・監視論は [最新性と監視](06-freshness-and-monitoring.md) を参照する。

本 docs は **設計思想と契約** だけを扱い、実 cron 行・実 hook ファイルはプロジェクトまたはグローバル設定側で運用する。

## shared-cli-spec パターンの適用

本 docs は agentops の三役 ((a) 設計思想カタログ / (b) 共有 CLI / (c) 雛形配布元) のうち、**思想層 (a)** を担う。実装層 (b) は agentops repo の共有 CLI に集約され、利用層 (host / 他 repo / cron / hook / shell scripts) は CLI を呼び出すだけで実装本体を touch しない。用語定義 (§三役 / §shared-cli-spec パターン を含む) は [docs/00-glossary.md §docs 分類 / リポジトリ責務](00-glossary.md#docs-分類--リポジトリ責務) を参照。

| 層 | 役割 | 実体 | `applies-to` |
| --- | --- | --- | --- |
| 思想層 | kind / channel mapping / DbC / rate-limit / 起動契約を固定する | 本 docs (`docs/18-notification-strategy.md`) | `global` |
| 実装層 | 思想を実現する共有 CLI 仕様 + 実体 | [`docs/11-monitoring-cli.md`](11-monitoring-cli.md) + `tools/agentops_monitor` (`scripts/agentops-watch notify --kind <kind>`) | `shared-cli-spec` |
| 利用層 | 共有 CLI を呼び出す | cron (`config/cron.example`) / Claude Code hook / Codex hook / shell scripts (host 側 `audit-*.sh` 等) | — (各層の運用ファイル) |

別 AI が読むときの指針:

- **思想 (本 docs)** は `applies-to: global` で全 host / 全 project に適用される。グローバル設定 (`~/.claude/CLAUDE.md` / `~/.codex/AGENTS.md`) で参照しても良い。
- **実装本体** (`tools/agentops_monitor`) を再実装しない。同等の通知が必要なら `agentops-watch notify --kind <kind>` を呼ぶ。
- **利用層** (cron 行 / hook ファイル / shell script) は各 host / 各 repo の運用責任。本 docs は **起動契約** と雛形だけを規定し、実ファイル本体は別途配置する。
- **環境変数の値** (Webhook URL) は host 側で export される `DISCORD_WEBHOOK_URL_{DAILLY,WEEKLY,MONTHLY,ANT_TIME}` を尊重する。本 docs / agentops repo に値そのものを書かない。

## 通知の目的 3 分類

| 分類 | 例 | channel | 起動方法 |
| --- | --- | --- | --- |
| digest | 日報 / 週報 / 月報の作業状況集計 | DAILLY / WEEKLY / MONTHLY | cron / systemd timer |
| session lifecycle | (廃止、2026-05-02) SessionStart / SessionEnd の通知は user 介入を要さない noise として hook 側から削除済み | — | hook 起動なし (kind 自体は CLI に残存し手動 alert / 第三者統合用) |
| alert | PermissionRequest 待ち / Stop failure / 高リスク変更着手 / cross-review 完了 / 任意のアラート | ANT_TIME (随時) | hook / 手動 / `notify --kind alert` |

`ANT_TIME` は「随時通知」を意味するユーザー固有の channel 名で、即応性重視の単一受け口として運用する (誤爆防止と即応性のため digest channel と分離)。

## channel と環境変数の固定マッピング

Webhook URL は `~/.bashrc` などで export 済みの **既存環境変数を正** とする。本 docs は新規 envvar を導入しない。

| 環境変数 | channel 名 | 発火元 | 主な内容 |
| --- | --- | --- | --- |
| `DISCORD_WEBHOOK_URL_DAILLY` | DAILLY | 朝の cron | `~/dev/` 配下プロジェクトの未完了 task / handoff / next-session.md / dirty worktree / stuck run |
| `DISCORD_WEBHOOK_URL_WEEKLY` | WEEKLY | 週次の cron | 週次集計 + 完了 plan 一覧 + 残課題サマリ |
| `DISCORD_WEBHOOK_URL_MONTHLY` | MONTHLY | 月初の cron | 月次集計 + archive サマリ + 陳腐化チェック対象 |
| `DISCORD_WEBHOOK_URL_ANT_TIME` | ANT_TIME (随時) | hook / `--kind alert` / `--kind permission-wait` / `--kind stop-failure` 等 | 承認待ち / Stop failure (品質ゲート違反) / 任意アラート (SessionStart / SessionEnd lifecycle 通知は 2026-05-02 に hook 側から削除済) |

hook 経路で retain する ANT_TIME 通知は `stop-failure` / `permission-wait` / `alert` の 3 種だけに固定する。`session-start` / `session-end` は CLI kind として互換維持するが、user 介入を要さない lifecycle 通知として hook からは発火しない。

**旧環境変数 `AGENTOPS_DISCORD_WEBHOOK_URL`** は deprecated。docs/11 の互換注記つきで残すが、新規実装・新規 cron は本 docs の 4 本立てに従う。

`ANT_TIME` の typo (本来 `ANY_TIME`) はユーザー環境で既に export 済みの実値であり、本 docs はその実値を尊重する (壊さない原則)。

## 通知種別 (kind) と channel の対応

`agentops-watch notify --kind <kind>` の `kind` は本 docs で網羅的に列挙する。CLI 実装本体は別 plan のため、ここでは **契約のみ** を確定する。

| kind | channel | 起動方法 | payload 概要 |
| --- | --- | --- | --- |
| `daily` | DAILLY | `agentops/scripts/audit-daily.sh` (cron `10 9 * * *`) | 当日の未完了 task / handoff / next-session.md / dirty worktree / stuck run の集計 (Claude 起動なし、軽量集計のみ。任意 `--message` を `audit log` field として末尾に追加) |
| `weekly` | WEEKLY | `agentops/scripts/audit-weekly.sh` (cron `0 9 * * 1`) | `claude -p /weekly-audit` skill 起動 (timeout 1800s) + 多 project 中量レビュー (Trinity / DbC / localize 4 戦略 / freshness drift)。tail 50 を `--message` の `audit log` field として送信 |
| `monthly` | MONTHLY | `agentops/scripts/audit-monthly.sh` (cron `0 11 1 * *`) | `claude -p /monthly-audit` skill 起動 (timeout 2400s) + 重量監査 (旧 quarterly 吸収): docs drift / dependency staleness via context7 / Trinity 境界違反 / archive 候補。tail 50 を `--message` の `audit log` field として送信 |
| `session-start` | ANT_TIME | (2026-05-02 廃止) hook 起動なし。kind は CLI に残存し手動 alert / 第三者統合からの呼び出し用 | プロジェクトパス / branch / 未完了 task 数 / next-session.md エントリ |
| `session-end` | ANT_TIME | (2026-05-02 廃止) 同上 | プロジェクトパス / branch / 当セッションで触ったファイル数 / 未完了 task 数 |
| `permission-wait` | ANT_TIME | PermissionRequest hook | 承認待ちの tool 名 / プロジェクトパス / 一時 stash の有無 |
| `alert` | ANT_TIME | 任意 (`--message <text>`) | 高リスク変更着手 / cross-review 完了 / 自由メッセージ |
| `stop-failure` | ANT_TIME | Stop hook (品質ゲート違反 block 時) | 失敗理由 / 直前 tool / プロジェクトパス |

digest kind (daily / weekly / monthly) の `--message` は任意で、cron スクリプト (例: `audit-*.sh`) が log 要約を embed に乗せる経路として使う。指定された場合は `sanitize_mention_text` を通し、Discord embed の field value 制限 (1024 文字) を尊重して truncate した上で `audit log` field を末尾に追加する。embed 全体の field 上限 (25) を超える場合は project field 数を 24 に制限して audit log の枠を確保する。

## 多プロジェクト走査ルール (auto-discovery)

cron 起動の digest (`daily` / `weekly` / `monthly`) では、`agentops-watch notify --auto-discover` (or `check --auto-discover`) で **4 root** を浅く scan する:

- `~/.claude` 直下 (Claude Code global)
- `~/.codex` 直下 (Codex global)
- `~/agentops` 直下 (本 repo)
- `~/dev/*` (1 階層 glob、max depth 1)

判定条件は **`<root>/.agentops` が directory として存在すること** のみ。空 `.agentops/` も対象に含める (ユーザー方針: 「対象を絞らず必ず scan」)。`.agentops/plans/current.md` や `tasks/*.md` の有無で gating はしない。broken symlink / OSError は continue で skip し、重複 path は `Path.resolve()` で dedupe。

非 git directory (`~/.claude` / `~/.codex` 等) でも `.agentops/{tasks,handoffs,runs,prompts}` 集計は実行する (CLI 内部で git status 失敗を early return せず fall-through)。

`--auto-discover` と `--projects` は **排他**。0 件マッチでも空 list を返し空 embed を 1 通送信する (毎朝送信を維持)。`alert` / `permission-wait` / `stop-failure` は単一プロジェクト指定のため走査不要。`session-start` / `session-end` の hook 起動は 2026-05-02 に廃止 (kind 自体は手動 alert 互換性のため CLI に残存)。

CLI 仕様の詳細は [docs/11-monitoring-cli.md §`--auto-discover` の走査仕様](11-monitoring-cli.md) を参照。

## payload 雛形 (Markdown → Discord embed)

Discord embed の最小構造は以下:

```jsonc
{
  "username": "agentops-watch",
  "allowed_mentions": { "parse": [] },
  "embeds": [
    {
      "title": "<kind> digest — <Asia/Tokyo timestamp>",
      "color": 3447003,
      "fields": [
        { "name": "project: <name>", "value": "branch: <branch>\nopen tasks: <n>\nhandoffs: <n>\nnext-session: <yes/no>", "inline": false }
      ],
      "footer": { "text": "DbC: stuck run / dirty worktree / freshness は別表" }
    }
  ]
}
```

`allowed_mentions: {"parse": []}` を **必須** とする。`alert --message <text>` のような任意テキストや branch / project 名に `@everyone` / `@here` / `<@user-id>` 等が紛れた場合の予期しない mention を防ぐ。実装側でも payload 組み立て時に sanitization を行う。Discord 公式 webhook docs の推奨に沿った設計。

具体テンプレートは実装 plan で `tools/agentops_monitor/notifiers/discord.py` 等に近接配置する想定 (本 PR は未生成、フィールド契約のみ規定)。

digest kind に `--message` が指定された場合の audit log field は次の形になる:

```jsonc
{
  "name": "audit log",
  "value": "[sanity-check] critical: 0, deprecated: 2",  // sanitize + 1024 truncate 済
  "inline": false
}
```

### channel 別テンプレート要件

| channel / kind | title 形式 | 必須 fields | 任意 fields |
| --- | --- | --- | --- |
| DAILLY | `daily digest — <YYYY-MM-DD>` | 未完了 task 数 / handoffs / next-session.md 有無 | dirty worktree / stuck run |
| WEEKLY | `weekly digest — <YYYY-Www>` | 完了 plan / 残 plan / 完了 task 数 | freshness alert |
| MONTHLY | `monthly digest — <YYYY-MM>` | archive 行追加件数 / 陳腐化 source 数 | open PR 集計 |
| ANT_TIME / `session-*` | (2026-05-02 廃止、hook 経路無し) `<kind>: <短い見出し>` | (互換のため残置) プロジェクトパス / branch / 発火 hook 名 | 任意の補足 message |
| ANT_TIME / `permission-wait` | `permission-wait: <tool 名>` | プロジェクトパス / branch / 待機中 tool | 一時 stash の有無 |
| ANT_TIME / `stop-failure` | `stop-failure: <短い見出し>` | プロジェクトパス / branch / 失敗理由 | 直前 tool 名 |
| ANT_TIME / `alert` | `alert: <短い見出し>` | message | プロジェクトパス / branch (指定時のみ) |

`alert` は **`--project <path>` を任意** とする (手動アラートやプロジェクト非依存の通知に対応)。プロジェクト指定がない場合は project / branch field を省略する。それ以外の ANT_TIME kind (`permission-wait` / `stop-failure`) は `--project <path>` 必須。`session-*` の hook 起動は廃止済だが、CLI に kind 自体は残しているため手動 alert 互換性のため `--project <path>` 必須仕様も維持する。

## SECRET 管理

- Webhook URL は `~/.bashrc` export を正とする (既存運用と一致)。`~/.claude/.env` 等への複製・移植は行わない。
- リポジトリ・diff・log・PR 本文・handoff・session 記録に Webhook URL の **値** を出さない。**変数名** だけを書く。
- `--dry-run` モードでは payload を stdout に出すが、URL は環境変数のまま参照させ、本 CLI も値を表示しない。
- 本 docs と関連 docs/雛形に Webhook URL の値そのものを **絶対に書かない**。

## 公式 Discord plugin との棲み分け

Claude Code 公式 plugin (`~/.claude/plugins/marketplaces/claude-plugins-official/external_plugins/discord/`) は MCP server で **双方向の Discord アクセス** (channel 一覧・DM 送信・履歴取得 等) を提供する。本 docs の対象は **一方向の webhook digest** のみで、用途が異なる。

| 用途 | 推奨 |
| --- | --- |
| 双方向の Discord 操作 (DM 送受信、対話的な channel 操作) | 公式 Discord plugin |
| 一方向の digest / alert (cron / hook 起動) | 本 docs + agentops-watch notify |
| 双方向アクセスを別セッションで遮断したい場合 | 公式 plugin を MCP `enabled: false` にする / disable する |

両者は併用可能だが、digest 用途では公式 plugin は overkill。

## cron / systemd timer の起動例 (3-tier 構成)

実 cron 行は wrapper script 経由で `agentops/scripts/audit-*.sh` を呼ぶ形に集約する。crontab 反映の手順と sample は [config/cron.example](../config/cron.example) を参照。

```cron
BASH_ENV=$HOME/.bashrc

# daily: 朝 9:10、軽量集計のみ (Claude 起動なし)
10 9 * * *  /home/<user>/agentops/scripts/audit-daily.sh

# weekly: 月曜 9:00、claude -p /weekly-audit + 多 project 中量レビュー
0 9 * * 1   /home/<user>/agentops/scripts/audit-weekly.sh

# monthly: 月初 1 日 11:00、claude -p /monthly-audit + 重量監査 (quarterly 吸収)
0 11 1 * *  /home/<user>/agentops/scripts/audit-monthly.sh
```

旧 quarterly cron (`0 9 1 1,4,7,10 *` で `audit-quarterly.sh`) は廃止。context7 重量 freshness 観点は monthly 側 skill (`/monthly-audit`) が吸収する。

systemd timer 派は同等の `OnCalendar=` 表現で書く (例: `OnCalendar=*-*-* 09:10:00`、Asia/Tokyo の timezone は host 側で設定済み前提)。

`permission-wait` / `stop-failure` / `alert` は cron ではなく **hook 起動 / 手動起動** が主なため、本 docs では起動契約のみ規定し、実 hook ファイルはグローバル `~/.claude/hooks/` または対象 CLI の hook 実装で扱う。`session-start` / `session-end` の hook 経路は 2026-05-02 に廃止 (user 介入を要さない noise として user 判断で削除)。kind 自体は CLI に残存し、第三者統合や手動 alert で再利用可能。

## ANT_TIME 頻度上限ガード

`ANT_TIME` channel は PermissionRequest 待ち / Stop failure / 任意アラートが集中する想定で、Discord 側 rate-limit に抵触しないよう **CLI 側に保守的な自前ガード** を入れる (2026-05-02 に SessionStart / SessionEnd の hook 経路が廃止されたため、頻度はかつての設計より低い)。

- **Discord 側 rate-limit**: 公式仕様上、固定値ではなく **応答ヘッダ** (`X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset` / `X-RateLimit-Reset-After` / `Retry-After`) に従う。HTTP 429 応答時は `Retry-After` ヘッダの秒数だけ待機する。詳細は [Discord 公式 Rate Limits docs](https://discord.com/developers/docs/topics/rate-limits) を参照する。
- **CLI 自前ガード (保守値)**: 1 分あたり 5 件 / 1 時間あたり 60 件 (実装 plan で調整可)。Discord 側の動的 limit より十分手前で skip させ、429 を出さない設計。
- **超過時の挙動**: stdout / stderr に warning を出し、当該 payload を skip。直近送信時刻と件数は `~/.cache/agentops-watch/anttime-rate.json` 等の host-local state に保存する (リポジトリには置かない)。
- **緊急 alert (`--kind alert --priority high`)**: 自前ガードを bypass する選択肢を残す (実装 plan で判断、デフォルトは bypass しない)。Discord 側 rate-limit (応答ヘッダ) は常に尊重する。

## DbC との関係

通知 CLI は [DbCと品質ゲート](03-dbc-and-quality-gates.md) のうち、observability 層を支える。5 条件は本章で具体化する:

- **適用前提**: 対象 channel の Webhook URL が環境変数に設定されていること、digest 系 (`daily` / `weekly` / `monthly`) では `--projects` 指定 YAML が読めること、ANT_TIME のうち `permission-wait` では `--project <path>` と `--message <tool>` (待機中 tool 名) が指定されること、`stop-failure` では `--project <path>` と `--message <text>` (失敗理由) が指定されること、`alert` では `--message <text>` が指定され (`--project <path>` は任意)、`session-*` (kind は残存しているが hook 経路廃止) を手動 alert として呼ぶ場合は `--project <path>` 必須、いずれの場合も `Asia/Tokyo` の host 時刻が利用可能であること。
- **適用不変**: Webhook URL の値を payload・log・stdout・stderr に出さない。secret をリポジトリに保存しない。プロジェクトのファイルを変更しない。`--dry-run` では URL を読まなくても payload を組み立てられる。すべての payload に `allowed_mentions: {"parse": []}` を含め、`@everyone` / `@here` / `<@user-id>` 等の予期しない mention を防ぐ。CLI 自前の頻度上限ガード (上記「ANT_TIME 頻度上限ガード」節) を超過した payload は warning + skip して継続し、本 DbC 停止条件としては扱わない。
- **適用完了**: text または JSON の report 出力 (実送信モードでは Discord HTTP 200/204 確認、`--dry-run` では payload を stdout に出すまで)。
- **適用停止**: Webhook URL 未設定で実送信を求められた / connect timeout / **外部側の HTTP 429 / 5xx 応答** (Discord サーバー側の rate-limit / 障害) / SECRET 漏洩疑義 / `--projects` YAML 読み込み失敗 — いずれも本 CLI を skip せずに **当該 invocation を停止** し DbC 停止条件として扱う。HTTP 429 を受けた場合、本 invocation は exit 2 で停止し、`Retry-After` ヘッダの値を host-local state に記録した上で、**次回起動 (cron / hook の次の発火) で当該 channel への送信を再開できるかを判定** する。invocation 内でリトライ・wait を行わない方針 (cron 連発による滞留を避ける)。CLI 自前の頻度上限ガードによる skip は本停止条件と区別する (前者は payload 単位で skip 継続、後者は CLI 全体を停止)。

## quarterly の monthly 吸収

旧 `/quarterly-review` skill と `/home/otaku/bin/audit-quarterly.sh` は本 plan で廃止 (`2026-04-30-discord-cron-3tier-redesign`)。

- monthly 側 skill (`/monthly-audit`) が context7 / WebFetch を使った重量 freshness check を吸収
- `audit-quarterly.sh` cron 行 (`0 9 1 1,4,7,10 *`) は crontab 反映時に削除
- 旧 quarterly skill 観点は `~/.claude/skills/monthly-audit/SKILL.md` の Procedure 3 (context7 / `freshness-audit` 内部呼び出し) に統合済み

季節境界の重量チェックタイミングは無くなるが、`monthly-audit` が毎月実行されるため累積遅延は最大 1 ヶ月で済む。

## 既存 cron 実装との関係 (運用観察)

**2026-04-30 移行完了**: 本 plan (`2026-04-30-discord-cron-3tier-redesign`) で `agentops/scripts/audit-{daily,weekly,monthly}.sh` への集約と auto-discovery 拡張が完了。

旧実装の状態:
- `~/dotfiles/bin/notify-pending-discord.sh` (daily / weekly 用): 内部参照する `discord-notify.sh` が dotfiles から削除済のため壊れた状態だった。crontab 切替で cron から外し、dead code 化。dotfiles repo 内の deprecation guard 追加は dotfiles 側別 PR で対応 (本 plan scope 外)。
- `/home/otaku/bin/audit-{weekly,monthly}.sh`: agentops-watch 経由で動作していた dotfiles 単一プロジェクト対象 wrapper。crontab 切替後は `agentops/scripts/audit-*.sh` への symlink 化 or 削除を PR-E で実施。
- `/home/otaku/bin/audit-quarterly.sh`: quarterly 廃止に伴い削除 (PR-E)。

サーバー状態通知の `metrics-collect.sh` / `server-report.sh` は Claude Code とは独立した運用であり、本 docs の対象外。

## スコープ外

- `tools/agentops_monitor` の `--kind` 拡張実装本体 + `tools/agentops_monitor/notifiers/discord.py` 等の実体生成 (本 docs は契約のみ)
- グローバル `~/.claude/hooks/session_start.py` / `session_end.py` の実体追加 (本 docs と並行する別 work で扱う)
- subagent 通知抑制 / SubagentStart / SubagentStop hook 設計 (将来 sentrux 等の出力 link が通知に乗る体験を入れた時点で別 plan)
- 公式 Discord plugin のセットアップ自動化
- `~/dotfiles/bin/notify-pending-discord.sh` の中身改修 (dotfiles repo 別管理)
- 実 cron 行の本 PR での反映 (B-1 docs 完了後、B-2 で user 確認後に処理)
- 旧 envvar `AGENTOPS_DISCORD_WEBHOOK_URL` の即時撤去 (deprecated 注記つきで段階的に縮退)

## 関連リンク

- [docs/06-freshness-and-monitoring.md](06-freshness-and-monitoring.md) — 上位の最新性・監視論
- [docs/11-monitoring-cli.md](11-monitoring-cli.md) — `agentops-watch notify` CLI 仕様 (実体)
- [docs/03-dbc-and-quality-gates.md](03-dbc-and-quality-gates.md) — DbC 5 条件の単一真ソース
- [docs/12-harness-engineering.md](12-harness-engineering.md) — harness と監視 CLI の責務分離
- [docs/17-cross-reference.md](17-cross-reference.md) — rule ↔ skill ↔ workflow ↔ hook 逆参照表
- [templates/claude/hooks/session-notify-stub.md](../templates/claude/hooks/session-notify-stub.md) — SessionStart/End hook 仕様メモ
- [rules/catalog.md](../rules/catalog.md) — `notification-policy` 候補
- [skills/catalog.md](../skills/catalog.md) — `notification-digest-writer` 候補
- [workflows/catalog.md](../workflows/catalog.md) — `notification-cron-setup` 候補
