---
last_reviewed: 2026-04-29
next_review_by: 2026-07-31
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
| session lifecycle | SessionStart / SessionEnd / next-session.md があるプロジェクトのセッション開始・終了 | ANT_TIME (随時) | Claude Code hook / Codex hook |
| alert | PermissionRequest 待ち / Stop failure / 高リスク変更着手 / cross-review 完了 / 任意のアラート | ANT_TIME (随時) | hook / 手動 / `notify --kind alert` |

`ANT_TIME` は「随時通知」を意味するユーザー固有の channel 名で、即応性重視の単一受け口として運用する (誤爆防止と即応性のため digest channel と分離)。

## channel と環境変数の固定マッピング

Webhook URL は `~/.bashrc` などで export 済みの **既存環境変数を正** とする。本 docs は新規 envvar を導入しない。

| 環境変数 | channel 名 | 発火元 | 主な内容 |
| --- | --- | --- | --- |
| `DISCORD_WEBHOOK_URL_DAILLY` | DAILLY | 朝の cron | `~/dev/` 配下プロジェクトの未完了 task / handoff / next-session.md / dirty worktree / stuck run |
| `DISCORD_WEBHOOK_URL_WEEKLY` | WEEKLY | 週次の cron | 週次集計 + 完了 plan 一覧 + 残課題サマリ |
| `DISCORD_WEBHOOK_URL_MONTHLY` | MONTHLY | 月初の cron | 月次集計 + archive サマリ + 陳腐化チェック対象 |
| `DISCORD_WEBHOOK_URL_ANT_TIME` | ANT_TIME (随時) | hook / `--kind alert` / `--kind permission-wait` 等 | SessionStart / SessionEnd / 承認待ち / 任意アラート |

**旧環境変数 `AGENTOPS_DISCORD_WEBHOOK_URL`** は deprecated。docs/11 の互換注記つきで残すが、新規実装・新規 cron は本 docs の 4 本立てに従う。

`ANT_TIME` の typo (本来 `ANY_TIME`) はユーザー環境で既に export 済みの実値であり、本 docs はその実値を尊重する (壊さない原則)。

## 通知種別 (kind) と channel の対応

`agentops-watch notify --kind <kind>` の `kind` は本 docs で網羅的に列挙する。CLI 実装本体は別 plan のため、ここでは **契約のみ** を確定する。

| kind | channel | 起動方法 | payload 概要 |
| --- | --- | --- | --- |
| `daily` | DAILLY | cron (例: `10 9 * * *`) | 当日の未完了 task / handoff / next-session.md / dirty worktree / stuck run の集計 (任意 `--message` を `audit log` field として末尾に追加) |
| `weekly` | WEEKLY | cron (例: `45 9 * * 1`) | 週次集計 + 直近 7 日の完了 plan / 残課題 (任意 `--message` を `audit log` field として末尾に追加) |
| `monthly` | MONTHLY | cron (例: `0 11 1 * *`) | 月次集計 + archive サマリ + freshness-sources.yml の陳腐化候補 (任意 `--message` を `audit log` field として末尾に追加) |
| `session-start` | ANT_TIME | SessionStart hook | プロジェクトパス / branch / 未完了 task 数 / next-session.md エントリ |
| `session-end` | ANT_TIME | SessionEnd / Stop hook | プロジェクトパス / branch / 当セッションで触ったファイル数 / 未完了 task 数 |
| `permission-wait` | ANT_TIME | PermissionRequest hook | 承認待ちの tool 名 / プロジェクトパス / 一時 stash の有無 |
| `alert` | ANT_TIME | 任意 (`--message <text>`) | 高リスク変更着手 / cross-review 完了 / 自由メッセージ |
| `stop-failure` | ANT_TIME | Stop hook (失敗時) | 失敗理由 / 直前 tool / プロジェクトパス |

digest kind (daily / weekly / monthly) の `--message` は任意で、cron スクリプト (例: `audit-*.sh`) が log 要約を embed に乗せる経路として使う。指定された場合は `sanitize_mention_text` を通し、Discord embed の field value 制限 (1024 文字) を尊重して truncate した上で `audit log` field を末尾に追加する。embed 全体の field 上限 (25) を超える場合は project field 数を 24 に制限して audit log の枠を確保する。

## 多プロジェクト走査ルール

cron 起動の digest (`daily` / `weekly` / `monthly`) では、`~/dev/` 直下を浅く scan して以下を満たすディレクトリを対象とする:

- `.agentops/plans/current.md` が存在する
- または `.agentops/tasks/*.md` (README.md 除く) が 1 件以上存在する
- または `.agentops/prompts/next-session.md` が存在する

上記いずれも無いプロジェクトは digest 対象外 (空通知防止)。`session-*` / `alert` / `permission-wait` は単一プロジェクト指定のため走査不要。

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
| ANT_TIME / `session-*` | `<kind>: <短い見出し>` | プロジェクトパス / branch / 発火 hook 名 | 任意の補足 message |
| ANT_TIME / `permission-wait` | `permission-wait: <tool 名>` | プロジェクトパス / branch / 待機中 tool | 一時 stash の有無 |
| ANT_TIME / `stop-failure` | `stop-failure: <短い見出し>` | プロジェクトパス / branch / 失敗理由 | 直前 tool 名 |
| ANT_TIME / `alert` | `alert: <短い見出し>` | message | プロジェクトパス / branch (指定時のみ) |

`alert` は **`--project <path>` を任意** とする (手動アラートやプロジェクト非依存の通知に対応)。プロジェクト指定がない場合は project / branch field を省略する。それ以外の ANT_TIME kind (`session-*` / `permission-wait` / `stop-failure`) は `--project <path>` 必須。

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

## cron / systemd timer の起動例 (仕様提示、実反映は別 plan)

実 cron 行はプロジェクト or グローバル設定側で運用するため、本 docs は **契約と起動例** のみを示す。

```cron
# DAILLY: 朝 9:10 に ~/dev/ 配下プロジェクトの digest
10 9 * * * /home/<user>/agentops/scripts/agentops-watch notify --kind daily --projects /home/<user>/agentops/config/projects.yml

# WEEKLY: 月曜 9:45 に週次集計
45 9 * * 1 /home/<user>/agentops/scripts/agentops-watch notify --kind weekly --projects /home/<user>/agentops/config/projects.yml

# MONTHLY: 月初 11:00 に月次集計 + archive サマリ
0 11 1 * * /home/<user>/agentops/scripts/agentops-watch notify --kind monthly --projects /home/<user>/agentops/config/projects.yml
```

systemd timer 派は同等の `OnCalendar=` 表現で書く (例: `OnCalendar=*-*-* 09:10:00`、Asia/Tokyo の timezone は host 側で設定済み前提)。

`session-*` / `permission-wait` / `alert` は cron ではなく **hook 起動** が主なため、本 docs では起動契約のみ規定し、実 hook ファイルはグローバル `~/.claude/hooks/` または対象 CLI の hook 実装で扱う。

## ANT_TIME 頻度上限ガード

`ANT_TIME` channel は SessionStart / SessionEnd / PermissionRequest 待ち / 任意アラートが集中するため、Discord 側 rate-limit に抵触しないよう **CLI 側に保守的な自前ガード** を入れる。

- **Discord 側 rate-limit**: 公式仕様上、固定値ではなく **応答ヘッダ** (`X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset` / `X-RateLimit-Reset-After` / `Retry-After`) に従う。HTTP 429 応答時は `Retry-After` ヘッダの秒数だけ待機する。詳細は [Discord 公式 Rate Limits docs](https://discord.com/developers/docs/topics/rate-limits) を参照する。
- **CLI 自前ガード (保守値)**: 1 分あたり 5 件 / 1 時間あたり 60 件 (実装 plan で調整可)。Discord 側の動的 limit より十分手前で skip させ、429 を出さない設計。
- **超過時の挙動**: stdout / stderr に warning を出し、当該 payload を skip。直近送信時刻と件数は `~/.cache/agentops-watch/anttime-rate.json` 等の host-local state に保存する (リポジトリには置かない)。
- **緊急 alert (`--kind alert --priority high`)**: 自前ガードを bypass する選択肢を残す (実装 plan で判断、デフォルトは bypass しない)。Discord 側 rate-limit (応答ヘッダ) は常に尊重する。

## DbC との関係

通知 CLI は [DbCと品質ゲート](03-dbc-and-quality-gates.md) のうち、observability 層を支える。5 条件は本章で具体化する:

- **適用前提**: 対象 channel の Webhook URL が環境変数に設定されていること、digest 系 (`daily` / `weekly` / `monthly`) では `--projects` 指定 YAML が読めること、ANT_TIME のうち `session-*` では `--project <path>` の指す path が存在すること、`permission-wait` では `--project <path>` と `--message <tool>` (待機中 tool 名) が指定されること、`stop-failure` では `--project <path>` と `--message <text>` (失敗理由) が指定されること、`alert` では `--message <text>` が指定され (`--project <path>` は任意)、`Asia/Tokyo` の host 時刻が利用可能であること。
- **適用不変**: Webhook URL の値を payload・log・stdout・stderr に出さない。secret をリポジトリに保存しない。プロジェクトのファイルを変更しない。`--dry-run` では URL を読まなくても payload を組み立てられる。すべての payload に `allowed_mentions: {"parse": []}` を含め、`@everyone` / `@here` / `<@user-id>` 等の予期しない mention を防ぐ。CLI 自前の頻度上限ガード (上記「ANT_TIME 頻度上限ガード」節) を超過した payload は warning + skip して継続し、本 DbC 停止条件としては扱わない。
- **適用完了**: text または JSON の report 出力 (実送信モードでは Discord HTTP 200/204 確認、`--dry-run` では payload を stdout に出すまで)。
- **適用停止**: Webhook URL 未設定で実送信を求められた / connect timeout / **外部側の HTTP 429 / 5xx 応答** (Discord サーバー側の rate-limit / 障害) / SECRET 漏洩疑義 / `--projects` YAML 読み込み失敗 — いずれも本 CLI を skip せずに **当該 invocation を停止** し DbC 停止条件として扱う。HTTP 429 を受けた場合、本 invocation は exit 2 で停止し、`Retry-After` ヘッダの値を host-local state に記録した上で、**次回起動 (cron / hook の次の発火) で当該 channel への送信を再開できるかを判定** する。invocation 内でリトライ・wait を行わない方針 (cron 連発による滞留を避ける)。CLI 自前の頻度上限ガードによる skip は本停止条件と区別する (前者は payload 単位で skip 継続、後者は CLI 全体を停止)。

## 既存 cron 実装との関係 (運用観察)

ユーザー環境には先行実装として `~/dotfiles/bin/notify-pending-discord.sh` (4/22 作成、daily/weekly 起動済) と `/home/otaku/bin/audit-{weekly,quarterly,monthly}.sh` (旧 dotfiles 残骸候補) が存在する。本 docs の `agentops-watch notify` 設計は **これらの後継** として位置づけるが、実 cron 切替・実スクリプト置換は **本 docs のスコープ外** (実装 plan で判断)。

サーバー状態通知の `metrics-collect.sh` / `server-report.sh` は Claude Code とは独立した運用であり、本 docs の対象外。

## スコープ外

- `tools/agentops_monitor` の `--kind` 拡張実装本体 + `tools/agentops_monitor/notifiers/discord.py` 等の実体生成 (本 docs は契約のみ)
- グローバル `~/.claude/hooks/session_start.py` / `session_end.py` の実体追加 (別 plan で機密ガードと統合)
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
